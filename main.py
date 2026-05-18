# main.py — World Clock for Raspberry Pi Pico 2 W + Waveshare Pico-ePaper-2.9-B
#
# Display layout (portrait, 128 × 296 px):
#   Three clock sections stacked vertically, each ~98 px tall.
#   Each section: red header bar (city name), 3× time, UTC offset, date.
#
# Copy config.py, epd2in9b.py, and this file to the Pico root.
# Edit config.py with your WiFi credentials and desired time zones.

import network
import ntptime
import time
import framebuf
from epd2in9b import EPD, W, H, INK, PAPER
from config import WIFI_SSID, WIFI_PASSWORD, NTP_HOST, CLOCKS

DAYS   = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")
MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")

SECTION_H  = H // len(CLOCKS)   # pixels per clock section
HEADER_H   = 18                  # red title bar height


# ── networking ────────────────────────────────────────────────────────────────

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        return True
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    deadline = time.ticks_add(time.ticks_ms(), 20_000)
    while not wlan.isconnected():
        if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
            return False
        time.sleep_ms(200)
    return True


def sync_ntp(retries=3):
    ntptime.host = NTP_HOST
    for attempt in range(retries):
        try:
            ntptime.settime()
            return True
        except Exception as e:
            print("NTP attempt", attempt + 1, "failed:", e)
            time.sleep(1)
    return False


# ── time helpers ──────────────────────────────────────────────────────────────

def local_time(utc_h, utc_m=0):
    """Return gmtime tuple adjusted for a UTC offset."""
    return time.gmtime(time.time() + utc_h * 3600 + utc_m * 60)


def utc_label(utc_h, utc_m=0):
    sign = "+" if utc_h >= 0 else ""
    if utc_m:
        return "UTC{}{}:{:02d}".format(sign, utc_h, abs(utc_m))
    return "UTC{}{}".format(sign, utc_h)


# ── drawing helpers ───────────────────────────────────────────────────────────

def cx(text, scale=1):
    """Horizontal center offset for text of given scale on the display."""
    return max(0, (W - len(text) * 8 * scale) // 2)


def draw_scaled(fb, text, x, y, scale, color):
    """Render text at an integer scale using fill_rect for each scaled pixel."""
    if scale == 1:
        fb.text(text, x, y, color)
        return
    n  = len(text) * 8          # pixel width at 1×
    tmp = bytearray(n)           # MONO_HLSB: n cols × 8 rows → n bytes
    tfb = framebuf.FrameBuffer(tmp, n, 8, framebuf.MONO_HLSB)
    tfb.fill(0)
    tfb.text(text, 0, 0, 1)     # render white-on-black in temp buffer
    for row in range(8):
        for col in range(n):
            bi  = (row * n + col) // 8
            bit = 7 - ((row * n + col) % 8)
            if (tmp[bi] >> bit) & 1:
                fb.fill_rect(x + col * scale, y + row * scale,
                             scale, scale, color)


# ── clock section renderer ────────────────────────────────────────────────────

def render_section(fb_bw, fb_red, sy, label, utc_h, utc_m, last):
    t        = local_time(utc_h, utc_m)
    time_str = "{:02d}:{:02d}".format(t[3], t[4])
    date_str = "{} {} {:02d}".format(DAYS[t[6]], MONTHS[t[1] - 1], t[2])
    utc_str  = utc_label(utc_h, utc_m)

    # Red header bar — city label in white
    fb_bw.fill_rect(0, sy, W, HEADER_H, PAPER)
    fb_red.fill_rect(0, sy, W, HEADER_H, INK)
    fb_red.text(label, cx(label), sy + 5, PAPER)   # PAPER = no red ink → white

    # Time at 3× scale — black on white
    draw_scaled(fb_bw, time_str, cx(time_str, 3), sy + 22, 3, INK)

    # UTC offset
    fb_bw.text(utc_str, cx(utc_str), sy + 54, INK)

    # Date
    fb_bw.text(date_str, cx(date_str), sy + 66, INK)

    # Section divider (skip on last clock)
    if not last:
        fb_bw.hline(0, sy + SECTION_H - 1, W, INK)


# ── screen composers ──────────────────────────────────────────────────────────

def draw_status(epd, line1, line2=""):
    """Full-screen status message (shown while connecting / on error)."""
    epd.fb_bw.fill(PAPER)
    epd.fb_red.fill(PAPER)
    # Draw a small red banner at top
    epd.fb_red.fill_rect(0, 0, W, HEADER_H, INK)
    epd.fb_red.text("WORLD CLOCK", cx("WORLD CLOCK"), 5, PAPER)
    epd.fb_bw.text(line1, cx(line1), 120, INK)
    if line2:
        epd.fb_bw.text(line2[:16], cx(line2[:16]), 136, INK)
    epd.show()


def draw_clocks(epd, synced):
    epd.fb_bw.fill(PAPER)
    epd.fb_red.fill(PAPER)
    for i, (label, utc_h, utc_m) in enumerate(CLOCKS):
        render_section(epd.fb_bw, epd.fb_red,
                       i * SECTION_H, label, utc_h, utc_m,
                       last=(i == len(CLOCKS) - 1))
    # If time was never synced, show a small warning at the bottom
    if not synced:
        warn = "* NO NTP SYNC *"
        epd.fb_bw.text(warn, cx(warn), H - 10, INK)
    epd.show()


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    epd = EPD()
    epd.init()

    draw_status(epd, "Connecting WiFi...", WIFI_SSID[:16])

    synced = False
    wifi_ok = connect_wifi()

    if wifi_ok:
        draw_status(epd, "Syncing time...")
        synced = sync_ntp()
        if not synced:
            draw_status(epd, "NTP failed —", "using RTC time")
            time.sleep(2)
    else:
        draw_status(epd, "WiFi failed —", "using RTC time")
        time.sleep(2)

    while True:
        draw_clocks(epd, synced)

        # Re-sync NTP once per hour (on the ~0-minute mark)
        t = time.localtime()
        if wifi_ok and t[4] == 0:           # minute == 0
            try:
                ntptime.settime()
                synced = True
            except Exception:
                pass

        # Sleep until the next full minute
        sleep_s = 60 - time.localtime()[5]
        time.sleep(max(1, sleep_s))


main()
