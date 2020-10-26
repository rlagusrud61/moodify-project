import time
import math
import threading
import pyaudio
import board
import neopixel
import wave
import numpy as np

OFF = (0, 0, 0)


def brightnessAdjustedColour(colour, brightness):
    return tuple(math.floor(brightness * colour) for colour in colour)


def wavelength_to_rgb(wavelength, gamma = 0.8)
    wavelength = float(wavelength)
    if 380 <= wavelength <= 440:
        attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
        R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
        G = 0.0
        B = (1.0 * attenuation) ** gamma
    elif 440 <= wavelength <= 490:
        R = 0.0
        G = ((wavelength - 440) / (490 - 440)) ** gamma
        B = 1.0
    elif 490 <= wavelength <= 510:
        R = 0.0
        G = 1.0
        B = (-(wavelength - 510) / (510 - 490)) ** gamma
    elif 510 <= wavelength <= 580:
        R = ((wavelength - 510) / (580 - 510)) ** gamma
        G = 1.0
        B = 0.0
    elif 580 <= wavelength <= 645:
        R = 1.0
        G = (-(wavelength - 645) / (645 - 580)) ** gamma
        B = 0.0
    elif 645 <= wavelength <= 750:
        attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
        R = (1.0 * attenuation) ** gamma
        G = 0.0
        B = 0.0
    else:
        R = 0.0
        G = 0.0
        B = 0.0
    R *= 255
    G *= 255
    B *= 255
    return tuple([int(R), int(G), int(B)])


class StripControl:

    def __init__(self, e):
        self.colour = OFF
        self.brightness = 0.2

        self.__brightness_adjusted_colour = OFF
        self.__pixel_pin = board.D18
        self.__ORDER = neopixel.GRB
        self.__num_pixels = 10
        self.__pixels = neopixel.NeoPixel(
            self.__pixel_pin,
            self.__num_pixels,
            brightness=self.brightness,
            auto_write=False,
            pixel_order=self.__ORDER
        )

        self.__e = e

        self.__refresh_rgb_strip()
        self.__delay = 0.5
        self.__start()

        self.turn_off()

    def show_colours(self):
        self.__pixels.show()
        time.sleep(self.__delay)

    def turn_off(self):
        self.__pixels.fill(OFF)
        self.show_colours()

    def setColour(self, newColour):
        self.colour = newColour
        print(f"New Colour: {self.colour}")
        self.__refresh_rgb_strip()

    def setBrightness(self, newBrightness):
        self.brightness = newBrightness
        print(f"New Brightness: {self.brightness}")
        self.__refresh_rgb_strip()

    def __refresh_rgb_strip(self):
        self.__brightness_adjusted_colour = brightnessAdjustedColour(self.colour, self.brightness)
        print(f"New Adjusted Colour: {self.__brightness_adjusted_colour}")
        self.__pixels.fill(self.__brightness_adjusted_colour)

    def __start(self):
        print("Starting Thread for Music Loop")
        threading.Thread(target=self.__musicLoop, daemon=True).start()

    def turnOnMusic(self):
        if not self.__e.isSet():
            print("Turning on Music")
            self.__e.set()

    def turnOffMusic(self):
        if self.__e.isSet():
            print("Turning off the music")
            self.__e.clear()

    def soundAnalyze(self, stream):
        data = stream.read(8192, exception_on_overflow=False)
        waveData = wave.struct.unpack("%dh"%(8192), data)
        npArrayData = np.array(waveData)
        volume = npArrayData[1:].argmax() + 1
        fftData=np.abs(np.fft.rfft(npArrayData))
        which = fftData[1:].argmax() + 1
        thefreq = which*44100/8192
        return[npArrayData[volume], thefreq]

    def __musicLoop(self):
        freqArray = [0, 0, 0, 0, 0]
        freqCounter = 0
        lightWave = 0
        targetFreq = 0
        p = pyaudio.PyAudio()
        stream = p.open(format = pyaudio.paInt16, channels = 1, rate = 44100, input=True,
                            frames_per_buffer = 8192)
        try:
            while True:
                self.__e.wait()
                # TODO: do the boogy
                # While in this loop use local colour/brightness declaration not the self.colour, self.brightness
                # Use brightnessAdjustedColour for proper values if needed.
                while self.__e.isSet():
                    soundData = self.soundAnalyze(stream)
                    if 100 < soundData[1] < 880:
                        freqArray[freqCounter] = soundData[1]
                        freqCounter += (freqCounter + 1) % 5
                    for i in freqArray:
                        targetFreq += freqArray[i]
                    if 100 < targetFreq < 880:
                        lightWave = targetFreq * (37/78) + 333

                    targetRGB = list(wavelength_to_rgb(lightWave))
                    currentRGB = list(self.colour)
                    # difference = tuple(((x-y) / 10) for x, y in zip(targetRGB, currentRGB))
                    while currentRGB != targetRGB:
                        for i in range(3):
                            if 10 >= currentRGB[i] - targetRGB[i] >= -10:
                                currentRGB[i] = targetRGB[i]
                            else:
                                if currentRGB[i] < targetRGB[i]:
                                    currentRGB[i] += 10
                                else:
                                    currentRGB[i] -= 10
                        self.setColour(tuple(currentRGB))
                        self.show_colours()
                        time.sleep(0.02)
        except Exception:
            stream.stop_stream()
            stream.close()
            p.terminate()
