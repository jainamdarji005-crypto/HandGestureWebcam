import cv2
import mediapipe as mp

print("OpenCV:", cv2.__version__)
print("MediaPipe:", mp.__version__)

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

print("MediaPipe Hands loaded successfully!")

hands.close()