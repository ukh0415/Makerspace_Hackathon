import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():

    # 1. 월드 파일 경로 설정 
    pkg_vehicle_gazebo = get_package_share_directory('vehicle_gazebo')
    world_path = os.path.join(pkg_vehicle_gazebo, 'worlds', 'classroom.sdf')

    # 2. 로봇 설명(URDF) 설정
    robot_description_raw = Command([
        'xacro ',
        PathJoinSubstitution([
            FindPackageShare('vehicle_description'),
            'urdf',
            'vehicle.xacro'
        ])
    ])

    robot_description_param = ParameterValue(robot_description_raw, value_type=str)

    return LaunchDescription([

        # 3. Gazebo 실행 설정
        ExecuteProcess(
            cmd=['gazebo', '--verbose', world_path, '-s', 'libgazebo_ros_factory.so'],
            output='screen'
        ),

        # Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description_param,
                'use_sim_time': True
            }]
        ),

        # 👈 추가: Joint State Publisher
        # 이 노드가 있어야 RViz에서 바퀴(joint)의 위치(TF)를 정상적으로 계산합니다.
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            parameters=[{'use_sim_time': True}]
        ),

        # Spawn robot
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-topic', 'robot_description',
                '-entity', 'vehicle',
                '-x', '0.0', '-y', '0.0', '-z', '0.5' 
            ],
            output='screen'
        )
    ])