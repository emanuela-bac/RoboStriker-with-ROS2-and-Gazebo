#!/usr/bin/env python3
"""
Ball Detection Node for Ball-Hitting Robot

This node subscribes to camera images, detects a red ball using color-based
segmentation with OpenCV, and publishes the ball's relative position.

Published Topics:
    /ball_position (geometry_msgs/Point): Relative position of detected ball
        - x: Horizontal position in image coordinates (-1.0 to 1.0, 0 is center)
        - y: Vertical position in image coordinates (-1.0 to 1.0, 0 is center)  
        - z: Estimated distance based on ball size (0.0 to 1.0, smaller = farther)

Subscribed Topics:
    /camera/image_raw (sensor_msgs/Image): Raw camera images from robot

ADJUSTABLE DETECTION PARAMETERS:
================================

1. COLOR DETECTION (Modify HSV ranges in __init__):
   - self.lower_red: Lower bound of red color in HSV
   - self.upper_red: Upper bound of red color in HSV
   
   For different colors:
   - Blue: lower=[100, 100, 100], upper=[130, 255, 255]
   - Green: lower=[40, 40, 40], upper=[80, 255, 255]
   - Yellow: lower=[20, 100, 100], upper=[30, 255, 255]

2. DETECTION SENSITIVITY:
   - self.min_contour_area: Minimum size to consider (default 500 pixels)
     Increase to ignore small noise, decrease to detect smaller/farther balls
   
   - self.blur_kernel: Gaussian blur size (default 15)
     Increase for more noise reduction, decrease for sharper detection
   
   - Morphological operations (erode/dilate iterations):
     Increase to remove more noise, decrease to preserve detail

3. DISTANCE ESTIMATION:
   - self.reference_ball_radius: Expected ball size at known distance (default 100 pixels)
     Adjust based on your camera and ball size
   
   - Distance calculation in calculate_distance():
     Modify the formula to match your specific setup

4. VISUALIZATION:
   - self.show_debug: Set to True to display annotated camera feed
     Useful for tuning detection parameters
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
import cv2
import numpy as np


class BallDetector(Node):
    """
    ROS2 node for detecting a colored ball in camera images
    
    This node uses HSV color space filtering and contour detection
    to identify and locate a ball in the robot's camera view.
    """
    
    def __init__(self):
        """Initialize the ball detector node with configurable parameters"""
        super().__init__('ball_detector')
        
        # ============================================================
        # CONFIGURATION PARAMETERS - ADJUST THESE FOR YOUR SETUP
        # ============================================================
        
        # HSV Color Range for RED ball detection
        # HSV is better than RGB for color detection under varying lighting
        # Red wraps around in HSV space, so we need two ranges
        # Range 1: Lower red values (0-10 in Hue)
        self.lower_red1 = np.array([0, 100, 100])
        self.upper_red1 = np.array([10, 255, 255])
        # Range 2: Upper red values (170-180 in Hue)
        self.lower_red2 = np.array([170, 100, 100])
        self.upper_red2 = np.array([180, 255, 255])
        
        # Alternative: Single range for other colors
        # Uncomment and modify for different ball colors:
        # self.lower_color = np.array([100, 100, 100])  # Blue
        # self.upper_color = np.array([130, 255, 255])
        
        # Detection sensitivity parameters
        self.min_contour_area = 500  # Minimum area in pixels to consider as ball
                                      # Increase (e.g., 1000) to ignore small objects
                                      # Decrease (e.g., 200) to detect smaller/distant balls
        
        self.blur_kernel = 15  # Gaussian blur kernel size (must be odd)
                               # Increase (e.g., 21) for more noise reduction
                               # Decrease (e.g., 7) for sharper but noisier detection
        
        # Morphological operation parameters for noise removal
        self.erode_iterations = 2   # Number of erosion passes (removes small noise)
        self.dilate_iterations = 2  # Number of dilation passes (fills gaps)
        
        # Distance estimation parameters
        self.reference_ball_radius = 100  # Expected radius in pixels at reference distance
                                          # Calibrate by measuring ball size at known distance
        
        # Debug visualization flag
        self.show_debug = False  # Set to True to see annotated images
                                 # (Opens CV2 window - not recommended for headless systems)
        
        # ============================================================
        # END CONFIGURATION PARAMETERS
        # ============================================================
        
        # Bridge between ROS and OpenCV images
        self.bridge = CvBridge()
        
        # Publisher for ball position
        self.position_publisher = self.create_publisher(
            Point,
            '/ball_position',
            10
        )
        
        # Subscriber to camera images
        self.image_subscriber = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        
        # State variables
        self.last_detection_time = self.get_clock().now()
        self.detection_count = 0
        
        self.get_logger().info('Ball Detector Node initialized')
        self.get_logger().info(f'Detecting balls with minimum area: {self.min_contour_area} pixels')
        self.get_logger().info(f'Debug visualization: {self.show_debug}')
    
    def image_callback(self, msg):
        """
        Process incoming camera images to detect the ball
        
        Args:
            msg (sensor_msgs/Image): Incoming camera image message
        """
        try:
            # Convert ROS Image message to OpenCV format (BGR color space)
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # Detect the ball in the image
            ball_position, annotated_image = self.detect_ball(cv_image)
            
            # If ball is detected, publish its position
            if ball_position is not None:
                self.position_publisher.publish(ball_position)
                self.detection_count += 1
                
                # Log detection periodically (every 30 detections)
                if self.detection_count % 30 == 0:
                    self.get_logger().info(
                        f'Ball detected at x={ball_position.x:.2f}, '
                        f'y={ball_position.y:.2f}, '
                        f'distance_score={ball_position.z:.2f}'
                    )
            
            # Display debug window if enabled
            if self.show_debug:
                cv2.imshow('Ball Detection', annotated_image)
                cv2.waitKey(1)
                
        except Exception as e:
            self.get_logger().error(f'Error processing image: {str(e)}')
    
    def detect_ball(self, image):
        """
        Detect red ball in image using color segmentation
        
        This function performs the following steps:
        1. Blur the image to reduce noise
        2. Convert to HSV color space (better for color detection)
        3. Create color mask using HSV thresholds
        4. Apply morphological operations to clean up mask
        5. Find contours in the mask
        6. Identify largest contour as the ball
        7. Calculate ball's relative position
        
        Args:
            image (numpy.ndarray): Input image in BGR format
            
        Returns:
            tuple: (ball_position, annotated_image)
                - ball_position (geometry_msgs/Point or None): Detected ball position
                - annotated_image (numpy.ndarray): Image with detection visualization
        """
        # Get image dimensions
        height, width = image.shape[:2]
        
        # Step 1: Apply Gaussian blur to reduce noise and improve detection
        blurred = cv2.GaussianBlur(image, (self.blur_kernel, self.blur_kernel), 0)
        
        # Step 2: Convert from BGR (OpenCV default) to HSV color space
        # HSV is more robust to lighting changes than RGB/BGR
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        
        # Step 3: Create binary mask for red color
        # Red wraps around in HSV, so we need two masks
        mask1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
        mask2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # For single-range colors (uncomment if using alternative color):
        # mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
        
        # Step 4: Morphological operations to remove noise
        # Erosion removes small white noise
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=self.erode_iterations)
        # Dilation fills in gaps and enlarges remaining objects
        mask = cv2.dilate(mask, kernel, iterations=self.dilate_iterations)
        
        # Step 5: Find contours (boundaries) in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create annotated image for visualization
        annotated_image = image.copy()
        
        # Initialize ball position as None (not detected)
        ball_position = None
        
        # Step 6: Find the largest contour (assumed to be the ball)
        if contours:
            # Sort contours by area and get the largest
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            # Only consider it a ball if it's large enough
            if area > self.min_contour_area:
                # Calculate the minimum enclosing circle around the contour
                ((x, y), radius) = cv2.minEnclosingCircle(largest_contour)
                
                # Calculate moments for more accurate centroid
                M = cv2.moments(largest_contour)
                if M["m00"] > 0:
                    # Centroid coordinates
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    # Step 7: Calculate relative position
                    # Convert pixel coordinates to normalized coordinates [-1, 1]
                    # where (0, 0) is image center
                    relative_x = (cx - width / 2) / (width / 2)
                    relative_y = (cy - height / 2) / (height / 2)
                    
                    # Estimate distance based on ball size (larger = closer)
                    distance_score = self.calculate_distance(radius)
                    
                    # Create Point message with ball position
                    ball_position = Point()
                    ball_position.x = float(relative_x)
                    ball_position.y = float(relative_y)
                    ball_position.z = float(distance_score)
                    
                    # Draw detection on annotated image
                    # Draw circle around detected ball
                    cv2.circle(annotated_image, (int(x), int(y)), int(radius), (0, 255, 0), 3)
                    # Draw crosshair at center
                    cv2.circle(annotated_image, (cx, cy), 5, (0, 0, 255), -1)
                    # Draw bounding box
                    cv2.drawContours(annotated_image, [largest_contour], 0, (255, 0, 0), 2)
                    
                    # Add text with position information
                    text = f'Ball: ({relative_x:.2f}, {relative_y:.2f}) dist={distance_score:.2f}'
                    cv2.putText(annotated_image, text, (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw center crosshair on image
        cv2.line(annotated_image, (width // 2 - 20, height // 2),
                (width // 2 + 20, height // 2), (0, 255, 255), 2)
        cv2.line(annotated_image, (width // 2, height // 2 - 20),
                (width // 2, height // 2 + 20), (0, 255, 255), 2)
        
        return ball_position, annotated_image
    
    def calculate_distance(self, detected_radius):
        """
        Calculate relative distance score based on detected ball size
        
        This is a simplified distance estimation. For more accurate results,
        you would need to:
        1. Know the actual ball size in meters
        2. Know camera intrinsic parameters (focal length)
        3. Use pinhole camera model: distance = (actual_size * focal_length) / pixel_size
        
        Args:
            detected_radius (float): Radius of detected ball in pixels
            
        Returns:
            float: Distance score from 0.0 (far) to 1.0 (close)
        """
        # Normalize by reference radius
        # Larger detected radius = closer = higher score
        if detected_radius > 0:
            # Cap the score at 1.0 (very close)
            distance_score = min(detected_radius / self.reference_ball_radius, 1.0)
        else:
            distance_score = 0.0
        
        return distance_score


def main(args=None):
    """
    Main entry point for the ball detector node
    
    Args:
        args: Command line arguments (None uses sys.argv)
    """
    # Initialize ROS2 Python client library
    rclpy.init(args=args)
    
    # Create the ball detector node
    ball_detector = BallDetector()
    
    try:
        # Spin the node to process callbacks
        rclpy.spin(ball_detector)
    except KeyboardInterrupt:
        # Handle graceful shutdown on Ctrl+C
        pass
    finally:
        # Cleanup
        ball_detector.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
