# pico-world-clock

A MicroPython world clock for the Raspberry Pi Pico 2 W and Waveshare Pico-ePaper-2.9-B display. Shows three configurable cities simultaneously in a portrait layout, synced to NTP on boot and updated every minute.

## Hardware

| Component | Notes |
|-----------|-------|
| Raspberry Pi Pico 2 W | Built-in WiFi required |
| Waveshare Pico-ePaper-2.9-B | 128×296 px, Red/Black/White, UC8151D controller |

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

## Setup

1. Flash [MicroPython for Pico 2 W](https://micropython.org/download/RPI_PICO2_W/) onto the board.
2. Copy all three files to the root of the Pico:
   - `main.py`
   - `config.py`
   - `epd2in9b.py`
3. Edit `config.py` with your WiFi credentials and desired time zones.
4. Power cycle the Pico — it connects to WiFi, syncs NTP, and starts displaying.

## Configuration

```python
# config.py
WIFI_SSID     = "YourNetworkName"
WIFI_PASSWORD = "YourPassword"

NTP_HOST = "pool.ntp.org"

CLOCKS = [
    ("SEATTLE",   -8, 0),   # (city label, UTC offset hours, UTC offset minutes)
    ("AMSTERDAM",  1, 0),
    ("SINGAPORE",  8, 0),
]
```

City labels are displayed in the red header bar. Maximum 16 characters.

**DST note:** UTC offsets are static — adjust the hour value manually when daylight saving time changes in your target city.

| City | Standard | Daylight |
|------|----------|----------|
| Seattle | −8 (PST) | −7 (PDT) — 2nd Sunday March → 1st Sunday November |
| Amsterdam | +1 (CET) | +2 (CEST) — last Sunday March → last Sunday October |
| Singapore | +8 (year-round, no DST) | — |

## Display

- 128×296 px portrait layout
- Three clocks stacked vertically, each with a red city-name header
- Time in large 24-hour digits, UTC offset and date below
- Refreshes every 60 seconds; re-syncs NTP every hour
- Shows `* NO NTP SYNC *` if time was never synced


(18 May 2026) There are 2 versions (switched in main.py):
   - handcoded - this was my original hack several months ago
   - claude - vibe coded off the app on my phone in a bus... (still tested off the laptop w/Thonny & the pico setup)
Overall the approach wasn't hugely different between the two and the result is pretty much the same. 

