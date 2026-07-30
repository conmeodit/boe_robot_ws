import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.actions import TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    gazebo_share = get_package_share_directory(
        'boe_robot_gazebo'
    )
    navigation_share = get_package_share_directory(
        'boe_robot_navigation'
    )

    default_world = os.path.join(
        gazebo_share,
        'worlds',
        'navigation_test.world'
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

    world = LaunchConfiguration('world')
    map_file = LaunchConfiguration('map')
    nav2_params_file = LaunchConfiguration('nav2_params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                gazebo_share,
                'launch',
                'simulation.launch.py'
            )
        ),
        launch_arguments={
            'world': world
        }.items()
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                navigation_share,
                'launch',
                'nav2.launch.py'
            )
        ),
        launch_arguments={
            'map': map_file,
            'params_file': nav2_params_file,
            'use_sim_time': use_sim_time
        }.items()
    )

    # Gazebo cần thời gian tạo world và spawn robot trước khi
    # AMCL, costmap và RViz2 bắt đầu nhận /scan, /odom và TF.
    delayed_navigation = TimerAction(
        period=5.0,
        actions=[navigation]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value=default_world,
            description='Absolute path to the Gazebo world file'
        ),
        DeclareLaunchArgument(
            'map',
            default_value=default_map,
            description='Absolute path to the BOE map YAML file'
        ),
        DeclareLaunchArgument(
            'nav2_params_file',
            default_value=default_params,
            description='Absolute path to the BOE Nav2 parameters'
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use the Gazebo simulation clock'
        ),
        simulation,
        delayed_navigation
    ])
