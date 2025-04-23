import cv2
import config
import threading
from gui import launch_gui
from filters.glasses_filter import GlassesFilter
from filters.mustache_filter import MustacheFilter
from detectors.face_mesh_tracker import FaceMeshTracker


# Shared flags dictionary
runtime_flags = {
    "ENABLE_GLASSES": config.ENABLE_GLASSES,
    "ENABLE_MUSTACHE": config.ENABLE_MUSTACHE,
    "CAMERA_INDEX": config.CAMERA_INDEX,
    "FRAME_WIDTH": config.FRAME_WIDTH,
    "FRAME_HEIGHT": config.FRAME_HEIGHT,
    "MAX_NUM_FACES": config.MAX_NUM_FACES,
    "DETECTION_CONFIDENCE": config.DETECTION_CONFIDENCE,
    "TRACKING_CONFIDENCE": config.TRACKING_CONFIDENCE,
    "REINITIALIZE_CAMERA": config.REINITIALIZE_CAMERA,
}
runtime_flags_lock = threading.Lock()
# Start GUI in a separate thread
gui_thread = threading.Thread(target=launch_gui, args=(runtime_flags, runtime_flags_lock,), daemon=True)
gui_thread.start()

# Initialize webcam
cap = cv2.VideoCapture(config.CAMERA_INDEX)

# Main tracker (updated per frame with active filters)
tracker = FaceMeshTracker()

while True:
    # Check for updates to runtime_flags
    with runtime_flags_lock:
        if runtime_flags["REINITIALIZE_CAMERA"]:
            cap.release()
            cap = cv2.VideoCapture(runtime_flags["CAMERA_INDEX"])
            if not cap.isOpened():
                print(f"Error: Could not open camera with index {runtime_flags['CAMERA_INDEX']}.")
                exit(1)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, runtime_flags["FRAME_WIDTH"])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, runtime_flags["FRAME_HEIGHT"])
            runtime_flags["REINITIALIZE_CAMERA"] = False  # Reset the flag

    # Read frame from webcam
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Dynamically update active filters
    filters = []
    if runtime_flags["ENABLE_GLASSES"]:
        filters.append(GlassesFilter())
    if runtime_flags["ENABLE_MUSTACHE"]:
        filters.append(MustacheFilter())
    tracker.filters = filters

    # Process frame
    frame = tracker.process_frame(rgb, frame)

    # Display frame
    cv2.imshow("AR Filter", frame)

    key = cv2.waitKey(1) & 0xFF
    if cv2.getWindowProperty("AR Filter", cv2.WND_PROP_VISIBLE) < 1 or key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()