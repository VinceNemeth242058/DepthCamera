# AR Filter Application

A real-time augmented reality filter application built with Python, OpenCV, and MediaPipe. This application allows users to apply virtual accessories like glasses and mustaches to faces detected through a webcam feed.

![AR Filter Demo](https://via.placeholder.com/800x450.png?text=AR+Filter+Demo)

## Features

- Real-time face tracking using MediaPipe's Face Mesh
- Customizable AR filters (glasses, mustache)
- Interactive GUI for toggling filters and adjusting settings
- Multi-threaded architecture for responsive performance
- Extensible filter system for creating custom effects

## Requirements

- Python 3.6+
- OpenCV (`cv2`)
- MediaPipe (`mediapipe`)
- Tkinter (`tkinter`) for GUI
- NumPy (`numpy`)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/VinceNemeth242058/DepthCamera.git
   cd DepthCamera
   ```

2. Install the required dependencies:
   ```bash
   pip install opencv-python mediapipe numpy
   ```

3. Ensure you have the filter assets in the correct location:
   - Place glasses image at `filters/assets/glasses.png`
   - Place mustache image at `filters/assets/moustache.png`

## Usage

### Running the Application

Run the main application:

```bash
python main.py
```

The application will start with a webcam feed showing detected faces and any enabled filters. A control GUI will also appear allowing you to toggle filters and adjust settings.

### Controls

- From the GUI:
  - Toggle Glasses: Apply virtual glasses to detected faces
  - Toggle Mustache: Apply virtual mustache to detected faces
  - Show/Hide Advanced Settings: Access camera and detection settings
  
- Keyboard shortcuts in the video window:
  - `q`: Quit the application

### Advanced Settings

- Camera Index: Select which camera to use (0-4)
- Resolution: Choose from preset resolutions
- Max Faces: Set the maximum number of faces to detect (1-5)
- Detection Confidence: Adjust the face detection sensitivity
- Tracking Confidence: Adjust the face tracking reliability

## Architecture Overview

### Main Components

1. **Face Detection and Tracking** (`detectors/face_mesh_tracker.py`)
   - Uses MediaPipe Face Mesh to detect and track facial landmarks
   - Provides key facial feature positions to filters

2. **Filter System** (`filters/base_filter.py`, `filters/glasses_filter.py`, etc.)
   - Abstract base class defining filter interface
   - Concrete implementations for specific effects

3. **GUI** (`gui.py`)
   - Settings interface built with Tkinter
   - Controls filter activation and camera settings

4. **Main Application** (`main.py`)
   - Orchestrates camera input, processing, and display
   - Manages threading between GUI and processing

### Threading Model

The application uses a multi-threaded architecture:
- Main thread: Camera capture, face detection, and filter application
- GUI thread: User interface for adjusting settings

## How It Works

### Face Mesh Detection

The application uses MediaPipe's Face Mesh to detect 468 facial landmarks in real-time. Here's how the face detection works:

```python
# From detectors/face_mesh_tracker.py
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
```

The `FaceMeshTracker` processes each frame from the webcam:

```python
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
```

### Filter System

Filters inherit from the `BaseFilter` class and implement the `apply` method:

```python
# From filters/base_filter.py
class BaseFilter:
    def apply(self, frame, landmarks, image_shape):
        """Override in subclasses to apply effect."""
        raise NotImplementedError("Filter must implement apply() method.")
```

The glasses filter overlays PNG glasses on the face, aligned with the eyes:

```python
# From filters/glasses_filter.py
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
```

### Dynamic Configuration

The application uses a shared configuration dictionary that can be updated via the GUI:

```python
# From main.py
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
```

## Creating Custom Filters

You can extend the application with your own custom filters by following these steps:

1. Create a new file in the `filters` directory, e.g., `filters/my_custom_filter.py`

2. Implement your filter class by inheriting from `BaseFilter`:

```python
from filters.base_filter import BaseFilter
import cv2

class MyCustomFilter(BaseFilter):
    def __init__(self):
        # Load any resources you need
        self.image = cv2.imread('path/to/your/asset.png', cv2.IMREAD_UNCHANGED)
        
    def apply(self, frame, landmarks, image_shape, precomputed):
        # Your filter implementation here
        # You can use the precomputed positions like precomputed["eyes"]
        # Or access specific landmarks like landmarks[0], landmarks[1], etc.
        
        # Example: Add a simple colored circle around the nose
        nose_tip = landmarks[4]  # Nose tip landmark index
        h, w, _ = image_shape
        nose_x = int(nose_tip.x * w)
        nose_y = int(nose_tip.y * h)
        
        cv2.circle(frame, (nose_x, nose_y), 20, (0, 255, 0), 2)
```

3. Update `main.py` to include your new filter:

```python
from filters.my_custom_filter import MyCustomFilter

# In the main loop, add your filter to the filters list:
filters = []
if runtime_flags["ENABLE_GLASSES"]:
    filters.append(GlassesFilter())
if runtime_flags["ENABLE_MUSTACHE"]:
    filters.append(MustacheFilter())
# Add your custom filter
filters.append(MyCustomFilter())
```

4. Optionally, add a toggle to the GUI in `gui.py`:

```python
def toggle_custom_filter():
    config_flags["ENABLE_CUSTOM_FILTER"] = not config_flags["ENABLE_CUSTOM_FILTER"]

# Add button to the GUI
tk.Button(win, text="Toggle Custom Filter", command=toggle_custom_filter, width=25).pack(pady=5)
```

### Understanding Key Face Landmarks

MediaPipe Face Mesh provides 468 facial landmarks. Here are some key landmark indices used in this application:

- Eyes:
  - Left eye: landmarks 159 (upper) and 145 (lower)
  - Right eye: landmarks 386 (upper) and 374 (lower)
- Mouth:
  - Upper lip: landmark 13
  - Lower lip: landmark 14

## Utility Functions

The application includes several utility functions for image processing:

### Image Overlay

The `overlay_png` function efficiently overlays a PNG image with transparency onto a frame:

```python
# From utils/drawing.py
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
```

### Image Rotation

The `rotate_with_bounding_box` function rotates an image while maintaining its visible content:

```python
# From utils/drawing.py
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
```

## Configuration

Default application settings are stored in `config.py`:

```python
# Feature Toggles
USE_FACE_MESH = True
USE_HUD = True

# Filter Toggles
ENABLE_GLASSES = False
ENABLE_MUSTACHE = False

# Webcam / Camera Settings
CAMERA_INDEX = 1
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Mediapipe Settings
MAX_NUM_FACES = 1
DETECTION_CONFIDENCE = 0.5
TRACKING_CONFIDENCE = 0.5
REINITIALIZE_CAMERA = False
```

## Troubleshooting

### Camera Issues
- If the camera doesn't open, check that the camera index is correct
- Some webcams don't support certain resolutions; try a lower resolution

### Performance Issues
- Reduce MAX_NUM_FACES to improve performance
- Lower the resolution in the advanced settings
- Ensure your system meets the minimum requirements

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [MediaPipe](https://google.github.io/mediapipe/) for the face mesh detection
- [OpenCV](https://opencv.org/) for image processing capabilities
