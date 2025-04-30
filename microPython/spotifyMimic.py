import machine
import utime
import lib.ili9341 as ili9341
import lib.xpt2046 as xpt2046

# Spotify colors (approximated for RGB565)
SPOTIFY_GREEN = ili9341.color565(29, 185, 84)   # #1DB954
SPOTIFY_WHITE = ili9341.color565(255, 255, 255) # #FFFFFF
SPOTIFY_BLACK = ili9341.color565(25, 20, 20)    # #191414

# Initialize SPI for display
spi = machine.SPI(2, baudrate=500000, sck=machine.Pin(14), mosi=machine.Pin(13), miso=machine.Pin(12))
cs = machine.Pin(15, machine.Pin.OUT)
dc = machine.Pin(2, machine.Pin.OUT)
rst = machine.Pin(33, machine.Pin.OUT)
backlight = machine.Pin(21, machine.Pin.OUT)
backlight.value(1)  # Turn on backlight

# Initialize display
display = ili9341.Display(spi, cs=cs, dc=dc, rst=rst, width=320, height=240, rotation=0)

# Initialize SPI for touch
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

# Draw Spotify-themed interface
def draw_interface():
    # Clear screen (Spotify black)
    display.clear(SPOTIFY_BLACK)
    
    # Song title and artist (placeholder)
    display.draw_text8x8(10, 10, "Song: [Loading...]", SPOTIFY_WHITE)
    display.draw_text8x8(10, 20, "Artist: [Loading...]", SPOTIFY_WHITE)
    display.draw_text8x8(10, 30, "Album: [Loading...]", SPOTIFY_WHITE)
    
    # Progress bar (white outline, green fill)
    display.draw_rectangle(10, 150, 200, 20, SPOTIFY_WHITE)  # Outline
    display.fill_rectangle(12, 152, 100, 16, SPOTIFY_GREEN)  # Fill (50% progress placeholder)
    
    # Skip and previous buttons
    display.fill_rectangle(250, 180, 50, 40, SPOTIFY_GREEN)  # Skip button
    display.fill_rectangle(190, 180, 50, 40, SPOTIFY_GREEN)  # Previous button
    display.draw_text8x8(260, 190, ">>", SPOTIFY_WHITE)     # Skip icon
    display.draw_text8x8(200, 190, "<<", SPOTIFY_WHITE)     # Previous icon

# Handle touch input
def handle_touch():
    coords = touch.get_touch()
    if coords:
        x, y = coords
        # Skip button (250-300, 180-220)
        if 250 <= x <= 300 and 180 <= y <= 220:
            print("Skip button pressed")
            # Placeholder for Spotify API call: POST /v1/me/player/next
            # Example: urequests.post("https://api.spotify.com/v1/me/player/next", headers={"Authorization": "Bearer <token>"})
        # Previous button (190-240, 180-220)
        elif 190 <= x <= 240 and 180 <= y <= 220:
            print("Previous button pressed")
            # Placeholder for Spotify API call: POST /v1/me/player/previous
            # Example: urequests.post("https://api.spotify.com/v1/me/player/previous", headers={"Authorization": "Bearer <token>"})
        return coords
    return None

# Update song info (placeholder for API)
def update_song_info():
    # Placeholder for Spotify API call: GET /v1/me/player/currently-playing
    # Example:
    # response = urequests.get("https://api.spotify.com/v1/me/player/currently-playing", headers={"Authorization": "Bearer <token>"})
    # song = response.json()
    # title = song["item"]["name"]
    # artist = song["item"]["artists"][0]["name"]
    # album = song["item"]["album"]["name"]
    # progress_ms = song["progress_ms"]
    # duration_ms = song["item"]["duration_ms"]
    
    # For now, use dummy data
    title = "Sample Song"
    artist = "Sample Artist"
    album = "Sample Album"
    progress_ms = 60000  # 1 minute
    duration_ms = 180000 # 3 minutes
    
    # Update display
    display.draw_text8x8(10, 10, f"Song: {title[:30]:30}", SPOTIFY_WHITE)
    display.draw_text8x8(10, 20, f"Artist: {artist[:30]:30}", SPOTIFY_WHITE)
    display.draw_text8x8(10, 30, f"Album: {album[:30]:30}", SPOTIFY_WHITE)
    
    # Update progress bar
    progress_width = int((progress_ms / duration_ms) * 196)  # Scale to 196px
    display.fill_rectangle(12, 152, 196, 16, SPOTIFY_BLACK)  # Clear old progress
    display.fill_rectangle(12, 152, progress_width, 16, SPOTIFY_GREEN)  # New progress

# Main loop
try:
    draw_interface()
    last_update = utime.ticks_ms()
    while True:
        # Update song info every 5 seconds
        if utime.ticks_diff(utime.ticks_ms(), last_update) >= 5000:
            update_song_info()
            last_update = utime.ticks_ms()
        
        # Handle touch input
        handle_touch()
        
        utime.sleep_ms(100)  # Reduce CPU usage
except Exception as e:
    print("Error:", e)