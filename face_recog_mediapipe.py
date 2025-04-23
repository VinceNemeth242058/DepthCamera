import cv2
import mediapipe as mp

# Init MediaPipe components
mp_face_detection = mp.solutions.face_detection
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

# Webcam
cap = cv2.VideoCapture(1)

# Toggle states
show_boxes = True
show_mesh = False

# FaceMesh config
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=5,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def get_eye_positions(landmarks, image_shape):
    h, w, _ = image_shape

    # Left Eye
    left_top = landmarks[159]
    left_bottom = landmarks[145]
    left_eye_x = int((left_top.x + left_bottom.x) / 2 * w)
    left_eye_y = int((left_top.y + left_bottom.y) / 2 * h)

    # Right Eye
    right_top = landmarks[386]
    right_bottom = landmarks[374]
    right_eye_x = int((right_top.x + right_bottom.x) / 2 * w)
    right_eye_y = int((right_top.y + right_bottom.y) / 2 * h)

    return (left_eye_x, left_eye_y), (right_eye_x, right_eye_y)


def get_mouth_position(landmarks, image_shape):
    h, w, _ = image_shape

    upper_lip = landmarks[13]
    lower_lip = landmarks[14]
    mouth_x = int((upper_lip.x + lower_lip.x) / 2 * w)
    mouth_y = int((upper_lip.y + lower_lip.y) / 2 * h)

    return (mouth_x, mouth_y)

# FaceDetection config
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # HUD text
    hud = "Press 'q' to quit | '1' toggle mesh | '2' toggle box"
    cv2.putText(frame, hud, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Show bounding boxes
    if show_boxes:
        results_box = face_detection.process(rgb)
        if results_box.detections:
            for detection in results_box.detections:
                mp_drawing.draw_detection(frame, detection)

    # Show mesh
    if show_mesh:
        results_mesh = face_mesh.process(rgb)
        if results_mesh.multi_face_landmarks:
            for face_landmarks in results_mesh.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_styles.get_default_face_mesh_tesselation_style()
                )

                eye_left, eye_right = get_eye_positions(face_landmarks.landmark, frame.shape)
                mouth = get_mouth_position(face_landmarks.landmark, frame.shape)

                # Draw them
                cv2.circle(frame, eye_left, 5, (0, 255, 255), -1)
                cv2.circle(frame, eye_right, 5, (0, 255, 255), -1)
                cv2.circle(frame, mouth, 5, (255, 0, 255), -1)

    cv2.imshow('MediaPipe Face Detection + Mesh', frame)

    key = cv2.waitKey(1) & 0xFF
    if cv2.getWindowProperty('MediaPipe Face Detection + Mesh', cv2.WND_PROP_VISIBLE) < 1:
        break
    elif key == ord('q'):
        break
    elif key == ord('1'):
        show_mesh = not show_mesh
    elif key == ord('2'):
        show_boxes = not show_boxes


cap.release()
cv2.destroyAllWindows()
face_mesh.close()
face_detection.close()
