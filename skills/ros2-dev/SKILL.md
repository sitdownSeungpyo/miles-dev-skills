---
name: ros2-dev
description: Production-grade ROS 2 development — packages, nodes, launch files, QoS, TF2, Nav2/MoveIt2, micro-ROS, colcon builds. Use when working with ROS 2 code, .launch.py files, package.xml, URDF, or when the user mentions robots, nodes, topics, services, or actions.
---

# ROS 2 Development

Expert guidance for ROS 2 (Humble/Iron/Jazzy) robotics development.

## Workflow

1. **Identify the distro first**: check `ROS_DISTRO` env var or `package.xml` format before writing code. API differences between Humble and Jazzy matter (e.g., `rclcpp` executor APIs).
2. **Package structure**: always generate compliant packages:
   - Python: `ros2 pkg create --build-type ament_python <name>`, entry points in `setup.py`, nodes in `<pkg>/<pkg>/`.
   - C++: `ament_cmake`, targets registered with `rclcpp_components` when composable.
3. **Build & verify**: `colcon build --symlink-install --packages-select <pkg>` then `source install/setup.bash` (or `local_setup.ps1` on Windows). Never skip sourcing after build.

## Node design rules

- Prefer **composable nodes** (`rclcpp_components` / lifecycle nodes) over standalone executables for production.
- Use **lifecycle nodes** for anything managing hardware (configure → activate → deactivate cleanup path).
- Timers and callbacks must be non-blocking; long work goes to a separate callback group + `MultiThreadedExecutor`.
- Declare all parameters with descriptors and defaults; support runtime reconfigure where sensible.

## QoS — get it right

| Use case | Profile |
|---|---|
| Sensor streams (lidar, camera, IMU) | `SensorDataQoS` (best-effort, small depth) |
| Commands (cmd_vel) | reliable, volatile, depth 1–10 |
| Latched state (map, robot_description) | reliable, `transient_local`, depth 1 |

QoS mismatch (best-effort pub → reliable sub) silently drops connections — always check with `ros2 topic info -v` when a subscription receives nothing.

## Debugging checklist

```bash
ros2 node list && ros2 topic list
ros2 topic info -v /topic        # QoS + endpoint check
ros2 topic hz /topic             # rate check
ros2 doctor --report             # environment issues
ros2 run tf2_tools view_frames   # TF tree
```
- Nodes can't see each other → check `ROS_DOMAIN_ID` and DDS (CycloneDDS vs FastDDS) mismatch.
- TF errors → verify `use_sim_time` consistency across all nodes.

## Launch files

- Python launch files; use `DeclareLaunchArgument` + `LaunchConfiguration` for every tunable.
- Group namespaced nodes with `GroupAction` + `PushRosNamespace`.
- Include other launch files via `IncludeLaunchDescription` with `PathJoinSubstitution(FindPackageShare(...))` — never hardcode paths.

## micro-ROS (ESP32/STM32/RP2040)

- Agent on host: `ros2 run micro_ros_agent micro_ros_agent serial --dev <port> -b 115200`.
- On MCU: allocate all entities at init (no dynamic allocation in loop), use `rclc_executor` with fixed handle count, and always check return codes (`RCCHECK`).
- Transport choice: serial for bench, UDP over WiFi for ESP32 in the field.

## Testing

- Python: `pytest` + `launch_testing`; C++: `gtest` + `ament_lint_auto`.
- Integration: `launch_testing` with process I/O assertions; bag-replay regression tests via `ros2 bag play`.
