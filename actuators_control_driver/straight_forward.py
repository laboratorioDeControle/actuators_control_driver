import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import math
import time

class StraightForwardNode(Node):
    def __init__(self):
        super().__init__('straight_forward_node')
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

    def stop_all(self):
        """Garante que todos os atuadores parem (mesmo sem hardware)."""
        try:
            self.get_logger().info("Parando todos os atuadores...")
            if self._thruster:
                self._thruster.speed_percent = 0.0
            if self._servo_top:
                self._servo_top.angle = 0.0
            if self._servo_right:
                self._servo_right.angle = 0.0
            if self._servo_down:
                self._servo_down.angle = 0.0
            if self._servo_left:
                self._servo_left.angle = 0.0
        except Exception as e:
            self.get_logger().error(f"Erro ao parar atuadores: {e}")

    def destroy_node(self):
        """Sobrescreve destroy_node para garantir parada segura."""
        self.stop_all()
        super().destroy_node()

        
    def publish_pattern(self):
        now = self.get_clock().now().seconds_nanoseconds()[0]
        elapsed = now - self.start_time
        thruster_msg = Float64MultiArray()
        rudder_msg = Float64MultiArray()
        # 0-3s: [0.0, pi/2, 0.0, -pi/2]
        if elapsed < 3:
            thruster_msg.data = [0.5]
            rudder_msg.data = [0.0, 0.0, 0.0, 0.0]    
        else:
            thruster_msg.data = [0.0]
            rudder_msg.data = [0.0, 0.0, 0.0, 0.0]
            return
        self.thruster_pub.publish(thruster_msg)
        self.rudder_pub.publish(rudder_msg)
        self.get_logger().info(f'Published: Rudder={rudder_msg.data} and Thruster={thruster_msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = StraightForwardNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Ctrl+C detectado. Encerrando com segurança...")
        node.stop_all()
    finally:
        node.destroy_node()
        rclpy.shutdown()
