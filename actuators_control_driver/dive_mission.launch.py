from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    config_file = os.path.join(
        get_package_share_directory('actuators_control_driver'),
        'actuators_control_driver',
        'dive_mission_config.yaml'
    )
    return LaunchDescription([
        Node(
            package='actuators_control_driver',
            executable='dive_mission.py',
            name='dive_mission_node',
            output='screen',
            parameters=[config_file]
        )
    ])
