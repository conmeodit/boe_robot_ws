import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    gazebo_share = get_package_share_directory(
        'boe_robot_gazebo'
    )

    rviz_config = os.path.join(
        gazebo_share,
        'config',
        'boe_lidar.rviz'
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
        rviz_node
    ])
