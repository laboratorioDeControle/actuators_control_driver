import time
import math
from actuators_control_driver.thruster import *
from actuators_control_driver.servo import Servo

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

import can


class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')

        self.get_logger().info("Inicializando ControlNode...")

        # ======================================================
        # Inicialização Barramento CAN / Hardware
        # ======================================================
        self._can_bus = can.interface.Bus(channel='can0', bustype='socketcan', bitrate=250000)

        # ======================================================
        # Inicialização dos dispositivos
        # ======================================================
        self._thruster = Thruster()
        self._servo_top = Servo()
        self._servo_right = Servo()
        self._servo_down = Servo()
        self._servo_left = Servo()

        # ======================================================
        # Assinaturas ROS 2
        # ======================================================
        self.thruster_sub = self.create_subscription(
            Float64MultiArray,
            '/lauv/controller/thrusters_setpoints',
            self.thruster_callback,
            10)

        self.rudder_sub = self.create_subscription(
            Float64MultiArray,
            '/lauv/controller/rudders_setpoints',
            self.rudder_callback,
            10)

        self.get_logger().info('ControlNode iniciado com sucesso.')

    # ======================================================
    # Callback do Thruster
    # ======================================================
    def thruster_callback(self, msg):
        if not self._thruster:
            self.get_logger().warn("Thruster não inicializado. Ignorando comando.")
            return

        raw_value = msg.data[0]
        clamped_value = self.clamp(raw_value, 0.0, 1.0)

        if raw_value != clamped_value:
            self.get_logger().warn(
                f"Thruster value {raw_value:.3f} fora do limite. Clamped para {clamped_value:.3f}"
            )

        self.get_logger().info(f'Thruster Setpoint: {clamped_value}')
        self._thruster.rotation_percent = clamped_value

        self.send_can_msg()

    # ======================================================
    # Callback dos Rudders
    # ======================================================
    def rudder_callback(self, msg):
        if not self._servo_top:
            self.get_logger().warn("Servos não inicializados. Ignorando comando.")
            return

        clamped_angles = []
        for i, rad in enumerate(msg.data):
            clamped = self.clamp(rad, -math.pi/2, math.pi/2)
            if rad != clamped:
                self.get_logger().warn(
                    f"Rudder[{i}] {rad:.3f} rad fora do limite. Clamped para {clamped:.3f} rad"
                )
            clamped_angles.append(clamped)

        self.get_logger().info(f'Rudder Setpoints (rad): {clamped_angles}')

        # Converte para graus e aplica aos servos
        self._servo_top.angle = self.rad2deg(clamped_angles[0])
        self._servo_right.angle = self.rad2deg(clamped_angles[1])
        self._servo_down.angle = self.rad2deg(clamped_angles[2])
        self._servo_left.angle = self.rad2deg(clamped_angles[3])

        self.send_can_msg()

    # ======================================================
    # Funções auxiliares
    # ======================================================
    def clamp(self, value, min_value, max_value):
        return max(min_value, min(value, max_value))

    def rad2deg(self, rad_value: float):
        return (rad_value * 180.0) / math.pi

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

            self.send_can_msg()
        except Exception as e:
            self.get_logger().error(f"Erro ao parar atuadores: {e}")

    def destroy_node(self):
        """Sobrescreve destroy_node para garantir parada segura."""
        self.stop_all()
        super().destroy_node()

    def send_can_msg(self):
        msg_list: list = [
            self._servo_top.msg_field,
            self._servo_down.msg_field,
            self._servo_left.msg_field,
            self._servo_right.msg_field
        ]

        msg_list += self._thruster.msg_field
        can_msg = can.Message(arbitration_id=0x001, data=msg_list, is_extended_id=False)
        print(msg_list)
        self._can_bus.send(can_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ControlNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Ctrl+C detectado. Encerrando com segurança...")
        node.stop_all()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
