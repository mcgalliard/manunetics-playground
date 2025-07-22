import serial
import struct
import time
import sys
import zlib

# Bootloader protocol constants
CMD_ERASE = b'\x01'
CMD_WRITE = b'\x02'
CMD_JUMP  = b'\x03'
ACK = b'\x79'
NACK = b'\x1F'

PORT       = "COM9"    # Adjust COM port
BAUD       = 115200
CHUNK_SIZE = 256       # Flash write block size
APP_ADDR   = 0x08004000
APP_ADDR = 0x08005000

FILE = r"C:\Users\cpmcg\STM32CubeIDE\workspace_1.16.0\c0-blinky\Debug\c0-blinky.bin"

def send_cmd(ser, cmd, payload=b'', retries=3):
    for attempt in range(retries):
        ser.write(cmd + payload)
        ack = ser.read(1)
        if ack == ACK:
            print("✅ ACK from board")
            return
        print(f"⚠️ Attempt {attempt+1} failed: got {ack.hex() if ack else 'no data'}")
    print(f"❌ Command {cmd.hex()} failed after {retries} attempts.")
    sys.exit(1)

def main():
    ser = serial.Serial(PORT, BAUD, timeout=5)  # Increased timeout
    ser.reset_input_buffer()  # Flush any noise
    time.sleep(2)  # Wait for STM32 boot/reset

    try:
        with open(FILE, "rb") as f:
            app_data = f.read()

        app_size = len(app_data)
        crc32 = zlib.crc32(app_data) & 0xFFFFFFFF
        print(f"ℹ️ App size: {app_size} bytes, CRC32: {crc32:08X}")

        # Send erase command
        print("🗑 Erasing flash...")
        addr_size_crc = struct.pack("<III", APP_ADDR, app_size, crc32)
        send_cmd(ser, CMD_ERASE, addr_size_crc)

        # Send application data in chunks
        print("📡 Sending firmware...")
        sent = 0
        start_time = time.time()
        while sent < app_size:
            remaining = app_size - sent
            chunk_size = min(CHUNK_SIZE, remaining)
            chunk = app_data[sent:sent + chunk_size]

            # Pad chunk if smaller than CHUNK_SIZE
            if chunk_size < CHUNK_SIZE:
                chunk += b'\xFF' * (CHUNK_SIZE - chunk_size)

            payload = struct.pack("<I", APP_ADDR + sent) + chunk
            send_cmd(ser, CMD_WRITE, payload)

            sent += chunk_size

            percent = (sent / app_size) * 100
            print(f"\rProgress: {percent:.2f}%", end="")
            sys.stdout.flush()

        elapsed = time.time() - start_time
        print(f"\n✅ Transfer complete in {elapsed:.1f} seconds.")

        # Send jump command
        print("🚀 Jumping to application...")
        send_cmd(ser, CMD_JUMP, struct.pack("<I", APP_ADDR))
        time.sleep(0.1)  # Give board time to switch context

        print("✅ Done. Bootloader exited.")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
