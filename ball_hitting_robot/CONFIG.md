# Configuration Reference - Ball-Hitting Robot

This document provides a comprehensive reference for all configurable parameters in the ball-hitting robot project.

---

## 🌍 World Configuration

**File**: `src/gazebo_simulation/worlds/ball_world.sdf`

### Ball Position
```xml
<model name="red_ball">
  <pose>X Y Z Roll Pitch Yaw</pose>
</model>
```

| Parameter | Default | Unit | Description |
|-----------|---------|------|-------------|
| X | 3.0 | meters | Forward distance from origin (+forward, -backward) |
| Y | 0.0 | meters | Lateral distance from origin (+left, -right) |
| Z | 0.2 | meters | Height above ground (keep at ball radius) |
| Roll | 0.0 | radians | Rotation around X-axis (usually 0) |
| Pitch | 0.0 | radians | Rotation around Y-axis (usually 0) |
| Yaw | 0.0 | radians | Rotation around Z-axis (usually 0) |

**Example Positions**:
- Close: `<pose>2 0 0.2 0 0 0</pose>`
- Far: `<pose>5 0 0.2 0 0 0</pose>`
- Left: `<pose>3 1 0.2 0 0 0</pose>`
- Right: `<pose>3 -1 0.2 0 0 0</pose>`

### Ball Physical Properties
```xml
<inertial>
  <mass>0.5</mass>  <!-- kg -->
</inertial>
```

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| mass | 0.5 | 0.1-2.0 | Ball mass (kg) - heavier = harder to push |
| radius | 0.2 | 0.1-0.5 | Ball size (meters) |
| mu (friction) | 1.0 | 0.0-2.0 | Surface friction - higher = less sliding |
| kp (stiffness) | 1000000.0 | 1000-1000000 | Contact stiffness - higher = less deformation |
| kd (damping) | 100.0 | 1-1000 | Contact damping - higher = less bouncy |

### Ball Color (for visual appearance)
```xml
<material>
  <ambient>R G B A</ambient>
  <diffuse>R G B A</diffuse>
</material>
```

| Color | Ambient | Diffuse |
|-------|---------|---------|
| Red | `1 0 0 1` | `1 0 0 1` |
| Blue | `0 0 1 1` | `0 0 1 1` |
| Green | `0 1 0 1` | `0 1 0 1` |
| Yellow | `1 1 0 1` | `1 1 0 1` |
| Orange | `1 0.5 0 1` | `1 0.5 0 1` |
| Purple | `0.5 0 0.5 1` | `0.5 0 0.5 1` |

---

## 🤖 Robot Configuration

**File**: `src/gazebo_simulation/urdf/robot.urdf`

### Robot Dimensions
```xml
<geometry>
  <box size="length width height"/>
</geometry>
```

| Component | Default Size | Description |
|-----------|--------------|-------------|
| Base | `0.6 0.4 0.2` | Main chassis (L×W×H meters) |
| Wheels | radius=`0.1`, length=`0.05` | Drive wheels |
| Caster | radius=`0.05` | Support wheel |
| Pusher | `0.05 0.3 0.15` | Front bumper |
| Camera | `0.05 0.05 0.05` | Camera housing |

### Camera Settings
```xml
<camera>
  <horizontal_fov>1.3962634</horizontal_fov>
  <image>
    <width>640</width>
    <height>480</height>
  </image>
  <update_rate>30</update_rate>
</camera>
```

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| horizontal_fov | 1.3962634 | 0.5-2.0 | Field of view (radians, ~80°) |
| width | 640 | 320-1920 | Image width (pixels) |
| height | 480 | 240-1080 | Image height (pixels) |
| update_rate | 30 | 10-60 | Frames per second |

### Differential Drive
```xml
<plugin name="diff_drive_controller">
  <wheel_separation>0.5</wheel_separation>
  <wheel_diameter>0.2</wheel_diameter>
  <max_wheel_torque>20</max_wheel_torque>
  <max_wheel_acceleration>1.0</max_wheel_acceleration>
</plugin>
```

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| wheel_separation | 0.5 | 0.3-1.0 | Distance between wheels (meters) |
| wheel_diameter | 0.2 | 0.1-0.4 | Wheel diameter (meters) |
| max_wheel_torque | 20 | 5-50 | Maximum torque (N⋅m) |
| max_wheel_acceleration | 1.0 | 0.5-5.0 | Max acceleration (rad/s²) |

---

## 👁️ Perception Configuration

**File**: `src/perception/perception/ball_detector.py`

### Color Detection (HSV)

For **RED** ball (wraps around HSV):
```python
self.lower_red1 = np.array([0, 100, 100])
self.upper_red1 = np.array([10, 255, 255])
self.lower_red2 = np.array([170, 100, 100])
self.upper_red2 = np.array([180, 255, 255])
```

For **other colors** (single range):

| Color | Lower HSV | Upper HSV |
|-------|-----------|-----------|
| Blue | `[100, 100, 100]` | `[130, 255, 255]` |
| Green | `[40, 40, 40]` | `[80, 255, 255]` |
| Yellow | `[20, 100, 100]` | `[30, 255, 255]` |
| Orange | `[10, 100, 100]` | `[20, 255, 255]` |
| Purple | `[130, 50, 50]` | `[160, 255, 255]` |

**HSV Tuning Tips**:
- Hue (H): Color (0-180)
- Saturation (S): Color intensity (0-255) - lower min to detect pale colors
- Value (V): Brightness (0-255) - lower min for darker environments

### Detection Sensitivity
```python
self.min_contour_area = 500      # Minimum detection size
self.blur_kernel = 15             # Noise reduction
self.erode_iterations = 2         # Noise removal passes
self.dilate_iterations = 2        # Gap filling passes
```

| Parameter | Default | Increase Effect | Decrease Effect |
|-----------|---------|-----------------|-----------------|
| min_contour_area | 500 | Ignore smaller objects | Detect farther/smaller balls |
| blur_kernel | 15 | More noise reduction | Sharper but noisier |
| erode_iterations | 2 | Remove more noise | Keep more detail |
| dilate_iterations | 2 | Fill larger gaps | Preserve sharp edges |

### Distance Estimation
```python
self.reference_ball_radius = 100  # Expected radius at reference distance
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| reference_ball_radius | 100 | Calibrated ball size (pixels) at 1 meter |

**Calibration**:
1. Place ball at known distance (e.g., 2m)
2. Enable debug mode: `self.show_debug = True`
3. Note detected radius in pixels
4. Adjust reference value

### Debug Options
```python
self.show_debug = False  # Set to True to show detection visualization
```

---

## 🎮 Control Configuration

**File**: `src/control/control/ball_controller.py`

### Alignment Parameters
```python
self.alignment_threshold = 0.1    # Centering tolerance
self.angular_speed_max = 0.5      # Max rotation speed
self.angular_kp = 2.0             # Rotation gain
```

| Parameter | Default | Increase Effect | Decrease Effect |
|-----------|---------|-----------------|-----------------|
| alignment_threshold | 0.1 | More tolerant alignment | More precise centering |
| angular_speed_max | 0.5 | Faster turning | Smoother turning |
| angular_kp | 2.0 | More aggressive turning | Gentler turning |

**Recommended Values**:
- Fast/aggressive: threshold=`0.15`, max_speed=`0.8`, kp=`3.0`
- Slow/precise: threshold=`0.05`, max_speed=`0.3`, kp=`1.0`

### Approach Parameters
```python
self.linear_speed_base = 0.3      # Base forward speed
self.linear_speed_max = 0.5       # Maximum forward speed
self.linear_kp = 0.3              # Speed gain
self.approach_angular_kp = 1.5    # Alignment correction while moving
```

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| linear_speed_base | 0.3 | 0.1-0.5 | Minimum approach speed (m/s) |
| linear_speed_max | 0.5 | 0.2-1.0 | Maximum approach speed (m/s) |
| linear_kp | 0.3 | 0.1-1.0 | Speed increase based on distance |
| approach_angular_kp | 1.5 | 0.5-3.0 | Alignment correction strength |

**Recommended Values**:
- Cautious approach: base=`0.2`, max=`0.4`, kp=`0.2`
- Fast approach: base=`0.4`, max=`0.8`, kp=`0.5`

### Hitting Parameters
```python
self.distance_threshold = 0.6     # When to trigger hit
self.hit_speed = 0.7              # Hit velocity
self.hit_duration = 2.0           # Hit duration
```

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| distance_threshold | 0.6 | 0.4-0.9 | Distance score to start hitting (0-1) |
| hit_speed | 0.7 | 0.3-1.5 | Forward speed during hit (m/s) |
| hit_duration | 2.0 | 0.5-5.0 | How long to push (seconds) |

**Recommended Values**:
- Gentle tap: threshold=`0.7`, speed=`0.4`, duration=`1.0`
- Strong hit: threshold=`0.5`, speed=`1.2`, duration=`3.0`

### Search Parameters
```python
self.search_angular_speed = 0.3   # Rotation while searching
self.detection_timeout = 2.0      # Max time without detection
```

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| search_angular_speed | 0.3 | 0.1-0.5 | Rotation speed while searching (rad/s) |
| detection_timeout | 2.0 | 0.5-5.0 | Time before entering search mode (s) |

---

## 🔧 Launch Configuration

**File**: `src/gazebo_simulation/launch/sim_robot.launch.py`

### Robot Spawn Position
```python
spawn_entity = Node(
    arguments=[
        '-x', '0.0',   # X position
        '-y', '0.0',   # Y position  
        '-z', '0.1',   # Z position
        '-Y', '0.0'    # Yaw rotation
    ]
)
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| -x | 0.0 | Forward/backward position (meters) |
| -y | 0.0 | Left/right position (meters) |
| -z | 0.1 | Height (meters) |
| -Y | 0.0 | Initial rotation (radians) |

**Example Positions**:
- Face ball from side: `'-x', '-2.0', '-y', '3.0', '-Y', '1.5708'` (90° left)
- Behind ball: `'-x', '4.0', '-Y', '3.14159'` (180° turn)

---

## 📊 Quick Reference Tables

### Effect of Parameter Changes

#### Making Robot More Aggressive
| Parameter | Change |
|-----------|--------|
| linear_speed_base | `0.3` → `0.5` |
| hit_speed | `0.7` → `1.0` |
| angular_speed_max | `0.5` → `0.8` |
| distance_threshold | `0.6` → `0.5` |

#### Making Detection More Robust
| Parameter | Change |
|-----------|--------|
| min_contour_area | `500` → `300` |
| blur_kernel | `15` → `21` |
| detection_timeout | `2.0` → `3.0` |

#### Making Robot More Precise
| Parameter | Change |
|-----------|--------|
| alignment_threshold | `0.1` → `0.05` |
| angular_kp | `2.0` → `1.5` |
| linear_speed_max | `0.5` → `0.3` |

---

## 🧪 Calibration Procedures

### Camera-Ball Distance Calibration

1. Place ball at known distance (e.g., 2 meters)
2. Enable debug mode in `ball_detector.py`:
   ```python
   self.show_debug = True
   ```
3. Run detection and note radius in pixels
4. Update `reference_ball_radius` accordingly

### Color Detection Tuning

1. Run with debug mode enabled
2. If detection fails:
   - Lower saturation minimum (2nd value in lower bound)
   - Lower value minimum (3rd value in lower bound)
   - Widen hue range
3. If false positives:
   - Raise saturation minimum
   - Raise minimum contour area

### Control Parameter Tuning

1. Start with default parameters
2. Observe behavior and adjust:
   - Overshoots target → Decrease angular_kp
   - Too slow → Increase speed parameters
   - Misses ball → Decrease alignment_threshold
   - Hits too weakly → Increase hit_speed/duration

---

## 📝 Configuration Checklist

Before running, verify:

- [ ] Ball position set in `ball_world.sdf`
- [ ] Ball color matches detection parameters
- [ ] Camera resolution appropriate for your system
- [ ] Control speeds safe for your environment
- [ ] Detection sensitivity tuned for lighting
- [ ] Debug mode disabled for production

---

**For more information, see README.md**
