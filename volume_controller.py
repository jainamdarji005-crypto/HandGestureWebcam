from pycaw.pycaw import AudioUtilities


class VolumeController:

    def __init__(self):

        devices = AudioUtilities.GetSpeakers()

        self.volume = devices.EndpointVolume

    def get_volume(self):

        value = self.volume.GetMasterVolumeLevelScalar()

        return float(value) * 100

    def set_volume(self, percent):

        percent = max(
            0,
            min(100, float(percent))
        )

        self.volume.SetMasterVolumeLevelScalar(
            percent / 100,
            None
        )

    def mute(self):

        self.volume.SetMute(
            1,
            None
        )

    def unmute(self):

        self.volume.SetMute(
            0,
            None
        )

    def is_muted(self):

        return bool(
            self.volume.GetMute()
        )