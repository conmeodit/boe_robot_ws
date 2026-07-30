import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import ExecuteProcess
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch.substitutions import LaunchConfiguration
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

    default_world_file = os.path.join(
        gazebo_share,
        'worlds',
        'empty.world'
    )

    world_argument = DeclareLaunchArgument(
        'world',
        default_value=default_world_file,
        description='Absolute path of the Gazebo world file'
    )

    world_file = LaunchConfiguration('world')
    extra_model_path = LaunchConfiguration('extra_model_path')
    spawn_x = LaunchConfiguration('spawn_x')
    spawn_y = LaunchConfiguration('spawn_y')
    spawn_z = LaunchConfiguration('spawn_z')

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
            'GAZEBO_MODEL_PATH': [
                clean_model_path,
                os.pathsep,
                extra_model_path
            ],
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
            '-timeout',
            '120.0',
            '-x',
            spawn_x,
            '-y',
            spawn_y,
            '-z',
            spawn_z
        ]
    )

    return LaunchDescription([
        world_argument,
        DeclareLaunchArgument(
            'extra_model_path',
            default_value=description_model_root,
            description='Additional Gazebo model directory for world meshes'
        ),
        DeclareLaunchArgument(
            'spawn_x',
            default_value='0.0',
            description='Initial robot X position in the Gazebo world'
        ),
        DeclareLaunchArgument(
            'spawn_y',
            default_value='0.0',
            description='Initial robot Y position in the Gazebo world'
        ),
        DeclareLaunchArgument(
            'spawn_z',
            default_value='0.002',
            description='Initial robot Z position in the Gazebo world'
        ),
        gazebo_server_launch,
        gazebo_client,
        robot_state_publisher_node,
        spawn_robot_node
    ])
