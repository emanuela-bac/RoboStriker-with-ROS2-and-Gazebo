# Ball-Hitting Robot - ROS2 Humble Gazebo Simulation

A complete ROS2 Humble project that simulates a robot capable of detecting a red ball and autonomously hitting/pushing it in Gazebo.

## 📋 Overview

This project demonstrates:
- **Gazebo Simulation**: Complete robot model with differential drive and camera sensor
- **Computer Vision**: Color-based ball detection using OpenCV
- **Autonomous Control**: State machine-based navigation and hitting behavior

### System Architecture

```
┌─────────────────┐
│   Gazebo Sim    │  - Physics simulation
│  (Robot + Ball) │  - Camera sensor
└────────┬────────┘
         │ /camera/image_raw
         ↓
┌─────────────────┐
│   Perception    │  - Ball detection (OpenCV)
│  (ball_detector)│  - Color segmentation
└────────┬────────┘
         │ /ball_position
         ↓
┌─────────────────┐
│    Control      │  - State machine
│(ball_controller)│  - Motion planning
└────────┬────────┘
         │ /cmd_vel
         ↓
┌─────────────────┐
│  Robot (Gazebo) │  - Execute motion
└─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Ubuntu 22.04
- ROS2 Humble
- Gazebo (gz-sim from Gazebo Garden or newer)
- Python 3.10+

### Install Dependencies

```bash
# Install ROS2 Humble (if not already installed)
# Follow: https://docs.ros.org/en/humble/Installation.html

# Install Gazebo
sudo apt install ros-humble-ros-gz

# Install Python dependencies
sudo apt install python3-opencv python3-pip
pip3 install opencv-python numpy

# Install ROS2 build tools
sudo apt install python3-colcon-common-extensions
```

### Build the Project

```bash
# Navigate to workspace
cd ~/Documents/PSD/ball_hitting_robot

# Source ROS2
source /opt/ros/humble/setup.bash

# Build all packages
colcon build --symlink-install

# Source the workspace
source install/setup.bash
```

### Run the Simulation

**Option 1: Launch complete system (recommended)**

```bash
# Source workspace
source install/setup.bash

# Launch everything
ros2 launch gazebo_simulation full_system.launch.py
```

This single command will:
1. Start Gazebo with the world and robot
2. Start the ball detection node
3. Start the control node
4. Robot will automatically detect and hit the ball!

**Option 2: Launch components separately (for debugging)**

```bash
# Terminal 1: Start Gazebo simulation
source install/setup.bash
ros2 launch gazebo_simulation sim_robot.launch.py

# Terminal 2: Start ball detector
source install/setup.bash
ros2 run perception ball_detector

# Terminal 3: Start controller
source install/setup.bash
ros2 run control ball_controller
```

## 📦 Package Structure

```
ball_hitting_robot/
├── src/
│   ├── gazebo_simulation/      # Gazebo world and robot model
│   │   ├── launch/
│   │   │   ├── sim_robot.launch.py       # Launch Gazebo
│   │   │   └── full_system.launch.py     # Launch everything
│   │   ├── urdf/
│   │   │   └── robot.urdf                # Robot description
│   │   ├── worlds/
│   │   │   └── ball_world.sdf            # Gazebo world with ball
│   │   ├── CMakeLists.txt
│   │   └── package.xml
│   │
│   ├── perception/             # Ball detection
│   │   ├── perception/
│   │   │   ├── __init__.py
│   │   │   └── ball_detector.py          # OpenCV detection node
│   │   ├── setup.py
│   │   ├── setup.cfg
│   │   └── package.xml
│   │
│   └── control/                # Robot control
│       ├── control/
│       │   ├── __init__.py
│       │   └── ball_controller.py        # Navigation controller
│       ├── setup.py
│       ├── setup.cfg
│       └── package.xml
│
├── build/                      # Build artifacts
├── install/                    # Installed files
└── README.md                   # This file
```

## ⚙️ Configuration Guide

### 1. Changing Ball Position

Edit: `src/gazebo_simulation/worlds/ball_world.sdf`

```xml
<!-- Line ~100: Modify the <pose> tag -->
<model name="red_ball">
  <pose>3 0 0.2 0 0 0</pose>  <!-- X Y Z Roll Pitch Yaw -->
  ...
</model>
```

**Examples:**
- `<pose>3 0 0.2 0 0 0</pose>` - 3m in front (default)
- `<pose>5 0 0.2 0 0 0</pose>` - 5m in front (farther)
- `<pose>2 1 0.2 0 0 0</pose>` - 2m front, 1m left
- `<pose>3 -1 0.2 0 0 0</pose>` - 3m front, 1m right

After changing, rebuild: `colcon build --packages-select gazebo_simulation`

### 2. Adjusting Detection Sensitivity

Edit: `src/perception/perception/ball_detector.py`

```python
# Line ~85-110: Color detection parameters
class BallDetector(Node):
    def __init__(self):
        # HSV color ranges for RED
        self.lower_red1 = np.array([0, 100, 100])
        self.upper_red1 = np.array([10, 255, 255])
        
        # Minimum size to detect
        self.min_contour_area = 500  # Increase to ignore noise
                                      # Decrease to detect smaller/farther balls
        
        # Blur amount (noise reduction)
        self.blur_kernel = 15  # Increase for more blur
```

**For different ball colors:**

```python
# BLUE ball
self.lower_color = np.array([100, 100, 100])
self.upper_color = np.array([130, 255, 255])

# GREEN ball
self.lower_color = np.array([40, 40, 40])
self.upper_color = np.array([80, 255, 255])

# YELLOW ball
self.lower_color = np.array([20, 100, 100])
self.upper_color = np.array([30, 255, 255])
```

And update the world file to match:
```xml
<!-- In ball_world.sdf, change ball color -->
<ambient>0 0 1 1</ambient>  <!-- Blue -->
<diffuse>0 0 1 1</diffuse>
```

After changing, rebuild: `colcon build --packages-select perception`

### 3. Tuning Robot Control Parameters

Edit: `src/control/control/ball_controller.py`

```python
# Line ~90-115: Control parameters
class BallController(Node):
    def __init__(self):
        # Alignment precision
        self.alignment_threshold = 0.1  # How centered (0-1)
        
        # Speed parameters
        self.angular_speed_max = 0.5    # Max rotation speed (rad/s)
        self.linear_speed_base = 0.3    # Base forward speed (m/s)
        self.linear_speed_max = 0.5     # Max forward speed (m/s)
        
        # When to start hitting
        self.distance_threshold = 0.6   # Distance score (0-1)
        
        # Hitting power
        self.hit_speed = 0.7            # Hit speed (m/s)
        self.hit_duration = 2.0         # Hit duration (seconds)
```

**Common adjustments:**
- **More aggressive approach**: Increase `linear_speed_base` and `linear_speed_max`
- **More powerful hit**: Increase `hit_speed` and `hit_duration`
- **More precise alignment**: Decrease `alignment_threshold`
- **Faster search**: Increase `search_angular_speed`

After changing, rebuild: `colcon build --packages-select control`

### 4. Modifying Robot Model

Edit: `src/gazebo_simulation/urdf/robot.urdf`

```xml
<!-- Base link dimensions (line ~50) -->
<geometry>
  <box size="0.6 0.4 0.2"/>  <!-- Length Width Height -->
</geometry>

<!-- Wheel parameters (line ~90, ~130) -->
<cylinder radius="0.1" length="0.05"/>  <!-- Radius Length -->

<!-- Camera field of view (line ~280) -->
<horizontal_fov>1.3962634</horizontal_fov>  <!-- ~80 degrees -->

<!-- Differential drive settings (line ~310) -->
<wheel_separation>0.5</wheel_separation>
<wheel_diameter>0.2</wheel_diameter>
<max_wheel_torque>20</max_wheel_torque>
```

After changing, rebuild: `colcon build --packages-select gazebo_simulation`

## 🐛 Debugging

### View Available Topics

```bash
# List all topics
ros2 topic list

# Expected topics:
# /camera/image_raw     - Camera images
# /ball_position        - Detected ball position
# /cmd_vel             - Velocity commands
# /odom                - Robot odometry
```

### Monitor Ball Detection

```bash
# Watch ball position updates
ros2 topic echo /ball_position

# Output format:
# x: 0.25    # Horizontal position (-1 to 1)
# y: -0.1    # Vertical position (-1 to 1)
# z: 0.45    # Distance score (0 to 1)
```

### Monitor Robot Commands

```bash
# Watch velocity commands
ros2 topic echo /cmd_vel

# Output format:
# linear.x: 0.3   # Forward speed
# angular.z: 0.2  # Rotation speed
```

### Enable Debug Visualization

Edit `ball_detector.py`:
```python
# Line ~115
self.show_debug = True  # Shows camera view with detection overlay
```

Rebuild and run. A window will show the camera feed with detected ball highlighted.

### Check Node Status

```bash
# List running nodes
ros2 node list

# Expected nodes:
# /ball_detector
# /ball_controller
# /robot_state_publisher
```

### View Node Logs

```bash
# Ball detector logs
ros2 run perception ball_detector --ros-args --log-level debug

# Controller logs  
ros2 run control ball_controller --ros-args --log-level debug
```

## 🎯 How It Works

### 1. Perception (Ball Detection)

The `ball_detector` node:
1. Subscribes to `/camera/image_raw`
2. Converts image to HSV color space
3. Filters for red color using threshold ranges
4. Finds contours in the filtered mask
5. Identifies largest contour as the ball
6. Calculates ball's position relative to camera center
7. Publishes position to `/ball_position`

### 2. Control (Navigation)

The `ball_controller` node implements a state machine:

**State: SEARCHING**
- No ball detected
- Robot rotates slowly to scan for ball
- Transitions to ALIGNING when ball detected

**State: ALIGNING**
- Ball detected but not centered
- Robot rotates to center ball in view
- Transitions to APPROACHING when centered

**State: APPROACHING**
- Ball centered in view
- Robot moves forward while maintaining alignment
- Speed increases as ball gets closer
- Transitions to HITTING when close enough

**State: HITTING**
- Final push at high speed
- Duration-based (2 seconds default)
- Returns to SEARCHING after hit completes

### 3. Robot Model

The robot features:
- **Differential drive**: Two independently-driven wheels
- **Caster wheel**: Front support for stability  
- **Camera**: Front-mounted, publishes RGB images
- **Pusher**: Front bumper element for hitting ball
- **Sensors**: Publishes odometry and camera data

## 📊 Topics and Messages

| Topic | Type | Description |
|-------|------|-------------|
| `/camera/image_raw` | `sensor_msgs/Image` | Raw camera feed (640x480 RGB) |
| `/camera/camera_info` | `sensor_msgs/CameraInfo` | Camera calibration data |
| `/ball_position` | `geometry_msgs/Point` | Detected ball position |
| `/cmd_vel` | `geometry_msgs/Twist` | Velocity commands to robot |
| `/odom` | `nav_msgs/Odometry` | Robot odometry (position, velocity) |
| `/tf` | `tf2_msgs/TFMessage` | Transform tree |

## 🔧 Troubleshooting

### Gazebo doesn't start
```bash
# Make sure Gazebo is properly installed
gz sim --version

# If not installed:
sudo apt install gz-garden
```

### Robot doesn't appear in Gazebo
```bash
# Check if URDF is valid
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat src/gazebo_simulation/urdf/robot.urdf)"

# Check Gazebo logs
gz log
```

### Ball not detected
- Check ball color matches detection parameters
- Enable debug visualization: set `show_debug = True` in `ball_detector.py`
- Verify camera is working: `ros2 topic echo /camera/image_raw`
- Adjust HSV color ranges in `ball_detector.py`

### Robot doesn't move
- Check velocity commands: `ros2 topic echo /cmd_vel`
- Verify controller is running: `ros2 node list`
- Check for errors: `ros2 node info /ball_controller`

### Build errors
```bash
# Clean and rebuild
rm -rf build install log
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

### Import errors (OpenCV)
```bash
# Install OpenCV for Python
pip3 install opencv-python
# Or system-wide:
sudo apt install python3-opencv
```

## 🎓 Learning Resources

- [ROS2 Humble Documentation](https://docs.ros.org/en/humble/)
- [Gazebo Documentation](https://gazebosim.org/docs)
- [OpenCV Python Tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)
- [URDF Tutorial](http://wiki.ros.org/urdf/Tutorials)

## 📝 License

Apache License 2.0

## 🤝 Contributing

This is an educational project. Feel free to modify and extend it for your needs!

## ✨ Features to Add

Some ideas for extending this project:
- [ ] Add obstacle avoidance
- [ ] Multiple ball detection and targeting
- [ ] Path planning (not just reactive control)
- [ ] Deep learning-based detection (YOLO)
- [ ] Kick mechanism (articulated joint)
- [ ] Multiple robots competing
- [ ] Score tracking system
- [ ] Different ball types (bouncy, heavy, etc.)

---

**Enjoy your ball-hitting robot! 🤖⚽**
