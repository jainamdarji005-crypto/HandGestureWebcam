from pycaw.pycaw import AudioUtilities


print("Getting Windows audio device...")

devices = AudioUtilities.GetSpeakers()

volume = devices.EndpointVolume

current = volume.GetMasterVolumeLevelScalar()

print(
    "Current volume:",
    current * 100,
    "%"
)

print("Setting volume to 50%...")

volume.SetMasterVolumeLevelScalar(
    0.50,
    None
)

print("Volume set successfully.")