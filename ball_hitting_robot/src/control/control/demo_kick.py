#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class DemoKick(Node):
    """
    Simple publisher that drives the robot forward briefly to kick the ball.
    Publishes on /cmd_vel so the ros_gz_bridge maps it to the DiffDrive topic.
    """
    def __init__(self):
        super().__init__('demo_kick')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self._tick)  # 10 Hz
        self.start_time = self.get_clock().now()
        self.phase = 'align'  # align -> approach -> hit -> stop
        self.get_logger().info('DemoKick started: will auto-drive to kick the ball.')

    def _tick(self):
        elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
        cmd = Twist()
        if elapsed < 1.0:
            # short rotation to face the ball (if needed)
            cmd.angular.z = 0.3
        elif elapsed < 6.0:
            # longer approach to reach the ball
            cmd.linear.x = 0.5
        elif elapsed < 9.0:
            # hit harder for a clear kick
            cmd.linear.x = 1.0
        else:
            # stop and exit
            try:
                if rclpy.ok():
                    self.pub.publish(Twist())
            except Exception:
                pass
            self.get_logger().info('DemoKick complete, stopping publisher (node stays alive).')
            # Cancel timer to stop publishing; leave shutdown to main finally
            self.timer.cancel()
            return
        self.pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = DemoKick()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
