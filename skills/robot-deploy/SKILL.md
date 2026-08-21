---
name: robot-deploy
description: Deployment and CI/CD for robots and embedded fleets — Docker for ROS 2, cross-compilation, OTA firmware updates, systemd services, GitHub Actions pipelines for firmware and robot software. Use when containerizing robot software, setting up CI for firmware/ROS packages, or planning OTA/fleet updates.
---

# Robot & Embedded Deployment

Deployment discipline for software that runs on physical machines: a bad deploy can brick hardware or move a robot unexpectedly. Bias toward staged rollout and rollback paths.

## Docker for ROS 2

- Base on `ros:<distro>-ros-base`; multi-stage build (build stage with colcon, runtime stage copying `install/`).
- `--network=host` + matching `ROS_DOMAIN_ID` for DDS discovery on LAN (or configure CycloneDDS unicast peers instead).
- Device access: map only what's needed (`--device=/dev/ttyUSB0`), add udev rules for stable symlinks (`/dev/robot_lidar`), never run `--privileged` in production.
- `docker compose` per robot: one service per subsystem, `restart: unless-stopped`, healthchecks that actually check topics (e.g., `ros2 topic hz` probe script).

## On-robot services (no Docker)

- systemd units: `After=network-online.target`, `Restart=on-failure` with `RestartSec` backoff, `WatchdogSec` + `sd_notify` for control loops; journald for logs with size caps.
- Environment sourced in the unit (`ExecStart=/bin/bash -c 'source install/setup.bash && ros2 launch ...'`).

## CI (GitHub Actions patterns)

- **Firmware**: build all PlatformIO/IDF/CMake targets on every PR; fail on warnings; attach `.bin`/`.elf` + size report as artifacts; tag-triggered release job signs images.
- **ROS packages**: `industrial_ci` or colcon build + test in the target distro container; lint (`ament_lint`) gates merge.
- Host-runnable unit tests always in CI; hardware-in-the-loop tests on a self-hosted runner wired to a bench board — separate required vs nightly jobs.

## OTA firmware updates

- Non-negotiables: A/B partitions (or MCUboot slots), image signing with production keys, version check, **self-test after boot with automatic rollback** if the new image doesn't confirm health.
- Staged rollout: bench board → one canary robot → fleet. Never fleet-wide in one step.
- Track versions server-side; devices report firmware version in every heartbeat.

## Cross-compilation

- Prefer building in an ARM container (`docker buildx --platform linux/arm64`) or on-target for small fleets; sysroot cross-compile only when build time forces it.
- Pin toolchain versions in the repo (container tag or `toolchain.cmake`), never "whatever is installed".

## Release checklist

1. Changelog + tagged version; firmware and app protocol versions compatible.
2. Rollback path tested (not just present).
3. Config/calibration files migrate or are preserved.
4. E-stop and safety behavior verified on canary before fleet rollout.
