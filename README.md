
# actuators_control_driver

## Overview

`actuators_control_driver` is a ROS 2 package responsible for receiving the thruster and rudders setpoint signals from the guidance system of the VSA (Veículo Submarino Autônomo) and converting them to a single CAN word which will be published to CAN node.

## Topics
- Subscribes to:
  - `/controller/thrusters_setpoints`: Receives thruster speed percentage setpoints as a `Float64MultiArray`. 
  Range: [-1.0] ~ [1.0]
  - `/controller/rudders_setpoints`: Receives rudder angle setpoints (in radians) as a `Float64MultiArray` for four rudders.
  Range: [-0.785, -0.785, -0.785, -0.785] ~ [0.785, 0.785, 0.785, 0.785]. Each servo is limited between -45° to 45°.
- Publishes to:
  - `/actuators_can_tx`: Sends a CAN word of type `UInt8MultiArray`.

## Main Components
- `control_node.py`: The `thruster_callback` and `rudder_callback` update the variables and call for send_can_msg() which will concatenate the data in 7 bytes of format [top, down, left, righ, direction, speed, enable].
- `actuators_test.py`: Basic actuators test.

## Dependencies
- rclpy
- std_msgs

## Usage

1. Start the ROS 2 node to control actuators:
	```bash
	ros2 run actuators_control_driver control_node
	```

2. (Optional) Publish test setpoints individually:
	```bash
	ros2 topic pub --once /controller/rudders_setpoints std_msgs/msg/Float64MultiArray "data: [-1.5, 0.0, 0.0, 0.0]"
	```
	**Output on `/actuators_can_tx`:** `[47, 128, 128, 128, 0, 0, 0]` (decimal) 
	
	or
	```bash
	ros2 topic pub --once /controller/thrusters_setpoints std_msgs/msg/Float64MultiArray "data: [0.5]"
	```
	**Output on `/actuators_can_tx`:** `[128, 128, 128, 128, 0, 128, 1]` (decimal) 
