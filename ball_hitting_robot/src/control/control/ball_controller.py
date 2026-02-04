#!/usr/bin/env python3
"""
Ball Controller Node for Ball-Hitting Robot

This node subscribes to ball position information from the perception system
and generates navigation commands to approach and hit the ball.

The controller implements a simple state machine:
1. SEARCHING: Rotate to find the ball
2. ALIGNING: Rotate to center the ball in view
3. APPROACHING: Move forward while keeping ball centered
4. HITTING: Final push to hit the ball

Published Topics:
    /cmd_vel (geometry_msgs/Twist): Velocity commands for robot movement
        - linear.x: Forward/backward velocity (m/s)
        - angular.z: Rotation velocity (rad/s)

Subscribed Topics:
    /ball_position (geometry_msgs/Point): Ball position from perception
        - x: Horizontal position (-1.0 to 1.0, 0 is center)
        - y: Vertical position (-1.0 to 1.0, 0 is center)
        - z: Distance score (0.0 far to 1.0 close)

ADJUSTABLE CONTROL PARAMETERS:
==============================

1. ALIGNMENT PARAMETERS:
   - self.alignment_threshold: How centered ball must be (default 0.1)
     Decrease for more precise alignment, increase for faster approach
   
   - self.angular_speed_max: Maximum rotation speed (default 0.5 rad/s)
     Increase for faster turning, decrease for smoother motion
   
   - self.angular_kp: Proportional gain for alignment (default 2.0)
     Increase for more aggressive turning, decrease for gentler turning

2. APPROACH PARAMETERS:
   - self.linear_speed_base: Base forward speed (default 0.3 m/s)
     Increase to approach faster, decrease for more control
   
   - self.linear_speed_max: Maximum forward speed (default 0.5 m/s)
     Safety limit on forward motion
   
   - self.distance_threshold: When to start hitting (default 0.6)
     Distance score above which robot enters hitting phase

3. HITTING PARAMETERS:
   - self.hit_speed: Speed during final hit (default 0.7 m/s)
     Increase for more powerful hit, decrease for gentle push
   
   - self.hit_duration: How long to push (default 2.0 seconds)
     Increase to push farther, decrease for shorter contact

4. TIMEOUT PARAMETERS:
   - self.detection_timeout: Max time without ball detection (default 2.0 s)
     Increase if ball detection is intermittent
   
   - self.search_angular_speed: Rotation speed while searching (default 0.3 rad/s)
     Adjust search pattern speed
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Point
from enum import Enum
import math


class ControlState(Enum):
    """
    States for the ball-hitting robot controller
    
    State transitions:
    SEARCHING -> ALIGNING (when ball detected)
    ALIGNING -> APPROACHING (when ball is centered)
    APPROACHING -> HITTING (when close enough)
    HITTING -> SEARCHING (after hit completes)
    Any state -> SEARCHING (if ball lost for too long)
    """
    SEARCHING = 1    # Rotating to find ball
    ALIGNING = 2     # Centering ball in view
    APPROACHING = 3  # Moving toward centered ball
    HITTING = 4      # Final push to hit ball


class BallController(Node):
    """
    ROS2 node for controlling robot to approach and hit a detected ball
    
    Uses a state machine to manage different phases of the ball-hitting task:
    searching, aligning, approaching, and hitting.
    """
    
    def __init__(self):
        """Initialize the ball controller node with configurable parameters"""
        super().__init__('ball_controller')
        
        # ============================================================
        # CONFIGURATION PARAMETERS - ADJUST THESE FOR YOUR SETUP
        # ============================================================
        
        # Alignment parameters (how to center the ball)
        self.alignment_threshold = 0.1  # Max deviation from center (0-1 scale)
                                        # Smaller = more precise, Larger = more tolerant
        self.angular_speed_max = 0.5    # Max rotation speed (rad/s)
                                        # Increase for faster turning
        self.angular_kp = 2.0           # Proportional gain for rotation control
                                        # Higher = more aggressive turning
        
        # Approach parameters (how to move toward ball)
        self.linear_speed_base = 0.3    # Base forward speed (m/s)
                                        # Increase to approach faster
        self.linear_speed_max = 0.5     # Maximum forward speed (m/s)
                                        # Safety limit
        self.linear_kp = 0.3            # Proportional gain for approach speed
                                        # Higher = accelerate more based on distance
        
        # Distance threshold to trigger hitting
        self.distance_threshold = 0.6   # Distance score (0-1) to start hitting
                                        # Higher = start hitting from farther away
                                        # Lower = get closer before hitting
        
        # Hitting parameters (final push)
        self.hit_speed = 0.7            # Forward speed during hit (m/s)
                                        # Increase for more powerful hit
        self.hit_duration = 2.0         # Duration of hitting motion (seconds)
                                        # Increase to push ball farther
        
        # Search parameters (when ball not visible)
        self.search_angular_speed = 0.3 # Rotation speed while searching (rad/s)
        self.detection_timeout = 2.0    # Max time without detection before searching (s)
        
        # Continuous alignment during approach
        self.approach_angular_kp = 1.5  # Rotation correction while approaching
                                        # Keep turning toward ball while moving forward
        
        # ============================================================
        # END CONFIGURATION PARAMETERS
        # ============================================================
        
        # State machine
        self.state = ControlState.SEARCHING
        self.last_ball_position = None
        self.last_detection_time = None
        
        # Hitting state tracking
        self.hit_start_time = None
        
        # Publisher for velocity commands
        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )
        
        # Subscriber to ball position
        self.ball_position_subscriber = self.create_subscription(
            Point,
            '/ball_position',
            self.ball_position_callback,
            10
        )
        
        # Control loop timer (runs at 10 Hz)
        self.control_timer = self.create_timer(0.1, self.control_loop)
        
        self.get_logger().info('Ball Controller Node initialized')
        self.get_logger().info(f'Initial state: {self.state.name}')
        self.get_logger().info(f'Alignment threshold: {self.alignment_threshold}')
        self.get_logger().info(f'Distance threshold for hitting: {self.distance_threshold}')
    
    def ball_position_callback(self, msg):
        """
        Receive ball position updates from perception system
        
        Args:
            msg (geometry_msgs/Point): Ball position data
                x: Horizontal position in normalized coordinates
                y: Vertical position in normalized coordinates  
                z: Distance score (0.0 = far, 1.0 = close)
        """
        # Store the latest ball position
        self.last_ball_position = msg
        self.last_detection_time = self.get_clock().now()
        
        # Log position periodically for debugging
        # Uncomment for detailed logging:
        # self.get_logger().info(
        #     f'Ball at x={msg.x:.2f}, y={msg.y:.2f}, dist={msg.z:.2f}'
        # )
    
    def control_loop(self):
        """
        Main control loop - called at regular intervals (10 Hz)
        
        Implements state machine logic and generates velocity commands
        based on current state and ball position.
        """
        # Create velocity command message
        cmd = Twist()
        
        # Get current time for timeout checks
        current_time = self.get_clock().now()
        
        # Check if we've lost the ball (no recent detections)
        if self.last_detection_time is None or \
           (current_time - self.last_detection_time).nanoseconds / 1e9 > self.detection_timeout:
            # Ball not detected recently - enter searching state
            if self.state != ControlState.SEARCHING:
                self.get_logger().info('Ball lost - entering SEARCHING state')
                self.state = ControlState.SEARCHING
        
        # State machine logic
        if self.state == ControlState.SEARCHING:
            cmd = self.search_behavior()
            
        elif self.state == ControlState.ALIGNING:
            cmd = self.align_behavior()
            
        elif self.state == ControlState.APPROACHING:
            cmd = self.approach_behavior()
            
        elif self.state == ControlState.HITTING:
            cmd = self.hit_behavior()
        
        # Publish velocity command
        self.cmd_vel_publisher.publish(cmd)
    
    def search_behavior(self):
        """
        Search for the ball by rotating in place
        
        Returns:
            Twist: Velocity command for searching (pure rotation)
        """
        cmd = Twist()
        
        # If ball is detected, transition to aligning
        if self.last_ball_position is not None and self.last_detection_time is not None:
            if (self.get_clock().now() - self.last_detection_time).nanoseconds / 1e9 < self.detection_timeout:
                self.get_logger().info('Ball detected - entering ALIGNING state')
                self.state = ControlState.ALIGNING
                return cmd
        
        # Rotate in place to search for ball
        cmd.angular.z = self.search_angular_speed
        
        return cmd
    
    def align_behavior(self):
        """
        Align robot to center the ball in camera view
        
        Returns:
            Twist: Velocity command for alignment (rotation only)
        """
        cmd = Twist()
        
        if self.last_ball_position is None:
            return cmd
        
        # Get horizontal position of ball (-1 to 1, where 0 is centered)
        ball_x = self.last_ball_position.x
        
        # Check if ball is centered enough
        if abs(ball_x) < self.alignment_threshold:
            # Ball is centered - transition to approaching
            self.get_logger().info('Ball aligned - entering APPROACHING state')
            self.state = ControlState.APPROACHING
            return cmd
        
        # Calculate rotation speed using proportional control
        # Positive ball_x means ball is to the left, so rotate left (positive angular.z)
        angular_velocity = self.angular_kp * ball_x
        
        # Clamp to maximum angular speed
        angular_velocity = max(-self.angular_speed_max, 
                              min(self.angular_speed_max, angular_velocity))
        
        cmd.angular.z = angular_velocity
        
        return cmd
    
    def approach_behavior(self):
        """
        Approach the ball while maintaining alignment
        
        Returns:
            Twist: Velocity command for approaching (forward motion + alignment correction)
        """
        cmd = Twist()
        
        if self.last_ball_position is None:
            return cmd
        
        ball_x = self.last_ball_position.x
        ball_distance = self.last_ball_position.z
        
        # If ball moves out of alignment, go back to aligning
        if abs(ball_x) > self.alignment_threshold * 2:
            self.get_logger().info('Ball out of alignment - returning to ALIGNING state')
            self.state = ControlState.ALIGNING
            return cmd
        
        # Check if close enough to hit
        if ball_distance > self.distance_threshold:
            self.get_logger().info(
                f'Close enough to hit (distance={ball_distance:.2f}) - entering HITTING state'
            )
            self.state = ControlState.HITTING
            self.hit_start_time = self.get_clock().now()
            return cmd
        
        # Calculate forward speed based on distance
        # Closer = faster (to maintain momentum for hit)
        linear_velocity = self.linear_speed_base + self.linear_kp * ball_distance
        linear_velocity = min(self.linear_speed_max, linear_velocity)
        
        # Maintain alignment while approaching (subtle correction)
        angular_velocity = self.approach_angular_kp * ball_x
        angular_velocity = max(-self.angular_speed_max * 0.5,
                              min(self.angular_speed_max * 0.5, angular_velocity))
        
        cmd.linear.x = linear_velocity
        cmd.angular.z = angular_velocity
        
        return cmd
    
    def hit_behavior(self):
        """
        Execute hitting motion - full speed forward push
        
        Returns:
            Twist: Velocity command for hitting (maximum forward speed)
        """
        cmd = Twist()
        
        # Check if hit duration has elapsed
        if self.hit_start_time is not None:
            elapsed_time = (self.get_clock().now() - self.hit_start_time).nanoseconds / 1e9
            
            if elapsed_time > self.hit_duration:
                # Hit complete - stop and return to searching
                self.get_logger().info('Hit complete - entering SEARCHING state')
                self.state = ControlState.SEARCHING
                self.last_ball_position = None
                self.hit_start_time = None
                return cmd
        
        # Full speed forward for the hit
        cmd.linear.x = self.hit_speed
        
        # Small alignment correction during hit
        if self.last_ball_position is not None:
            ball_x = self.last_ball_position.x
            cmd.angular.z = self.approach_angular_kp * ball_x * 0.5
        
        return cmd


def main(args=None):
    """
    Main entry point for the ball controller node
    
    Args:
        args: Command line arguments (None uses sys.argv)
    """
    # Initialize ROS2 Python client library
    rclpy.init(args=args)
    
    # Create the ball controller node
    ball_controller = BallController()
    
    try:
        # Spin the node to process callbacks
        rclpy.spin(ball_controller)
    except KeyboardInterrupt:
        # Handle graceful shutdown on Ctrl+C
        pass
    finally:
        # Send stop command before shutdown
        stop_cmd = Twist()
        ball_controller.cmd_vel_publisher.publish(stop_cmd)
        
        # Cleanup
        ball_controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
