# epd2in9b.py — Waveshare Pico-ePaper-2.9-B driver (Red/Black/White, 128x296)
# Controller: UC8151D
# Wiring (module plugs directly onto Pico header):
#   SCK  → GP10   MOSI → GP11   CS  → GP9
#   DC   → GP8    RST  → GP12   BUSY→ GP13

from machine import Pin, SPI
import framebuf
import time

# Native resolution in portrait (controller orientation)
W = 128
H = 296

# Buffer color convention:  0 = ink active (black or red),  1 = no ink (white)
INK   = 0
PAPER = 1


class EPD:
    def __init__(self):
        # MISO omitted so GP12 is free for RST
        self._spi  = SPI(1, 4_000_000, polarity=0, phase=0,
                         sck=Pin(10), mosi=Pin(11))
        self._cs   = Pin(9,  Pin.OUT, value=1)
        self._dc   = Pin(8,  Pin.OUT, value=0)
        self._rst  = Pin(12, Pin.OUT, value=1)
        self._busy = Pin(13, Pin.IN)

        self._bw_buf  = bytearray(W * H // 8)   # 4736 bytes
        self._red_buf = bytearray(W * H // 8)
        self.fb_bw    = framebuf.FrameBuffer(self._bw_buf,  W, H, framebuf.MONO_HLSB)
        self.fb_red   = framebuf.FrameBuffer(self._red_buf, W, H, framebuf.MONO_HLSB)

    # ── low-level SPI helpers ──────────────────────────────────────────────

    def _cmd(self, b):
        self._dc(0); self._cs(0)
        self._spi.write(bytes([b]))
        self._cs(1)

    def _dat(self, *bs):
        self._dc(1); self._cs(0)
        self._spi.write(bytes(bs))
        self._cs(1)

    def _write_buf(self, buf):
        self._dc(1); self._cs(0)
        self._spi.write(buf)
        self._cs(1)

    def _wait_idle(self):
        time.sleep_ms(10)
        while self._busy():          # HIGH = busy on UC8151D
            time.sleep_ms(10)

    def _hw_reset(self):
        self._rst(0); time.sleep_ms(10)
        self._rst(1); time.sleep_ms(10)

    # ── public API ─────────────────────────────────────────────────────────

    def init(self):
        self._hw_reset()
        self._wait_idle()

        self._cmd(0x00); self._dat(0x0F, 0x89)            # panel setting
        self._cmd(0x01); self._dat(0x07, 0x00, 0x0B, 0x0B, 0x03)  # power
        self._cmd(0x06); self._dat(0x17, 0x17, 0x17)      # booster soft-start
        self._cmd(0x04)                                    # power on
        self._wait_idle()
        self._cmd(0x50); self._dat(0x77)                   # VCOM & data interval
        self._cmd(0x60); self._dat(0x22)                   # TCON
        self._cmd(0x61); self._dat(0x80, 0x01, 0x28)       # resolution 128×296
        self._cmd(0x82); self._dat(0x08)                   # VCOM DC

    def show(self):
        """Push both framebuffers to the display and trigger a refresh (~4 s)."""
        self._cmd(0x10); self._write_buf(self._bw_buf)     # black/white channel
        self._cmd(0x13); self._write_buf(self._red_buf)    # red channel
        self._cmd(0x12)                                    # refresh
        time.sleep_ms(100)
        self._wait_idle()

    def clear(self):
        self.fb_bw.fill(PAPER)
        self.fb_red.fill(PAPER)
        self.show()

    def sleep(self):
        self._cmd(0x02); self._wait_idle()   # power off
        self._cmd(0x07); self._dat(0xA5)    # deep sleep
