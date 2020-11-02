import pyaudio
from scipy import signal
import numpy as np


def getHex(observedFreq, lowcut, highcut):
    freq = observedFreq
    if observedFreq > highcut:
        freq = highcut
    elif observedFreq < lowcut:
        freq = lowcut
    return min(max(255 * (freq - lowcut) / (highcut - lowcut), 10), 255)


class SignalAnalyser:

    def __init__(self):
        self.names = ["red", "green", "blue"]
        self.low_cuts = [130, 260, 520]
        self.high_cuts = [260, 520, 1040]
        self.amplitudeThreshold = 300
        self.amplitudeScaleFactor = 5000
        self.fs = 44100
        self.nf = 44100 / 2
        self.order = 4
        self.CHUNK = 4096
        self.p = pyaudio.PyAudio()  # start the PyAudio class
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=self.fs, input=True,
                                  frames_per_buffer=self.CHUNK)  # uses default input device
        self.stream.stop_stream()

    def analyse_data(self, signal_data):
        freq_peaks = {}
        base_amplitude = np.average(np.abs(signal_data)) * 2

        for name, low, high in zip(self.names, self.low_cuts, self.high_cuts):
            data_copy = signal_data
            freqPeak, amp = self.perform_octave_analysis(low, high, data_copy)
            newData = {name: {"freqPeak": freqPeak, "freqAmplitude": amp}}
            freq_peaks.update(newData)
        return freq_peaks, base_amplitude

    def perform_octave_analysis(self, low_cut, high_cut, x):
        b, a = signal.butter(
            N=self.order,
            Wn=np.array([low_cut, high_cut]) / self.nf,
            btype='bandpass',
            analog=False,
            output='ba'
        )
        # Filter signal
        filteredSpeech = signal.filtfilt(b, a, x)
        filteredSpeech = np.hanning(self.CHUNK) * filteredSpeech

        peak = np.average(np.abs(filteredSpeech)) * 2
        fft = abs(np.fft.fft(filteredSpeech).real)
        fft = fft[:int(len(fft) / 2)]  # keep only first half
        freq = np.fft.fftfreq(self.CHUNK, 1.0 / self.fs)
        freq = freq[:int(len(freq) / 2)]  # keep only first half
        freqPeak = freq[np.where(fft == np.max(fft))[0][0]] + 1
        return freqPeak, peak

    def getRGB(self, freq_data):
        RGB = []
        for name, low, high in zip(self.names, self.low_cuts, self.high_cuts):
            print(name, freq_data[name]['freqAmplitude'])
            hexValue = round(getHex(freq_data[name]['freqPeak'], low, high))
            brightnessScaledHex = round(hexValue * freq_data[name]['freqAmplitude'])
            RGB.append(brightnessScaledHex)
        return tuple(RGB)

    def get_next(self):
        self.stream.start_stream()
        data = np.frombuffer(self.stream.read(self.CHUNK), dtype=np.int16)
        self.stream.stop_stream()

        rgb_metadata, base_amplitude = self.analyse_data(data)
        print(rgb_metadata)
        for component in rgb_metadata.keys():
            if rgb_metadata[component]['freqAmplitude'] > self.amplitudeThreshold:
                adjustedAMP = max(min(rgb_metadata[component]['freqAmplitude'] / self.amplitudeScaleFactor, 1.0), 0.1)
            else:
                adjustedAMP = 0
            rgb_metadata[component]['freqAmplitude'] = adjustedAMP
        print(rgb_metadata)
        return rgb_metadata

    def terminate(self):
        self.stream.close()
        self.p.terminate()


if __name__ == '__main__':
    newAnalysis = SignalAnalyser()
    while True:
        colour_metadata = newAnalysis.get_next()
        rgb = newAnalysis.getRGB(colour_metadata)
        print(rgb)
