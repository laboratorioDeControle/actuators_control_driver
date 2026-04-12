import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import math
import time

class SimulatorNode(Node):
    def __init__(self):
        super().__init__('guidance_simulator')
        self.thruster_pub = self.create_publisher(
            Float64MultiArray,
            '/controller/thrusters_setpoints',
            10)
        self.rudder_pub = self.create_publisher(
            Float64MultiArray,
            '/controller/rudders_setpoints',
            10)
        self.timer = self.create_timer(1.0, self.publish_test_data)
        self.angle = -math.pi * 0.5  # Começa em -pi/2
        self.direction = 1     # 1 para crescente, -1 para decrescente
        self.count = 0

    def test_rudder(self):
        """Alterna entre dois comandos de rudder por 5 segundos cada, em loop infinito."""
        while rclpy.ok():
            # Primeiro comando
            rudder_msg = Float64MultiArray()
            rudder_msg.data = [0.0, 0.0, 0.0, 0.0]
            i = self.count % 4
            rudder_msg.data[i] = self.angle
            self.rudder_pub.publish(rudder_msg)
            self.get_logger().info(f'test_rudder: {rudder_msg.data}')
            time.sleep(1)
            self.count += 1
            
    def publish_test_data(self):
        # Simula um valor de setpoint para thruster
        thruster_msg = Float64MultiArray()
        thruster_msg.data = [0.0]  # Exemplo: 30% da potência máxima
        self.thruster_pub.publish(thruster_msg)

        # Simula valores de setpoint para os 4 servos (em radianos)
        rudder_msg = Float64MultiArray()
        rudder_msg.data = [self.angle, 0.0, -self.angle, 0.0]
        self.rudder_pub.publish(rudder_msg)

        self.get_logger().info(f'Publicado: Thruster={thruster_msg.data}, Rudder={rudder_msg.data}')

        # Atualiza o ângulo de 15 em 15 graus (em radianos)
        step = math.radians(45)
        self.angle += self.direction * step

        # Inverte a direção ao atingir os limites
        if self.angle > math.pi * 0.5:
            self.angle = math.pi * 0.5
            self.direction = -1
        elif self.angle < -math.pi * 0.5:
            self.angle = -math.pi * 0.5
            self.direction = 1

def main(args=None):
    rclpy.init(args=args)
    node = SimulatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()