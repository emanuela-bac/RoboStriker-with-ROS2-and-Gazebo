import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
import time

class FakeBallPublisher(Node):
    def __init__(self):
        super().__init__('fake_ball_publisher')
        # Publică pe același topic pe care îl așteaptă nodul tău de control
        # Publish to absolute topic so controller definitely receives it
        self.publisher_ = self.create_publisher(Point, '/ball_position', 10)
        
        # Publish rapidly so the controller transitions immediately
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
    # Secvența de poziții (Z = Distanța; X = Offset Lateral)
    # Positions designed to quickly drive the controller through states:
        # Align immediately, approach briefly, then trigger hit
        self.positions = [
            Point(x=0.0, y=0.0, z=0.3),  # aligned, moderate distance -> APPROACHING
            Point(x=0.0, y=0.0, z=0.7),  # aligned, close -> HITTING
            Point(x=0.0, y=0.0, z=0.7),  # keep sending close alignment during hit
        ]
        self.sequence_index = 0
        self.get_logger().info('Fake Ball Publisher initialized. Starting sequence.')

    def timer_callback(self):
        current_position = self.positions[self.sequence_index]
        self.publisher_.publish(current_position)
        
        self.get_logger().info(
            f'Published demo position {self.sequence_index + 1}: '
            f'x={current_position.x:.2f}, z={current_position.z:.2f} '
            f'-> driving APPROACHING/HITTING'
        )

        # Trecem la următoarea poziție, și revenim la început când terminăm secvența
        self.sequence_index = (self.sequence_index + 1) % len(self.positions)

def main(args=None):
    rclpy.init(args=args)
    fake_ball_publisher = FakeBallPublisher()
    try:
        rclpy.spin(fake_ball_publisher)
    except KeyboardInterrupt:
        pass
    finally:
        fake_ball_publisher.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()