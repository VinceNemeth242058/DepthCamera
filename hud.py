import cv2

def draw_hud(frame):
    text = "Press 'q' to quit"
    cv2.putText(frame, text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
