---
name: platformio-arduino
description: PlatformIO and Arduino-framework rapid prototyping — platformio.ini configuration, multi-environment builds, library management, non-blocking patterns for AVR/ESP32/RP2040/STM32. Use when the project contains platformio.ini, .ino files, or the user mentions Arduino or PlatformIO.
---

# PlatformIO / Arduino Prototyping

Fast, correct prototyping on the Arduino framework via PlatformIO (preferred) or Arduino CLI.

## platformio.ini patterns

```ini
[env]                      ; shared base
framework = arduino
monitor_speed = 115200
lib_deps =
    bblanchon/ArduinoJson@^7

[env:esp32dev]
platform = espressif32
board = esp32dev

[env:pico]
platform = raspberrypi
board = pico
```

- One `[env:...]` per target board; share settings in `[env]`.
- Pin library versions (`@^x.y`) — unpinned deps break builds months later.
- `build_flags = -DDEBUG_LEVEL=3` for compile-time config; `monitor_filters = esp32_exception_decoder` on ESP32.

## Commands

```bash
pio run -e esp32dev             # build
pio run -e esp32dev -t upload   # flash
pio device monitor              # serial monitor
pio test -e native              # host-side unit tests
```

## Code rules (prototyping ≠ sloppy)

- **Never `delay()` in loop** for multitasking sketches — use `millis()` non-blocking timers or a tiny scheduler:
  ```cpp
  if (millis() - lastRun >= interval) { lastRun = millis(); doWork(); }
  ```
- Model behavior as a **state machine** (enum + switch) once a sketch has more than two modes.
- Debounce buttons (25–50 ms), rate-limit serial prints.
- `F()` macro for string literals on AVR to save RAM.
- Sensor code: always handle the "sensor not found / NaN reading" path.

## Common recipes

- **ESP32 WiFi + MQTT telemetry**: `WiFi.onEvent` reconnect logic + `PubSubClient` with backoff; never block on `WiFi.begin`.
- **EEPROM/Preferences config**: version-tag the struct; on mismatch, load defaults.
- **SD/flash logging**: buffer writes, flush periodically; handle card-removed errors.

## When to graduate off Arduino

Recommend moving to ESP-IDF / STM32 HAL / Zephyr when the user needs: precise ISR timing, DMA, OTA with rollback, secure boot, or RTOS task design. Say so explicitly instead of stretching the Arduino layer.
