import math
import cv2
import numpy as np

def overlay_png(frame, overlay, center):
    """Optimized overlay of RGBA PNG on BGR image at center."""
    h, w, _ = frame.shape
    oh, ow, _ = overlay.shape

    x1 = max(int(center[0] - ow / 2), 0)
    y1 = max(int(center[1] - oh / 2), 0)
    x2 = min(x1 + ow, w)
    y2 = min(y1 + oh, h)

    overlay_x1 = max(0, -int(center[0] - ow / 2))
    overlay_y1 = max(0, -int(center[1] - oh / 2))
    overlay_x2 = overlay_x1 + (x2 - x1)
    overlay_y2 = overlay_y1 + (y2 - y1)

    alpha = overlay[overlay_y1:overlay_y2, overlay_x1:overlay_x2, 3:] / 255.0
    frame[y1:y2, x1:x2] = (1 - alpha) * frame[y1:y2, x1:x2] + alpha * overlay[overlay_y1:overlay_y2, overlay_x1:overlay_x2, :3]

def calculate_rotation_angle(p1, p2):
    """Returns angle in degrees between two points"""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.degrees(math.atan2(dy, dx))


def rotate_with_bounding_box(image, angle):
    """Rotate the image and adjust its bounding box to prevent cropping."""
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)

    # Calculate rotation matrix
    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    # Compute the new bounding dimensions
    cos = abs(M[0, 0])
    sin = abs(M[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    # Adjust the rotation matrix to account for translation
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]

    # Perform the rotation
    rotated = cv2.warpAffine(image, M, (new_w, new_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    return rotated