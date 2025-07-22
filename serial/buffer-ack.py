
FILE = "C:\\Users\\cpmcg\\STM32CubeIDE\\workspace_1.16.0\\spoon\\Debug\\spoon.elf"
import serial
import time
import struct

PORT = "COM8"
BAUD = 2000000
CHUNK_SIZE = 512
ACK = b'\x06'
FINAL = b'\x04'

ser = serial.Serial(PORT, BAUD, timeout=2)
time.sleep(2)  # Allow STM32 reset

with open(FILE, "rb") as f:
    data = f.read()

total_size = len(data)
num_chunks = (total_size + CHUNK_SIZE - 1) // CHUNK_SIZE

# Build header: size + chunks count, little-endian uint32
header = struct.pack('<II', total_size, num_chunks)

# Send header and wait for ACK
ser.write(header)
ack = ser.read(1)
if ack != ACK:
    print("Header ACK failed")
    ser.close()
    exit(1)

sent = 0
start_time = last_report = time.time()

for chunk_i in range(num_chunks):
    chunk_start = chunk_i * CHUNK_SIZE
    chunk_end = min(chunk_start + CHUNK_SIZE, total_size)
    chunk = data[chunk_start:chunk_end]

    # Pad last chunk if needed
    if len(chunk) < CHUNK_SIZE:
        chunk += b'\x00' * (CHUNK_SIZE - len(chunk))

    ser.write(chunk)
    ack = ser.read(1)
    if ack != ACK:
        print(f"Chunk {chunk_i} ACK failed")
        break

    sent += len(chunk)

    # Print progress every second
    now = time.time()
    if now - last_report >= 1 or sent == total_size:
        percent = (sent / total_size) * 100
        elapsed = now - start_time
        speed = sent / elapsed / 1024
        print(f"\rSent: {percent:.2f}% | Speed: {speed:.1f} KB/s", end='')
        last_report = now

# Send final message and wait for ACK
ser.write(FINAL)
final_ack = ser.read(1)
if final_ack == ACK:
    print("\nTransfer complete!")
else:
    print("\nNo final ACK or unexpected response")

ser.close()
