import network
import ntptime
import time
import picoepaper29b
from writer import Writer
import ezFBfont_courB14_ascii_17
from config import WIFI_SSID, WIFI_PASSWORD, NTP_HOST, CLOCKS

W = 296   # landscape width
H = 128   # landscape height


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
    return time.gmtime(time.time() + utc_h * 3600 + utc_m * 60)


# ── screen composers ──────────────────────────────────────────────────────────

def draw_status(epd, line1, line2=""):
    epd.Clear(0xff)
    epd.fill(0xff)
    epd.text(line1, (W - len(line1) * 8) // 2, H // 2 - 8, 0x00)
    if line2:
        epd.text(line2[:16], (W - len(line2[:16]) * 8) // 2, H // 2 + 8, 0x00)
    epd.display(epd.buffer)


def draw_clocks(epd, wri, synced):
    epd.Clear(0xff)
    epd.fill(0xff)
    section_h = H // len(CLOCKS)
    for i, (label, utc_h, utc_m) in enumerate(CLOCKS):
        t        = local_time(utc_h, utc_m)
        time_str = "{:02d}:{:02d}".format(t[3], t[4])
        date_str = "{:02d}/{:02d}/{}".format(t[2], t[1], t[0])
        row = i * section_h + 4
        wri.set_textpos(epd, row, 5)
        wri.printstring("{} {}".format(label, time_str), invert=True)
        epd.text(date_str, 185, row + 5, 0x00)
        if i < len(CLOCKS) - 1:
            epd.hline(0, (i + 1) * section_h, W, 0x00)
    if not synced:
        warn = "* NO NTP SYNC *"
        epd.text(warn, (W - len(warn) * 8) // 2, H - 10, 0x00)
    epd.display(epd.buffer)


# ── main ──────────────────────────────────────────────────────────────────────

def worldclock():
    epd = picoepaper29b.EPD_2in9_Landscape()
    epd.init()
    wri = Writer(epd, ezFBfont_courB14_ascii_17)
    wri.set_clip(wrap=False)

    draw_status(epd, "Connecting WiFi...", WIFI_SSID[:16])

    synced = False
    wifi_ok = connect_wifi()

    if wifi_ok:
        draw_status(epd, "Syncing time...")
        synced = sync_ntp()
        if not synced:
            draw_status(epd, "NTP failed", "using RTC time")
            time.sleep(2)
    else:
        draw_status(epd, "WiFi failed", "using RTC time")
        time.sleep(2)

    while True:
        draw_clocks(epd, wri, synced)

        t = time.localtime()
        if wifi_ok and t[4] == 0:
            try:
                ntptime.settime()
                synced = True
            except Exception:
                pass

        sleep_s = 60 - time.localtime()[5]
        time.sleep(max(1, sleep_s))
