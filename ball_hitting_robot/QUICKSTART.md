# Quick Start Guide - Ball-Hitting Robot

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
cd ~/Documents/PSD/ball_hitting_robot
./setup.sh
```

This will install:
- ROS2 Humble
- Gazebo simulation
- Python dependencies (OpenCV, NumPy)
- Build tools

### Step 2: Build the Project
```bash
./build.sh
```

This compiles all ROS2 packages.

### Step 3: Run the Simulation
```bash
./run.sh
```

That's it! The robot will:
1. ✅ Start in Gazebo
2. ✅ Detect the red ball with its camera
3. ✅ Automatically navigate toward it
4. ✅ Hit/push the ball

---

## 📺 What You'll See

1. **Gazebo Window**: 3D simulation with robot and red ball
2. **Terminal Output**: Status messages from detection and control nodes
3. **Robot Behavior**:
   - Searches for ball (rotating)
   - Aligns with ball (centering in view)
   - Approaches ball (moving forward)
   - Hits ball (final push)

---

## 🎮 Try These Experiments

### Change Ball Position
```bash
# Edit the world file
nano src/gazebo_simulation/worlds/ball_world.sdf

# Find line with <pose>3 0 0.2 0 0 0</pose>
# Change to: <pose>5 1 0.2 0 0 0</pose> (5m forward, 1m left)

# Rebuild and run
./build.sh
./run.sh
```

### Make Robot Faster
```bash
# Edit the controller
nano src/control/control/ball_controller.py

# Find and increase:
# self.linear_speed_base = 0.5  (was 0.3)
# self.hit_speed = 1.0  (was 0.7)

# Rebuild and run
colcon build --packages-select control
./run.sh
```

### Detect Different Color Ball
```bash
# 1. Change ball color in world
nano src/gazebo_simulation/worlds/ball_world.sdf
# Change: <ambient>0 0 1 1</ambient> (blue ball)

# 2. Update detection parameters
nano src/perception/perception/ball_detector.py
# Uncomment blue color range lines (~95-97)

# Rebuild and run
./build.sh
./run.sh
```

---

## 🐛 Troubleshooting

### Problem: Build fails
```bash
# Clean rebuild
./build.sh clean
```

### Problem: Gazebo doesn't start
```bash
# Check Gazebo installation
gz sim --version

# Reinstall if needed
sudo apt install gz-garden
```

### Problem: Ball not detected
```bash
# Test camera
ros2 topic echo /camera/image_raw

# Enable debug view
nano src/perception/perception/ball_detector.py
# Set: self.show_debug = True
```

### Problem: Robot doesn't move
```bash
# Check velocity commands
ros2 topic echo /cmd_vel

# Verify controller is running
ros2 node list
```

---

## 📚 Learn More

See **README.md** for:
- Complete documentation
- Detailed configuration guide
- Architecture explanation
- Advanced troubleshooting

---

## 🎓 Understanding the Code

### Key Files:

1. **Robot Model**: `src/gazebo_simulation/urdf/robot.urdf`
   - Defines robot structure, sensors, and physics

2. **World**: `src/gazebo_simulation/worlds/ball_world.sdf`
   - Contains ball position and environment

3. **Detection**: `src/perception/perception/ball_detector.py`
   - OpenCV-based color detection
   - Publishes ball position

4. **Control**: `src/control/control/ball_controller.py`
   - State machine controller
   - Navigation and hitting logic

5. **Launch**: `src/gazebo_simulation/launch/full_system.launch.py`
   - Starts all components

---

## 🤝 Need Help?

1. Check **README.md** for detailed documentation
2. Review terminal error messages
3. Use `ros2 topic list` and `ros2 node list` to debug
4. Enable debug mode in detection node

---

**Happy Robot Building! 🤖⚽**
