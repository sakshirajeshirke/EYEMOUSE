# import speech_recognition as sr
# r = sr.Recognizer()
# with sr.Microphone() as source:
#     print("Say something!")
#     audio = r.listen(source)
#     try:
#         print("You said: " + r.recognize_google(audio))
#     except sr.UnknownValueError:
#         print("Could not understand audio")
import pyautogui
import time
time.sleep(2)  # Give time to switch focus
pyautogui.scroll(100)  # Should scroll up
pyautogui.moveTo(500, 500)  # Should move cursor
pyautogui.click()  # Should click