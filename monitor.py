import numpy as np
from scipy.signal import lfilter
import sounddevice as sd
import soundfile as sf
from waveform_analysis.weighting_filters.ABC_weighting import A_weighting
import time

def get_loudness(samples):
    return 20*np.log10(np.sqrt(np.mean(samples**2)))

class Monitor:

    def __init__(self, samplerate, channels, blocksize, debounce, threshold, warning_file):
        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize
        self.debounce = debounce
        self.threshold = threshold
        self.warning_data, self.warning_samplerate = sf.read(warning_file)

    def __warn(self):
        sd.play(self.warning_data, self.warning_samplerate)

    def start(self):
        self.running = True
        self.last_warning_time = 0

        def input_callback(indata, frames, _time, status):
            if status:
                print(status)
            
            # perform A-weighting to account for how sensitive the human ear is to different frequencies
            # see https://gist.github.com/endolith/148112
            b, a = A_weighting(self.samplerate)
            weighted_indata = lfilter(b, a, indata)

            # calculate loudness
            # again, see https://gist.github.com/endolith/148112
            loudness = get_loudness(weighted_indata)

            if loudness > self.threshold and (time.time() - self.last_warning_time) > self.debounce:
                self.last_warning_time = time.time()
                self.__warn()
                print("{:+.2f} dB (too loud!)".format(loudness))
            else:
                print("{:+.2f} dB (acceptable)".format(loudness))

        with sd.InputStream(callback=input_callback, blocksize=self.blocksize, samplerate=self.samplerate, channels=self.channels):
            while self.running:
                sd.sleep(100)

    def stop(self):
        self.running = False
