import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    navigation_share = get_package_share_directory(
        'boe_robot_navigation'
    )
    nav2_bringup_share = get_package_share_directory(
        'nav2_bringup'
    )

    default_map = os.path.join(
        navigation_share,
        'maps',
        'boe_map.yaml'
    )
    default_params = os.path.join(
        navigation_share,
        'config',
        'nav2_params.yaml'
    )
    # Dùng cấu hình RViz riêng của robot BOE.
    # File này bật sẵn RobotModel, LaserScan và các công cụ Nav2.
    default_rviz = os.path.join(
        navigation_share,
        'config',
        'boe_slam.rviz'
    )

    map_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                nav2_bringup_share,
                'launch',
                'bringup_launch.py'
            )
        ),
        launch_arguments={
            'map': map_file,
            'params_file': params_file,
            'use_sim_time': use_sim_time,
            'autostart': 'True',
            'use_composition': 'False'
        }.items()
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='boe_nav2_rviz',
        output='screen',
        arguments=['-d', default_rviz],
        parameters=[{
            'use_sim_time': use_sim_time
        }]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'map',
            default_value=default_map,
            description='Absolute path to the BOE map YAML file'
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params,
            description='Absolute path to the BOE Nav2 parameter file'
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use the Gazebo simulation clock'
        ),
        nav2_bringup,
        rviz
    ])
