import cv2
import mediapipe as mp
import pyautogui
import numpy as np
from pynput import keyboard
import speech_recognition as sr
import threading
import time

# Initialize constants and objects
pyautogui.FAILSAFE = False
cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("Error: Could not open webcam")
    exit()

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    refine_landmarks=True,  # Enables iris tracking
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    max_num_faces=1  # Matches NUM_FACES=1
)
screen_w, screen_h = pyautogui.size()
recognizer = sr.Recognizer()

# Predefine landmark indices
EYE_LANDMARKS = [474, 475, 476, 477]  # Iris landmarks
LEFT_EYE = [145, 159]  # Left eye landmarks for blink detection

# Global state variables
use_eye_control = True
show_landmarks = True
running = True
voice_command = None
voice_status = "Initializing..."
MOVE_DISTANCE = 50

def voice_listener():
    global voice_command, running, voice_status
    try:
        mic = sr.Microphone()
        with mic as source:
            print("Microphone initialized successfully")
            voice_status = "Voice control ready"
            recognizer.adjust_for_ambient_noise(source, duration=1)
            while running:
                try:
                    print("Listening for command...")
                    audio = recognizer.listen(source, timeout=None, phrase_time_limit=3)
                    command = recognizer.recognize_google(audio).lower()
                    voice_command = command
                    voice_status = f"Command: {command}"
                    print(f"Voice command detected: {command}")
                except sr.UnknownValueError:
                    voice_status = "Could not understand audio"
                except sr.RequestError as e:
                    voice_status = f"Speech service error: {e}"
                time.sleep(0.5)
    except Exception as e:
        voice_status = f"Microphone init failed: {e}"
        print(f"Microphone initialization failed: {e}")

def process_frame(frame, face_mesh, screen_w, screen_h):
    global use_eye_control, show_landmarks, voice_command, voice_status
    frame = cv2.flip(frame, 1)
    frame_h, frame_w = frame.shape[:2]
    
    # Process voice commands
    if voice_command:
        print(f"Processing command: {voice_command}")
        current_x, current_y = pyautogui.position()
        command = voice_command.lower().strip()
        
        if "scroll" in command and "up" in command:
            print("Executing scroll up")
            pyautogui.scroll(100)
        elif "scroll" in command and "down" in command:
            print("Executing scroll down")
            pyautogui.scroll(-100)
        elif "scroll" in command and "left" in command:
            pyautogui.hscroll(-100)
        elif "scroll" in command and "right" in command:
            pyautogui.hscroll(100)
        elif "move" in command and "up" in command:
            pyautogui.moveTo(current_x, max(0, current_y - MOVE_DISTANCE))
        elif "move" in command and "down" in command:
            pyautogui.moveTo(current_x, min(screen_h, current_y + MOVE_DISTANCE))
        elif "move" in command and "left" in command:
            pyautogui.moveTo(max(0, current_x - MOVE_DISTANCE), current_y)
        elif "move" in command and "right" in command:
            pyautogui.moveTo(min(screen_w, current_x + MOVE_DISTANCE), current_y)
        elif "left click" in command:
            pyautogui.click()
        elif "right click" in command:
            pyautogui.rightClick()
        elif "double click" in command:
            pyautogui.doubleClick()
        time.sleep(0.1)
        voice_command = None

    status_text = f"Mode: {'Eye' if use_eye_control else 'Normal'} Mouse | {voice_status}"
    status_color = (0, 255, 0) if "ready" in voice_status.lower() or "command" in voice_status.lower() else (0, 0, 255)
    
    if not use_eye_control:
        cv2.putText(frame, status_text, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        return frame, False
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)
    
    if not results.multi_face_landmarks:
        cv2.putText(frame, status_text + " (No Face)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        return frame, False
    
    landmarks = results.multi_face_landmarks[0].landmark
    
    cursor_lm = landmarks[475]
    screen_x = np.clip(screen_w * cursor_lm.x, 0, screen_w)
    screen_y = np.clip(screen_h * cursor_lm.y, 0, screen_h)
    pyautogui.moveTo(screen_x, screen_y)
    
    if show_landmarks:
        for idx in EYE_LANDMARKS:
            lm = landmarks[idx]
            x, y = int(lm.x * frame_w), int(lm.y * frame_h)
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
        
        left_eye = [landmarks[i] for i in LEFT_EYE]
        for lm in left_eye:
            x, y = int(lm.x * frame_w), int(lm.y * frame_h)
            cv2.circle(frame, (x, y), 2, (0, 255, 255), -1)
    else:
        left_eye = [landmarks[i] for i in LEFT_EYE]
    
    cv2.putText(frame, status_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
    
    return frame, (left_eye[0].y - left_eye[1].y) < 0.004

def on_press(key):
    global use_eye_control, show_landmarks, running
    try:
        if key == keyboard.KeyCode.from_char('m'):
            use_eye_control = not use_eye_control
            print(f"Switched to {'Eye' if use_eye_control else 'Normal'} Mouse")
        elif key == keyboard.KeyCode.from_char('t'):
            show_landmarks = not show_landmarks
            print(f"Landmarks: {'Visible' if show_landmarks else 'Hidden'}")
        elif key == keyboard.KeyCode.from_char('q'):
            running = False
            return False
    except AttributeError:
        pass

def main():
    global running
    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener.start()
    
    voice_thread = threading.Thread(target=voice_listener, daemon=True)
    voice_thread.start()
    
    time.sleep(2)
    
    try:
        while running:
            ret, frame = cam.read()
            if not ret:
                print("Failed to capture frame")
                break
                
            frame, should_click = process_frame(frame, face_mesh, screen_w, screen_h)
            
            if use_eye_control and should_click:
                pyautogui.click()
                pyautogui.sleep(0.5)
                
            cv2.imshow('Mouse Control', frame)
            cv2.waitKey(1)
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        running = False
        keyboard_listener.stop()
        cam.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("Starting Mouse Control Program")
    print("Press 'm' to toggle between Eye Mouse and Normal Mouse")
    print("Press 't' to toggle landmark visibility")
    print("Press 'q' to quit")
    print("Voice commands: 'scroll up', 'scroll down', 'scroll left', 'scroll right',")
    print("'move up', 'move down', 'move left', 'move right',")
    print("'left click', 'right click', 'double click'")
    main()