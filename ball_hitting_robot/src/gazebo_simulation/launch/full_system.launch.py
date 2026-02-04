#!/usr/bin/env python3
"""Clean, minimal launch for the ball-hitting robot using ros_gz_sim.

Starts Gazebo Sim with the provided world, sets up resource paths so Ignition
can find packaged models, and starts ros_gz_bridge plus ROS nodes after a short
delay to allow the simulator to initialize.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, LogInfo, SetEnvironmentVariable, DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('gazebo_simulation')
    ros_gz_pkg = get_package_share_directory('ros_gz_sim')

    world_file = os.path.join(pkg, 'worlds', 'ball_world.sdf')
    models_path = os.path.join(pkg, 'models')
    worlds_path = os.path.join(pkg, 'worlds')

    # Start Gazebo GUI using ExecuteProcess so it is NOT required and won't shut down ROS nodes on exit.
    # Workaround for Wayland: unset WAYLAND_DISPLAY and force Qt to xcb.
    gazebo_cmd = f"env -u WAYLAND_DISPLAY QT_QPA_PLATFORM=xcb ign gazebo -r {world_file}"
    gazebo_process = ExecuteProcess(
        cmd=['bash', '-lc', gazebo_cmd],
        output='screen'
    )

    # Read URDF for robot_state_publisher (URDF used only for TF)
    urdf_file = os.path.join(pkg, 'urdf', 'robot.urdf')
    robot_desc = ''
    try:
        with open(urdf_file, 'r') as f:
            robot_desc = f.read()
    except Exception:
        robot_desc = ''

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True, 'robot_description': robot_desc}]
    )

    # Spawn the tuned SDF for the robot with functional wheels
    model_sdf = os.path.join(pkg, 'models', 'ball_hitting_robot', 'model.sdf')
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',            
        # Keep the spawned entity name as 'ball_hitting_robot' so existing bridges remain valid
        # Spawn at ground level; wheel centers are at z=0.12 so they sit on the ground
        arguments=['-file', model_sdf, '-name', 'ball_hitting_robot', '-x', '0.0', '-y', '0.0', '-z', '0.0'],
        output='screen'
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
        ],
        output='screen'
    )

    # Explicit bridge for Gazebo's model-scoped DiffDrive topic, with ROS remap to /cmd_vel
    bridge_model_cmd = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/model/ball_hitting_robot/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
        ],
        remappings=[('/model/ball_hitting_robot/cmd_vel', '/cmd_vel')],
        output='screen'
    )

    ball_detector = Node(
        package='perception', executable='ball_detector', name='ball_detector',
        output='screen', parameters=[{'use_sim_time': True}]
    )
    ball_controller = Node(
        package='control', executable='ball_controller', name='ball_controller',
        output='screen', parameters=[{'use_sim_time': True}]
    )
    ball_perceptor = Node(
        package='control', executable='ball_perceptor', name='ball_perceptor',
        output='screen', parameters=[{'use_sim_time': True}]
    )
    fake_ball_pub = Node(
        package='control', executable='fake_ball_publisher', name='fake_ball_publisher',
        output='screen', parameters=[{'use_sim_time': True}]
    )

    # Start nodes quickly so the demo kick begins immediately
    start_delay = 0.5

    return LaunchDescription([
            LogInfo(msg=['Starting Gazebo (GUI) with Wayland workaround: env -u WAYLAND_DISPLAY QT_QPA_PLATFORM=xcb']),
            LogInfo(msg=['World: ', world_file]),
            SetEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH', models_path + ':' + worlds_path + ':' + os.environ.get('IGN_GAZEBO_RESOURCE_PATH', '')),
            SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', models_path + ':' + worlds_path + ':' + os.environ.get('GZ_SIM_RESOURCE_PATH', '')),
            gazebo_process,
            TimerAction(period=start_delay, actions=[
            LogInfo(msg=['Gazebo should be up; launching bridge and ROS nodes...']),
            robot_state_publisher,
            spawn_entity,
            bridge,
            bridge_model_cmd,
            ball_detector,
            ball_controller,
            fake_ball_pub,
            ball_perceptor,
            # Auto-kick demo publisher to guarantee movement on launch
            Node(
                package='control', executable='demo_kick', name='demo_kick',
                output='screen', parameters=[{'use_sim_time': True}]
            ),
        ]),
    ])
