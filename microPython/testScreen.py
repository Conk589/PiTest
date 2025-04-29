import machine
import utime

try:
    import ili9341
except ImportError:
    print("Error: ili9341.py not found in /lib")
    raise

try:
    import xpt2046
except ImportError:
    print("Error: xpt2046.py not found in /lib")
    raise

# Initialize SPI for display (500 kHz)
try:
    spi = machine.SPI(2, baudrate=500000, sck=machine.Pin(14), mosi=machine.Pin(13), miso=machine.Pin(12))
except Exception as e:
    print("Display SPI initialization failed:", e)
    raise

# Display pins
cs = machine.Pin(15, machine.Pin.OUT)
dc = machine.Pin(2, machine.Pin.OUT)
rst = machine.Pin(33, machine.Pin.OUT)
backlight = machine.Pin(21, machine.Pin.OUT)  # Changed to GPIO21

# Turn on backlight
backlight.value(1)

# Initialize ILI9341 display
try:
    display = ili9341.Display(
        spi,
        cs=cs,
        dc=dc,
        rst=rst,
        width=320,
        height=240,
        rotation=0
    )
    print("Display initialized")
except Exception as e:
    print("Display initialization failed:", e)
    raise

# Clear display and show initial message
try:
    display.clear(ili9341.color565(0, 0, 0))  # Black background
    display.draw_text8x8(10, 10, "ESP32 CYD", ili9341.color565(255, 255, 255))  # White
    display.draw_text8x8(10, 20, "Touch Test", ili9341.color565(0, 255, 0))  # Green
    print("Initial text displayed")
except Exception as e:
    print("Initial display write failed:", e)

# Initialize SPI for touch (250 kHz)
try:
    touch_spi = machine.SPI(1, baudrate=250000, sck=machine.Pin(25), mosi=machine.Pin(32), miso=machine.Pin(39))
    touch_cs = machine.Pin(33, machine.Pin.OUT)
    touch = xpt2046.Touch(
        spi=touch_spi,
        cs=touch_cs,
        width=320,
        height=240,
        x_min=200,
        x_max=3900,
        y_min=200,
        y_max=3700
    )
    print("Touch initialized")
except Exception as e:
    print("Touch initialization failed:", e)

# Lightweight CPU usage
def get_cpu_usage():
    start = utime.ticks_ms()
    for _ in range(500):
        pass
    busy_time = utime.ticks_diff(utime.ticks_ms(), start)
    total_time = 100
    usage = min(100, max(0, (busy_time / total_time) * 100))
    return int(usage)

# Touch and CPU test
try:
    last_coords = None
    last_usage = None
    start_time = utime.ticks_ms()
    for i in range(100):  # ~10 seconds
        coords = touch.get_touch()
        if coords != last_coords:
            if last_coords:
                x, y = last_coords
                display.draw_text8x8(10, 40, f"Touch: ({x:3d}, {y:3d}) ", ili9341.color565(0, 0, 0))
            if coords:
                x, y = coords
                display.draw_text8x8(10, 40, f"Touch: ({x:3d}, {y:3d}) ", ili9341.color565(255, 255, 0))
                print(f"Touch at: ({x}, {y})")
            last_coords = coords

        if utime.ticks_diff(utime.ticks_ms(), start_time) >= 1000:
            usage = get_cpu_usage()
            if usage != last_usage:
                if last_usage is not None:
                    display.draw_text8x8(250, 220, f"{last_usage:3d}%", ili9341.color565(0, 0, 0))
                display.draw_text8x8(250, 220, f"{usage:3d}%", ili9341.color565(255, 0, 0))
                last_usage = usage
            start_time = utime.ticks_ms()

        utime.sleep_ms(100)
    print("Touch and CPU test complete.")
except Exception as e:
    print("Test loop error:", e)

print("Script complete. Enter REPL for manual control.")