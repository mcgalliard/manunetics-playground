import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import serial
import struct
import time
import zlib
import sys

# Bootloader protocol constants
CMD_ERASE = b'\x01'
CMD_WRITE = b'\x02'
CMD_JUMP  = b'\x03'
ACK = b'\x79'
NACK = b'\x1F'

PORT       = "COM8"    # Adjust COM port
BAUD       = 300000
CHUNK_SIZE = 256       # Flash write block size
APP_ADDR = 0x08004000

FILE = r"C:\Users\cpmcg\STM32CubeIDE\workspace_1.16.0\f0nuleoblinkyblinky\Release\f0nuleoblinkyblinky.bin"


class BootloaderGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("STM32 Bootloader Programmer")
        self.geometry("500x300")

        # Progress bar
        self.progress = ttk.Progressbar(self, length=400, mode='determinate')
        self.progress.pack(pady=20)

        # Status display
        self.status_text = scrolledtext.ScrolledText(self, width=60, height=10, state='disabled')
        self.status_text.pack(padx=10)

        # Start button
        self.start_button = ttk.Button(self, text="Start Programming", command=self.start_programming)
        self.start_button.pack(pady=10)

    def log(self, message):
        self.status_text.configure(state='normal')
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.configure(state='disabled')

    def send_cmd(self, ser, cmd, payload=b'', retries=3):
        for attempt in range(retries):
            ser.write(cmd + payload)
            ack = ser.read(1)
            if ack == ACK:
                self.log("ACK from board")
                return True
            self.log(f"⚠️ Attempt {attempt+1} failed: got {ack.hex() if ack else 'no data'}")
        self.log(f"❌ Command {cmd.hex()} failed after {retries} attempts.")
        return False

    def start_programming(self):
        self.start_button.config(state='disabled')
        self.progress['value'] = 0
        self.status_text.configure(state='normal')
        self.status_text.delete('1.0', tk.END)
        self.status_text.configure(state='disabled')
        threading.Thread(target=self.program_firmware, daemon=True).start()

    def update_progress(self, percent):
        # Update progress bar in main thread
        self.progress.after(0, lambda: self.progress.config(value=percent))

    def program_firmware(self):
        try:
            ser = serial.Serial(PORT, BAUD, timeout=2)
            time.sleep(2)  # Wait for STM32 boot/reset

            with open(FILE, "rb") as f:
                app_data = f.read()

            app_size = len(app_data)
            crc32 = zlib.crc32(app_data) & 0xFFFFFFFF
            self.log(f"ℹ️ App size: {app_size} bytes, CRC32: {crc32:08X}")

            self.log("🗑 Erasing flash...")
            addr_size_crc = struct.pack("<III", APP_ADDR, app_size, crc32)
            if not self.send_cmd(ser, CMD_ERASE, addr_size_crc):
                raise RuntimeError("Erase command failed.")

            self.log("📡 Sending firmware...")
            sent = 0
            start_time = time.time()

            while sent < app_size:
                remaining = app_size - sent
                chunk_size = min(CHUNK_SIZE, remaining)
                chunk = app_data[sent:sent + chunk_size]

                if chunk_size < CHUNK_SIZE:
                    chunk += b'\xFF' * (CHUNK_SIZE - chunk_size)

                payload = struct.pack("<I", APP_ADDR + sent) + chunk
                if not self.send_cmd(ser, CMD_WRITE, payload):
                    raise RuntimeError(f"Write command failed at offset {sent}")

                sent += chunk_size
                percent = (sent / app_size) * 100
                self.update_progress(percent)
                self.log(f"Progress: {percent:.2f}%")

            elapsed = time.time() - start_time
            self.log(f"✅ Transfer complete in {elapsed:.1f} seconds.")

            self.log("🚀 Jumping to application...")
            if not self.send_cmd(ser, CMD_JUMP, struct.pack("<I", APP_ADDR)):
                raise RuntimeError("Jump command failed.")

            ser.close()
            self.log("✅ Done. Bootloader exited.")
        except Exception as e:
            self.log(f"❌ Error: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            self.start_button.config(state='normal')


if __name__ == "__main__":
    app = BootloaderGUI()
    app.mainloop()
