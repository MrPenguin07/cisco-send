<p align="center">
  <img src="https://github.com/MrPenguin07/cisco-send/assets/127086564/afb724e9-8302-41f9-a461-0057d2348ed3" alt="cisco-send-128x128" />
</p>

<h1 align="center">
  Cisco-send scripts
</h1>


Send a local config to Cisco device over serial/console connection. 

These scripts were created as an alternative to the cumbersome tftp and xmodem etc methods of sending configs.  
Copy pasting a config directly usually works for smaller configs however at a certain point configs are too large - data is sent too quickly and the device chokes, causing errors in the final config.  

Herein lies the simplicity of automation by script - read a local config and send it to the device, with a configurable delay between lines to prevent errors.  
This method does not require setting up an IP on the device for TFTP, an FTP server running on your end device - or xmodem voodoo magic sending data over 9600 baud prior to configuring a device.  

**Rapid deployment; wipe and send.**

This repository contains both an advanced multi-threaded asynchronous python - and a simple Bash version of the script.

#### TO-DO 
- [ ] add SSH & possibly telnet support
- [ ] ask user to pull current config and write locally as backup
- [ ] support wiping device to clean state prior to sending config
- [ ] sanitize log file strings for cleaner output (\b, \r etc.)
- [ ] handle keyboard interrupts & exception handling when --device-file invalid
  
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
```
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
```
- **`cisco-send.py`**: Python script for sending config files to running-config.

- **`cisco-send-gns3.py`**: GNS3 version of the script, send configs into virtual devices.
- **`gns3-serial-bridge.sh`**: Used in conjunction with cisco-send-gns3.py. Maps telnet port to device file.

- **`requirements.txt`**: Lists Python packages required for the Python version.
- **`cisco-send.sh`**: Bash script for sending config files to running-config.

## Usage

### Python Script

```
usage: cisco-send.py [-h] [--device-file DEVICE_FILE] [--delay DELAY] input_file

Send a local config to a device over a serial/console connection.

positional arguments:
  input_file            Path to the config file for the Cisco device (Router/Switch).

options:
  -h, --help            show this help message and exit
  --device-file DEVICE_FILE
                        Path to device file. Default is --device-file /dev/ttyUSB0
  --delay DELAY         Delay between sending lines, in seconds. Default is --delay 0.2s
```

Confirm your device file, default is set to `/dev/ttyUSB0`  
  + `DEFAULT_DEVICE_FILE` and `DEFAULT_DELAY` variables can be set permanently inside script.
  + **--device-file** and **--delay** are optional and override the defaults.

#### Install dependencies;  
`pip install -r requirements.txt` || `<your-pkg-manager> install pyserial`

#### Run script;
```bash
python3 cisco-send.py <input_file>
```

Replace `<input_file>` with the path to the config file for the cisco device (Router/Switch)  


You'll likely want to add the script to your `$PATH` ie. ~/.local/bin/ 

### GNS3 Serial Bridge

The gns3-serial-bridge.sh script works in conjunction with cisco-send-gns3.py to connect a Cisco device in GNS3 to a local device file, similar to a regular serial connection to `/dev/ttyUSB0` etc.
How to use:

 + Start your Switch/Router device in GNS3. Right-click, select 'show node information'.  
   Note the line `Console is on port 5000 and type is telnet`
 + Run ./gns3-serial-bridge.sh as a regular user.
 + You'll be prompted to provide a virtual device file name (default is ~/ttyCisco).  
   (Note that if you change the default, you must also update the DEFAULT_DEVICE_FILE variable inside cisco-send-gns3.py)
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

- **Asynchronous Reading**: Uses a separate thread to read from the serial port and print syslog messages.
- **User Authentication:** Detects & then handles password authentication if required.
- **Automatic Elevation:** Detects device state and elevates to (config)# mode automatically.
- **Syslog Buffering:** Stores all syslog messages in a buffer.
- **User Prompts:**
  +  Asks if the user wants to print buffered syslog messages to the terminal.
  +  Offers to save running-config to startup-config.
  +  Provides an option to save syslog buffer to a local log file.
- **Asks to write running-config to memory**: Save the new config to startup-config
- **Command line switches**: to override default `--device-file` and `--delay`

### Bash Version

- **No External Dependencies**: Doesn't require any additional libraries.
- **No support if require credentials to enter Config# mode**: Start with fresh device, wipe it, or manually enter # prompt prior to running script.
- **No support for printing syslog messages**: No syslog response returned to console due to bash single thread limitations.
