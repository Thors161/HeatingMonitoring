Some scripts and 3d models for monitoring a heating installation from a Raspberry Pi. 

The read data is published over MQTT (some as well to Domoticz). The MQTT message are consumed by home assistant.

The scripts read out:
- [Multiple ds18b20](./ds18b20) connected temperature sensors to the system. 
- [Kamstrup multical 303](./kamstrup%20multical%20303), using a wired mbus connection.
- [Multiple Eastron SDM120](./eastron%20sdm120c) using daisy-chained modbus RS485
- [Wilo Yonos Pico circulation pump](./wilo%20yonos%20pico), that alternates the power and flow on a 7 segment display. Read using the RPi camera. For this also 3d model files are included. A custom seven segment OCR was implemented for the Wilo LED display as the existing solutions did not work very well. 

Pump in home assistant:

![Wilo hass](./wilo%20yonos%20pico/wilo-home-assistant.png)

Camera on pump:

![Pump](./wilo%20yonos%20pico/wilo-yonos-pico.png)

Heatpump monitor in home assistant:

![Heatpump hass](Home%20assistant/heatpump.png)

