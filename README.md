# pico-world-clock

A MicroPython world clock for the Raspberry Pi Pico 2 W and Waveshare Pico-ePaper-2.9-B display. Shows four configurable cities simultaneously in a landscape layout, synced to NTP on boot and updated every minute.

## Hardware

| Component | Notes |
|-----------|-------|
| Raspberry Pi Pico 2 W | Built-in WiFi required |
| Waveshare Pico-ePaper-2.9-B | 296×128 px, Red/Black/White, UC8151D controller |

The display module plugs directly onto the Pico's 40-pin header — no extra wiring needed.

### GPIO mapping

| Signal | GPIO |
|--------|------|
| SCK | GP10 |
| MOSI | GP11 |
| CS | GP9 |
| DC | GP8 |
| RST | GP12 |
| BUSY | GP13 |

## Files

| File | Description |
|------|-------------|
| `main.py` | Entry point — imports and calls `worldclock()` |
| `worldclockclaude.py` | Main implementation |
| `worldclockhandcoded.py` | Original hand-coded reference implementation |
| `config.py` | WiFi credentials and clock configuration |

## Dependencies

The following libraries must be present on the Pico (not included in this repo):

- `picoepaper29b` — display driver for Waveshare Pico-ePaper-2.9-B
- `writer` — font rendering helper
- `ezFBfont_courB14_ascii_17` — Courier Bold 14pt font

## Setup

1. Flash [MicroPython for Pico 2 W](https://micropython.org/download/RPI_PICO2_W/) onto the board.
2. Install the dependencies above onto the Pico.
3. Copy these files to the root of the Pico:
   - `main.py`
   - `worldclockclaude.py`
   - `config.py`
4. Edit `config.py` with your WiFi credentials and desired time zones.
5. Power cycle the Pico — it connects to WiFi, syncs NTP, and starts displaying.

## Configuration

```python
# config.py
WIFI_SSID     = "YourNetworkName"
WIFI_PASSWORD = "YourPassword"

NTP_HOST = "pool.ntp.org"

CLOCKS = [
    ("SEA", -8, 0),   # (city label, UTC offset hours, UTC offset minutes)
    ("GMT",  0, 0),
    ("AMS",  1, 0),
    ("SIN",  8, 0),
]
```

**DST note:** UTC offsets are static — adjust the hour value manually when daylight saving time changes in your target city.

| City | Standard | Daylight |
|------|----------|----------|
| Seattle | −8 (PST) | −7 (PDT) — 2nd Sunday March → 1st Sunday November |
| Amsterdam | +1 (CET) | +2 (CEST) — last Sunday March → last Sunday October |
| Singapore | +8 (year-round, no DST) | — |

## Display

- 296×128 px landscape layout
- Four clocks stacked vertically with inverted city-name header per row
- Time in 24-hour format, date to the right
- Refreshes every 60 seconds; re-syncs NTP every hour
- Shows `* NO NTP SYNC *` if time was never synced
- Status messages shown on screen during WiFi connect and NTP sync

## Implementations

Two implementations are included, selectable in `main.py`:

- **`worldclockclaude.py`** — structured implementation with robust error handling: 20-second WiFi timeout, 3 NTP retries, boot status screens, hourly re-sync, and sleep aligned to the minute boundary
- **`worldclockhandcoded.py`** — original hand-coded version; simpler but raises on WiFi failure and drifts slightly over time

(lol!  Looks like Claude was not impressed with my descriptions or code quality!)
