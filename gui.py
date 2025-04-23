import tkinter as tk
from tkinter import ttk

def launch_gui(config_flags, runtime_flags_lock):
    def toggle_glasses():
        config_flags["ENABLE_GLASSES"] = not config_flags["ENABLE_GLASSES"]

    def toggle_mustache():
        config_flags["ENABLE_MUSTACHE"] = not config_flags["ENABLE_MUSTACHE"]

    def toggle_advanced():
        if advanced_panel.winfo_ismapped():
            advanced_panel.pack_forget()
        else:
            advanced_panel.pack(pady=10)

    # Create the main window
    win = tk.Tk()
    win.title("AR Filter Settings")
    win.geometry("300x450")

    # Add buttons for toggling filters
    tk.Button(win, text="Toggle Glasses", command=toggle_glasses, width=25).pack(pady=5)
    tk.Button(win, text="Toggle Mustache", command=toggle_mustache, width=25).pack(pady=5)
    tk.Button(win, text="Show/Hide Advanced Settings", command=toggle_advanced).pack(pady=5)

    # Advanced settings panel
    advanced_panel = tk.Frame(win)

    # Camera index dropdown
    tk.Label(advanced_panel, text="Camera Index:").pack()
    cam_indices = list(range(0, 5))
    cam_index_var = tk.IntVar(value=config_flags.get("CAMERA_INDEX", 0))
    cam_dropdown = ttk.Combobox(advanced_panel, values=cam_indices, textvariable=cam_index_var, state="readonly")
    cam_dropdown.pack()

    # Resolution dropdown
    tk.Label(advanced_panel, text="Resolution:").pack()
    resolutions = ["640x480", "1280x720", "1920x1080"]
    resolution_var = tk.StringVar(value=f"{config_flags['FRAME_WIDTH']}x{config_flags['FRAME_HEIGHT']}")
    resolution_dropdown = ttk.Combobox(advanced_panel, values=resolutions, textvariable=resolution_var, state="readonly")
    resolution_dropdown.pack()

    # Max Faces slider
    tk.Label(advanced_panel, text="Max Faces:").pack()
    max_faces_var = tk.IntVar(value=config_flags["MAX_NUM_FACES"])
    tk.Scale(advanced_panel, from_=1, to=5, orient=tk.HORIZONTAL, variable=max_faces_var).pack()

    # Detection confidence slider
    tk.Label(advanced_panel, text="Detection Confidence:").pack()
    detect_conf = tk.DoubleVar(value=config_flags["DETECTION_CONFIDENCE"])
    tk.Scale(advanced_panel, from_=0.1, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, variable=detect_conf).pack()

    # Tracking confidence slider
    tk.Label(advanced_panel, text="Tracking Confidence:").pack()
    track_conf = tk.DoubleVar(value=config_flags["TRACKING_CONFIDENCE"])
    tk.Scale(advanced_panel, from_=0.1, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, variable=track_conf).pack()

    # Apply button to update settings
    def apply_advanced_settings():
        with runtime_flags_lock:
            config_flags["CAMERA_INDEX"] = cam_index_var.get()
            config_flags["MAX_NUM_FACES"] = max_faces_var.get()
            config_flags["DETECTION_CONFIDENCE"] = detect_conf.get()
            config_flags["TRACKING_CONFIDENCE"] = track_conf.get()
            config_flags["REINITIALIZE_CAMERA"] = True

            # Update resolution
            width, height = map(int, resolution_var.get().split("x"))
            config_flags["FRAME_WIDTH"] = width
            config_flags["FRAME_HEIGHT"] = height

    tk.Button(advanced_panel, text="Apply Settings", command=apply_advanced_settings).pack(pady=10)

    # Start the GUI loop
    win.mainloop()