import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import math
import time

class YoyoNode(Node):
    def __init__(self):
        super().__init__('yoyo_node')
        self.thruster_pub = self.create_publisher(
            Float64MultiArray,
            '/controller/thrusters_setpoints',
            10)
        self.rudder_pub = self.create_publisher(
            Float64MultiArray,
            '/controller/rudders_setpoints',
            10)
        self.timer = self.create_timer(0.1, self.publish_pattern)
        self.start_time = self.get_clock().now().seconds_nanoseconds()[0]

    def zero_outputs(self):
        thruster_msg = Float64MultiArray()
        thruster_msg.data = [0.0]
        self.thruster_pub.publish(thruster_msg)
        rudder_msg = Float64MultiArray()
        rudder_msg.data = [0.0, 0.0, 0.0, 0.0]
        self.rudder_pub.publish(rudder_msg)
        self.get_logger().info('All outputs set to zero.')
        
    def publish_pattern(self):
        now = self.get_clock().now().seconds_nanoseconds()[0]
        elapsed = now - self.start_time
        thruster_msg = Float64MultiArray()
        rudder_msg = Float64MultiArray()
        # 0-3s: [0.0, pi/2, 0.0, -pi/2]
        if elapsed < 30:
            thruster_msg.data = [0.0]
            rudder_msg.data = [0.0, 0.0, 0.0, 0.0]
        elif elapsed < 35:
            thruster_msg.data = [0.4]
            rudder_msg.data = [0.0, 0.0, 0.0, 0.0]
        elif elapsed < 40:
            thruster_msg.data = [0.9]
            rudder_msg.data = [0.0, math.pi * 0.3, 0.0, -math.pi * 0.3]
        # 3-8s: [0.0, 0.0, 0.0, 0.0]
        # elif elapsed < 60:
        #     thruster_msg.data = [0.7]
        #     rudder_msg.data = [0.0, 0.0, 0.0, 0.0]
        # # 8-11s: [0.0, -pi/2, 0.0, pi/2]
        elif elapsed < 60:
            thruster_msg.data = [0.9]
            rudder_msg.data = [0.0, -math.pi * 0.3, 0.0, math.pi * 0.3]
        # 12-17s: [0.0, 0.0, 0.0, 0.0]
        elif elapsed < 90:
            thruster_msg.data = [0.0]
            rudder_msg.data = [0.0, 0.0, 0.0, 0.0]    
        else:
            thruster_msg.data = [0.0]
            rudder_msg.data = [0.0, 0.0, 0.0, 0.0]  
            # Optionally, stop or repeat
            #self.start_time = now
            return
        self.thruster_pub.publish(thruster_msg)
        self.rudder_pub.publish(rudder_msg)
        self.get_logger().info(f'Published: Rudder={rudder_msg.data} and Thruster={thruster_msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = YoyoNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.zero_outputs()
    finally:
        node.zero_outputs()
        node.destroy_node()
        rclpy.shutdown()
