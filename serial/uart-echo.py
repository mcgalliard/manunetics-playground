import serial
import time

port = "COM9"  # Adjust to your COM port
baudrate = 115200

# Open the serial port
ser = serial.Serial(port, baudrate, timeout=1)
time.sleep(2)  # Let the STM32 boot if reset on connect

# Test bytes to send
test_bytes = b'ABCDEaja;fa;nsdovfj ;lsdkfnasj;klvjas;lkvjadnlkdsavjn;lkdsajf;kljsad;flj;adlskjf;lksadjvnlksdja'  # ASCII bytes for easy debugging

for byte in test_bytes:
    print(f"Sending: {chr(byte)} ({byte:#02x})")
    ser.write(bytes([byte]))  # Send single byte
    response = ser.read(1)    # Read echo back
    if response:
        print(f"Received: {chr(response[0])} ({response.hex()})")
    else:
        print("No response (timeout)")

ser.close()
