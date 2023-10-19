#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <input_file>"
  exit 1
fi

# Check the input file exists and is readable
input_file="$1"
if [ ! -f "$input_file" ]; then
  echo "Error: File not found or not readable: $input_file"
  exit 1
fi

check_error() {
  if [ $? -ne 0 ]; then
    echo "Error: $1"
    exit 1
  fi
}

# Configure variables

# Adjust the delay (in seconds)
delay_between_lines=0.2

# Set variables and serial interface to "8N1".
device_file="/dev/ttyUSB0"
baud_rate=9600
data_bits=8
parity="-parenb"
stop_bits="-cstopb"

# Optionally set baud to 1200,4800,9600,19200,38400,57600,115200
 #   cs8:     8 data bits
 #   -parenb: No parity (because of the '-')
 #   -cstopb: 1 stop bit (because of the '-')
 #   -echo: Without this option, Linux will sometimes automatically send back
 #          any received characters, even if you are just reading from the serial
 #          port with a command like 'cat'. Some terminals will print codes
 #          like "^B" when receiving back a character like ASCII ETX (hex 03).
 #   -crtscts: Disables RTS/CTS (req. to send/clear to send hardware flow control
 #    litout:  Disables output processing,

# extras="-brkint -imaxbel -icrnl -opost -onlcr -isig -icanon -iexten \
#        -echo -echoe -echok -echoctl -echoke -noflsh -ixon -crtscts"

echo "##"
echo "------------"
echo "Setting serial port baud, parity, and stop bits to "8N1" on /dev/ttyUSB0"

# Configure the serial port
stty -F "$device_file" sane
check_error "Failed to configure serial port to sane"
sleep 1

stty -F "$device_file" "$baud_rate" cs"$data_bits" "$parity" "$stop_bits" -echo -crtscts litout
check_error "Failed to set serial port parameters"
sleep 1

# Enable configuration mode
echo "en" > "$device_file" && echo "conf t" > "$device_file"
check_error "Failed to enable configuration mode"
sleep 1

echo "Done."
echo "------------"
echo "Reading $input_file, sending line by line with delay of $delay_between_lines"
echo ".."
echo "..."
# Read the file line by line and send each line with a delay
while IFS= read -r line; do
    echo "$line"
    echo -e "$line\r" > "$device_file"
    check_error "Failed to send the command: $line"
    sleep "$delay_between_lines"
done < "$input_file"

echo "Done."
echo "-----------------------"
echo "Configuration complete."
