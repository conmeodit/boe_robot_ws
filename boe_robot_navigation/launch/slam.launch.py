import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    navigation_share = get_package_share_directory(
        'boe_robot_navigation'
    )

    default_params_file = os.path.join(
        navigation_share,
        'config',
        'mapper_params_online_async.yaml'
    )

    rviz_config_file = os.path.join(
        navigation_share,
        'config',
        'boe_slam.rviz'
    )

    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')

    use_sim_time_argument = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use the Gazebo simulation clock'
    )

    params_file_argument = DeclareLaunchArgument(
        'params_file',
        default_value=default_params_file,
        description='Absolute path to the SLAM Toolbox parameter file'
    )

    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            params_file,
            {
                'use_sim_time': use_sim_time
            }
        ]
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='boe_slam_rviz',
        output='screen',
        arguments=[
            '-d',
            rviz_config_file
        ],
        parameters=[{
            'use_sim_time': use_sim_time
        }]
    )

    return LaunchDescription([
        use_sim_time_argument,
        params_file_argument,
        slam_toolbox_node,
        rviz_node
    ])
