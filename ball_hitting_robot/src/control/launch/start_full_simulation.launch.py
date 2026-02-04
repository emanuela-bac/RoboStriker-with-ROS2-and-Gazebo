import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = 'control'
    pkg_share_dir = get_package_share_directory(pkg_name)
    
    # 1. Calea către URDF și WORLD file
    # Folosim numele corect al fișierului URDF:
    robot_description_path = os.path.join(pkg_share_dir, 'urdf', 'ball_hitting_robot.urdf')
    world_path = os.path.join(pkg_share_dir, 'worlds', 'my_hitting_arena.world')
    
    # Verifică dacă fișierul URDF există
    if not os.path.exists(robot_description_path):
        # Dacă ai folosit un alt nume de fișier, schimbă aici:
        robot_description_path = os.path.join(pkg_share_dir, 'urdf', 'sim_robot.urdf') 

    # 2. Lansarea Gazebo
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
        ),
        # Încărcăm arena ta (my_hitting_arena.world)
        launch_arguments={'world': world_path}.items(),
    )

    # 3. Publicarea stării robotului (Robot State Publisher)
    # Acesta citește URDF-ul și publică geometria
    # 3. Publicarea stării robotului (Robot State Publisher)
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        # ACEASTĂ LINIE ESTE CRITICĂ: Trebuie să includă calea completă, NU sim_robot.urdf.
        parameters=[{'robot_description': Command(['cat ', robot_description_path])}]
    )

    # 4. Spawnează modelul robotului în Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', 
                   '-entity', 'ball_hitting_robot', # Numele robotului din URDF
                   '-x', '0.0', '-y', '0.0', '-z', '0.1'], # Pozitie initiala in world
        output='screen'
    )
    
    # 5. Nodul de Percepție (Translator: Gazebo State -> /ball_position)
    ball_perceptor_node = Node(
        package=pkg_name,
        executable='ball_perceptor',
        output='screen'
    )

    # 6. Nodul Tău de Control (Creierul)
    ball_controller_node = Node(
        package=pkg_name,
        executable='ball_controller',
        output='screen'
    )
    
    # 7. Nu mai este necesară lansarea controller-ului (diff_drive) separat, 
    #    deoarece plugin-ul din URDF se ocupă de asta și ascultă /cmd_vel.

    return LaunchDescription([
        gazebo_launch,
        robot_state_publisher_node,
        spawn_entity,
        ball_perceptor_node,
        ball_controller_node,
    ])