import cv2
import os
import shutil
import subprocess
import time
from pathlib import Path

from hand_detector import HandDetector
from gesture_detector import GestureDetector
from volume_controller import VolumeController
from snap_detector import SnapDetector


def open_chrome():
    """Open Google Chrome on Windows; return True if launch was requested."""
    chrome = shutil.which("chrome") or shutil.which("chrome.exe")

    if not chrome:
        candidates = [
            Path(os.environ.get("PROGRAMFILES", r"C:\\Program Files"))
            / "Google/Chrome/Application/chrome.exe",
            Path(os.environ.get("PROGRAMFILES(X86)", r"C:\\Program Files (x86)"))
            / "Google/Chrome/Application/chrome.exe",
            Path(os.environ.get("LOCALAPPDATA", ""))
            / "Google/Chrome/Application/chrome.exe",
        ]
        chrome = next((str(p) for p in candidates if p.is_file()), None)

    try:
        if chrome:
            subprocess.Popen([chrome])
        else:
            # Windows can resolve the registered Chrome application.
            subprocess.Popen(
                ["cmd", "/c", "start", "", "chrome"],
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        return True
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"Could not launch Chrome: {exc}")
        return False


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Could not open webcam.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)

    hand_detector = HandDetector(max_hands=2)
    gesture_detector = GestureDetector()
    volume_controller = VolumeController()

    left_snap_detector = SnapDetector()
    right_snap_detector = SnapDetector()

    last_volume = volume_controller.get_volume()
    volume_controller.unmute()

    flash_until = 0
    flash_duration = 0.12

    # Gesture action state prevents repeated Chrome launches while Shaka is held.
    shaka_was_active = False
    last_chrome_launch = 0.0
    chrome_cooldown = 2.0

    # Scroll tracking uses normalized index fingertip y-coordinates.
    previous_index_y = None
    scroll_accumulator = 0.0
    scroll_threshold = 0.012
    scroll_amount = 2
    pyautogui = None
    scroll_warning_shown = False

    print()
    print("--------------------------------------")
    print(" HAND GESTURE CONTROL")
    print("--------------------------------------")
    print(" FIST       = Mute")
    print(" OPEN HAND  = Unmute")
    print(" PINCH      = Volume")
    print(" SNAP       = Screen Flash")
    print(" SHAKA      = Open Google Chrome")
    print(" INDEX UP   = Scroll up")
    print(" INDEX DOWN = Scroll down")
    print(" Press Q to quit")
    print("--------------------------------------")
    print()

    try:
        while True:
            success, frame = cap.read()
            if not success:
                print("ERROR: Could not read webcam frame.")
                break

            frame = cv2.flip(frame, 1)
            frame, hands = hand_detector.process(frame)
            hand_count = len(hands)
            gesture = "NO HAND"
            volume_percent = volume_controller.get_volume()

            if hand_count > 0:
                # Check snapping on each detected hand.
                for index, hand in enumerate(hands):
                    snap_detector = (
                        left_snap_detector if index == 0
                        else right_snap_detector
                    )
                    if snap_detector.detect(hand["landmarks"]):
                        print("SNAP DETECTED!")
                        flash_until = time.monotonic() + flash_duration

                first_hand = hands[0]
                result = gesture_detector.detect(first_hand)
                gesture = result["gesture"]

                if gesture == "FIST":
                    volume_controller.mute()
                    shaka_was_active = False
                    previous_index_y = None
                    scroll_accumulator = 0.0

                elif gesture == "OPEN":
                    volume_controller.unmute()
                    shaka_was_active = False
                    previous_index_y = None
                    scroll_accumulator = 0.0

                elif gesture == "SHAKA":
                    now = time.monotonic()
                    if (
                        not shaka_was_active
                        and now - last_chrome_launch >= chrome_cooldown
                    ):
                        if open_chrome():
                            print("SHAKA DETECTED: Opening Google Chrome")
                            last_chrome_launch = now
                    shaka_was_active = True
                    previous_index_y = None
                    scroll_accumulator = 0.0

                elif gesture == "INDEX_POINT":
                    shaka_was_active = False
                    current_y = result["index_y"]

                    if previous_index_y is not None:
                        # MediaPipe y decreases when the fingertip moves up.
                        scroll_accumulator += previous_index_y - current_y

                        if abs(scroll_accumulator) >= scroll_threshold:
                            if pyautogui is None:
                                try:
                                    import pyautogui as pyautogui_module
                                    pyautogui = pyautogui_module
                                except ImportError:
                                    if not scroll_warning_shown:
                                        print(
                                            "Scrolling requires pyautogui. "
                                            "Install it with: pip install pyautogui"
                                        )
                                        scroll_warning_shown = True
                            if pyautogui is not None:
                                # Positive scroll is up; negative scroll is down.
                                direction = 1 if scroll_accumulator > 0 else -1
                                pyautogui.scroll(direction * scroll_amount)
                            scroll_accumulator = 0.0

                    previous_index_y = current_y

                elif gesture == "VOLUME":
                    shaka_was_active = False
                    previous_index_y = None
                    scroll_accumulator = 0.0
                    new_volume = gesture_detector.distance_to_volume(
                        result["pinch_distance"]
                    )
                    if abs(new_volume - last_volume) >= 1:
                        volume_controller.set_volume(new_volume)
                        last_volume = new_volume

                else:
                    shaka_was_active = False
                    previous_index_y = None
                    scroll_accumulator = 0.0

                volume_percent = volume_controller.get_volume()
            else:
                shaka_was_active = False
                previous_index_y = None
                scroll_accumulator = 0.0

            if time.monotonic() < flash_until:
                frame[:] = 255
                cv2.putText(
                    frame, "SNAP!", (350, 280),
                    cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 0), 4
                )
            else:
                cv2.rectangle(frame, (20, 20), (470, 215), (30, 30, 30), -1)
                cv2.putText(
                    frame, f"Hands: {hand_count}", (35, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2
                )
                cv2.putText(
                    frame, f"Gesture: {gesture}", (35, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2
                )
                cv2.putText(
                    frame, f"Volume: {volume_percent:.0f}%", (35, 125),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2
                )
                cv2.putText(
                    frame, "Shaka = Chrome | Index move = Scroll", (35, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1
                )
                cv2.putText(
                    frame, "Q = Quit", (35, 190),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1
                )

            cv2.imshow("Hand Gesture Volume Control", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        hand_detector.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
