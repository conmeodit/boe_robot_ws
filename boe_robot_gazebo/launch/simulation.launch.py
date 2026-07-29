import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    description_share = get_package_share_directory(
        'boe_robot_description'
    )

    gazebo_share = get_package_share_directory(
        'boe_robot_gazebo'
    )

    gazebo_ros_share = get_package_share_directory(
        'gazebo_ros'
    )

    xacro_file = os.path.join(
        description_share,
        'urdf',
        'boe_robot.urdf.xacro'
    )

    world_file = os.path.join(
        gazebo_share,
        'worlds',
        'empty.world'
    )

    model_file = os.path.join(
        gazebo_share,
        'models',
        'boe_robot',
        'model.sdf'
    )

    robot_description = ParameterValue(
        Command([
            'xacro ',
            xacro_file
        ]),
        value_type=str
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True
        }]
    )

    # Chỉ khởi động Gazebo server.
    # Không dùng gzclient của gazebo_ros vì nó thêm nhầm
    # toàn bộ /opt/ros/humble/share vào GAZEBO_MODEL_PATH.
    gazebo_server_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                gazebo_ros_share,
                'launch',
                'gazebo.launch.py'
            )
        ),
        launch_arguments={
            'world': world_file,
            'verbose': 'true',
            'gui': 'false'
        }.items()
    )

    # Danh sách thư mục model hợp lệ.
    description_model_root = os.path.dirname(description_share)

    clean_model_path = os.pathsep.join([
        '/usr/share/gazebo-11/models',
        description_model_root
    ])

    # Tự khởi động Gazebo client với model path sạch.
    gazebo_client = ExecuteProcess(
        cmd=[
            'gzclient',
            '--gui-client-plugin=libgazebo_ros_eol_gui.so'
        ],
        output='screen',
        additional_env={
            'GAZEBO_MODEL_PATH': clean_model_path,
            'GAZEBO_MODEL_DATABASE_URI': ''
        }
    )

    spawn_robot_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_boe_robot',
        output='screen',
        arguments=[
            '-file',
            model_file,
            '-entity',
            'boe_robot',
            '-x',
            '0.0',
            '-y',
            '0.0',
            '-z',
            '0.002'
        ]
    )

    return LaunchDescription([
        gazebo_server_launch,
        gazebo_client,
        robot_state_publisher_node,
        spawn_robot_node
    ])
