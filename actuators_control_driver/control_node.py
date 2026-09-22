import time
import math
from actuators_control_driver.thruster import *
from actuators_control_driver.servo import Servo

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray, UInt8MultiArray


class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')

        self.get_logger().info("Starting ControlNode...")

        # ======================================================
        # Servo offset parameters (degrees)
        # ======================================================
        self.declare_parameter('servo_top_offset_deg', 0.0)
        self.declare_parameter('servo_right_offset_deg', 0.0)
        self.declare_parameter('servo_down_offset_deg', 0.0)
        self.declare_parameter('servo_left_offset_deg', 0.0)

        servo_top_offset = self.get_parameter('servo_top_offset_deg').get_parameter_value().double_value
        servo_right_offset = self.get_parameter('servo_right_offset_deg').get_parameter_value().double_value
        servo_down_offset = self.get_parameter('servo_down_offset_deg').get_parameter_value().double_value
        servo_left_offset = self.get_parameter('servo_left_offset_deg').get_parameter_value().double_value

        # ======================================================
        # Starting devices
        # ======================================================
        self._thruster = Thruster()
        self._servo_top = Servo(min_angle=-math.pi/4, max_angle=math.pi/4,
                 min_output=0x4e, max_output=0xb2, offset_deg=servo_top_offset)
        self._servo_right = Servo(min_angle=-math.pi/4, max_angle=math.pi/4,
                 min_output=0x4e, max_output=0xb2, offset_deg=servo_right_offset)
        self._servo_down = Servo(min_angle=-math.pi/4, max_angle=math.pi/4,
                 min_output=0x4e, max_output=0xb2, offset_deg=servo_down_offset)
        self._servo_left = Servo(min_angle=-math.pi/4, max_angle=math.pi/4,
                 min_output=0x4e, max_output=0xb2, offset_deg=servo_left_offset)

        # ======================================================
        # ROS 2 Subscriptions
        # ======================================================
        self.thruster_sub = self.create_subscription(
            Float64MultiArray,
            '/controller/thrusters_setpoints',
            self.thruster_callback,
            10)

        self.rudder_sub = self.create_subscription(
            Float64MultiArray,
            '/controller/rudders_setpoints',
            self.rudder_callback,
            10)
        
        self.can_bus_pub = self.create_publisher(UInt8MultiArray, '/actuators_can_tx', 10)

        self.get_logger().info('ControlNode started successfully.')

    # ======================================================
    # Callback do Thruster
    # ======================================================
    def thruster_callback(self, msg):
        if not self._thruster:
            self.get_logger().warn("Thruster not initialized. Ignoring command.")
            return

        raw_value = msg.data[0]
        clamped_value = self.clamp(raw_value, -1.0, 1.0)

        if raw_value != clamped_value:
            self.get_logger().warn(
                f"Thruster value {raw_value:.3f} out of range. Clamped to {clamped_value:.3f}"
            )

        self.get_logger().info(f'Thruster Setpoint: {clamped_value}')
        self._thruster.rotation_percent = clamped_value
        self._thruster.enable = True

        self.send_can_msg()

    # ======================================================
    # Callback dos Rudders
    # ======================================================
    def rudder_callback(self, msg):
        if not self._servo_top:
            self.get_logger().warn("Servos not initialized. Ignoring command.")
            return

        # Verificar se os valores de offset foram atualizados
        servo_top_offset = self.get_parameter('servo_top_offset_deg').get_parameter_value().double_value
        servo_right_offset = self.get_parameter('servo_right_offset_deg').get_parameter_value().double_value
        servo_down_offset = self.get_parameter('servo_down_offset_deg').get_parameter_value().double_value
        servo_left_offset = self.get_parameter('servo_left_offset_deg').get_parameter_value().double_value

        # Atualizar offsets nos servos (se mudaram)
        self._servo_top.offset_deg = servo_top_offset
        self._servo_right.offset_deg = servo_right_offset
        self._servo_down.offset_deg = servo_down_offset
        self._servo_left.offset_deg = servo_left_offset

        clamped_angles = []
        for i, rad in enumerate(msg.data):
            clamped = self.clamp(rad, -math.pi/4, math.pi/4)
            if rad != clamped:
                self.get_logger().warn(
                    f"Rudder[{i}] {rad:.3f} rad out of range. Clamped to {clamped:.3f} rad"
                )
            clamped_angles.append(clamped)

        self.get_logger().info(f'Rudder Setpoints (rad): {clamped_angles}')

        # Aplica os ângulos aos servos (os offsets são aplicados em msg_field)
        # Os offsets são somados após o mapeamento, não estando sujeitos à restrição de margem do ângulo
        self._servo_top.angle = clamped_angles[3]
        self._servo_right.angle = clamped_angles[2]
        self._servo_down.angle = clamped_angles[1]
        self._servo_left.angle = clamped_angles[0]

        self.send_can_msg()

    # ======================================================
    # Helper functions
    # ======================================================
    def clamp(self, value, min_value, max_value):
        return max(min_value, min(value, max_value))

    # def rad2deg(self, rad_value: float):
    #     return (rad_value * 180.0) / math.pi

    def stop_all(self):
        """Ensures all actuators stop (even without hardware)."""
        try:
            self.get_logger().info("Stopping all actuators...")
            if self._thruster:
                self._thruster.speed_percent = 0.0
                self._thruster.enable = False
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
            self.get_logger().error(f"Error stopping actuators: {e}")

    def destroy_node(self):
        """Overrides destroy_node to ensure safe shutdown."""
        self.stop_all()
        super().destroy_node()

    def send_can_msg(self):
        msg_list: list = [
            self._servo_left.msg_field,
            self._servo_down.msg_field,
            self._servo_right.msg_field,
            self._servo_top.msg_field
        ]

        msg_list += self._thruster.msg_field

        msg = UInt8MultiArray()
        msg.data = msg_list

        self.can_bus_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ControlNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Ctrl+C detected. Shutting down safely...")
        node.stop_all()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
