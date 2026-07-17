import serial.tools.list_ports
import serial
import time

SERIAL_PORT="/dev/cu.usbmodem1203"
BAUD_RATE=115200

def get_available_ports():
    ports=serial.tools.list_ports.comports()
    if not ports:
        print("No Serial Port Fetched")
        return []
    print("Ports Serial Available:")
    available_ports=[]
    for port in ports:
        print(f"- Port: {port.device}")
        print(f"  Description: {port.description}")
        print(f"  Productor: {port.manufacturer}")
        print(f"  Hardware ID: {port.hwid}")
        available_ports.append(port.device)
    return available_ports

def main():
    try:
        print(f"Open {SERIAL_PORT} with {BAUD_RATE} baud...")
        ser=serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(1)
        ser.reset_input_buffer()
        print("Listening...")
        while True:
            if ser.in_waiting>0:
                raw_line=ser.readline().decode('utf-8', errors='ignore')
                clean_line=raw_line.strip()
                if not clean_line:
                    continue
                data=[int(x) for x in clean_line.split(',')]
                print(data)
                
    except serial.SerialException as e:
        print(f"Connection Error: {e}")
    except KeyboardInterrupt:
        print("Program Ended Forced")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial Port Close Correctly")
if __name__=="__main__":
    ports_list=get_available_ports()
    main()