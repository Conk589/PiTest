import machine
import sys
import time
import uselect
from ili9341 import Display, color565

# Pin definitions for ILI9341 on CYD (SPI2)
spi = machine.SPI(2, baudrate=1000000, sck=machine.Pin(14), mosi=machine.Pin(13), miso=machine.Pin(12))
cs = machine.Pin(15, machine.Pin.OUT)
dc = machine.Pin(2, machine.Pin.OUT)
rst = machine.Pin(33, machine.Pin.OUT)
backlight = machine.Pin(21, machine.Pin.OUT)

# Initialize display
display = Display(spi, cs=cs, dc=dc, rst=rst, width=240, height=320, rotation=0)
backlight.on()

# Startup sequence
display.clear(color=0)
display.draw_text8x8(10, 10, "Test Display", color565(255, 255, 255))
time.sleep(2)
display.draw_text8x8(10, 30, "ESP32 Running", color565(0, 255, 0))
display.fill_rectangle(10, 50, 50, 50, color565(255, 0, 0))
time.sleep(5)
display.clear()

def draw_progress_bar(x, y, width, height, progress, fg_color, bg_color):
    """Draw a progress bar with percentage fill."""
    display.fill_rectangle(x, y, width, height, bg_color)  # Background
    fill_width = int(width * (progress / 100))  # Calculate filled portion
    if fill_width > 0:
        display.fill_rectangle(x, y, fill_width, height, fg_color)  # Foreground

def read_and_display_data():
    """Read serial data and update display with metrics and progress bars."""
    # Initialize display once
    display.clear()
    display.draw_text8x8(10, 10, "System Monitor", color565(255, 255, 255))
    labels = ["CPU", "RAM", "GPU Usage", "Disk", "Net Sent", "Net Recv", "CPU Temp", "GPU Temp", "CPU Clock"]
    units = ["%", "%", "%", "%", "MB", "MB", "C", "C", "MHz"]
    values = [0.0] * 9
    y_positions = [30, 48, 66, 84, 102, 120, 138, 156, 174]  # 18-pixel spacing for 9 metrics

    # Draw initial labels
    for i, (label, y, unit) in enumerate(zip(labels, y_positions, units)):
        text = f"{label}: {values[i]}{unit}"
        display.draw_text8x8(10, y, text, color565(255, 255, 255))
        if label in ["CPU", "RAM", "GPU Usage"]:
            draw_progress_bar(120, y, 100, 10, values[i], color565(0, 255, 0), color565(50, 50, 50))

    buffer = ""
    while True:
        # Non-blocking read from USB-serial (sys.stdin)
        char = sys.stdin.read(1) if sys.stdin in uselect.select([sys.stdin], [], [], 0.1)[0] else None
        if char:
            print(f"Char: {repr(char)} (ord: {ord(char)})")  # Debug
            if char == '|' and buffer:
                print(f"Received: {buffer} (len: {len(buffer)})")  # Debug
                # Parse data
                for i, (label, unit) in enumerate(zip(labels, units)):
                    if buffer.startswith(label):
                        try:
                            value = float(buffer.split(':')[1].split(unit)[0].strip())
                            values[i] = value
                            # Update only the changed metric
                            text = f"{label}: {value}{unit}"
                            # Clear the text area (8x8 font, estimate width)
                            display.fill_rectangle(10, y_positions[i], 200, 8, color565(0, 0, 0))
                            display.draw_text8x8(10, y_positions[i], text, color565(255, 255, 255))
                            # Update progress bar for CPU, RAM, or GPU Usage
                            if label in ["CPU", "RAM", "GPU Usage"]:
                                draw_progress_bar(120, y_positions[i], 100, 10, value, color565(0, 255, 0), color565(50, 50, 50))
                        except Exception as e:
                            print(f"Parse error: {e}")
                buffer = ""
            else:
                buffer += char
        time.sleep(0.01)
        print("Heartbeat: Loop running")  # Debug

read_and_display_data()