import math


class GestureDetector:
    THUMB_TIP = 4
    THUMB_IP = 3
    INDEX_MCP = 5
    INDEX_TIP = 8
    INDEX_PIP = 6
    MIDDLE_TIP = 12
    MIDDLE_PIP = 10
    RING_TIP = 16
    RING_PIP = 14
    PINKY_TIP = 20
    PINKY_PIP = 18

    def __init__(self):
        # Normalized MediaPipe distance used for volume mapping.
        self.min_distance = 0.03
        self.max_distance = 0.35

    @staticmethod
    def distance(a, b):
        return math.hypot(a.x - b.x, a.y - b.y)

    def extended_fingers(self, landmarks):
        pairs = [
            (self.INDEX_TIP, self.INDEX_PIP),
            (self.MIDDLE_TIP, self.MIDDLE_PIP),
            (self.RING_TIP, self.RING_PIP),
            (self.PINKY_TIP, self.PINKY_PIP),
        ]
        return sum(1 for tip, pip in pairs
                   if landmarks[tip].y < landmarks[pip].y)

    def is_shaka(self, landmarks):
        # Shaka: thumb and pinky extended; index, middle and ring folded.
        other_fingers_folded = all(
            landmarks[tip].y > landmarks[pip].y
            for tip, pip in (
                (self.INDEX_TIP, self.INDEX_PIP),
                (self.MIDDLE_TIP, self.MIDDLE_PIP),
                (self.RING_TIP, self.RING_PIP),
            )
        )
        pinky_extended = (
            landmarks[self.PINKY_TIP].y
            < landmarks[self.PINKY_PIP].y
        )

        # Thumb extension is measured geometrically so it works with
        # either hand and with the mirrored webcam image.
        thumb_tip_to_index_mcp = self.distance(
            landmarks[self.THUMB_TIP], landmarks[self.INDEX_MCP]
        )
        thumb_ip_to_index_mcp = self.distance(
            landmarks[self.THUMB_IP], landmarks[self.INDEX_MCP]
        )
        thumb_extended = thumb_tip_to_index_mcp > (
            thumb_ip_to_index_mcp * 1.25
        )

        return other_fingers_folded and pinky_extended and thumb_extended

    def is_index_point(self, landmarks):
        # Index raised, with middle/ring/pinky folded.
        index_extended = (
            landmarks[self.INDEX_TIP].y
            < landmarks[self.INDEX_PIP].y
        )
        other_fingers_folded = all(
            landmarks[tip].y > landmarks[pip].y
            for tip, pip in (
                (self.MIDDLE_TIP, self.MIDDLE_PIP),
                (self.RING_TIP, self.RING_PIP),
                (self.PINKY_TIP, self.PINKY_PIP),
            )
        )
        return index_extended and other_fingers_folded

    def detect(self, hand_data):
        landmarks = hand_data["landmarks"]

        pinch_distance = self.distance(
            landmarks[self.THUMB_TIP],
            landmarks[self.INDEX_TIP],
        )
        fingers = self.extended_fingers(landmarks)

        # Check specific gestures before the general volume fallback.
        if self.is_shaka(landmarks):
            gesture = "SHAKA"
        elif self.is_index_point(landmarks):
            gesture = "INDEX_POINT"
        elif fingers == 0:
            gesture = "FIST"
        elif fingers == 4:
            gesture = "OPEN"
        else:
            gesture = "VOLUME"

        return {
            "gesture": gesture,
            "pinch_distance": pinch_distance,
            "index_y": landmarks[self.INDEX_TIP].y,
        }

    def distance_to_volume(self, distance):
        value = (
            (distance - self.min_distance)
            / (self.max_distance - self.min_distance)
        )
        value = max(0.0, min(1.0, value))
        return value * 100
