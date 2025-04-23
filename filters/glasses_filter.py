import cv2
import numpy as np
from filters.base_filter import BaseFilter
from utils.drawing import calculate_rotation_angle
from utils.drawing import rotate_with_bounding_box
from utils.drawing import overlay_png

class GlassesFilter(BaseFilter):
    def __init__(self):
        self.image = cv2.imread('C:/Users/nemev/Coding/Projects/RealSenseChallenge/filters/assets/glasses.png', cv2.IMREAD_UNCHANGED)

    def apply(self, frame, landmarks, image_shape, precomputed):
        glasses_center = precomputed["eyes"]
        h, w, _ = image_shape

        left_eye = landmarks[159]
        right_eye = landmarks[386]

        p1 = (int(left_eye.x * w), int(left_eye.y * h))
        p2 = (int(right_eye.x * w), int(right_eye.y * h))

        # Determine angle and size
        angle = -calculate_rotation_angle(p1, p2)
        width = int(abs(p2[0] - p1[0]) * 2)
        overlay = cv2.resize(self.image, (width, int(width / 3)))

        # Rotate overlay
        overlay = rotate_with_bounding_box(overlay, angle)

        overlay_png(frame, overlay, glasses_center)