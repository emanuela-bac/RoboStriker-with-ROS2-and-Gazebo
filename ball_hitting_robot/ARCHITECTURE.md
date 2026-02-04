# System Architecture Diagram

## Overall System Flow

```
                    BALL-HITTING ROBOT SYSTEM
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   GAZEBO SIMULATION                       │  │
│  │                                                            │  │
│  │  ┌────────────┐              ┌──────────────┐            │  │
│  │  │   WORLD    │              │    ROBOT     │            │  │
│  │  │            │              │              │            │  │
│  │  │  - Ground  │              │  - Chassis   │            │  │
│  │  │  - Ball    │◄─────────────┤  - Wheels    │            │  │
│  │  │  - Light   │   Physics    │  - Camera    │            │  │
│  │  └────────────┘              │  - Pusher    │            │  │
│  │                               └──────┬───────┘            │  │
│  └───────────────────────────────────────┼──────────────────┘  │
│                                           │                      │
│                              ┌────────────┴─────────────┐       │
│                              │                          │       │
│                    /camera/image_raw         /odom      │       │
│                        (Images)           (Position)    │       │
│                              │                          │       │
│  ┌───────────────────────────▼──────────────────────────────┐  │
│  │                    ROS2 TOPICS (Communication)           │  │
│  └───────────────────────────┬──────────────────────────────┘  │
│                              │                                  │
│  ┌───────────────────────────▼──────────────────────────────┐  │
│  │              PERCEPTION NODE (ball_detector)             │  │
│  │                                                           │  │
│  │  1. Receive camera images                                │  │
│  │  2. Convert to HSV color space                           │  │
│  │  3. Filter red color (or configured color)               │  │
│  │  4. Find contours                                        │  │
│  │  5. Identify largest contour as ball                     │  │
│  │  6. Calculate position (x, y, distance)                  │  │
│  │                                                           │  │
│  │  Output: /ball_position                                  │  │
│  │          (x: -1 to 1, y: -1 to 1, z: 0 to 1)            │  │
│  └───────────────────────────┬──────────────────────────────┘  │
│                              │                                  │
│                              │ /ball_position                   │
│                              │                                  │
│  ┌───────────────────────────▼──────────────────────────────┐  │
│  │              CONTROL NODE (ball_controller)              │  │
│  │                                                           │  │
│  │  STATE MACHINE:                                          │  │
│  │                                                           │  │
│  │  ┌──────────┐  Ball      ┌──────────┐  Centered  ┌────┐ │  │
│  │  │SEARCHING │─detected──►│ALIGNING  │───────────►│APP─│ │  │
│  │  └────▲─────┘            └──────────┘            │ROA─│ │  │
│  │       │                                           │CHI─│ │  │
│  │       │  Hit                                      │NG  │ │  │
│  │       │ complete        ┌──────────┐  Close      └──┬─┘ │  │
│  │       └─────────────────│ HITTING  │◄─────enough────┘   │  │
│  │                         └──────────┘                     │  │
│  │                                                           │  │
│  │  Output: /cmd_vel (linear.x, angular.z)                 │  │
│  └───────────────────────────┬──────────────────────────────┘  │
│                              │                                  │
│                              │ /cmd_vel                         │
│                              │                                  │
│  ┌───────────────────────────▼──────────────────────────────┐  │
│  │                   ROBOT ACTUATORS                        │  │
│  │                                                           │  │
│  │              Left Wheel    Right Wheel                   │  │
│  │                  ▼              ▼                         │  │
│  │             [Differential Drive Controller]              │  │
│  │                       ▼                                   │  │
│  │                  Robot Motion                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Detail

```
Camera Sensor → Image (640x480 RGB) → ball_detector Node
                                            ↓
                                    OpenCV Processing:
                                    - GaussianBlur
                                    - BGR to HSV
                                    - Color Mask
                                    - Morphology (erode/dilate)
                                    - Find Contours
                                    - Calculate Centroid
                                            ↓
                          geometry_msgs/Point (x, y, z)
                                            ↓
                                  ball_controller Node
                                            ↓
                                    State Machine Logic:
                                    - Determine current state
                                    - Calculate velocities
                                    - Generate command
                                            ↓
                          geometry_msgs/Twist (linear, angular)
                                            ↓
                                  Differential Drive Plugin
                                            ↓
                                    Wheel Velocities
                                            ↓
                                      Robot Movement
```

## Package Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                  ROS2 HUMBLE INSTALLATION                   │
├─────────────────────────────────────────────────────────────┤
│  • rclpy                  • sensor_msgs                     │
│  • geometry_msgs          • nav_msgs                        │
│  • std_msgs               • tf2                             │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌──────────────┐  ┌─────────────┐
│  gazebo_    │  │  perception  │  │   control   │
│ simulation  │  │              │  │             │
├─────────────┤  ├──────────────┤  ├─────────────┤
│ • ros_gz    │  │ • cv_bridge  │  │ • rclpy     │
│ • robot_    │  │ • opencv     │  │ • geometry_ │
│   state_    │  │ • numpy      │  │   msgs      │
│   publisher │  │              │  │             │
└─────────────┘  └──────────────┘  └─────────────┘
```

## File Organization

```
ball_hitting_robot/
│
├── 📄 Documentation Files
│   ├── README.md           - Main documentation
│   ├── QUICKSTART.md       - Quick start guide  
│   ├── CONFIG.md           - Configuration reference
│   ├── PROJECT_SUMMARY.md  - Project overview
│   └── ARCHITECTURE.md     - This file
│
├── 🔧 Setup & Build Scripts
│   ├── setup.sh            - Install dependencies
│   ├── build.sh            - Build workspace
│   └── run.sh              - Launch system
│
└── 📦 src/ (ROS2 Packages)
    │
    ├── gazebo_simulation/  - Simulation Package
    │   ├── 🚀 launch/
    │   │   ├── sim_robot.launch.py      - Launch Gazebo
    │   │   └── full_system.launch.py    - Launch everything
    │   ├── 🤖 urdf/
    │   │   └── robot.urdf               - Robot model
    │   ├── 🌍 worlds/
    │   │   └── ball_world.sdf           - World + ball
    │   ├── 📋 package.xml
    │   └── 🔨 CMakeLists.txt
    │
    ├── perception/         - Ball Detection Package
    │   ├── perception/
    │   │   ├── __init__.py
    │   │   └── 👁️ ball_detector.py     - Detection node
    │   ├── 📋 package.xml
    │   ├── ⚙️ setup.py
    │   └── ⚙️ setup.cfg
    │
    └── control/            - Robot Control Package
        ├── control/
        │   ├── __init__.py
        │   └── 🎮 ball_controller.py    - Control node
        ├── 📋 package.xml
        ├── ⚙️ setup.py
        └── ⚙️ setup.cfg
```

## State Machine Detailed

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTROL STATE MACHINE                     │
└─────────────────────────────────────────────────────────────┘

STATE: SEARCHING
┌──────────────────────────────────────────────────────────┐
│ Condition: No ball detected in timeout period            │
│ Action:    Rotate in place                               │
│            angular.z = search_angular_speed              │
│            linear.x = 0.0                                │
│ Exit:      Ball detected → ALIGNING                      │
└──────────────────────────────────────────────────────────┘

STATE: ALIGNING
┌──────────────────────────────────────────────────────────┐
│ Condition: Ball detected but not centered                │
│ Action:    Rotate to center ball                         │
│            angular.z = angular_kp * ball_x               │
│            linear.x = 0.0                                │
│ Exit:      |ball_x| < alignment_threshold → APPROACHING │
└──────────────────────────────────────────────────────────┘

STATE: APPROACHING
┌──────────────────────────────────────────────────────────┐
│ Condition: Ball centered, not close enough yet           │
│ Action:    Move forward while maintaining alignment      │
│            linear.x = base_speed + kp * distance         │
│            angular.z = approach_angular_kp * ball_x      │
│ Exit:      distance > threshold → HITTING                │
│            |ball_x| > 2*alignment_threshold → ALIGNING   │
└──────────────────────────────────────────────────────────┘

STATE: HITTING
┌──────────────────────────────────────────────────────────┐
│ Condition: Close enough to ball                          │
│ Action:    Full speed forward push                       │
│            linear.x = hit_speed                          │
│            angular.z = small correction                  │
│ Duration:  hit_duration seconds                          │
│ Exit:      Time elapsed → SEARCHING                      │
└──────────────────────────────────────────────────────────┘
```

## ROS2 Topic Graph

```
                         NODES & TOPICS

┌─────────────┐
│   Gazebo    │
│  Simulator  │
└──────┬──────┘
       │
       ├──► /camera/image_raw ────────┐
       │    (sensor_msgs/Image)        │
       │                               ▼
       ├──► /camera/camera_info    ┌───────────────┐
       │    (sensor_msgs/           │ ball_detector │
       │     CameraInfo)            │     NODE      │
       │                            └───────┬───────┘
       ├──► /odom                           │
       │    (nav_msgs/Odometry)             │
       │                                    ▼
       │                          /ball_position
       │                        (geometry_msgs/Point)
       │                                    │
       │                                    │
       │                                    ▼
       │                            ┌───────────────┐
       │                            │ball_controller│
       │                            │     NODE      │
       │                            └───────┬───────┘
       │                                    │
       │                                    ▼
       │                              /cmd_vel
       │                        (geometry_msgs/Twist)
       │                                    │
       ◄────────────────────────────────────┘

┌────────────────────┐
│robot_state_publisher│────► /tf
│       NODE          │      (tf2_msgs/TFMessage)
└────────────────────┘
```

## Build & Launch Flow

```
┌─────────────────────────────────────────────────────────┐
│  1. SETUP PHASE (./setup.sh)                            │
├─────────────────────────────────────────────────────────┤
│  ✓ Install ROS2 Humble                                  │
│  ✓ Install Gazebo                                       │
│  ✓ Install Python dependencies                          │
│  ✓ Install build tools                                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  2. BUILD PHASE (./build.sh)                            │
├─────────────────────────────────────────────────────────┤
│  ✓ Source ROS2 environment                              │
│  ✓ Run colcon build                                     │
│    - Build gazebo_simulation (CMake)                    │
│    - Build perception (Python setuptools)               │
│    - Build control (Python setuptools)                  │
│  ✓ Generate install/ directory                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  3. LAUNCH PHASE (./run.sh)                             │
├─────────────────────────────────────────────────────────┤
│  ✓ Source workspace                                     │
│  ✓ Launch full_system.launch.py                         │
│                                                          │
│    Launch Order:                                        │
│    1. Start Gazebo (gz sim)                             │
│    2. Spawn robot (ros_gz_sim create)                   │
│    3. Start robot_state_publisher                       │
│    4. Start ros_gz_bridge                               │
│    5. Start ball_detector node                          │
│    6. Start ball_controller node                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  4. RUNTIME                                             │
├─────────────────────────────────────────────────────────┤
│  Robot actively detecting and hitting ball              │
│  - Camera publishes at 30 Hz                            │
│  - Detection runs on each frame                         │
│  - Control loop runs at 10 Hz                           │
│  - Robot moves autonomously                             │
└─────────────────────────────────────────────────────────┘
```

## Coordinate Systems

```
WORLD FRAME (odom)
     Z
     │
     │
     └────► X
    ╱
   ╱
  Y

X: Forward
Y: Left
Z: Up

CAMERA OPTICAL FRAME
     Y
     │
     │
     └────► Z (forward)
    ╱
   ╱
  X (right)

IMAGE COORDINATES
(0,0) ────────► X (width)
  │
  │
  ▼
  Y (height)

BALL POSITION (published)
x: [-1, 1]  -1=right, 0=center, 1=left
y: [-1, 1]  -1=bottom, 0=center, 1=top
z: [0, 1]   0=far, 1=close
```

## Timing Diagram

```
Time →

Camera:       |─Image─|─Image─|─Image─|─Image─|  (30 Hz)
              ↓       ↓       ↓       ↓

Detector:     |─Proc─|─Proc─|─Proc─|─Proc─|    (30 Hz)
              ↓Pub    ↓Pub    ↓Pub    ↓Pub

Controller:   |──Control─|──Control─|──        (10 Hz)
              ↓Cmd       ↓Cmd

Robot:        |──────Move──────|──────Move──   (continuous)
```

## Success Criteria Checklist

✅ Robot spawns in Gazebo
✅ Ball is visible in world
✅ Camera publishes images
✅ Ball detector identifies ball
✅ Ball position is published
✅ Controller receives position
✅ Controller enters SEARCHING (if needed)
✅ Controller enters ALIGNING
✅ Robot rotates to center ball
✅ Controller enters APPROACHING
✅ Robot moves forward
✅ Controller enters HITTING
✅ Robot hits ball
✅ Ball moves from impact
✅ Controller returns to SEARCHING

---

**For implementation details, see the source code files.**
**For configuration options, see CONFIG.md.**
**For usage instructions, see README.md and QUICKSTART.md.**
