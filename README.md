# postoolspy
Global positioning solutions using combined GNSS and IMU. This helps synchronize GPS and IMU data for geospatial data acquisition.

## Scripts
To use scripts, you must run the following command in order from the project directory
- pip install -e .

This allows you call call scripts from the terminal

## Supported Interfaces
- USB/UART
- NTRIP
- Mission Planner MAVLINK Server (Coming soon)

## Supported Hardware

### RTK GNSS
1) u-blox 
    - ZED-F9P
    - NEO-M8P
2) Locosys
    - RTK1612-EVK
3) NMEA over USB

### IMU
1) Vectornav
    - 100

### SLAM
1) None
