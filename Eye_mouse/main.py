import cv2
import mediapipe as mp
import pyautogui
import numpy as np
from pynput import keyboard
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize constants and objects
pyautogui.FAILSAFE = False

cam = cv2.VideoCapture(0)
if not cam.isOpened():
    logging.error("Could not open webcam. Ensure it's connected and not in use.")
    exit()

try:
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
except Exception as e:
    logging.error(f"Failed to initialize MediaPipe FaceMesh: {e}")
    exit()

screen_w, screen_h = pyautogui.size()

# Predefine landmark indices
EYE_LANDMARKS = [474, 475, 476, 477]  # Iris landmarks
LEFT_EYE = [145, 159]  # Left eye landmarks for blink detection

# Global state variables
use_eye_control = True
show_landmarks = True
running = True

def process_frame(frame, face_mesh, screen_w, screen_h):
    global use_eye_control, show_landmarks
    try:
        frame = cv2.flip(frame, 1)
        frame_h, frame_w = frame.shape[:2]
        
        if not use_eye_control:
            cv2.putText(frame, "Mode: Normal Mouse", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return frame, False
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            cv2.putText(frame, "Mode: Eye Mouse (No Face Detected)", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
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
        
        cv2.putText(frame, "Mode: Eye Mouse", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return frame, (left_eye[0].y - left_eye[1].y) < 0.004
    
    except Exception as e:
        logging.error(f"Error processing frame: {e}")
        return frame, False

def on_press(key):
    global use_eye_control, show_landmarks, running
    try:
        if key == keyboard.KeyCode.from_char('m'):
            use_eye_control = not use_eye_control
            mode = "Eye Mouse" if use_eye_control else "Normal Mouse"
            logging.info(f"Switched to {mode}")
        elif key == keyboard.KeyCode.from_char('t'):
            show_landmarks = not show_landmarks
            logging.info(f"Landmarks: {'Visible' if show_landmarks else 'Hidden'}")
        elif key == keyboard.KeyCode.from_char('q'):
            running = False
            logging.info("Quit command received")
            return False
    except AttributeError:
        pass

def main():
    global running  # Declare running as global to avoid UnboundLocalError
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    try:
        while running:
            ret, frame = cam.read()
            if not ret:
                logging.error("Failed to capture frame")
                break
                
            frame, should_click = process_frame(frame, face_mesh, screen_w, screen_h)
            
            if use_eye_control and should_click:
                pyautogui.click()
                pyautogui.sleep(0.5)
                logging.info("Click executed")
                
            cv2.imshow('Mouse Control', frame)
            cv2.waitKey(1)
            
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        running = False
        listener.stop()
        cam.release()
        cv2.destroyAllWindows()
        logging.info("Program terminated")

if __name__ == "__main__":
    logging.info("Starting Mouse Control Program")
    logging.info("Press 'm' to toggle Eye/Normal Mouse, 't' for landmarks, 'q' to quit")
    main()