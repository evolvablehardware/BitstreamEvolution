import serial
import time
import os
import threading
import sys
import pathlib

# ==============================
# Configuration
# ==============================
PORT = "/dev/ttyACM0"   # Change to COMx on Windows
BAUD = 115200            # ignored by TinyUSB but needed by pyserial
FILENAME = "blinky_bitstream.bin"
CHUNK_SIZE = 512         # bytes per write
INTER_CHUNK_DELAY = 0.00001  # seconds
SHOW_RX = False           # print incoming text from device
# ==============================

def read_from_device(ser: serial.Serial):
    """Thread that continuously reads from the Pico and prints output."""
    while ser.is_open:
        try:
            data = ser.read(ser.in_waiting or 1)
            if data:
                # Print raw text to stdout (decode safely)
                sys.stdout.write(data.decode(errors='replace'))
                sys.stdout.flush()
        except serial.SerialException:
            break
        except OSError:
            break

def write_to_device(ser: serial.Serial, data: bytes):
    """Write binary data to the Pico in chunks."""
    last_percent = -1
    total_len = len(data)
    for i in range(0, total_len, CHUNK_SIZE):
        chunk = data[i:i+CHUNK_SIZE]
        ser.write(chunk)
        ser.flush()
        time.sleep(INTER_CHUNK_DELAY)
        if(SHOW_RX):
            current_percent = int((i + len(chunk)) * 100 / total_len)

            if current_percent > last_percent:
                print(f"\rProgress: {current_percent:6.2f}%", end="", flush=True)
                last_percent = current_percent
    
    
def flash_bitstream(serial_port_fd:str, bitstream_addr:str):
    if not os.path.exists(bitstream_addr):
        print(f"Error: file '{bitstream_addr}' not found.")
        return
    
    # Read entire binary file
    with open(bitstream_addr, "rb") as f:
        data = f.read()
    data_len = len(data)
    print(f"File size: {data_len} bytes")
    
    # Open serial connection
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    time.sleep(2)  # give Pico time to enumerate and reset
    
    write_to_device(ser, data)
    ser.close()
    

    
    
    
def main():
    if not os.path.exists(FILENAME):
        print(f"Error: file '{FILENAME}' not found.")
        return

    # Read entire binary file
    with open(FILENAME, "rb") as f:
        data = f.read()
    data_len = len(data)
    print(f"File size: {data_len} bytes")

    # Open serial connection
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    time.sleep(2)  # give Pico time to enumerate and reset

    # Start background thread for reading device output
    if SHOW_RX:
        reader_thread = threading.Thread(target=read_from_device, args=(ser,), daemon=True)
        reader_thread.start()

    print("Starting transfer...")
    # Send the file in chunks
    write_to_device(ser, data)

    print("\nTransfer complete. Waiting for device response...")

    # Give Pico time to finish responding
    time.sleep(2)

    ser.close()
    print("Closed serial port.")

if __name__ == "__main__":
    main()

