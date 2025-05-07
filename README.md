# EYEMOUSE
````markdown
# Eye & Voice-Controlled Mouse Interface

This Python project allows users to control their mouse using eye movements (via webcam) and voice commands. Built using `MediaPipe`, `OpenCV`, `PyAutoGUI`, and `SpeechRecognition`, it enables hands-free navigation with iris tracking and basic speech recognition.

## Features

- 👁️ **Eye Control Mode**  
  Move your mouse cursor using your eye position captured via webcam.

- 🎤 **Voice Commands**  
  Issue voice commands like scrolling, clicking, and moving the cursor.

- 👀 **Landmark Display**  
  Optionally visualize face and eye landmarks on the video feed.

- ⌨️ **Keyboard Shortcuts**  
  - `m`: Toggle Eye Control Mode  
  - `t`: Toggle Landmark Visibility  
  - `q`: Quit the application

## Voice Commands Supported

You can say the following commands:

- `"scroll up"`, `"scroll down"`, `"scroll left"`, `"scroll right"`
- `"move up"`, `"move down"`, `"move left"`, `"move right"`
- `"left click"`, `"right click"`, `"double click"`

## Requirements

- Python 3.7+
- Webcam
- Microphone

## Installation

1. **Clone the repository** or copy the script.

2. **Install dependencies:**

```bash
pip install opencv-python mediapipe pyautogui numpy pynput SpeechRecognition pyaudio
````

> **Note:** If you face issues installing `pyaudio`, refer to platform-specific installation guides (especially on Windows or macOS).

## Running the Script

Run the script using:

```bash
python app.py
```

## Controls

* Look at different parts of the screen to move the mouse cursor.
* Blink (detected via iris depth) to click when in Eye Control mode.
* Speak voice commands aloud to trigger actions.
* Use the keyboard shortcuts (`m`, `t`, `q`) for control.

## Troubleshooting

* **No Webcam Detected:** Ensure your webcam is connected and accessible.
* **Voice Recognition Fails:** Try speaking clearly and ensure a working microphone.
* **PyAudio Errors:** You may need to install it with:

  * Windows: Use a precompiled `.whl` from [https://www.lfd.uci.edu/\~gohlke/pythonlibs/#pyaudio](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
  * macOS: `brew install portaudio && pip install pyaudio`

## Notes

* For best performance, run in a well-lit environment.
* The script is set up to track one face only.
* Eye control works best with minimal head movement.

## License

This project is open-source and free to use for personal and educational purposes.

---
