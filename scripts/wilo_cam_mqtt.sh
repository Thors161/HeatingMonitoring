#!/bin/bash
# captures images from the Pi camera (used rev 2.1 NOIR), with the printed custom holder
# publishes the read values to MQTT, both the readings and the images itself

flow_read=false
power_read=false

# Require two readings that are the same, when the display switches the result is a mix
# Ideally two readings from the same display sequence are used as that guarantees the
# display is not transitioning. However pythson startup is too slow for this now (~2.5 sec)
flow_read1=unknown
power_read1=unknown

flow_read2=unknown
power_read2=unknown

max_tries=10
tries=0

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

while [[ $tries -le $max_tries && ("$flow_read" == "false" || "$power_read" == "false") ]]; do

    echo "Reading: $tries"

    rm /tmp/wilo_cap.jpg
    rm /tmp/wilo.jpg
    # Capture images fast (time) to make two reading on the same displayed value,
    # as the image is small this works.
    raspistill -t 100 -o /tmp/wilo_cap.jpg -w 320 -h 240
    convert /tmp/wilo_cap.jpg -crop 144x120+70+110 /tmp/wilo.jpg

    # Input string to check
    #input=`ssocr -D remove_isolated -d -1 -c decimal -a -t 25 --foreground=white --background=black --number-pixels=5 /tmp/wilo.jpg`
    input=`python3 "$SCRIPT_DIR/wiloocr.py" /tmp/wilo.jpg`
    #removes spaces
    input=$(echo "$input" | sed 's/^[ \t]*//;s/[ \t]*$//')
    echo "Wilo: value: \"$input\""


    # Check if the input is a numerical value with a decimal, and between 0.0 and 3.0
    if [[ $input =~ ^[0-9]+\.[0-9]+$ ]]; then  # Check if it contains a dot and is numerical
        # Convert string to a float and check range
        if (( $(echo "$input >= 0.0" | bc -l) && $(echo "$input <= 3.0" | bc -l) )); then

            if [ "$flow_read1" != "unknown" ] && [ "$flow_read2" != "unknown" ]; then
                # two different values in place, and a third one read
                echo "Wilo: Read two different flow values: $flow_read1 $flow_read2"

                if [ "$input" = "$flow_read2" ]; then
                    flow_read1=$input
                    echo "Wilo: Valid flow value 1: $input"
                elif [ "$input" = "$flow_read1" ]; then
                    flow_read2=$input
                    echo "Wilo: Valid flow value 2: $input"
                else
                    # start over
                    flow_read1=unknown
                    flow_read2=unknown
               fi
            fi

            if [ "$flow_read1" = "unknown" ]; then
		flow_read1=$input;
	        echo "Wilo: Valid flow value 1: $input"
            elif [ "$flow_read2" = "unknown" ]; then
                flow_read2=$input;
                echo "Wilo: Valid flow value 2: $input"
            fi

	    if [ "$flow_read1" = "$flow_read2" ]; then
                echo "Wilo: Read two identical flow values: $flow_read1 $flow_read2"
                flow_read=true
            fi
        else
            echo "Wilo: Invalid flow value: $input"
        fi
        cp /tmp/wilo.jpg /tmp/wilo_flow.jpg
    else
        # Check if the input is an integer, does not start with 0, and is between 2 and 75
        if [[ $input =~ ^[1-9][0-9]*$ ]]; then  # Check if it's an integer and doesn't start with 0
            if [ "$input" -ge 2 ] && [ "$input" -le 75 ]; then  # Check if the integer is between 2 and 75

                if [ "$power_read1" != "unknown" ] && [ "$power_read2" != "unknown" ]; then
                    # two different values in place, and a third one read
                    echo "Wilo: Read two different power values: $power_read1 $power_read2"

                    if [ "$input" = "$power_read2" ]; then
                        power_read1=$input
                        echo "Wilo: Valid power value 1: $input"
                    elif [ "$input" = "$power_read1" ]; then
                        power_read2=$input
                        echo "Wilo: Valid power value 2: $input"
                    else
                        # start over
                        power_read1=unknown
                        power_read2=unknown
                   fi
                fi

                if [ "$power_read1" = "unknown" ]; then
                    power_read1=$input;
                    echo "Wilo: Valid power value 1: $input"
                elif [ "$power_read2" = "unknown" ]; then
                    power_read2=$input;
                    echo "Wilo: Valid power value 2: $input"
                fi

                if [ "$power_read1" = "$power_read2" ]; then
                    echo "Wilo: Read two identical power values: $power_read1 $power_read2"
                    power_read=true
                fi
            else
                echo "Wilo: Invalid power value: $input"
            fi
        fi
        cp /tmp/wilo.jpg /tmp/wilo_power.jpg
    fi
    ((tries++))
    #sleep 1
done

if [ "$flow_read" = "false" ]; then
    flow_read1=0
fi

if [ "$power_read" = "false" ]; then
    power_read1=0
fi

echo "Wilo: Publishing values: $flow_read1 $power_read1"

mosquitto_pub -h MQTTBROKER -u USERNAME -P PASSWORD -t /wilo/flow -m "{\"flow_m3_h\":$flow_read1}"
mosquitto_pub -h MQTTBROKER -u USERNAME -P PASSWORD -t /wilo/flow_image -f /tmp/wilo_flow.jpg

mosquitto_pub -h MQTTBROKER -u USERNAME -P PASSWORD -t /wilo/power -m "{\"power_w\":$power_read1}"
mosquitto_pub -h MQTTBROKER -u USERNAME -P PASSWORD -t /wilo/power_image -f /tmp/wilo_power.jpg

