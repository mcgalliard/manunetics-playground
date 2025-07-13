from saleae import automation
import os
from datetime import datetime

# Connect to Logic 2 Automation API
with automation.Manager.connect(port=10430) as manager:
    # Configure device: monitor digital channel 0 at 10 MSa/s
    device_configuration = automation.LogicDeviceConfiguration(
        enabled_digital_channels=[0],  # Only channel 0
        digital_sample_rate=10_000_000,  # 10 MHz sampling
    )

    # Set up a timed 5-second capture
    capture_configuration = automation.CaptureConfiguration(
        capture_mode=automation.TimedCaptureMode(duration_seconds=5.0)
    )

    # Create output folder with timestamp
    output_dir = os.path.join(
        os.getcwd(),
        f'output-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
    )
    os.makedirs(output_dir, exist_ok=True)

    # Start capturing
    with manager.start_capture(
        device_configuration=device_configuration,
        capture_configuration=capture_configuration
    ) as capture:
        print("Capturing UART data for 5 seconds...")
        capture.wait()  # Wait until capture finishes

        # Add UART analyzer to digital channel 0
        uart_analyzer = capture.add_analyzer('Async Serial', settings={'Input Channel': 0,
                               'Bit Rate (Bits/s)': 115200,
                               'Bits per Frame': 8,
                               'Stop Bits': 1})

        print("Exporting data...")

        # Export UART decoded data to CSV
        uart_csv_path = os.path.join(output_dir, 'uart_data.csv')
        capture.export_data_table(
            filepath=uart_csv_path,
            analyzers=[uart_analyzer]
        )

        # Save the entire capture
        capture_file_path = os.path.join(output_dir, 'capture.sal')
        capture.save_capture(filepath=capture_file_path)

        print(f"Export complete. Files saved in: {output_dir}")
