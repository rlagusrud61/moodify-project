import pyaudio
from scipy import signal
import numpy as np
from colr import color


def getOctaveRGB(observedFreq, lowcut, highcut, scaledBrightness):
    increment = (highcut - lowcut)/3
    # print(f"{lowcut}<={observedFreq}<={highcut}: increment:{increment}: first:{increment+lowcut}, second:{2*increment + lowcut}")
    # print(f"scaledBrightness: {scaledBrightness}")
    if observedFreq < lowcut:
        rgb = [0, 0, 0]
    elif observedFreq < increment + lowcut:
        rgb = [0, 0, scaledBrightness*(observedFreq/(increment + lowcut))*255]
    elif observedFreq < 2*increment + lowcut:
        rgb = [0, scaledBrightness*(observedFreq/((2 * increment) + lowcut))*255, 0]
    elif observedFreq < 3*increment + lowcut:
        rgb = [scaledBrightness*(observedFreq/((3 * increment) + lowcut))*255, 0, 0]
    else:
        rgb = [0, 0, 0]
    # print(f"RGB: {rgb}")
    return rgb


class SignalAnalyser:

    def __init__(self):
        self.names = ["red", "green", "blue"]
        self.low_cuts = [110, 240, 500]
        self.high_cuts = [280, 540, 1240]
        self.amplitudeThreshold = 150
        self.amplitudeScaleFactor = 500
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
        octaveRGBs = []
        for name, low, high in zip(self.names, self.low_cuts, self.high_cuts):
            octaveRGB = getOctaveRGB(freq_data[name]['freqPeak'], low, high, freq_data[name]['freqAmplitude'])
            octaveRGBs.append(octaveRGB)
            # print(name, octaveRGB, freq_data[name]['freqAmplitude'])
        return tuple([min(round(sum(x)), 255) for x in zip(octaveRGBs[0], octaveRGBs[1], octaveRGBs[2])])

    def get_next(self):
        self.stream.start_stream()
        data = np.frombuffer(self.stream.read(self.CHUNK), dtype=np.int16)
        self.stream.stop_stream()

        rgb_metadata, base_amplitude = self.analyse_data(data)
        # print(rgb_metadata)
        for component in rgb_metadata.keys():
            if rgb_metadata[component]['freqAmplitude'] > self.amplitudeThreshold:
                adjustedAMP = max(min(rgb_metadata[component]['freqAmplitude'] / self.amplitudeScaleFactor, 1.0), 0.1)
            else:
                adjustedAMP = 0
            rgb_metadata[component]['freqAmplitude'] = adjustedAMP
        # print(rgb_metadata)
        return rgb_metadata

    def terminate(self):
        self.stream.close()
        self.p.terminate()


if __name__ == '__main__':
    newAnalysis = SignalAnalyser()
    while True:
        colour_metadata = newAnalysis.get_next()
        rgb = newAnalysis.getRGB(colour_metadata)
        print(color(f"FINAL: {rgb}", fore=(255, 255, 255), back=rgb))
