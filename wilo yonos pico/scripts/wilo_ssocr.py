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


class WiloSsocr:

    def __init__(self, rois_digit1, rois_digit2, roi_dot, segment_min_px_count, dot_min_px_count):
        self.rois_digit1 = rois_digit1

        self.rois_digit2 = rois_digit2

        self.roi_dot = roi_dot

        self.segment_min_px_count = segment_min_px_count
        self.dot_min_px_count = dot_min_px_count

        #  --a--
        # |     |
        # f     b
        # |     |
        #  --g--
        # |     |
        # e     c
        # |     |
        #  --d--
        self._segment_map = {
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

        self._overlay_color_roi_true = (0, 255, 0)
        self._overlay_color_roi_false = (0, 0, 255)
        self._overlay_alpha = 0.2

    def _segment_list(self, digit):
        for key, value in self._segment_map.items():
            if value == digit:
                return key

        return [0, 0, 0, 0, 0, 0, 0]

    def _draw_rois_digit(self, image, rois, digit):
        overlay = image.copy()

        for index, roi in enumerate(rois):
            x, y, w, h = roi
            key = self._segment_list(digit)
            if key[index]:
                cv2.rectangle(image, (x, y), (x + w, y + h), self._overlay_color_roi_true, 1)
            else:
                cv2.rectangle(image, (x, y), (x + w, y + h), self._overlay_color_roi_false, 1)

        cv2.addWeighted(overlay, self._overlay_alpha, image, 1 - self._overlay_alpha, 0, image)

    def _draw_roi_dot(self, image, roi, dot):
        overlay = image.copy()

        x, y, w, h = roi
        if dot:
            cv2.rectangle(image, (x, y), (x + w, y + h), self._overlay_color_roi_true, 1)
        else:
            cv2.rectangle(image, (x, y), (x + w, y + h), self._overlay_color_roi_false, 1)

        cv2.addWeighted(overlay, self._overlay_alpha, image, 1 - self._overlay_alpha, 0, image)

    def _detect_7_segment(self, a, b, c, d, e, f, g):
        segments = (a, b, c, d, e, f, g)
        return self._segment_map.get(segments, "")

    @staticmethod
    def _count_white_pixels_in_roi(threshold_image, x, y, w, h):
        roi = threshold_image[y:y + h, x:x + w]
        count = cv2.countNonZero(roi)
        return count

    def _detect_digit(self, threshold_image, rois, min_px_count):
        segments = []
        for roi in rois:
            x, y, w, h = roi
            count = self._count_white_pixels_in_roi(threshold_image, x, y, w, h)
            segments.append(count > min_px_count)

        a, b, c, d, e, f, g = segments
        return self._detect_7_segment(a, b, c, d, e, f, g)

    @staticmethod
    def _detect_dot(threshold_image, roi, min_px_count):
        x, y, w, h = roi
        count = WiloSsocr._count_white_pixels_in_roi(threshold_image, x, y, w, h)
        return count > min_px_count

    def detect_number(self, image, draw_rois):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, threshold_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)

        digit1 = self._detect_digit(threshold_image, self.rois_digit1, self.segment_min_px_count)
        digit2 = self._detect_digit(threshold_image, self.rois_digit2, self.segment_min_px_count)
        dot = self._detect_dot(threshold_image, self.roi_dot, self.dot_min_px_count)

        if draw_rois:
            self._draw_rois_digit(image, self.rois_digit1, digit1)
            self._draw_roi_dot(image, self.roi_dot, dot)
            self._draw_rois_digit(image, self.rois_digit2, digit2)

        # cv2.imshow('Image Window', threshold_image)
        # cv2.waitKey(0)

        return f"{digit1}{'.' if dot else ''}{digit2}"
