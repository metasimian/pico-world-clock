# config.py — edit this file before deploying to your Pico

WIFI_SSID     = "YourNetworkName"
WIFI_PASSWORD = "YourPassword"

NTP_HOST = "pool.ntp.org"

# Three clocks: (display label, UTC offset hours, UTC offset minutes)
# Labels: max 16 characters (each char is 8 px wide on a 128 px display)
# DST is not handled automatically — adjust the hour offset seasonally if needed.
#   US Eastern:  -5 standard / -4 daylight
#   UK:           0 standard / +1 summer (BST)
#   Japan:       +9 (no DST)
CLOCKS = [
    ("NEW YORK",  -5, 0),
    ("LONDON",     0, 0),
    ("TOKYO",      9, 0),
]
