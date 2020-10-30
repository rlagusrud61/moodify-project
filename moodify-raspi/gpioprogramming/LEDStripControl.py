import time
import math
import threading
import board
import neopixel
from gpioprogramming.SoundAnalyser import SignalAnalyser, wavelength_to_rgb

OFF = (0, 0, 0)


def brightnessAdjustedColour(colour, brightness):
    return tuple(math.floor(brightness * colour) for colour in colour)


class StripControl:

    def __init__(self, e):
        self.colour = OFF
        self.brightness = 0.5

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
        self.__signalAnalyser = SignalAnalyser()
        self.__refresh_rgb_strip(self.colour, self.brightness)
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
        self.__refresh_rgb_strip(self.colour, self.brightness)

    def setBrightness(self, newBrightness):
        self.brightness = newBrightness
        print(f"New Brightness: {self.brightness}")
        self.__refresh_rgb_strip(self.colour, self.brightness)

    def __refresh_rgb_strip(self, colour, brightness):
        self.__brightness_adjusted_colour = brightnessAdjustedColour(colour, brightness)
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

    def __musicLoop(self):

        try:
            while True:
                #print("Going to wait!!!")
                self.__e.wait()
                #print("Finsihed Waiting!!")
                # TODO: do the boogy
                # While in this loop use local colour/brightness declaration not the self.colour, self.brightness
                # Use brightnessAdjustedColour for proper values if needed.
                #print("finished waiting. Goto BOOGIE")
                while self.__e.isSet():
                    targetFreq, brightness = self.__signalAnalyser.get_next_pair()
                    print("Frequency:", targetFreq)
                    print("Brightness:", brightness)
                    rgb_colour = wavelength_to_rgb(targetFreq)
                    self.__refresh_rgb_strip(rgb_colour, brightness)
                    self.show_colours()
                    time.sleep(0.01)
        finally:
            self.__signalAnalyser.terminate()
