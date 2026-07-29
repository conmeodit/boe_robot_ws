import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    gazebo_share = get_package_share_directory(
        'boe_robot_gazebo'
    )

    simulation_launch = os.path.join(
        gazebo_share,
        'launch',
        'simulation.launch.py'
    )

    lidar_test_world = os.path.join(
        gazebo_share,
        'worlds',
        'lidar_test.world'
    )

    rviz_config = os.path.join(
        gazebo_share,
        'config',
        'boe_lidar.rviz'
    )

    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            simulation_launch
        ),
        launch_arguments={
            'world': lidar_test_world
        }.items()
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='boe_lidar_rviz',
        output='screen',
        arguments=[
            '-d',
            rviz_config
        ],
        parameters=[{
            'use_sim_time': True
        }]
    )

    return LaunchDescription([
        simulation,
        rviz_node
    ])
