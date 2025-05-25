import serial
import wmi
import psutil
import time
import serial.tools.list_ports

def get_openhardwaremonitor_data():
    try:
        w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        sensors = w.Sensor()
        data = {
            "CPU": None,
            "CPU Temp": None,
            "CPU Clock": None,
            "GPU Usage": None,
            "GPU Temp": None,
            "RAM": None,
            "Disk": None,
            "Net Sent": None,
            "Net Recv": None
        }
        # Debug: Print all sensors
        print("Available sensors:")
        for sensor in sensors:
            print(f"Sensor: {sensor.Name}, Type: {sensor.SensorType}, Value: {sensor.Value}")
        
        for sensor in sensors:
            if sensor.SensorType == "Load" and "CPU Total" in sensor.Name:
                data["CPU"] = round(sensor.Value, 1)
            elif sensor.SensorType == "Load" and "Memory" in sensor.Name:
                data["RAM"] = round(sensor.Value, 1)
            elif sensor.SensorType == "Load" and "Used Disk" in sensor.Name:
                data["Disk"] = round(sensor.Value, 1)
            elif sensor.SensorType == "Temperature" and "CPU Package" in sensor.Name:
                data["CPU Temp"] = round(sensor.Value, 1)
            elif sensor.SensorType == "Temperature" and "GPU Core" in sensor.Name:
                data["GPU Temp"] = round(sensor.Value, 1)
            elif sensor.SensorType == "Clock" and "CPU Core" in sensor.Name:
                data["CPU Clock"] = round(sensor.Value, 1)
            elif sensor.SensorType == "Load" and "GPU Core" in sensor.Name:
                data["GPU Usage"] = round(sensor.Value, 1)
        # Network data via psutil
        net_io = psutil.net_io_counters()
        data["Net Sent"] = round(net_io.bytes_sent / (1024 * 1024), 1)  # MB
        data["Net Recv"] = round(net_io.bytes_recv / (1024 * 1024), 1)  # MB
        return data
    except Exception as e:
        print(f"WMI error: {e}")
        return None

def test_serial():
    print("Available ports:", [port.device for port in serial.tools.list_ports.com_ports()])
    for attempt in range(1, 4):
        try:
            ser = serial.Serial('COM3', 115200, timeout=1)
            print(f"Connected to {ser.port} on attempt {attempt}")
            ser.reset_input_buffer()  # Clear input buffer
            ser.reset_output_buffer()  # Clear output buffer
            while True:
                text = input("Enter text to send (or 'exit' to quit): ")
                if text.lower() == 'exit':
                    break
                ser.write((text + ' |').encode('utf-8'))
                print(f"Sending: {text} |")
                time.sleep(0.1)
                print("Data sent successfully")
            ser.close()
            break
        except serial.SerialException as e:
            print(f"Failed to connect on attempt {attempt}: {e}")
            time.sleep(1)
    else:
        print("All attempts failed")

def send_system_info():
    try:
        ser = serial.Serial('COM3', 115200, timeout=1)
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        print(f"Connected to {ser.port}")
        while True:
            data = get_openhardwaremonitor_data()
            if data:
                lines = [
                    f"CPU: {data['CPU']}%",
                    f"CPU Temp: {data['CPU Temp']}C",
                    f"CPU Clock: {data['CPU Clock']}MHz",
                    f"GPU Usage: {data['GPU Usage']}%",
                    f"GPU Temp: {data['GPU Temp']}C",
                    f"RAM: {data['RAM']}%",
                    f"Disk: {data['Disk']}%",
                    f"Net Sent: {data['Net Sent']}MB",
                    f"Net Recv: {data['Net Recv']}MB"
                ]
                for line in lines:
                    ser.write((line + ' |').encode('utf-8'))
                    print(f"Sending: {line} |")
                    time.sleep(0.05)  # Fast update
            else:
                print("Failed to get system data")
            time.sleep(.5)  # Fast cycle
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    send_system_info()
    # test_serial()