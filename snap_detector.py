import math
import time

class SnapDetector:

    THUMB_TIP = 4
    INDEX_TIP = 8

    def __init__(self):
        self.previous_distance = None
        self.previous_time = time.monotonic()

        # Adjust these if snap detection is too sensitive
        self.snap_distance = 0.08
        self.min_time_between_snaps = 0.35

        self.last_snap_time = 0

    @staticmethod
    def distance(a, b):
        return math.hypot(
            a.x - b.x,
            a.y - b.y
        )

    def detect(self, landmarks):

        current_distance = self.distance(
            landmarks[self.THUMB_TIP],
            landmarks[self.INDEX_TIP]
        )

        current_time = time.monotonic()

        if self.previous_distance is None:
            self.previous_distance = current_distance
            self.previous_time = current_time
            return False

        distance_change = (
            self.previous_distance - current_distance
        )

        time_since_last_snap = (
            current_time - self.last_snap_time
        )

        snap = False

        # Fast thumb/index movement
        if (
            distance_change > self.snap_distance
            and time_since_last_snap > self.min_time_between_snaps
        ):
            snap = True
            self.last_snap_time = current_time

        self.previous_distance = current_distance
        self.previous_time = current_time

        return snap