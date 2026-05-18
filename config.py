# config.py — edit this file before deploying to your Pico

WIFI_SSID     = "YourNetworkName"
WIFI_PASSWORD = "YourPassword"

NTP_HOST = "pool.ntp.org"

# Clocks: (display label, UTC offset hours, UTC offset minutes)
# DST is not handled automatically — adjust the hour offset seasonally if needed.
#   Seattle:    -8 standard (PST) / -7 daylight (PDT)
#   Amsterdam:  +1 standard (CET) / +2 daylight (CEST)
#   Singapore:  +8 year-round (no DST)
CLOCKS = [
    ("SEA", -8, 0),
    ("GMT",  0, 0),
    ("AMS",  1, 0),
    ("SIN",  8, 0),
]
