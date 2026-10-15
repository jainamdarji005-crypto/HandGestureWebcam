import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera could not be opened")
    exit()

print("Camera started. Press Q to quit.")

while True:

    success, frame = cap.read()

    if not success:
        print("Could not read frame")
        break

    frame = cv2.flip(frame, 1)

    cv2.imshow("Camera Test", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()