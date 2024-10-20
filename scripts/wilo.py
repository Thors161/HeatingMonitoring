# MIT License
#
# Copyright (c) 2024 Thors161
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#    1. The above copyright notice and this permission notice shall be included
#       in all copies or substantial portions of the Software.
#
#    2. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#       OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#       MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#       IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#       CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#       TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#       SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from wilo_mqttbroker import MQTT_HOST, MQTT_USERNAME, MQTT_PASSWORD
from wilo_ssocr import WiloSsocr
import os
import subprocess
import cv2

#  --a--
# |     |
# f     b
# |     |
#  --g--
# |     |
# e     c
# |     |
#  --d--
rois_digit1 = [
    [25, 7, 35, 20],  # a
    [50, 20, 20, 35],  # b
    [50, 60, 20, 35],  # c
    [20, 92, 35, 20],  # d
    [10, 60, 20, 35],  # e
    [10, 20, 20, 35],  # f
    [22, 48, 35, 20],  # g
]

rois_digit2 = [
    [89, 7, 35, 20],  # a
    [114, 20, 20, 35],  # b
    [114, 60, 20, 35],  # c
    [84, 92, 35, 20],  # d
    [74, 60, 20, 35],  # e
    [74, 20, 20, 35],  # f
    [86, 48, 35, 20],  # g
]

roi_dot = [62, 96, 20, 20]

segment_min_px_count = 100
dot_min_px_count = 50

crop_x, crop_y = 70, 110
crop_width, crop_height = 144, 120

capture_file = "/tmp/wilo_cap.jpg"
flow_file = "/tmp/wilo_flow.jpg"
power_file = "/tmp/wilo_power.jpg"

draw_ssocr_regions = True

# Require two readings that are the same, when the display switches the result is a mix
# Ideally two readings from the same display sequence are used as that guarantees the
# display is not transitioning. However python startup is too slow for this now (~2.5 sec)

flow_read = False
power_read = False

flow_read1 = "unknown"
flow_read2 = "unknown"

power_read1 = "unknown"
power_read2 = "unknown"

max_tries = 10
tries = 0

max_empty_reads = 3
empty_reads = 0

wilo_ssocr = WiloSsocr(rois_digit1, rois_digit2, roi_dot, segment_min_px_count, dot_min_px_count)

while tries < max_tries and (not flow_read or not power_read):
    print(f"Wilo: reading {tries}")

    if os.path.exists(capture_file):
        os.remove(capture_file)

    command = [
        "raspistill",
        "-t", "500",
        "-w", "320",
        "-h", "240",
        "-o", capture_file
    ]

    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"Wilo: cannot capture: {result.returncode}")
        exit(-1)

    image = cv2.imread(capture_file)
    cropped_image = image[crop_y:crop_y + crop_height, crop_x:crop_x + crop_width]

    text = wilo_ssocr.detect_number(cropped_image, draw_ssocr_regions);

    if text:
        # flow contains a dot
        if '.' in text:
            value = float(text)
            if 0.0 <= value <= 3.0:
                # valid flow value

                if flow_read1 != "unknown" and flow_read2 != "unknown" and flow_read1 != flow_read2:
                    print(f"Wilo: Read two different flow values: {flow_read1} {flow_read2}")

                    if text is flow_read2:
                        flow_read1 = text
                    elif text is flow_read1:
                        flow_read2 = text
                    else:
                        # start over
                        flow_read1 = "unknown"
                        flow_read2 = "unknown"

                if flow_read1 == "unknown":
                    flow_read1 = text
                    print(f"Wilo: Valid flow value 1: {flow_read1}")
                elif flow_read2 == "unknown":
                    flow_read2 = text
                    print(f"Wilo: Valid flow value 2: {flow_read2}")

                if flow_read1 == flow_read2:
                    print(f"Wilo: Read two identical flow values: {flow_read1}")
                    flow_read = True
            else:
                print(f"Wilo: Invalid flow value: {text}")

            cv2.imwrite(flow_file, cropped_image)
        else:
            value = int(text)
            if 2 <= value <= 75:
                # valid power value

                if power_read1 != "unknown" and power_read2 != "unknown" and power_read1 != power_read2:
                    print(f"Wilo: Read two different power values: {power_read1} {power_read2}")

                    if text == power_read2:
                        power_read1 = text
                    elif text == power_read1:
                        power_read2 = text
                    else:
                        # start over
                        power_read1 = "unknown"
                        power_read2 = "unknown"

                if power_read1 == "unknown":
                    power_read1 = text
                    print(f"Wilo: Valid power value 1: {power_read1}")
                elif power_read2 == "unknown":
                    power_read2 = text
                    print(f"Wilo: Valid power value 2: {power_read2}")

                if power_read1 == power_read2:
                    print(f"Wilo: Read two identical power values: {power_read1}")
                    power_read = True
            else:
                print(f"Wilo: Invalid power value: {text}")

            cv2.imwrite(power_file, cropped_image)
    else:
        # empty read, pump off
        empty_reads += 1
        if empty_reads == max_empty_reads:
            print(f"Wilo: off")
            flow_read = True
            flow_read1 = 0
            power_read = True
            power_read1 = 0

            cv2.imwrite(flow_file, cropped_image)
            cv2.imwrite(power_file, cropped_image)

    tries += 1

if not flow_read:
    flow_read1 = "0.0"

if not power_read:
    power_read1 = "0"

print(f"Wilo: Publishing values: {flow_read1} {power_read1}")

command = [
    "mosquitto_pub",
    "-h", MQTT_HOST,
    "-u", MQTT_USERNAME,
    "-P", MQTT_PASSWORD,
    "-t", "/wilo/flow",
    "-m", f"{{\"flow_m3_h\":{flow_read1}}}\""
]
result = subprocess.run(command)

command = [
    "mosquitto_pub",
    "-h", MQTT_HOST,
    "-u", MQTT_USERNAME,
    "-P", MQTT_PASSWORD,
    "-t", "/wilo/flow_image",
    "-f", flow_file
]
result = subprocess.run(command)

command = [
    "mosquitto_pub",
    "-h", MQTT_HOST,
    "-u", MQTT_USERNAME,
    "-P", MQTT_PASSWORD,
    "-t", "/wilo/power",
    "-m", f"{{\"power_w\":{power_read1}}}\""
]
result = subprocess.run(command)

command = [
    "mosquitto_pub",
    "-h", MQTT_HOST,
    "-u", MQTT_USERNAME,
    "-P", MQTT_PASSWORD,
    "-t", "/wilo/power_image",
    "-f", power_file
]
result = subprocess.run(command)
