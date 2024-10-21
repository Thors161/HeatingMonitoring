#!/bin/bash
# based on: https://forums.raspberrypi.com/viewtopic.php?t=63085 
# a script to read and save temperature readings from all the group 28 1-wire temperature sensors
# and publishes to MQTT 
#
# get all devices in the '28' family

TS=$(date +%s)

FILES=`ls /sys/bus/w1/devices/w1_bus_master1/ | grep '^28'`
# iterate through all the devices
for file in $FILES
    do
      # get the 2 lines of the response from the device
      GETDATA=`cat /sys/bus/w1/devices/w1_bus_master1/$file/w1_slave`
      GETDATA1=`echo "$GETDATA" | grep crc`
      GETDATA2=`echo "$GETDATA" | grep t=`
      # get temperature
      TEMP=`echo $GETDATA2 | sed -n 's/.*t=//;p'`
      #TEMPC=$(bc <<< "scale=2;$TEMP/1000") 
      TEMPC=$(echo|awk "{printf \"%.2f\",$TEMP/1000}")  
      #
        # test if crc is 'YES' and temperature is not -62 or +85
        if [ `echo $GETDATA1 | sed 's/^.*\(...\)$/\1/'` == "YES" -a $TEMP != "-62" -a $TEMP != "85000"  ]
           then
               # crc is 'YES' and temperature is not -62 or +85 - so save result
               mosquitto_pub -h MQTTBROKER -u USERNAME -P PASSWORD -t /ds18b20/set1/$file -m "{\"temp\":$TEMPC}"
               echo $TEMPC
               #echo `date +"%d-%m-%Y %H:%M:%S "; echo $GETDATA2 | sed -n 's/.*t=//;p'` >> /var/1w_files/$file
           else
               # there was an error (crc not 'yes' or invalid temperature)
               echo "error" $FILE   
        fi
    done
    mosquitto_pub -h MQTTBROKER -u USERNAME -P PASSWORD -t /ds18b20/set1/updated -m "{\"update_timestamp\":$TS}"
exit 0
