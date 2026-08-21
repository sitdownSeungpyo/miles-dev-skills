---
name: embedded-firmware
description: Embedded firmware engineering for STM32, ESP32, nRF, and ARM Cortex-M — bare-metal, FreeRTOS, Zephyr, HAL drivers, interrupts, DMA, low power. Use when writing or debugging MCU firmware, ISRs, linker scripts, HAL code, RTOS tasks, or device drivers.
---

# Embedded Firmware Engineering

Senior embedded engineer behavior for ARM Cortex-M (STM32, nRF), ESP32 (ESP-IDF), and similar MCUs.

## Workflow (always in this order)

1. **Analyze constraints**: MCU part number, flash/RAM budget, clock tree, power budget, real-time deadlines. State assumptions if the user didn't give them.
2. **Design architecture**: bare-metal superloop vs RTOS decision; interrupt priority map; peripheral ownership per task.
3. **Implement drivers**: HAL/LL (STM32), ESP-IDF APIs (ESP32), Zephyr device tree (nRF).
4. **Optimize resources**: measure before optimizing (`arm-none-eabi-size`, `.map` file, `uxTaskGetStackHighWaterMark`).
5. **Test & verify**: on-target test plan, not just compile success.

## MUST DO

- `volatile` for every variable shared between ISR and main context; use atomics or critical sections for multi-byte data.
- Keep ISRs short: set a flag / push to queue, defer work to task context (`xQueueSendFromISR` + `portYIELD_FROM_ISR`).
- Check every HAL/driver return code. No silent failures on hardware.
- Feed a watchdog (IWDG/Task WDT) from the main control path only — never from a timer ISR.
- Debounce inputs, timeout every blocking peripheral wait, handle bus error recovery (I2C stuck-bus clock-out).
- Static allocation by default: no `malloc` after init in real-time paths; use FreeRTOS static APIs or memory pools.

## MUST NOT DO

- No `printf` in ISRs; no blocking delays (`HAL_Delay`) inside RTOS tasks — use `vTaskDelay`.
- No floating point in ISRs on cores without FPU lazy stacking configured.
- Never ignore priority inversion: use mutexes (priority inheritance), not binary semaphores, for shared resources.
- Never ship with default/dev signing keys (Zephyr/MCUboot, ESP secure boot).

## Platform quick reference

### STM32 (HAL/CubeMX)
- Prefer LL or register access in hot paths; HAL for init.
- DMA for anything > ~1 kB/s sustained (UART RX: DMA circular + IDLE-line interrupt pattern).
- Debug hard faults: inspect `SCB->CFSR`, stacked PC/LR; enable `-g3 -Og` for debug builds.

### ESP32 (ESP-IDF)
- Pin time-critical tasks to a core (`xTaskCreatePinnedToCore`); WiFi/BT runs on core 0.
- Use `esp_timer` for µs timing; NVS for config storage; enable Task WDT.
- OTA: two app partitions + rollback (`esp_ota_mark_app_valid_cancel_rollback`).

### Zephyr / nRF
- Everything through device tree + Kconfig; never bypass with raw registers unless justified.
- MCUboot for secure boot/OTA: production keys, image signing, version monotonicity, rollback protection.

## Low power

- Order of wins: sleep modes > clock gating > peripheral off > clock scaling.
- Design event-driven: wake on EXTI/RTC, do work, return to STOP/light-sleep. Measure with a power profiler before claiming numbers.

## Verification

- Unit test hardware-independent logic on host (Ceedling/Unity, GoogleTest).
- On-target: assert timing with GPIO toggle + logic analyzer; check stack high-water marks and CPU load before release.
