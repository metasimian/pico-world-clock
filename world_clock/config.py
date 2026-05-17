# config.py — edit this file before deploying to your Pico

WIFI_SSID     = "YourNetworkName"
WIFI_PASSWORD = "YourPassword"

NTP_HOST = "pool.ntp.org"

# Three clocks: (display label, UTC offset hours, UTC offset minutes)
# Labels: max 16 characters (each char is 8 px wide on a 128 px display)
# DST is not handled automatically — adjust the hour offset seasonally if needed.
#   Seattle:    -8 standard (PST) / -7 daylight (PDT)
#   Amsterdam:  +1 standard (CET) / +2 daylight (CEST)
#   Singapore:  +8 year-round (no DST)
CLOCKS = [
    ("SEATTLE",   -8, 0),
    ("AMSTERDAM",  1, 0),
    ("SINGAPORE",  8, 0),
]
