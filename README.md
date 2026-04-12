
# actuators_control_driver

## Overview

`actuators_control_driver` is a ROS 2 package responsible for controlling the thruster and rudders of the VSA (Veículo Submarino Autônomo). It interfaces with hardware actuators and receives setpoints via ROS 2 topics to command the vehicle's propulsion and steering mechanisms.

## Responsibilities
- Controls the thruster and four rudders of the VSA.
- Subscribes to the following ROS 2 topics for actuator setpoints:
  - `/controller/thrusters_setpoints`: Receives thruster speed setpoints as a `Float64MultiArray`.
  - `/controller/rudders_setpoints`: Receives rudder angle setpoints (in radians) as a `Float64MultiArray` for four rudders.
- Converts received setpoints to hardware commands using GPIO via the `pigpio` library.

## Main Components
- `control_node.py`: Implements the ROS 2 node that subscribes to the setpoint topics and commands the thruster and rudders accordingly.
- `guidance_simulator.py`: Provides a simulator node that publishes example setpoints to the control topics for testing and development purposes.

## Installation

Before running the package, ensure you have the required dependencies installed:

```bash
pip install pigpio gpiozero
```

## Usage

1. Give permission with:
    ```bash
    sudo pigpiod 
    ```
2. Start the ROS 2 node to control actuators:
	```bash
	ros2 run actuators_control_driver control_node
	```
3. (Optional) Run the simulator to publish test setpoints:
	```bash
	ros2 run actuators_control_driver guidance_simulator
	```
4. (Optional) Publish test setpoints individually:
	```bash
	ros2 topic pub --once /controller/rudders_setpoints std_msgs/msg/Float64MultiArray "data: [-1.5, -0.0, 0.0, 0.0]"
	or
	ros2 topic pub --once /controller/thruster_setpoints std_msgs/msg/Float64MultiArray "data: [0.5]"
	or
	ros2 topic pub -r 1 /controller/rudders_setpoints std_msgs/msg/Float64MultiArray "data: [-1.5, -0.0, 0.0, 0.0]"
	or
	ros2 topic pub -r 1 /controller/thruster_setpoints std_msgs/msg/Float64MultiArray "data: [0.5]"
	```

## Topics
- `/controller/thrusters_setpoints` (`std_msgs/msg/Float64MultiArray`): Thruster speed setpoints.
- `/controller/rudders_setpoints` (`std_msgs/msg/Float64MultiArray`): Rudder angle setpoints (in radians).

## Dependencies
- rclpy
- std_msgs
- pigpio (Python library)
- gpiozero