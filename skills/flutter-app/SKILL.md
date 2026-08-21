---
name: flutter-app
description: Flutter/Dart mobile app development — Riverpod state management, BLE/serial device connectivity, platform channels, robot controller apps, testing, release builds. Use when working with pubspec.yaml, .dart files, or building iOS/Android apps, especially device-control or IoT companion apps.
---

# Flutter App Development

Production Flutter standards, with patterns for device-control / robot companion apps.

## Project defaults

- State management: Riverpod (v2, code-gen `@riverpod`) unless the project already uses BLoC — match existing.
- Structure: feature-first (`lib/features/<feature>/{data,domain,presentation}`); models with `freezed` + `json_serializable`.
- Navigation: `go_router`. Lint: `flutter_lints`/`very_good_analysis`, no analyzer warnings in delivered code.
- Async UI state: `AsyncValue<T>` (loading/error/data) — every screen handles all three.

## Widget rules

- `const` constructors everywhere possible; small widgets over deep `build` methods.
- Never do work in `build`; side effects live in providers/controllers.
- Rebuild scope: `select`/`Consumer` to avoid whole-screen rebuilds on high-rate updates.
- Design for both platforms: safe areas, back-gesture, text scaling, dark mode.

## Device connectivity (BLE / WiFi / serial)

- **BLE**: `flutter_blue_plus`. Connection is a state machine (scanning → connecting → discovering → ready → lost); expose it as a provider, auto-reconnect with backoff, and surface state in the UI. Request runtime permissions correctly (Android 12+ `BLUETOOTH_SCAN/CONNECT`, iOS `NSBluetoothAlwaysUsageDescription`).
- **MTU & throughput**: negotiate MTU on Android; chunk writes; use notifications (not polling reads) for telemetry.
- **WiFi/WebSocket to robot**: `web_socket_channel` with reconnect + heartbeat; same rule as web — command UI reflects only acknowledged state, e-stop is never optimistic.
- **USB serial** (Android): `usb_serial`; handle detach events.
- High-rate telemetry: buffer in the data layer, emit to UI at ≤15 Hz; charts with `fl_chart` on decimated data.

## Platform channels

- Only when no maintained plugin exists. `MethodChannel` for calls, `EventChannel` for streams; define the contract (method names, types) in one Dart file; handle `PlatformException` on every call.

## Testing & release

- Unit test providers/repositories with mocked data sources (`mocktail`); widget tests for each screen's three async states; `integration_test` for the connect-and-control happy path.
- Release: flavors (`dev`/`prod`) with separate bundle IDs; Android — R8, signed AAB; iOS — check `Info.plist` permission strings or face App Store rejection.
- Version telemetry protocol between app and firmware; app must handle older-firmware responses gracefully.
