#!/usr/bin/env python3
"""Clean, minimal launch (alternate name) for the ball-hitting robot using ros_gz_sim.

This is a clean copy created to avoid the corrupted/multiple-duplicate file
that was present in the workspace. Use this launch file while I finish
cleaning the original.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, LogInfo, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('gazebo_simulation')
    ros_gz_pkg = get_package_share_directory('ros_gz_sim')

    world_file = os.path.join(pkg, 'worlds', 'ball_world.sdf')
    models_path = os.path.join(pkg, 'models')
    worlds_path = os.path.join(pkg, 'worlds')

    # Run headless server-only to avoid Qt/GUI plugin issues in CI/headless setups
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(ros_gz_pkg, 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'gz_args': f'-r -s {world_file}'}.items()
    )

    # Read URDF for robot_state_publisher (we keep URDF for TF only)
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
            '/camera/image@sensor_msgs/msg/Image@gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
        ],
        output='screen'
    )

    ball_detector = Node(package='perception', executable='ball_detector', name='ball_detector', output='screen', parameters=[{'use_sim_time': True}])
    ball_controller = Node(package='control', executable='ball_controller', name='ball_controller', output='screen', parameters=[{'use_sim_time': True}])
    ball_perceptor = Node(package='control', executable='ball_perceptor', name='ball_perceptor', output='screen', parameters=[{'use_sim_time': True}])
    fake_ball_pub = Node(package='control', executable='fake_ball_publisher', name='fake_ball_publisher', output='screen', parameters=[{'use_sim_time': True}])

    start_delay = 3.0

    return LaunchDescription([
        LogInfo(msg=['Starting ros_gz_sim with world: ', world_file]),
        SetEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH', models_path + ':' + worlds_path + ':' + os.environ.get('IGN_GAZEBO_RESOURCE_PATH', '')),
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', models_path + ':' + worlds_path + ':' + os.environ.get('GZ_SIM_RESOURCE_PATH', '')),
        sim_launch,
        TimerAction(period=start_delay, actions=[
            LogInfo(msg=['Gazebo should be up; launching bridge and ROS nodes...']),
            robot_state_publisher,
            spawn_entity,
            bridge,
            ball_detector,
            ball_controller,
            fake_ball_pub,
            ball_perceptor,
        ]),
    ])
