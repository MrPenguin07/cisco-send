 # cisco-send scripts

Send a local config to device over serial/console connection. 

These scripts were created as an alternative to the cumbersome tftp and xmodem etc methods of sending configs. Copy pasting a config directly usually works for smaller configs however at a certain point configs are too large - data is sent too quickly and the device chokes, causing errors in the final config. 

Herein lies the simplicity of automation by script - read a local config and send it to the device, with a configurable delay between lines to prevent errors.

This repository contains both an advanced multi-threaded asynchronous python - and a simple Bash version of the script.

## Table of Contents

- [Files](#files)
- [Usage](#usage)
  - [Python Script](#python-script)
  - [GNS3 Serial Bridge](#gns3-serial-bridge)
  - [Bash Script](#bash-script)
- [Features](#features)
  - [Python Version](#python-version)
  - [Bash Version](#bash-version)

## Files

 .
├──  Bash-Version
│  └──  cisco-send.sh
├──  send-GNS3
│  ├──  cisco-send-gns3.py
│  └──  gns3-serial-bridge.sh
├──  cisco-send.py
├──  LICENSE
├──  README.md
└──  requirements.txt

- **`cisco-send.py`**: Python script for sending config files to running-config.

- **`cisco-send-gns3.py`**: GNS3 version of the script, send configs into virtual devices.
- **`gns3-serial-bridge.sh`**: Used in conjunction with cisco-send-gns3.py. Maps telnet port to device file.

- **`requirements.txt`**: Lists Python packages required for the Python version.
- **`cisco-send.sh`**: Bash script for sending config files to running-config.

## Usage

### Python Script

Confirm your device file, default is set to `/dev/ttyUSB0` - edit accordingly if required.

Run the Python script using the following commands:

Install dependencies;
`pip install -r requirements.txt` || `<your-pkg-manager> install pyserial`

Run script;
```bash
python3 cisco-send.py <input_file>
```

Replace `<input_file>` with the path to the config file for the cisco device (Router/Switch)

You'll likely want to add the script to your `$PATH` ie. ~/.local/bin/ 

### GNS3 Serial Bridge

The gns3-serial-bridge.sh script works in conjunction with cisco-send-gns3.py to connect a Cisco device in GNS3 to your local terminal.
How to use:

 + Run ./gns3-serial-bridge.sh as a regular user.
 + You'll be prompted to provide a virtual device file name (default is ~/ttyCisco). Note that if you change the default, you must also update the device_file variable inside cisco-send-gns3.py.
 + Provide the GNS3 device telnet port number when prompted (default is 5000).
 + The script will then execute socat to map the provided telnet port to your virtual device file.
 + Optionally, you'll be asked if you would like to launch screen with 8N1 configuration.

Now the GNS3 device can be treated as a regular serial device - connecting with other terminal programs, or executing the cisco-send-gns3.py script.

### Bash Script

Run the Bash script using the following command:

```bash
chmod +x cisco-send.sh
./cisco-send.sh <input_file>
```

Replace `<input_file>` with the path to the config file.

## Features

### Python Version

- **Asynchronous Reading**: Uses a separate thread to read from the serial port and print syslog messages asynchronously.
- **User Authentication:** Handles username and password authentication if required.
- **Automatic Elevation:** Detects device state and elevates to (config)# mode automatically.
- **Syslog Buffering:** Stores all syslog messages in a buffer.
- **User Prompts:**
      +  Asks if the user wants to print buffered syslog messages to the terminal.
      +  Offers to save running-config to startup-config.
      +  Provides an option to save syslog buffer to a local log file.
- **Asks to write running-config to memory**: Save the new config to startup-config

### Bash Version

- **No External Dependencies**: Doesn't require any additional libraries.
- **No support if require credentials to enter Config# mode**: Start with fresh device, wipe it, or manually enter # prompt prior to running script.
- **No support for printing syslog messages**: No syslog response returned to console due to bash single thread limitations.