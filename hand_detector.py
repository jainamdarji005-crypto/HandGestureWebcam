import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class HandDetector:

    def __init__(
        self,
        model_path="hand_landmarker.task",
        max_hands=2,
        detection_confidence=0.7,
        tracking_confidence=0.7
    ):

        # -----------------------------
        # MediaPipe model
        # -----------------------------

        base_options = python.BaseOptions(
            model_asset_path=model_path
        )

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_hands,

            min_hand_detection_confidence=detection_confidence,
            min_hand_presence_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )

        self.detector = (
            vision.HandLandmarker.create_from_options(
                options
            )
        )

        self.timestamp = 0

    # =====================================================
    # PROCESS FRAME
    # =====================================================

    def process(self, frame):

        # -----------------------------
        # Convert BGR → RGB
        # -----------------------------

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        # -----------------------------
        # Timestamp
        # -----------------------------

        self.timestamp += 33

        # -----------------------------
        # Detect hands
        # -----------------------------

        result = self.detector.detect_for_video(
            mp_image,
            self.timestamp
        )

        # -----------------------------
        # No hands
        # -----------------------------

        if not result.hand_landmarks:

            return frame, []

        h, w, _ = frame.shape

        hands = []

        # =================================================
        # PROCESS EVERY HAND
        # =================================================

        for i, landmarks in enumerate(
            result.hand_landmarks
        ):

            # ---------------------------------------------
            # Hand label
            # ---------------------------------------------

            hand_label = "Unknown"

            if result.handedness:

                hand_label = (
                    result
                    .handedness[i][0]
                    .category_name
                )

            # ---------------------------------------------
            # Hand connections
            # ---------------------------------------------

            connections = [

                # Thumb
                (0, 1),
                (1, 2),
                (2, 3),
                (3, 4),

                # Index
                (0, 5),
                (5, 6),
                (6, 7),
                (7, 8),

                # Middle
                (0, 9),
                (9, 10),
                (10, 11),
                (11, 12),

                # Ring
                (0, 13),
                (13, 14),
                (14, 15),
                (15, 16),

                # Pinky
                (0, 17),
                (17, 18),
                (18, 19),
                (19, 20),

                # Palm
                (5, 9),
                (9, 13),
                (13, 17)
            ]

            # ---------------------------------------------
            # Draw connections
            # ---------------------------------------------

            for start, end in connections:

                x1 = int(
                    landmarks[start].x * w
                )

                y1 = int(
                    landmarks[start].y * h
                )

                x2 = int(
                    landmarks[end].x * w
                )

                y2 = int(
                    landmarks[end].y * h
                )

                cv2.line(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

            # ---------------------------------------------
            # Draw landmarks
            # ---------------------------------------------

            for landmark in landmarks:

                x = int(
                    landmark.x * w
                )

                y = int(
                    landmark.y * h
                )

                cv2.circle(
                    frame,
                    (x, y),
                    5,
                    (0, 0, 255),
                    -1
                )

            # ---------------------------------------------
            # Display hand label
            # ---------------------------------------------

            wrist_x = int(
                landmarks[0].x * w
            )

            wrist_y = int(
                landmarks[0].y * h
            )

            cv2.putText(
                frame,
                hand_label,
                (
                    wrist_x,
                    wrist_y - 15
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )

            # ---------------------------------------------
            # Store hand
            # ---------------------------------------------

            hands.append({

                "landmarks": landmarks,

                "label": hand_label,

                "width": w,

                "height": h
            })

        return frame, hands

    # =====================================================
    # CLOSE
    # =====================================================

    def close(self):

        self.detector.close()