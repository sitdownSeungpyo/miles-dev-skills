---
name: hw-debug
description: Hardware and communication debugging — UART/serial, I2C, SPI, CAN, BLE, SWD/JTAG, logic analyzers, oscilloscope strategy. Use when firmware "doesn't respond", a bus device isn't detected, data is corrupted, or the user is debugging serial/CAN/I2C/SPI communication.
---

# Hardware & Bus Debugging

Systematic hardware debugging. Always narrow the problem layer-by-layer: power → clock → electrical → protocol → firmware logic. Never guess-and-flash repeatedly.

## First questions (ask or check before proposing fixes)

1. Did this ever work, or is it a new bring-up? What changed last?
2. Is it reproducible or intermittent? (Intermittent → suspect power, ground, EMI, race conditions.)
3. What test equipment is available (logic analyzer, scope, multimeter)?

## Serial / UART

- 90% of failures: **baud mismatch, TX/RX swapped, missing common ground, wrong logic level (5V vs 3.3V)**. Check these in that order.
- Garbage characters → baud/clock error (check MCU clock config; internal RC oscillators drift), or level mismatch.
- Works on bench, fails in field → ground loops, cable length, missing termination; suggest RS-485 for long runs.
- Windows: identify port via `[System.IO.Ports.SerialPort]::GetPortNames()` or Device Manager; monitor with `pio device monitor` / PuTTY.

## I2C

- Device not ACKing: scan first (`i2cdetect`, or a scanner sketch). No devices at all → check pull-ups (2.2k–10k), bus voltage, SDA/SCL swap.
- Stuck bus (SDA held low): clock out 9 pulses manually, then re-init peripheral — put this recovery in production firmware.
- Address confusion: datasheets mix 7-bit and 8-bit (shifted) addresses — verify both interpretations.
- Long wires/EMI → drop to 100 kHz, stronger pull-ups, shielded cable.

## SPI

- No/garbage data: verify **mode (CPOL/CPHA)** against datasheet first, then CS polarity/timing, then MISO/MOSI orientation.
- Multiple slaves: each CS deasserted high before another asserts; check for MISO not tri-stating (bus contention).
- High speed failures → reduce clock, check trace length and ringing on scope.

## CAN / CAN-FD

- Bus-off or no ACK: exactly two 120Ω terminators (measure ~60Ω across H/L, powered off), matching bitrate + sample point (~87.5%).
- Single node on bench never gets ACK — use loopback mode or a second node for testing.
- Tools: `candump`/`cansend` (SocketCAN on Linux), PCAN/Kvaser on Windows; decode with DBC where available.

## SWD/JTAG & on-chip debug

- Can't attach: check reset line, `NRST` config, low-power mode blocking debug (connect under reset), readout protection (RDP).
- Hard fault analysis: read `SCB->CFSR/HFSR`, recover stacked PC from MSP/PSP; map to source with `arm-none-eabi-addr2line`.
- Prefer `defmt`/RTT/ITM logging over UART printf when timing matters.

## Logic analyzer / scope strategy

- Logic analyzer for protocol correctness (use protocol decoders); scope for signal integrity (rise times, ringing, voltage levels).
- Trigger on the failure, not the happy path (e.g., trigger on NACK, error frame, or a GPIO you toggle in the error handler).
- Instrument firmware: toggle a spare GPIO at key points to correlate code with bus traffic.

## Report format

When diagnosing, present: **observed symptom → layer isolated → evidence → most likely cause → cheapest next test**. One hypothesis tested at a time.
