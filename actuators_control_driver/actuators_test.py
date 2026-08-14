import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import math

class ActuatorsTestNode(Node):
    def __init__(self):
        super().__init__('actuators_test_node')

        # Publishers
        self.thruster_pub = self.create_publisher(Float64MultiArray, '/controller/thrusters_setpoints', 10)
        self.rudder_pub = self.create_publisher(Float64MultiArray, '/controller/rudders_setpoints', 10)

        # Timer e referência de tempo
        self.timer = self.create_timer(0.5, self.publish_pattern)
        self.start_time = self.get_clock().now().seconds_nanoseconds()[0]

    def publish_pattern(self):
        now = self.get_clock().now().seconds_nanoseconds()[0]
        elapsed = now - self.start_time

        # Mensagens padrão
        thruster_msg = Float64MultiArray()
        thruster_msg.data = [0.0]
        rudder_msg = Float64MultiArray()
        rudder_msg.data = [0.0, 0.0, 0.0, 0.0]

        # Fase 0: thruster
        if 0 <= elapsed < 2:
            thruster_msg.data = [0.5]
            self.get_logger().info('Testing thruster')

        # Fase 1: rudder 1
        elif 1 <= elapsed < 3:
            rudder_msg.data[0] = math.pi * 0.5
            self.get_logger().info('Testing rudder 1')

        # Fase 2: rudder 2
        elif 2 <= elapsed < 4:
            rudder_msg.data[1] = math.pi * 0.5
            self.get_logger().info('Testing rudder 2')

        # Fase 3: rudder 3
        elif 3 <= elapsed < 5:
            rudder_msg.data[2] = math.pi * 0.5
            self.get_logger().info('Testing rudder 3')

        # Fase 4: rudder 4
        elif 4 <= elapsed < 6:
            rudder_msg.data[3] = math.pi * 0.5
            self.get_logger().info('Testing rudder 4')

        # Fim: encerra o nó após completar as 5 fases
        elif elapsed >= 7:
            self.get_logger().info('Test sequence complete.')
            raise rclpy.executors.ExternalShutdownException()

        # Publica mensagens
        self.thruster_pub.publish(thruster_msg)
        self.rudder_pub.publish(rudder_msg)

def main(args=None):
    rclpy.init(args=args)
    node = ActuatorsTestNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except rclpy.executors.ExternalShutdownException:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()