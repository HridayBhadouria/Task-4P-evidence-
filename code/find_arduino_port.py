"""I list the serial ports that Windows can see."""

from serial.tools import list_ports


ports = list(list_ports.comports())

if not ports:
    print("No serial ports were found. Connect the Arduino and try again.")
else:
    print("Available serial ports:")
    for port in ports:
        print(f"{port.device} - {port.description}")
