"""
Game manager node

Responsibilities:
- Subscribe to '/ball_position' (geometry_msgs/Point) published by perception node
- Detect when ball enters goal area (configurable params)
- Increment and publish score on '/game/score' (std_msgs/Int32)
- Publish a reset pose on '/game/reset_pose' (geometry_msgs/Pose) so a spawn/reset helper can act

This node deliberately separates detection/score logic from the simulator-specific
spawn/delete operations so it will work regardless of whether you use classic
Gazebo or the newer gz-sim/ros_gz bridge. Hook a small helper that listens on
`/game/reset_pose` and calls the appropriate simulator spawn/delete services if
you want automated resets.
"""
import rclpy
from rclpy.node import Node

from std_msgs.msg import Int32
from geometry_msgs.msg import Point, Pose, Quaternion


class GameManager(Node):
    def __init__(self):
        super().__init__('game_manager')

        # Parameters
        self.declare_parameter('goal_x', 10.0)
        self.declare_parameter('goal_half_width', 1.0)
        self.declare_parameter('reset_pose_x', 3.0)
        self.declare_parameter('reset_pose_y', 0.0)
        self.declare_parameter('reset_pose_z', 0.2)

        self.goal_x = self.get_parameter('goal_x').value
        self.goal_half_width = self.get_parameter('goal_half_width').value
        self.reset_pose_x = self.get_parameter('reset_pose_x').value
        self.reset_pose_y = self.get_parameter('reset_pose_y').value
        self.reset_pose_z = self.get_parameter('reset_pose_z').value

        # State
        self.score = 0
        self._last_goal_time = None
        self._goal_cooldown = 1.0  # seconds to avoid duplicate counts

        # Publishers
        self.score_pub = self.create_publisher(Int32, '/game/score', 10)
        self.reset_pose_pub = self.create_publisher(Pose, '/game/reset_pose', 10)

        # Subscriber to ball_position
        self.ball_sub = self.create_subscription(Point, '/ball_position', self.ball_cb, 10)

        self.get_logger().info('GameManager started: goal_x=%.2f, half_width=%.2f' % (self.goal_x, self.goal_half_width))

    def ball_cb(self, msg: Point):
        # Check if ball crossed the goal plane in +x direction and is within width
        import time
        now = time.time()
        if msg.x >= self.goal_x and abs(msg.y) <= self.goal_half_width:
            # Debounce goals by cooldown
            if self._last_goal_time is None or (now - self._last_goal_time) > self._goal_cooldown:
                self._last_goal_time = now
                self.score += 1
                self.get_logger().info('GOAL! score=%d (ball at x=%.2f y=%.2f)' % (self.score, msg.x, msg.y))
                score_msg = Int32()
                score_msg.data = self.score
                self.score_pub.publish(score_msg)

                # Publish reset pose for whoever is responsible for respawning the ball
                reset = Pose()
                reset.position.x = float(self.reset_pose_x)
                reset.position.y = float(self.reset_pose_y)
                reset.position.z = float(self.reset_pose_z)
                # keep a neutral orientation
                reset.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
                self.reset_pose_pub.publish(reset)


def main(args=None):
    rclpy.init(args=args)
    node = GameManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
