# This test has to be done manually as this test checks for connected audio devices.

import pyaudio
import sounddevice

p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    print(p.get_device_info_by_index(i).get('name'))
