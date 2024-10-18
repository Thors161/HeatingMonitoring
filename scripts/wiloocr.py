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

#  --a--
# |     |
# f     b
# |     |
#  --g--
# |     |
# e     c
# |     |
#  --d--
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

overlay_color_roi_true = (0, 255, 0)
overlay_color_roi_false = (0, 0, 255)
overlay_alpha = 0.2


def segment_list(digit):
    for key, value in segment_map.items():
        if value == digit:
            return key

    return [0, 0, 0, 0, 0, 0, 0]


def draw_rois_digit(image, rois, digit):
    overlay = image.copy()

    for index, roi in enumerate(rois):
        x, y, w, h = roi
        key = segment_list(digit)
        if key[index]:
            cv2.rectangle(image, (x, y), (x + w, y + h), overlay_color_roi_true, 1)
        else:
            cv2.rectangle(image, (x, y), (x + w, y + h), overlay_color_roi_false, 1)

    cv2.addWeighted(overlay, overlay_alpha, image, 1 - overlay_alpha, 0, image)


def draw_roi_dot(image, roi, dot):
    overlay = image.copy()

    x, y, w, h = roi
    if dot:
        cv2.rectangle(image, (x, y), (x + w, y + h), overlay_color_roi_true, 1)
    else:
        cv2.rectangle(image, (x, y), (x + w, y + h), overlay_color_roi_false, 1)

    cv2.addWeighted(overlay, overlay_alpha, image, 1 - overlay_alpha, 0, image)


def count_white_pixels_in_roi(threshold_image, x, y, w, h):
    roi = threshold_image[y:y + h, x:x + w]
    count = cv2.countNonZero(roi)
    return count


def detect_7_segment(a, b, c, d, e, f, g):
    segments = (a, b, c, d, e, f, g)
    return segment_map.get(segments, "")


def detect_digit(threshold_image, rois, min_px_count):
    segments = []
    for roi in rois:
        x, y, w, h = roi
        count = count_white_pixels_in_roi(threshold_image, x, y, w, h)
        segments.append(count > min_px_count)

    a, b, c, d, e, f, g = segments
    return detect_7_segment(a, b, c, d, e, f, g)


def detect_dot(threshold_image, roi, min_px_count):
    x, y, w, h = roi
    count = count_white_pixels_in_roi(threshold_image, x, y, w, h)
    return count > min_px_count


def detect_number(image_file, draw_regions):
    image = cv2.imread(image_file)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, threshold_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    digit1 = detect_digit(threshold_image, rois_digit1, segment_min_px_count)
    digit2 = detect_digit(threshold_image, rois_digit2, segment_min_px_count)
    dot = detect_dot(threshold_image, roi_dot, dot_min_px_count)

    if draw_regions:
        draw_rois_digit(image, rois_digit1, digit1)
        draw_roi_dot(image, roi_dot, dot)
        draw_rois_digit(image, rois_digit2, digit2)

        cv2.imwrite(image_file, image)

    # cv2.imshow('Image Window', image)
    # cv2.waitKey(0)

    cv2.imwrite(image_file, image)

    return f"{digit1}{'.' if dot else ''}{digit2}"


if __name__ == "__main__":
    draw_regions = True
    file = sys.argv[1]
    print(detect_number(file, draw_regions))

