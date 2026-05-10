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
# RoboStriker

RoboStriker is a focused, portfolio-ready ROS 2 + Ignition/Gazebo project that demonstrates a perception-driven differential-drive robot whose goal is to detect and strike a ball in simulation.

Why this repo is hireable
- Clear ROS 2 skills: nodes, messages, launch files and topic bridging (ros_gz_bridge)
- Simulation and model authoring: SDF/URDF, sensors, joints and plugins
- Perception + control: camera-based detection (OpenCV) and a simple reactive controller
- Reproducible demo with a short GIF/video you can place at the top of the README

Quick start (short)

```bash
# from repository root
colcon build --symlink-install
source install/setup.bash
ros2 launch gazebo_simulation full_system.launch.py use_demo_kick:=true
```

This will start Ignition/Gazebo with the demo world, bring up the perception and control nodes and (if enabled) auto-drive the robot toward the ball.

Recording an animated demo (GIF)

Use the provided script to record the screen and convert to a compact GIF. Example (records 8s and crops to a 800x600 region starting at X=100,Y=100):

```bash
chmod +x scripts/capture_demo.sh
# Record and create GIF
scripts/capture_demo.sh /tmp/robo_demo.gif 8 100:100:800x600

# Result: /tmp/robo_demo.gif (optimize with gifsicle if desired)
```

Notes about the script
- Requires ffmpeg and ImageMagick or gifsicle for optional optimization
- Uses X11 screen capture; if your session is Wayland, use an XWayland session or alternative recorder (see script header)

Repository layout (short)

```
.
├── src/
│   ├── gazebo_simulation/   # SDF models, world, launch files
│   ├── perception/          # ball_detector node (OpenCV)
│   └── control/             # controller and demo_kick
├── scripts/
│   └── capture_demo.sh      # Record & convert demo to GIF
└── README.md
```

What to include in your portfolio page
- A short GIF (use the script) placed at the top of the README
- A one-paragraph "What I built / What I learned" section
- Tech stack bullets (ROS 2, Ignition/Gazebo, OpenCV, CI)
- A minimal smoke-test command (headless launch + a topic-check script)

License

Choose a permissive license (MIT recommended) and add a LICENSE file.

Want me to:
- add a short architecture diagram (SVG) and an example GIF at the top of the README
- create a tiny GitHub Actions job that runs a headless smoke-test on push
If so, say which you'd like first and I will add it.
After changing, rebuild: `colcon build --packages-select perception`
