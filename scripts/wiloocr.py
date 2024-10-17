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

import cv2
import sys

roisd1 = [
    [25,  7, 35, 20],  # a
    [50, 20, 20, 35],  # b
    [50, 60, 20, 35],  # c
    [20, 92, 35, 20],  # d
    [10, 60, 20, 35],  # e
    [10, 20, 20, 35],  # f
    [22, 48, 35, 20],  # g
]

roisd2 = [
    [89,  7, 35, 20],  # a
    [114, 20, 20, 35],  # b
    [114, 60, 20, 35],  # c
    [84, 92, 35, 20],  # d
    [74, 60, 20, 35],  # e
    [74, 20, 20, 35],  # f
    [86, 48, 35, 20],  # g
]

roidot = [62, 96, 20, 20]

segment_min_px_count = 100
dot_min_px_count = 50

def draw_rois(image, rois):
    for roi in rois:
        x, y, w, h = roi
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)

def count_white_pixels_in_roi(thresholded_image, x, y, w, h):
    # Extract the region of interest (ROI)
    roi = thresholded_image[y:y+h, x:x+w]

    # Count white pixels (value 255) in the ROI
    count = cv2.countNonZero(roi)

    return count

#  --a--
# |     |
# f     b
# |     |
#  --g--
# |     |
# e     c
# |     |
#  --d--

def detect_7_segment(a, b, c, d, e, f, g):
    # Define the segment-to-digit mappings
    segment_map = {
        (1, 1, 1, 1, 1, 1, 0): 0,
        (0, 1, 1, 0, 0, 0, 0): 1,
        (1, 1, 0, 1, 1, 0, 1): 2,
        (1, 1, 1, 1, 0, 0, 1): 3,
        (0, 1, 1, 0, 0, 1, 1): 4,
        (1, 0, 1, 1, 0, 1, 1): 5,
        (1, 0, 1, 1, 1, 1, 1): 6,
        (1, 1, 1, 0, 0, 0, 0): 7,
        (1, 1, 1, 1, 1, 1, 1): 8,
        (1, 1, 1, 1, 0, 1, 1): 9
    }

    # Get the tuple of booleans
    segments = (a, b, c, d, e, f, g)

    # Detect the digit based on the segments
    return segment_map.get(segments, "")

def detect_digit(thresholded_image, rois, min_px_count):
    segments = []
    for roi in rois:
        x, y, w, h = roi
        count = count_white_pixels_in_roi(thresholded_image, x, y, w, h)
        segments.append(count > min_px_count)

    a, b, c, d, e, f, g = segments
    return detect_7_segment(a, b, c, d, e, f, g)

def detect_dot(thresholded_image, roi, min_px_count):
    x, y, w, h = roi
    count = count_white_pixels_in_roi(thresholded_image, x, y, w, h)
    return count > min_px_count

def detect_number(imagefile):
    image = cv2.imread(imagefile)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresholded_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    digit1 = detect_digit(thresholded_image, roisd1, segment_min_px_count)
    digit2 = detect_digit(thresholded_image, roisd2, segment_min_px_count)
    dot = detect_dot(thresholded_image, roidot, dot_min_px_count)

    #image = cv2.cvtColor(thresholded_image, cv2.COLOR_GRAY2BGR)

    #draw_rois(image, roisd1)
    #draw_rois(image, roisd2)
    #draw_rois(image, [roidot])

    #cv2.imshow('Image Window', image)
    #cv2.waitKey(0)

    return f"{digit1}{'.' if dot else ''}{digit2}"

if __name__ == "__main__":
    file = sys.argv[1]
    print(detect_number(file))



