import machine
import utime
import sys
import lib.ili9341 as ili9341

# Initialize SPI for ILI9341 display
spi = machine.SPI(2, baudrate=1000000, sck=machine.Pin(14), mosi=machine.Pin(13), miso=machine.Pin(12))
cs = machine.Pin(15, machine.Pin.OUT)
dc = machine.Pin(2, machine.Pin.OUT)
rst = machine.Pin(33, machine.Pin.OUT)
backlight = machine.Pin(21, machine.Pin.OUT)
backlight.value(1)

# Initialize display
try:
    display = ili9341.Display(spi, cs=cs, dc=dc, rst=rst, width=240, height=320, rotation=90)
except Exception as e:
    print(f"Display init error: {e}")

# Colors
WHITE = ili9341.color565(255, 255, 255)
BLACK = ili9341.color565(0, 0, 0)
RED = ili9341.color565(255, 0, 0)

# Test display
def test_display():
    display.clear(BLACK)
    display.draw_text8x8(10, 10, "Test Display", WHITE, background=BLACK)
    display.draw_text8x8(10, 20, "ESP32 Running", WHITE, background=BLACK)
    display.draw_rectangle(10, 40, 100, 20, RED)
    utime.sleep(5)

# Function to read and display data
def read_and_display_data():
    display.clear(BLACK)
    display.draw_text8x8(10, 10, "Waiting for data...", WHITE, background=BLACK)
    buffer = ""
    last_data_displayed = utime.ticks_ms()
    last_heartbeat = utime.ticks_ms()
    
    # Clear serial buffer
    try:
        sys.stdin.read(1000)
        print("Cleared stdin buffer")
    except Exception as e:
        print(f"Failed to clear stdin buffer: {e}")
    
    while True:
        try:
            # Heartbeat
            if utime.ticks_diff(utime.ticks_ms(), last_heartbeat) > 1000:
                print("Heartbeat: Loop running")
                last_heartbeat = utime.ticks_ms()
            
            # Clear buffer periodically
            if utime.ticks_diff(utime.ticks_ms(), last_data_displayed) > 5000:
                try:
                    sys.stdin.read(1000)
                    print("Periodic buffer clear")
                except Exception as e:
                    print(f"Periodic buffer clear error: {e}")
            
            char = None
            received = False
            
            # Non-blocking read
            try:
                for _ in range(5):  # Limit attempts
                    char = sys.stdin.read(1)
                    if char:
                        print(f"Char: {repr(char)} (ord: {ord(char)})")
                        buffer += char
                        received = True
                        break
                    utime.sleep_ms(1)
            except Exception as e:
                print(f"Stdin read error: {e}")
            
            if received:
                display.clear(BLACK)
                display_text = buffer[-10:] if len(buffer) > 10 else buffer
                print(f"Displaying raw: {display_text}")
                display.draw_text8x8(10, 10, display_text, WHITE, background=BLACK)
                last_data_displayed = utime.ticks_ms()
                
                if char == '\n' or len(buffer) >= 100:
                    line = buffer.strip()
                    print(f"Received: {line} (len: {len(line)})")
                    
                    display.clear(BLACK)
                    lines = line.split('\n')
                    y_position = 10
                    for text in lines:
                        if text:
                            if len(text) > 20:
                                text = text[:20]
                            print(f"Displaying: {text} at y={y_position}")
                            display.draw_text8x8(10, y_position, text, WHITE, background=BLACK)
                            y_position += 10
                            if y_position > 300:
                                break
                    buffer = ""
                    last_data_displayed = utime.ticks_ms()
            
            # Status message
            if utime.ticks_diff(utime.ticks_ms(), last_data_displayed) > 15000:
                display.clear(BLACK)
                display.draw_text8x8(10, 10, "No data received", RED, background=BLACK)
                print("Displayed: No data received")
                last_data_displayed = utime.ticks_ms()
        
        except Exception as e:
            print(f"Error reading data: {e}")
            display.clear(BLACK)
            display.draw_text8x8(10, 10, f"Error: {str(e)[:10]}", RED, background=BLACK)
            utime.sleep(2)
            last_data_displayed = utime.ticks_ms()
        
        utime.sleep_ms(10)

# Main program
try:
    print("Booting...")
    utime.sleep(5)
    test_display()
    read_and_display_data()
except Exception as e:
    print(f"Fatal error: {e}")
    display.clear(BLACK)
    display.draw_text8x8(10, 10, f"Fatal: {str(e)[:10]}", RED, background=BLACK)