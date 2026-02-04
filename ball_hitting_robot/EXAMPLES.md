# Usage Examples - Ball-Hitting Robot

This document provides practical examples for common use cases and scenarios.

---

## 🚀 Basic Usage

### Example 1: Run Complete System (Default)

```bash
# Navigate to workspace
cd ~/Documents/PSD/ball_hitting_robot

# Source and run
source install/setup.bash
./run.sh
```

**Expected Behavior:**
- Gazebo opens with robot and red ball 3m ahead
- Robot rotates searching for ball
- Once detected, robot centers the ball
- Robot approaches the ball
- Robot hits the ball, pushing it forward

---

## 🎯 Configuration Examples

### Example 2: Change Ball to Different Position

**Scenario**: Place ball 5 meters forward and 2 meters to the left

1. Edit world file:
```bash
nano src/gazebo_simulation/worlds/ball_world.sdf
```

2. Find and modify (around line 100):
```xml
<model name="red_ball">
  <pose>5 2 0.2 0 0 0</pose>  <!-- Changed from 3 0 0.2 0 0 0 -->
  ...
</model>
```

3. Rebuild and run:
```bash
colcon build --packages-select gazebo_simulation
source install/setup.bash
./run.sh
```

### Example 3: Detect Blue Ball Instead of Red

**Scenario**: Change the ball color to blue and update detection

1. Change ball visual in world:
```bash
nano src/gazebo_simulation/worlds/ball_world.sdf
```

Find (around line 135):
```xml
<material>
  <ambient>0 0 1 1</ambient>   <!-- Blue: was 1 0 0 1 -->
  <diffuse>0 0 1 1</diffuse>   <!-- Blue: was 1 0 0 1 -->
  <specular>0.5 0.5 0.5 1</specular>
  <emissive>0 0 0.2 1</emissive>  <!-- Blue: was 0.2 0 0 1 -->
</material>
```

2. Update detection parameters:
```bash
nano src/perception/perception/ball_detector.py
```

Find (around line 95) and replace red ranges:
```python
# Comment out red ranges:
# self.lower_red1 = np.array([0, 100, 100])
# self.upper_red1 = np.array([10, 255, 255])
# self.lower_red2 = np.array([170, 100, 100])
# self.upper_red2 = np.array([180, 255, 255])

# Add blue range:
self.lower_blue = np.array([100, 100, 100])
self.upper_blue = np.array([130, 255, 255])
```

And modify detection logic (around line 210):
```python
# Change mask creation:
# mask1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
# mask2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2)
# mask = cv2.bitwise_or(mask1, mask2)

# To:
mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
```

3. Rebuild:
```bash
colcon build --packages-select gazebo_simulation perception
source install/setup.bash
./run.sh
```

### Example 4: Make Robot More Aggressive

**Scenario**: Faster approach and stronger hit

```bash
nano src/control/control/ball_controller.py
```

Modify parameters (around line 90-115):
```python
# Increased speeds for more aggressive behavior
self.linear_speed_base = 0.5      # Was 0.3
self.linear_speed_max = 0.8       # Was 0.5
self.angular_speed_max = 0.8      # Was 0.5
self.hit_speed = 1.2              # Was 0.7
self.hit_duration = 3.0           # Was 2.0
```

Rebuild:
```bash
colcon build --packages-select control
source install/setup.bash
./run.sh
```

### Example 5: Make Robot More Precise

**Scenario**: Slower, more accurate alignment

```bash
nano src/control/control/ball_controller.py
```

Modify:
```python
# More precise but slower
self.alignment_threshold = 0.05   # Was 0.1 (tighter tolerance)
self.angular_speed_max = 0.3      # Was 0.5 (slower rotation)
self.linear_speed_base = 0.2      # Was 0.3 (slower approach)
self.linear_speed_max = 0.3       # Was 0.5
self.angular_kp = 1.5             # Was 2.0 (gentler turning)
```

Rebuild:
```bash
colcon build --packages-select control
source install/setup.bash
./run.sh
```

---

## 🐛 Debugging Examples

### Example 6: Visualize Ball Detection

**Scenario**: See what the camera sees with detection overlay

```bash
nano src/perception/perception/ball_detector.py
```

Change (around line 115):
```python
self.show_debug = True  # Was False
```

Rebuild and run:
```bash
colcon build --packages-select perception
source install/setup.bash
./run.sh
```

A window will appear showing:
- Original camera view
- Detected ball with green circle
- Red center point
- Blue bounding box
- Position text overlay

Press 'q' or close window to stop.

### Example 7: Monitor Ball Detection in Real-Time

```bash
# Terminal 1: Run system
./run.sh

# Terminal 2: Monitor ball position
source install/setup.bash
ros2 topic echo /ball_position
```

Output:
```
x: 0.15        # Ball slightly left of center
y: -0.05       # Ball slightly below center
z: 0.45        # Ball at medium distance
---
```

### Example 8: Monitor Robot Commands

```bash
# Terminal 1: Run system
./run.sh

# Terminal 2: Monitor velocity commands
source install/setup.bash
ros2 topic echo /cmd_vel
```

Output shows robot's movement commands:
```
linear:
  x: 0.35      # Forward speed
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.12      # Turning speed
---
```

### Example 9: Check All Active Topics

```bash
source install/setup.bash
ros2 topic list
```

Expected output:
```
/ball_position
/camera/camera_info
/camera/image_raw
/cmd_vel
/odom
/parameter_events
/rosout
/tf
/tf_static
```

### Example 10: Verify Nodes Are Running

```bash
source install/setup.bash
ros2 node list
```

Expected output:
```
/ball_controller
/ball_detector
/robot_state_publisher
/ros_gz_bridge
```

---

## 🎮 Advanced Scenarios

### Example 11: Robot Starts Behind the Ball

**Scenario**: Place robot behind ball, facing away

1. Modify spawn position in launch file:
```bash
nano src/gazebo_simulation/launch/sim_robot.launch.py
```

Change (around line 75):
```python
spawn_entity = Node(
    arguments=[
        '-x', '4.0',    # Behind ball (ball is at x=3)
        '-y', '0.0',
        '-z', '0.1',
        '-Y', '3.14159' # 180 degrees (facing backward)
    ]
)
```

2. Run:
```bash
colcon build --packages-select gazebo_simulation
source install/setup.bash
./run.sh
```

Robot will rotate 180°, find ball, and hit it.

### Example 12: Multiple Ball Positions to Test

**Scenario**: Quickly test different ball positions

Create a script `test_positions.sh`:
```bash
#!/bin/bash

# Array of positions to test
positions=(
    "2 0 0.2"    # Close center
    "5 0 0.2"    # Far center
    "3 1 0.2"    # Left
    "3 -1 0.2"   # Right
    "4 2 0.2"    # Far left
)

for pos in "${positions[@]}"; do
    echo "Testing position: $pos"
    
    # Update world file
    sed -i "s/<pose>[0-9.]* [0-9.-]* [0-9.]* 0 0 0/<pose>$pos 0 0 0/" \
        src/gazebo_simulation/worlds/ball_world.sdf
    
    # Rebuild
    colcon build --packages-select gazebo_simulation
    
    # Run for 30 seconds
    timeout 30 ./run.sh
    
    sleep 2
done
```

### Example 13: Increase Detection Range

**Scenario**: Detect smaller/farther balls

```bash
nano src/perception/perception/ball_detector.py
```

Change:
```python
self.min_contour_area = 200  # Was 500 (detect smaller objects)
```

And in control node:
```bash
nano src/control/control/ball_controller.py
```

Change:
```python
self.distance_threshold = 0.4  # Was 0.6 (start hitting earlier)
```

Rebuild:
```bash
colcon build --packages-select perception control
source install/setup.bash
./run.sh
```

### Example 14: Slower Search Pattern

**Scenario**: Robot searches more slowly for better detection

```bash
nano src/control/control/ball_controller.py
```

Change:
```python
self.search_angular_speed = 0.15  # Was 0.3 (slower rotation)
self.detection_timeout = 3.0      # Was 2.0 (more patient)
```

Rebuild:
```bash
colcon build --packages-select control
source install/setup.bash
./run.sh
```

---

## 📊 Performance Tuning Examples

### Example 15: Optimize for Speed

**All changes for fastest performance:**

```bash
# Control (more aggressive)
nano src/control/control/ball_controller.py
```
```python
self.alignment_threshold = 0.15      # More tolerant
self.angular_speed_max = 0.8         # Faster turning
self.linear_speed_base = 0.5         # Faster approach
self.linear_speed_max = 1.0          # Higher max speed
self.hit_speed = 1.5                 # Powerful hit
self.search_angular_speed = 0.5      # Fast search
```

```bash
# Perception (less processing)
nano src/perception/perception/ball_detector.py
```
```python
self.blur_kernel = 7                 # Less blur (faster)
self.erode_iterations = 1            # Fewer operations
self.dilate_iterations = 1
```

Rebuild all:
```bash
colcon build
source install/setup.bash
./run.sh
```

### Example 16: Optimize for Accuracy

**All changes for best accuracy:**

```bash
# Control (more precise)
nano src/control/control/ball_controller.py
```
```python
self.alignment_threshold = 0.05      # Very tight
self.angular_speed_max = 0.3         # Gentle turning
self.angular_kp = 1.2                # Less aggressive
self.linear_speed_base = 0.2         # Slow approach
self.linear_speed_max = 0.4          # Limited speed
self.search_angular_speed = 0.2      # Careful search
```

```bash
# Perception (more processing)
nano src/perception/perception/ball_detector.py
```
```python
self.blur_kernel = 21                # More noise reduction
self.min_contour_area = 600          # Ignore small noise
self.erode_iterations = 3            # More cleanup
self.dilate_iterations = 3
```

Rebuild:
```bash
colcon build
source install/setup.bash
./run.sh
```

---

## 🔧 Troubleshooting Examples

### Example 17: Ball Not Detected - Debug Steps

```bash
# Step 1: Verify camera is working
source install/setup.bash
ros2 topic hz /camera/image_raw

# Should show ~30 Hz
# If nothing, camera isn't publishing

# Step 2: Enable debug visualization
nano src/perception/perception/ball_detector.py
# Set: self.show_debug = True

# Step 3: Check if color range is correct
# In debug window, adjust HSV values if needed

# Step 4: Lower detection threshold
# Set: self.min_contour_area = 100
```

### Example 18: Robot Doesn't Move - Debug Steps

```bash
# Step 1: Check if controller is receiving ball position
ros2 topic echo /ball_position

# If empty, perception isn't detecting ball

# Step 2: Check if controller is publishing commands
ros2 topic echo /cmd_vel

# If empty, controller has issue

# Step 3: Check controller logs
ros2 run control ball_controller --ros-args --log-level debug

# Step 4: Manually test robot movement
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.2, y: 0, z: 0}, angular: {x: 0, y: 0, z: 0.0}}"
# Robot should move forward if working
```

---

## 📚 Learning Examples

### Example 19: Understanding State Transitions

Add logging to see state changes:

```bash
nano src/control/control/ball_controller.py
```

Add after state changes:
```python
# In align_behavior, after state change:
self.get_logger().info(f'STATE CHANGE: ALIGNING → APPROACHING at x={ball_x:.2f}')

# In approach_behavior:
self.get_logger().info(f'STATE: APPROACHING - distance={ball_distance:.2f}, aligned={abs(ball_x) < self.alignment_threshold}')

# In hit_behavior:
elapsed = (self.get_clock().now() - self.hit_start_time).nanoseconds / 1e9
self.get_logger().info(f'STATE: HITTING - elapsed={elapsed:.1f}s / {self.hit_duration}s')
```

Now run and watch terminal for detailed state information.

### Example 20: Add Custom Behavior - Celebration After Hit

```bash
nano src/control/control/ball_controller.py
```

Add new state:
```python
class ControlState(Enum):
    SEARCHING = 1
    ALIGNING = 2
    APPROACHING = 3
    HITTING = 4
    CELEBRATING = 5  # New state
```

Add behavior:
```python
def celebrate_behavior(self):
    """Spin in place after successful hit"""
    cmd = Twist()
    
    if self.celebrate_start_time is None:
        self.celebrate_start_time = self.get_clock().now()
    
    elapsed = (self.get_clock().now() - self.celebrate_start_time).nanoseconds / 1e9
    
    if elapsed > 2.0:  # Celebrate for 2 seconds
        self.get_logger().info('Celebration complete - entering SEARCHING')
        self.state = ControlState.SEARCHING
        self.celebrate_start_time = None
        return Twist()
    
    # Spin in place
    cmd.angular.z = 1.0
    return cmd
```

Update hit_behavior exit:
```python
def hit_behavior(self):
    # ... existing code ...
    if elapsed_time > self.hit_duration:
        self.get_logger().info('Hit complete - CELEBRATING!')
        self.state = ControlState.CELEBRATING
        self.celebrate_start_time = None
        return cmd
```

Add to control_loop:
```python
elif self.state == ControlState.CELEBRATING:
    cmd = self.celebrate_behavior()
```

---

## 💡 Tips and Tricks

### Quick Parameter Testing

Create a parameters YAML file `config/control_params.yaml`:
```yaml
ball_controller:
  ros__parameters:
    linear_speed_base: 0.4
    hit_speed: 0.9
    alignment_threshold: 0.08
```

Load with:
```bash
ros2 run control ball_controller --ros-args --params-file config/control_params.yaml
```

### Recording and Playback

Record a session:
```bash
ros2 bag record -a -o test_run
```

Playback:
```bash
ros2 bag play test_run
```

### Remote Monitoring

On robot computer:
```bash
./run.sh
```

On another computer (same network):
```bash
export ROS_DOMAIN_ID=0  # Match robot's domain
ros2 topic list
ros2 topic echo /ball_position
```

---

**For more examples and documentation, see README.md and CONFIG.md**
