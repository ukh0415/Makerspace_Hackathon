# launch/robot_launch.py 예시
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='my_robot_controller', executable='motor_driver_node'),
        Node(package='my_robot_controller', executable='odom_node'),
        Node(package='my_robot_controller', executable='navigator_node'),
    ])
