#!/bin/bash

# Function to cleanup background socat process
cleanup() {
    echo "Cleaning up..."
    kill $socat_pid 2>/dev/null
    exit 0
}

# Trap to call cleanup function upon script termination
trap cleanup EXIT

# Ask user for virtual device path/name
read -p "Enter the path/name for the virtual device [default: $HOME/ttyCisco]: " device_path
device_path=${device_path:-"$HOME/ttyCisco"}

# Ask user for GNS3 device serial port
read -p "Enter the port number GNS3 is listening for telnet [default: 5000]: " port
port=${port:-5000}

# Start socat
echo "Starting socat..."
socat pty,link="$device_path",rawer tcp:127.0.0.1:"$port" &
socat_pid=$!

# Check if socat started successfully
if [ $? -ne 0 ]; then
    echo "Error: socat failed to start"
    exit 1
fi

echo "socat started with PID $socat_pid"

# Ask to launch screen
read -p "Would you like to launch screen into the device? [y/N]: " launch_screen
if [[ $launch_screen == "y" || $launch_screen == "Y" ]]; then
    # Ask for baud rate
    read -p "Enter the baud rate [default: 9600]: " baud_rate
    baud_rate=${baud_rate:-9600}

    # Launch screen in a subshell
    echo "Launching screen..."
    (
        screen "$device_path" "$baud_rate",cs8
    )
    echo "Screen session ended. socat is still running with PID $socat_pid."
    echo "Press Ctrl-C to kill socat and exit."
else
    echo "Done. socat is running with PID $socat_pid."
    echo "You can manually connect to the device with screen or another terminal program."
    echo "Press Ctrl-C to kill socat and exit."
fi

# Loop to keep the script running
while true; do
    sleep 1
done

