FILE = "C:\\Users\\cpmcg\\STM32CubeIDE\\workspace_1.16.0\\spoon\\Debug\\spoon.elf"

import serial
import time
import base64
import sys

PORT = "COM8"
BAUD = 115200
ser = serial.Serial(PORT, BAUD, timeout=0.5)
time.sleep(2)

with open(FILE, "rb") as f:
    elf_bytes = f.read()

b64_bytes = base64.b64encode(elf_bytes)
total_len = len(b64_bytes)

sent = 0
echoed = bytearray()
start_time = last_report = time.time()

while sent < total_len or len(echoed) < total_len:
    # Send next byte if available
    if sent < total_len:
        ser.write(b64_bytes[sent:sent+1])
        sent += 1
        time.sleep(0.01)  # 10 ms delay

    # Read any available echoed bytes
    while ser.in_waiting:
        echoed.extend(ser.read(ser.in_waiting))

    # Progress report every 1 second
    now = time.time()
    if now - last_report >= 1:
        sent_pct = sent / total_len * 100
        echo_pct = len(echoed) / total_len * 100
        elapsed = now - start_time
        speed = len(echoed) / elapsed / 1024
        print(f"\rSent: {sent_pct:.1f}%, Echoed: {echo_pct:.1f}%, Speed: {speed:.1f} KB/s", end="")
        last_report = now

print(f"\nDone in {time.time()-start_time:.1f}s")

ser.close()

if echoed == b64_bytes:
    print("✅ Echo verified!")
else:
    print("❌ Echo mismatch!")
