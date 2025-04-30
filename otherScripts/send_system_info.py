import psutil
import serial
import time
import platform
import binascii
import serial.tools.list_ports
import threading
import queue

# Serial port configuration
SERIAL_PORT = 'COM3'  # Adjust as needed
BAUD_RATE = 115200
TIMEOUT = 3

# Queue for serial writes
write_queue = queue.Queue()

# Function to open serial port
def open_serial_port():
    for attempt in range(3):
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT, rtscts=True)
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            print(f"Connected to {SERIAL_PORT} on attempt {attempt+1}")
            return ser
        except serial.SerialException as e:
            print(f"Serial connection error on attempt {attempt+1}: {e}")
            time.sleep(2)
    raise serial.SerialException("Failed to open serial port after 3 attempts")

# Serial writer thread
def serial_writer():
    ser = None
    while True:
        try:
            if not ser or not ser.is_open:
                ser = open_serial_port()
            
            data = write_queue.get()  # Block until data is available
            if data == "STOP":
                break
            
            for attempt in range(3):
                try:
                    ser.reset_input_buffer()
                    ser.reset_output_buffer()
                    print("Sending:", data.replace('\n', ' | '))
                    print(f"Bytes sent: {len(data.encode('utf-8'))}")
                    print(f"Bytes (hex): {binascii.hexlify(data.encode('utf-8')).decode()}")
                    ser.write(data.encode('utf-8'))
                    ser.flush()
                    print("Data sent successfully")
                    break
                except serial.SerialException as e:
                    print(f"Serial error on attempt {attempt+1}: {e}")
                    if attempt == 2:
                        ser.close()
                        ser = open_serial_port()
                    time.sleep(1)
        except Exception as e:
            print(f"Writer error: {e}")
            if ser and ser.is_open:
                ser.close()
            ser = None
            time.sleep(2)

# Function to get system info
def get_system_info():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    mem_usage = memory.percent
    disk = psutil.disk_usage('/')
    disk_usage = disk.percent
    net = psutil.net_io_counters()
    net_sent = net.bytes_sent / (1024 * 1024)
    net_recv = net.bytes_recv / (1024 * 1024)
    return cpu_usage, mem_usage, disk_usage, net_sent, net_recv

# Function to send system info via serial
def send_system_info():
    try:
        # Start serial writer thread
        writer_thread = threading.Thread(target=serial_writer, daemon=True)
        writer_thread.start()
        
        time.sleep(10)  # Wait for ESP32 to boot
        
        # Send test message
        test_data = "TEST: OK\n"
        write_queue.put(test_data)
        time.sleep(2)
        
        while True:
            cpu_usage, mem_usage, disk_usage, net_sent, net_recv = get_system_info()
            data = (
                f"CPU: {cpu_usage:.1f}%\n"
                f"RAM: {mem_usage:.1f}%\n"
                f"Disk: {disk_usage:.1f}%\n"
                f"Net Sent: {net_sent:.1f}MB\n"
                f"Net Recv: {net_recv:.1f}MB\n"
            )
            write_queue.put(data)
            time.sleep(5)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        write_queue.put("STOP")

# Test function for manual serial input
def test_serial():
    try:
        # Start serial writer thread
        writer_thread = threading.Thread(target=serial_writer, daemon=True)
        writer_thread.start()
        
        time.sleep(10)  # Wait for ESP32 to boot
        prompt_count = 0
        
        while True:
            user_input = input("Enter text to send (or 'exit' to quit): ")
            prompt_count += 1
            print(f"Prompt #{prompt_count}")
            if user_input.lower() == 'exit':
                write_queue.put("STOP")
                break
            data = user_input + '\n'
            write_queue.put(data)
            time.sleep(1)  # Allow writer to process
    except Exception as e:
        print(f"Error: {e}")
    finally:
        write_queue.put("STOP")

# Run the function
if __name__ == "__main__":
    ports = [p.device for p in serial.tools.list_ports.comports()]
    print(f"Available ports: {ports}")
    test_serial()
    # send_system_info()