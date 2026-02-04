import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
# Importăm tipul de mesaj de la Gazebo (Statele modelului)
from gazebo_msgs.msg import ModelState 
import math

class BallPerceptor(Node):
    def __init__(self):
        super().__init__('ball_perceptor')
        
        # Subscriber: Ascultă poziția reală a mingii publicată de Gazebo (Ground Truth)
        # Topic: /gazebo/ball_position_gt (Definit în fișierul World)
        self.state_subscription = self.create_subscription(
            ModelState,
            '/gazebo/ball_position_gt',
            self.state_callback,
            10)
        
        # Publisher: Publică pe topicul așteptat de ball_controller
        self.ball_position_publisher = self.create_publisher(
            Point,
            'ball_position', 
            10)
        
        self.get_logger().info('Ball Perceptor Node initialized, subscribing to Gazebo state...')

    def state_callback(self, msg):
        # Extragem poziția mingii (x, y, z) din mesajul ModelState
        position_in_world = msg.pose.position
        
        # Atenție la conversia cadrelor:
        # Nodul de control așteaptă: X=Lateral, Z=Distanță în față
        # Gazebo (standard): X=Înainte/Înapoi, Y=Lateral
        
        ball_point = Point()
        ball_point.x = position_in_world.y  # Y din Gazebo -> X (Lateral) pentru robot
        ball_point.y = 0.0                  
        ball_point.z = position_in_world.x  # X din Gazebo -> Z (Distanță) pentru robot
        
        self.ball_position_publisher.publish(ball_point)
        # self.get_logger().info(f'Published ball position: x={ball_point.x:.2f}, z={ball_point.z:.2f}')

def main(args=None):
    rclpy.init(args=args)
    ball_perceptor = BallPerceptor()
    try:
        rclpy.spin(ball_perceptor)
    except KeyboardInterrupt:
        pass
    finally:
        ball_perceptor.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()