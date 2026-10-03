"""I save PIR readings from the Arduino into a CSV file."""

import argparse
import csv
import time
from datetime import datetime
from pathlib import Path

import serial


def read_arguments():
    parser = argparse.ArgumentParser(description="Save PIR readings from an Arduino.")
    parser.add_argument("--port", required=True, help="Arduino port, for example COM3")
    parser.add_argument("--minutes", type=float, default=125, help="Collection time in minutes")
    parser.add_argument("--output", default="raw_pir_data.csv", help="Output CSV file name")
    return parser.parse_args()


def main():
    args = read_arguments()
    output_path = Path(args.output)
    end_time = time.monotonic() + (args.minutes * 60)
    saved_rows = 0
    skipped_lines = 0

    try:
        with serial.Serial(args.port, 9600, timeout=2) as arduino, output_path.open(
            "w", newline="", encoding="utf-8"
        ) as output_file:
            writer = csv.DictWriter(
                output_file, fieldnames=["sample_number", "timestamp", "pir_reading"]
            )
            writer.writeheader()

            # I wait for the Arduino to reset after the serial port opens.
            time.sleep(2)
            arduino.reset_input_buffer()

            print(f"Saving PIR readings for {args.minutes} minutes.")
            print("Press Ctrl+C only if you need to stop early.")

            while time.monotonic() < end_time:
                line = arduino.readline().decode("utf-8", errors="ignore").strip()

                # I only save the 0 and 1 values sent by the Arduino.
                if line not in {"0", "1"}:
                    if line:
                        skipped_lines += 1
                        print(f"Skipped unexpected serial text: {line}")
                    continue

                saved_rows += 1
                row = {
                    "sample_number": saved_rows,
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                    "pir_reading": int(line),
                }
                writer.writerow(row)
                output_file.flush()
                print(f"Saved row {saved_rows}: PIR = {line}")

    except serial.SerialException as error:
        print(f"Could not open {args.port}: {error}")
        print("Check the Arduino cable and the COM port, then try again.")
        return
    except KeyboardInterrupt:
        print("Collection stopped early by the user.")

    print(f"Finished. Saved rows: {saved_rows}")
    print(f"Skipped serial lines: {skipped_lines}")
    print(f"Raw data file: {output_path.resolve()}")


if __name__ == "__main__":
    main()
