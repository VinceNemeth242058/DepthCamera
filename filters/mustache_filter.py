import cv2
import numpy as np
from filters.base_filter import BaseFilter
from utils.drawing import calculate_rotation_angle
from utils.drawing import rotate_with_bounding_box
from utils.drawing import overlay_png

class MustacheFilter(BaseFilter):
    def __init__(self):
        self.image = cv2.imread('C:/Users/nemev/Coding/Projects/RealSenseChallenge/filters/assets/moustache.png', cv2.IMREAD_UNCHANGED)

    def apply(self, frame, landmarks, image_shape, precomputed):
        mouth_center = precomputed["mouth"]
        h, w, _ = image_shape

        left_eye = landmarks[159]
        right_eye = landmarks[386]

        # Points to calculate
        eye1 = (int(left_eye.x * w), int(left_eye.y * h))
        eye2 = (int(right_eye.x * w), int(right_eye.y * h))

        # Rotation angle
        angle = -calculate_rotation_angle(eye1, eye2)

        # Resize filter
        width = int(abs(eye2[0] - eye1[0]) * 1.3)
        overlay = cv2.resize(self.image, (width, int(width / 2)))

        # Rotate PNG
        overlay = rotate_with_bounding_box(overlay, angle)

        # Overlay on frame
        overlay_png(frame, overlay, mouth_center)