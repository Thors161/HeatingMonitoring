Some scripts and 3d models for monitoring a heating installation from a Raspberry Pi. 

The read data is published over MQTT, and some as well to Domoticz. 

The scripts read out:
- All ds18b20 connected temperature sensors to the system. 
- Kamstrup multical 303, using a wired mbus connection.
- Multiple Eastron SDM120 using daisy-chained modbus RS485
- Wilo Yonos Pico circulation pump, that alternates the power and flow on a 7 segment display. Read using the RPi camera. For this also 3d model files are included. 



