
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import math
import time


class DiveMissionNode(Node):
	def __init__(self):
		super().__init__('dive_mission_node')
		self.thruster_pub = self.create_publisher(Float64MultiArray, '/controller/thrusters_setpoints', 10)
		self.rudder_pub = self.create_publisher(Float64MultiArray, '/controller/rudders_setpoints', 10)

		self.declare_parameter('start_still_duration', 10)
		self.declare_parameter('start_thruster_duration', 5)
		self.declare_parameter('alternancia_duration', 5)
		self.declare_parameter('thruster_power', 0.5)
		self.declare_parameter('rudder_angle_deg', 20)
		self.declare_parameter('num_alternancias', 4)

		self.start_still_duration = self.get_parameter('start_still_duration').get_parameter_value().double_value
		self.start_thruster_duration = self.get_parameter('start_thruster_duration').get_parameter_value().double_value
		self.alternancia_duration = self.get_parameter('alternancia_duration').get_parameter_value().double_value
		self.thruster_power = self.get_parameter('thruster_power').get_parameter_value().double_value
		self.rudder_angle_deg = self.get_parameter('rudder_angle_deg').get_parameter_value().double_value
		self.num_alternancias = int(self.get_parameter('num_alternancias').get_parameter_value().integer_value)

	def run(self):
		# Fase 1: Todas as saídas zeradas
		self.get_logger().info(f'Fase 1: Todas as saídas zeradas por {self.start_still_duration} segundos')
		self.publish_setpoints(thruster=0.0, rudders=[0.0, 0.0, 0.0, 0.0])
		time.sleep(self.start_still_duration)

		# Fase 2: Thruster 50%, rudders zerados
		self.get_logger().info(f'Fase 2: Thruster {self.thruster_power*100:.0f}%, rudders zerados por {self.start_thruster_duration} segundos')
		self.publish_setpoints(thruster=self.thruster_power, rudders=[0.0, 0.0, 0.0, 0.0])
		time.sleep(self.start_thruster_duration)

		# Fase 3: Alternância dos lemes 2 e 4
		angle_rad_pos = math.radians(self.rudder_angle_deg)
		angle_rad_neg = math.radians(-self.rudder_angle_deg)
		self.get_logger().info(f'Fase 3: Alternando lemes 2 e 4 entre +{self.rudder_angle_deg} e -{self.rudder_angle_deg} graus, {self.num_alternancias} vezes, cada alternância por {self.alternancia_duration} segundos')
		for i in range(self.num_alternancias):
			if i % 2 == 0:
				self.publish_setpoints(thruster=self.thruster_power, rudders=[0.0, angle_rad_pos, 0.0, angle_rad_pos])
				self.get_logger().info(f'Alternância {i+1}: +{self.rudder_angle_deg} graus')
				time.sleep(self.alternancia_duration)
			else:
				self.publish_setpoints(thruster=self.thruster_power, rudders=[0.0, angle_rad_neg, 0.0, angle_rad_neg])
				self.get_logger().info(f'Alternância {i+1}: -{self.rudder_angle_deg} graus')
				time.sleep(self.alternancia_duration)

		self.get_logger().info('Missão finalizada.')

	def publish_setpoints(self, thruster, rudders):
		thruster_msg = Float64MultiArray()
		thruster_msg.data = [thruster]
		rudder_msg = Float64MultiArray()
		rudder_msg.data = rudders
		self.thruster_pub.publish(thruster_msg)
		self.rudder_pub.publish(rudder_msg)

# Exemplo de uso:
if __name__ == '__main__':
	rclpy.init()
	node = DiveMissionNode()
	try:
		node.run()
	finally:
		node.destroy_node()
		rclpy.shutdown()