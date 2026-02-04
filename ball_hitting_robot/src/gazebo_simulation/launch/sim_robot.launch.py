#!/usr/bin/env python3
"""
Launch file for Gazebo simulation of ball-hitting robot

This launch file:
1. Starts Gazebo with the custom world containing the red ball
2. Spawns the robot model into the simulation
3. Starts robot_state_publisher to broadcast TF transforms

Usage:
    ros2 launch gazebo_simulation sim_robot.launch.py

Configuration:
- World file: Located in worlds/ball_world.sdf
- Robot model: Located in urdf/robot.urdf
- Starting robot pose: Can be modified in spawn_entity arguments
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """
    Generate launch description for Gazebo simulation
    
    Returns:
        LaunchDescription: Complete launch configuration
    """
    
    # Get package directories
    gazebo_simulation_pkg = get_package_share_directory('gazebo_simulation')
    
    # Path to world file
    world_file = os.path.join(
        gazebo_simulation_pkg,
        'worlds',
        'ball_world.sdf'
    )
    
    # Path to robot URDF
    urdf_file = os.path.join(
        gazebo_simulation_pkg,
        'urdf',
        'robot.urdf'
    )
    
    # Read URDF file
    with open(urdf_file, 'r') as file:
        robot_desc = file.read()
    
    # Declare launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    
    # Launch Gazebo with the specified world
    # Use gzserver to start the simulation server and gzclient for GUI when
    # available. Some installations of `gz` do not provide the `sim` subcommand
    # so calling `gzserver <world.sdf>` is more portable.
    gazebo_server = ExecuteProcess(
        cmd=['gzserver', world_file],
        output='screen'
    )

    # Try to launch gzclient (GUI) as a separate process. On headless systems
    # this may fail; it's safe to keep it optional in the launch output.
    gazebo_client = ExecuteProcess(
        cmd=['gzclient'],
        output='screen'
    )
    
    # Robot State Publisher - publishes robot transforms to /tf
    # This node converts URDF joint states to TF transforms
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': robot_desc
        }]
    )
    
    # Spawn the robot in Gazebo at specified position
    # TO CHANGE ROBOT STARTING POSITION:
    # Modify -x, -y, -z arguments below
    # -x: forward/backward (default: 0)
    # -y: left/right (default: 0)
    # -z: height (default: 0.1)
    # -Y: rotation/yaw in radians (default: 0)
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'ball_hitting_robot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1',
            '-Y', '0.0'
        ],
        output='screen'
    )
    
    # Bridge to connect Gazebo topics to ROS2 topics
    # This allows ROS2 nodes to receive data from Gazebo sensors
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Bridge camera image topic
            '/camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image',
            # Bridge camera info topic
            '/camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
            # Bridge odometry topic
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            # Bridge command velocity (bidirectional)
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
        ],
        output='screen'
    )
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time from Gazebo'
        ),
    gazebo_server,
    gazebo_client,
        robot_state_publisher_node,
        spawn_entity,
        bridge,
    ])
