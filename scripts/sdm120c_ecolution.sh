#!/bin/bash
# Reads data from an Eastron SDM120 power meter, and publishes the values to MQTT (and domoticz)

DOMOTICZ="http://127.0.0.1:8080/json.htm?type=command"

values=`sudo sdm120c -a 1 -b 9600 -z 10 -w 5 -j 1 -i -p -v -c -P N -q /dev/ttyUSB1`

echo ${values}

V=`echo ${values} | awk '{print $1}'`
A=`echo ${values} | awk '{print $2}'`
W=`echo ${values} | awk '{print $3}'`
WH=`echo ${values} | awk '{print $4}'`

TS=$(date +%s)

# Only upload W and T if both W and T are not empty or "NOK"
if [[ -n $W ]] && [[ $WH -gt "1" ]] && [[ NOK != $WH ]]; then
#echo Valid read
curl -s "${DOMOTICZ}&param=udevice&idx=33&nvalue=0&svalue=$W;$WH"
mosquitto_pub -h MQTTBROKER -u USERNAME -P PASSWORD -t /sdm120/electricity_ecolution -m "{\"power\":$W,\"energy\":$WH,\"voltage\":$V,\"current\":$A,\"update_timestamp\":$TS}"
else
echo  Invalid read
curl -s "${DOMOTICZ}&param=addlogmessage&message=Error+reading+Eastron+kWh+meter.+Values+skipped!"
fi

curl -s "${DOMOTICZ}&param=addlogmessage&message=SDM120C"


