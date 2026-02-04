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
from launch.conditions import IfCondition
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

    # Spawn the tuned SDF for the robot with functional wheels using a shell process.
    # This allows logging of exit codes and a simple retry on failure.
    model_sdf = os.path.join(pkg, 'models', 'ball_hitting_robot', 'model.sdf')
    spawn_cmd = (
        f"ros2 run ros_gz_sim create -world ball_world -file {model_sdf} "
        f"-name ball_hitting_robot -x 0.0 -y 0.0 -z 0.0"
    )
    spawn_script = (
        f"echo 'Spawning robot with ros_gz_sim create ...' && "
        f"({spawn_cmd}) || (sleep 1; {spawn_cmd}) ; "
        f"code=$?; echo 'Spawn completed (exit code '\"$code\"')'; exit $code"
    )
    spawn_process = ExecuteProcess(
        cmd=['bash', '-lc', spawn_script],
        output='screen'
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
        ],
        output='screen'
    )

    # Explicit bridge for Gazebo's model-scoped DiffDrive topic, with ROS remap to /cmd_vel
    # Bridge model-scoped cmd_vel as ROS->Gazebo only and remap ROS topic /cmd_vel -> model-scoped topic
    bridge_model_cmd = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/model/ball_hitting_robot/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
        ],
        remappings=[('/model/ball_hitting_robot/cmd_vel', '/cmd_vel')],
        output='screen'
    )

    ball_detector = Node(
        package='perception', executable='ball_detector', name='ball_detector',
        output='screen', parameters=[{'use_sim_time': True}]
    )
    # Conditional nodes (gated by launch arguments below)
    ball_controller = Node(
        package='control', executable='ball_controller', name='ball_controller',
        output='screen', parameters=[{'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('use_controller'))
    )
    ball_perceptor = Node(
        package='control', executable='ball_perceptor', name='ball_perceptor',
        output='screen', parameters=[{'use_sim_time': True}]
    )
    fake_ball_pub = Node(
        package='control', executable='fake_ball_publisher', name='fake_ball_publisher',
        output='screen', parameters=[{'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('use_fake_ball'))
    )

    demo_kick_node = Node(
        package='control', executable='demo_kick', name='demo_kick',
        output='screen', parameters=[{'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('use_demo_kick'))
    )

    # Give Gazebo time to fully initialize before spawning and bridging
    start_delay = 2.5

    # Launch arguments to gate optional nodes
    declare_use_demo_kick = DeclareLaunchArgument(
        'use_demo_kick', default_value='false',
        description='If true, start the demo_kick node to auto-drive on launch'
    )
    declare_use_controller = DeclareLaunchArgument(
        'use_controller', default_value='false',
        description='If true, start the ball_controller node'
    )
    declare_use_fake_ball = DeclareLaunchArgument(
        'use_fake_ball', default_value='false',
        description='If true, start the fake_ball_publisher node'
    )

    return LaunchDescription([
            declare_use_demo_kick,
            declare_use_controller,
            declare_use_fake_ball,
            LogInfo(msg=['Starting Gazebo (GUI) with Wayland workaround: env -u WAYLAND_DISPLAY QT_QPA_PLATFORM=xcb']),
            LogInfo(msg=['World: ', world_file]),
            SetEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH', models_path + ':' + worlds_path + ':' + os.environ.get('IGN_GAZEBO_RESOURCE_PATH', '')),
            SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', models_path + ':' + worlds_path + ':' + os.environ.get('GZ_SIM_RESOURCE_PATH', '')),
            gazebo_process,
            TimerAction(period=start_delay, actions=[
            LogInfo(msg=['Gazebo should be up; spawning robot and launching bridges/ROS nodes...']),
            LogInfo(msg=['Spawning from SDF: ', model_sdf]),
            robot_state_publisher,
            spawn_process,
            bridge,
            bridge_model_cmd,
            ball_detector,
            ball_controller,
            fake_ball_pub,
            ball_perceptor,
            demo_kick_node,
        ]),
    ])
