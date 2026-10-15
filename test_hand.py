import cv2

from hand_detector import HandDetector


detector = HandDetector()

cap = cv2.VideoCapture(0)

print("Starting hand detection...")
print("Press Q to quit.")

while True:

    success, frame = cap.read()

    if not success:
        print("Could not read camera.")
        break

    frame = cv2.flip(frame, 1)

    frame, hand_data = detector.process(frame)

    if hand_data is not None:
        cv2.putText(
            frame,
            "HAND DETECTED",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

    else:
        cv2.putText(
            frame,
            "NO HAND",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

    cv2.imshow(
        "MediaPipe Hand Test",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
detector.close()
cv2.destroyAllWindows()