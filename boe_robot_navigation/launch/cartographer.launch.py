import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    navigation_share = get_package_share_directory(
        'boe_robot_navigation'
    )

    configuration_directory = os.path.join(
        navigation_share,
        'config'
    )
    configuration_basename = 'boe_cartographer_2d.lua'
    rviz_config_file = os.path.join(
        navigation_share,
        'config',
        'boe_slam.rviz'
    )

    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')
    resolution = LaunchConfiguration('resolution')
    publish_period_sec = LaunchConfiguration('publish_period_sec')

    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time
        }],
        arguments=[
            '-configuration_directory',
            configuration_directory,
            '-configuration_basename',
            configuration_basename
        ]
    )

    occupancy_grid_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        name='cartographer_occupancy_grid_node',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time
        }],
        arguments=[
            '-resolution',
            resolution,
            '-publish_period_sec',
            publish_period_sec
        ]
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='boe_cartographer_rviz',
        output='screen',
        arguments=[
            '-d',
            rviz_config_file
        ],
        parameters=[{
            'use_sim_time': use_sim_time
        }],
        condition=IfCondition(use_rviz)
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use the Gazebo simulation clock'
        ),
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Open RViz2 with the BOE SLAM configuration'
        ),
        DeclareLaunchArgument(
            'resolution',
            default_value='0.05',
            description='Occupancy grid resolution in metres per cell'
        ),
        DeclareLaunchArgument(
            'publish_period_sec',
            default_value='1.0',
            description='Occupancy grid publishing period'
        ),
        cartographer_node,
        occupancy_grid_node,
        rviz_node
    ])
