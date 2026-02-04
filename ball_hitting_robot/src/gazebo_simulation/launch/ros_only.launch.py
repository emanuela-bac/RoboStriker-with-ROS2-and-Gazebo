#!/usr/bin/env python3
"""Start only ROS-side nodes and bridges, assuming Ignition Gazebo is already running.
Use when starting the GUI manually (e.g., with QT_QPA_PLATFORM=xcb).
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import LogInfo, SetEnvironmentVariable, TimerAction
from launch_ros.actions import Node

def generate_launch_description():
    pkg = get_package_share_directory('gazebo_simulation')
    models_path = os.path.join(pkg, 'models')
    worlds_path = os.path.join(pkg, 'worlds')

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

    # Spawn the tuned SDF for the robot
    model_sdf = os.path.join(pkg, 'models', 'ball_hitting_robot', 'model.sdf')
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-file', model_sdf, '-name', 'ball_hitting_robot', '-x', '0.0', '-y', '0.0', '-z', '0.1'],
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
    demo_kick = Node(
        package='control', executable='demo_kick', name='demo_kick',
        output='screen', parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        LogInfo(msg=['Starting ROS nodes (no Gazebo launcher). Make sure Ignition Gazebo is already running.']),
        SetEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH', models_path + ':' + worlds_path + ':' + os.environ.get('IGN_GAZEBO_RESOURCE_PATH', '')),
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', models_path + ':' + worlds_path + ':' + os.environ.get('GZ_SIM_RESOURCE_PATH', '')),
        TimerAction(period=0.5, actions=[
            robot_state_publisher,
            spawn_entity,
            bridge,
            bridge_model_cmd,
            ball_detector,
            ball_controller,
            fake_ball_pub,
            ball_perceptor,
            demo_kick,
        ]),
    ])
