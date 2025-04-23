import cv2
import mediapipe as mp
import config

class FaceMeshTracker:
    def __init__(self, filters=None):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=config.MAX_NUM_FACES,
        refine_landmarks=True,
        min_detection_confidence=config.DETECTION_CONFIDENCE,
        min_tracking_confidence=config.TRACKING_CONFIDENCE
        )
        self.filters = filters if filters else []

    def process_frame(self, rgb_frame, display_frame):
        results = self.face_mesh.process(rgb_frame)
        if results.multi_face_landmarks:
            for landmarks in results.multi_face_landmarks:
                precomputed = {
                    "eyes": self.get_eye_positions(landmarks.landmark, display_frame.shape),
                    "mouth": self.get_mouth_position(landmarks.landmark, display_frame.shape),
                }
                for f in self.filters:
                    f.apply(display_frame, landmarks.landmark, display_frame.shape, precomputed)
        return display_frame

    def get_eye_positions(self, landmarks, image_shape):
        """Calculate the midpoint between the eyes."""
        h, w, _ = image_shape
        left_y = int((landmarks[159].y + landmarks[145].y) / 2 * h)
        left_x = int((landmarks[159].x + landmarks[145].x) / 2 * w)
        right_y = int((landmarks[386].y + landmarks[374].y) / 2 * h)
        right_x = int((landmarks[386].x + landmarks[374].x) / 2 * w)
        # Return the midpoint between the eyes
        center_x = (left_x + right_x) // 2
        center_y = (left_y + right_y) // 2
        return (center_x, center_y)

    def get_mouth_position(self, landmarks, image_shape):
        h, w, _ = image_shape
        x = int((landmarks[13].x + landmarks[14].x) / 2 * w)
        y = int((landmarks[13].y + landmarks[14].y) / 2 * h)
        return (x, y)