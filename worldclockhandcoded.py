import time
import os
import ntptime
import datetime
import network
import picoepaper29b
import courier20
import ezFBfont_courB14_ascii_17
from writer import Writer
from config import WIFI_SSID, WIFI_PASSWORD, NTP_HOST, CLOCKS

# @TODO wifi info should not be hard-coded... put in .env or something


# @TODO Fix timezone from hard-coded to dyanmic (ie: daylight savings)
tz_SGT = 8 * 3600 #'Asia/Singapore'
tz_CET = 1 * 3600 #'Europe/Amsterdam'
tz_PST = -8 * 3600 #'US/Pacifc'

time_format = "{:02d}:{:02d}"
date_format = "{:02d}/{:02d}/{}"


def print_date(epd, wri, tz_offset=0, label="GMT", row=0):
    tz_time = time.localtime(time.time() + tz_offset)
    tz_formatted_time = time_format.format(tz_time[3], tz_time[4], )
    tz_formatted_date = date_format.format(tz_time[2], tz_time[1], tz_time[0])
    wri.set_textpos(epd, row, 5)
    wri.printstring(label + " " + tz_formatted_time, invert=True)        
    epd.text(tz_formatted_date, 120, row+5, 0x00)

def init_wifi_time():
    #Get the current time
    current_time = time.localtime()
    #Format the current time as "dd/mm/yyyy HH:MM"
    formatted_time = time_format.format(current_time[2], current_time[1], current_time[0], current_time[3], current_time[4])
    print("Local time before synchronization：%s" %str(formatted_time))
    
    #init & connect to wifi
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )
        try:
          #make sure to have internet connection
          ntptime.host = NTP_HOST
          ntptime.settime()
          formatted_time = time_format.format(current_time[2], current_time[1], current_time[0], current_time[3], current_time[4])
          print("Local time after synchronization：%s" %str(formatted_time))
        except:
          print("Error syncing time")

def worldclock():
    init_wifi_time();
    
    epd = picoepaper29b.EPD_2in9_Landscape()
    epd.init()
    wri = Writer(epd, ezFBfont_courB14_ascii_17)
    wri.set_clip(wrap=False)

    while True: 
        epd.Clear(0xff)
        epd.fill(0xff)
        print_date(epd, wri, tz_offset=tz_PST, label="PST", row=5)
        print_date(epd, wri, tz_offset=0, label="GMT", row=30)
        print_date(epd, wri, tz_offset=tz_CET, label="CET", row=55)
        print_date(epd, wri, tz_offset=tz_SGT, label="SGT", row=80)
        
        epd.display(epd.buffer)
        epd.delay_ms(2000)
        time.sleep(60)
