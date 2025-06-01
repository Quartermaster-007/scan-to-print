import os
import winsound

SOUND_SUCCESS = r'C:\Windows\Media\Windows Print complete.wav'
SOUND_ERROR = r'C:\Windows\Media\Windows Foreground.wav'

def play_success():
    if os.path.exists(SOUND_SUCCESS):
        winsound.PlaySound(SOUND_SUCCESS, winsound.SND_FILENAME | winsound.SND_ASYNC)

def play_error():
    if os.path.exists(SOUND_ERROR):
        winsound.PlaySound(SOUND_ERROR, winsound.SND_FILENAME | winsound.SND_ASYNC)
