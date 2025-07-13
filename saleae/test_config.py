import json
import os
from datetime import datetime
from saleae import automation

# Load configuration from JSON file
CONFIG_FILE = "C:\\Users\\manunetics\\Documents\\manunetics-playground\\saleae\\saleae_config.json"

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

# Extract device configuration
device_config = config["device_config"]
analyzers_config = config["analyzers"]

# Set up output directory
if device_config["output_directory"] == "default":
    output_dir = os.path.join(
        os.getcwd(),
        f'output-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
    )
else:
    output_dir = os.path.abspath(device_config["output_directory"])

os.makedirs(output_dir, exist_ok=True)

# Connect to Logic 2 Automation API
with automation.Manager.connect(port=10430) as manager:
    # Configure device
    device_configuration = automation.LogicDeviceConfiguration(
        enabled_digital_channels=[0],
        digital_sample_rate=device_config["digital_sample_rate"]
    )

    # Set up timed capture
    capture_configuration = automation.CaptureConfiguration(
        capture_mode=automation.TimedCaptureMode(
            duration_seconds=device_config["capture_length_sec"]
        )
    )

    # Start capturing
    with manager.start_capture(
        device_configuration=device_configuration,
        capture_configuration=capture_configuration
    ) as capture:
        print(f"Capturing data for {device_config['capture_length_sec']} seconds...")
        capture.wait()  # Wait until capture finishes

        # Add analyzers from config
        for name, analyzer in analyzers_config.items():
            print(f"Adding analyzer: {name}")
            uart_analyzer = capture.add_analyzer(
                analyzer["type"],
                settings={
                    "Input Channel": analyzer["input_channel"],
                    "Bit Rate (Bits/s)": int(analyzer["baud"]),
                    "Bits per Frame": 8,
                    "Stop Bits": 1 
                }
            )

            # Export analyzer data to CSV
            csv_path = os.path.join(output_dir, f"{name}_data.csv")
            capture.export_data_table(
                filepath=csv_path,
                analyzers=[uart_analyzer]
            )
            print(f"Exported {name} data to: {csv_path}")

        # Save the entire capture
        capture_file_path = os.path.join(output_dir, 'capture.sal')
        capture.save_capture(filepath=capture_file_path)
        print(f"Capture file saved to: {capture_file_path}")

print(f"All files saved in: {output_dir}")
