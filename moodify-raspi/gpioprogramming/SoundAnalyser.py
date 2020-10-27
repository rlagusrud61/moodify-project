import numpy as np
import pyaudio
import sounddevice
from scipy.signal import butter, sosfilt


def wavelength_to_rgb(wavelength, gamma=0.8):
    wavelength = float(wavelength)
    wavelength = wavelength/3 + 340
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
        G = B = 0.0
    else:
        R = G = B = 0.0
    R *= 255
    G *= 255
    B *= 255
    return tuple([int(R), int(G), int(B)])


class SignalAnalyser:

    def __init__(self):
        self.lowcut = 80
        self.highcut = 920
        self.fs = 44100
        self.order = 10
        self.CHUNK = 4096
        self.p = pyaudio.PyAudio()  # start the PyAudio class
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=self.fs, input=True,
                                  frames_per_buffer=self.CHUNK)  # uses default input device
        self.stream.stop_stream()

    def __butter_bandpass(self):
        nyq = 0.5 * self.fs
        low = self.lowcut / nyq
        high = self.highcut / nyq
        sos = butter(self.order, [low, high], analog=False, btype='band', output='sos')
        return sos

    def __butter_bandpass_filter(self, data):
        sos = self.__butter_bandpass()
        y = sosfilt(sos, data)
        return y

    def analyse_data(self, data):
        x = np.hanning(self.CHUNK) * data
        y = self.__butter_bandpass_filter(x)
        peak = np.average(np.abs(y)) * 2
        fft = abs(np.fft.fft(y).real)
        fft = fft[:int(len(fft) / 2)]  # keep only first half
        freq = np.fft.fftfreq(self.CHUNK, 1.0 / self.fs)
        freq = freq[:int(len(freq) / 2)]  # keep only first half
        freqPeak = freq[np.where(fft == np.max(fft))[0][0]] + 1
        return fft, freq, freqPeak, peak

    def get_next_pair(self):
        self.stream.start_stream()
        data = np.frombuffer(self.stream.read(self.CHUNK), dtype=np.int16)
        self.stream.stop_stream()
        _, _, peak_req, amp = self.analyse_data(data)
        adjustedAMP = 0
        if amp > 2:
            adjustedAMP = max(min(amp/20, 1), 0.1)
        return peak_req, adjustedAMP

    def terminate(self):
        self.stream.close()
        self.p.terminate()


if __name__ == '__main__':
    newAnalysis = SignalAnalyser()
    lastFreq = 0
    weight = 0.70
    while True:
        thisFreq, thisAmp = newAnalysis.get_next_pair()
        average = thisFreq * weight + (1 - weight) * lastFreq
        lastFreq = thisFreq
        print((round(average), thisAmp, wavelength_to_rgb(average)))
