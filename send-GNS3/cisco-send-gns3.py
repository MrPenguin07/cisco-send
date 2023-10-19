# Import required libraries
import serial
import time
import sys
import os
import re
import threading
import queue
import argparse
from datetime import datetime


# Error checking function
def check_error(condition, message):
    if not condition:
        print(f"Error: {message}")
        cleanup()
        sys.exit(1)

DEFAULT_DEVICE_FILE = os.path.expanduser('~/ttyCisco')
DEFAULT_DELAY = 0.2

# Command-line argument parsing
parser = argparse.ArgumentParser(description='Send a local config to a device over a serial/console connection.')

# Mandatory argument
parser.add_argument('input_file', type=str, help='Path to the config file for the Cisco device (Router/Switch).')

# Optional arguments
parser.add_argument('--device-file', type=str, default=DEFAULT_DEVICE_FILE, help=f'Path to device file. Default is --device-file {DEFAULT_DEVICE_FILE}')
parser.add_argument('--delay', type=float, default=DEFAULT_DELAY, help=f'Delay between sending lines, in seconds. Default is {DEFAULT_DELAY}s')

# Parse the arguments
args = parser.parse_args()

input_file = args.input_file
device_file = args.device_file
delay_between_lines = args.delay

# Check the input file exists and is readable
check_error(os.path.isfile(input_file), f"File not found or not readable: {input_file}")

# Set variables and serial interface to "8N1"
baud_rate = 9600
data_bits = 8
parity = serial.PARITY_NONE
stop_bits = serial.STOPBITS_ONE

# Configure the serial port
print("------------")
print(f"Setting serial port baud, parity, and stop bits to '8N1' on {args.device_file}")

try:
    ser = serial.Serial(args.device_file, baudrate=baud_rate, bytesize=data_bits, parity=parity, stopbits=stop_bits, rtscts=False, timeout=1)
except Exception as e:
    check_error(False, f"Failed to set serial port parameters: {str(e)}")

# Initialize a thread-safe queue to hold received data
q = queue.Queue()
# Initialize a thread-safe queue to hold detected prompts
prompt_queue = queue.Queue()

# Initialize an empty list to act as a buffer for the device responses
response_buffer = []

# Function to read from port
def read_from_port(serial_port, q, prompt_queue):
    while True:
        reading = serial_port.readline().decode('utf-8').strip()
        if reading:
            # Append the reading to the response buffer instead of printing it
            response_buffer.append(reading)
            q.put(reading)

            if is_prompt(reading):
                prompt_queue.put(reading)

# Start reader thread
reader_thread = threading.Thread(target=read_from_port, args=(ser, q, prompt_queue))
reader_thread.daemon = True  # Daemonize thread
reader_thread.start()

def cleanup():
    # Close the serial port
    if ser.is_open:
        print("Closing serial port...")
        ser.close()
    print("Cleanup complete.")

def is_prompt(line):
    patterns = [
        r"initial configuration dialog",
        r"terminate autoinstall",
        r"Press RETURN",
        r"User Access Verification",
        r"Password:",
        r">",
        r"#(?!.*\(config\)#)",  # matches '#' but not '(config)#'
        r".*\(config\)#"
    ]

    return any(re.search(pattern, line) for pattern in patterns)

def determine_device_state(serial_port, prompt_queue, MAX_RETRIES=15, WAIT_INTERVAL=4):
    attempts = 0

    while attempts < MAX_RETRIES:
        try:
            device_state = prompt_queue.get(timeout=WAIT_INTERVAL)
            print(f"Device state: {device_state}")
        except queue.Empty:
            serial_port.write(b"\r\n")
            print("Reading current device prompt...")
#            attempts += 1
            time.sleep(4)
            continue

        if re.search(r"initial configuration dialog", device_state):
            serial_port.write(b"no\r\n")
            time.sleep(4)
            try:
                device_state = prompt_queue.get(timeout=3)
            except queue.Empty:
                continue

        elif re.search(r"terminate autoinstall|Press RETURN", device_state):
            serial_port.write(b"\r\n")
            time.sleep(4)
            try:
                device_state = prompt_queue.get(timeout=3)
            except queue.Empty:
                continue

        elif re.search(r"Password:|User Access Verification", device_state):
            password = input("Please enter the password: ").strip()
            serial_port.write(f"{password}\r\n".encode('utf-8'))
            time.sleep(4)
            try:
                device_state = prompt_queue.get(timeout=3)
            except queue.Empty:
                continue

        elif re.search(r">", device_state):
            print(f"Entered User Exec Mode (>). Sending 'en'.")
            serial_port.write(b"en\r")
            time.sleep(4)
            try:
                device_state = prompt_queue.get(timeout=3)
            except queue.Empty:
                continue

            if "Password:" in device_state or "User Access Verification" in device_state:
                password = input("Please enter the password: ").strip()
                serial_port.write(f"{password}\r\n".encode('utf-8'))
                time.sleep(2)

        elif re.search(r".*\(config\)#", device_state):
            print("Entered Global Config Mode (config)#.")
            return

        elif re.search(r"#(?!.*\(config\)#)", device_state):
            print(f"Entered Privileged Exec Mode (#). Sending 'conf t'.")
            serial_port.write(b"conf t\r")
            time.sleep(4)
            try:
                device_state = prompt_queue.get(timeout=3)
            except queue.Empty:
                continue

        else:
            print("Unknown device state. Retrying...")
            attempts += 1
            time.sleep(WAIT_INTERVAL)

    print("Max retries reached. Exiting.")
    cleanup()
    sys.exit(1)

determine_device_state(ser, prompt_queue)

print("------------")
print("Device is at hostname(config)# prompt and ready to accept config")
print("CAUTION: Is your device clean? If not, quit this script and manually run '# erase startup-config' && 'reload' first")
print("A wipe feature will be integrated into this script in a future release")
## TO-DO ask user to pull current config and write locally as backup ##
user_response = input("Confirm sending config to device? yes/no (exit): ").strip().lower()

if user_response in ['yes', 'y']:
    print(f"Reading {input_file}, sending line by line with delay of {delay_between_lines}")
elif user_response in ['no', 'n']:
    cleanup()
    print("Exiting the program.")
    exit()
else:
    print("Invalid input. Exiting the program.")
    exit()

print("..")
print("...")

# Read the file line by line and send each line with a delay
with open(input_file, 'r') as f:
    for line in f:
        line = line.strip()
        # Skip lines that start with "!"
        if line.startswith("!"):
            continue
        print(line)
        try:
            ser.write(f"{line}\r\n".encode('utf-8'))
        except Exception as e:
            check_error(False, f"Failed to send the command: {line}, Error: {str(e)}")

        time.sleep(delay_between_lines)

print("Configuration complete.")
print("-----------------------")

# Ask user to save running-config to startup-config
def save_config_to_startup(serial_port):
    user_input = input("Save running-config to startup-config? (y/n): ").strip().lower()
    if user_input == 'y':
        print("Writing to memory...")
        serial_port.write(b"write memory\r")
        time.sleep(1)
        print("Configuration saved.")
    else:
        print("Configuration not saved.")

save_config_to_startup(ser)

def print_and_save_responses():
    # Ask user if they want to print the buffered responses to the console
    user_input = input("Print device responses to console? (y/n): ").strip().lower()
    if user_input == 'y':
        for response in response_buffer:
            print(response)

    # Ask user if they want to save the buffered responses to a log file
    user_input = input("Save responses to logfile? (y/n): ").strip().lower()

    if user_input == 'y' or user_input == 'yes':
        # Construct the default log file path
        date_str = datetime.now().strftime('%d-%m-%Y-%H:%M')
        default_log_file_path = os.path.expanduser(f"~/{date_str}-{os.path.basename(input_file)}-log.txt")

        # Ask user for confirmation or modification
        user_file_input = input(f"Save to default path: {default_log_file_path}? (y/n): ").strip().lower()
        if user_file_input != 'y' and user_file_input != 'yes':
            custom_log_file_path = input("Enter the custom path and filename: ").strip()
            log_file_path = os.path.expanduser(custom_log_file_path)
        else:
            log_file_path = default_log_file_path

        # Save to the log file
        with open(log_file_path, 'w') as log_file:
            for response in response_buffer:
                log_file.write(f"{response}\n")
        print(f"Responses saved to {log_file_path}")

print_and_save_responses()

if __name__ == "__main__":
    try:
        pass
    finally:
        cleanup()

sys.exit(0)
