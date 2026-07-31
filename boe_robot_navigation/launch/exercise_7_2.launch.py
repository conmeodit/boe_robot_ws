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
    turtlebot3_gazebo_share = get_package_share_directory(
        'turtlebot3_gazebo'
    )

    default_world = os.path.join(
        gazebo_share,
        'worlds',
        'boe_turtlebot3_house.world'
    )
    turtlebot3_model_path = os.path.join(
        turtlebot3_gazebo_share,
        'models'
    )

    world = LaunchConfiguration('world')
    use_rviz = LaunchConfiguration('use_rviz')
    configuration_basename = LaunchConfiguration(
        'configuration_basename'
    )

    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                gazebo_share,
                'launch',
                'simulation.launch.py'
            )
        ),
        launch_arguments={
            'world': world,
            'extra_model_path': turtlebot3_model_path,
            'spawn_x': '-2.0',
            'spawn_y': '-0.5',
            'spawn_z': '0.002'
        }.items()
    )

    cartographer = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                navigation_share,
                'launch',
                'cartographer.launch.py'
            )
        ),
        launch_arguments={
            'configuration_basename': configuration_basename,
            'use_sim_time': 'true',
            'use_rviz': use_rviz,
            'resolution': '0.05',
            'publish_period_sec': '1.0'
        }.items()
    )

    delayed_cartographer = TimerAction(
        period=5.0,
        actions=[cartographer]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value=default_world,
            description='Gazebo house world used for exercise 7.2'
        ),
        DeclareLaunchArgument(
            'configuration_basename',
            default_value='boe_cartographer_2d.lua',
            description='Cartographer profile used for this scan'
        ),
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Open RViz2 for Cartographer SLAM'
        ),
        simulation,
        delayed_cartographer
    ])
