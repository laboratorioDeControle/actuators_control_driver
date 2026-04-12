import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import math
import time

class LoraSimulatorNode(Node):
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

    def run(self):
        import serial
        ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
        print("Receptor iniciado. Aguardando comandos...")
        thruster_msg = Float64MultiArray()
        rudder_msg = Float64MultiArray()
        try:
            while rclpy.ok():
                linha = ser.readline().decode('utf-8').strip()
                if linha:
                    try:
                        angulo_str, velocidade_str = linha.split(",")
                        angulo = math.radians(float(angulo_str))
                        velocidade = float(velocidade_str)
                        print(f"Recebido: Ângulo={angulo}, Velocidade={velocidade}")
                        # Simula um valor de setpoint para thruster
                        thruster_msg.data = [velocidade]  # Exemplo: 30% da potência máxima
                        self.thruster_pub.publish(thruster_msg)
                        rudder_msg.data = [angulo, 0.0, -angulo, 0.0]    
                        self.rudder_pub.publish(rudder_msg)
                    except ValueError:
                        print("Mensagem inválida:", linha)
        except KeyboardInterrupt:
            pass
        finally:
            ser.close()
        
def main(args=None):
    rclpy.init(args=args)
    node = LoraSimulatorNode()
    try:
        node.run()
    except KeyboardInterrupt:
        node.zero_outputs()
    finally:
        node.zero_outputs()
        node.destroy_node()
        rclpy.shutdown()
