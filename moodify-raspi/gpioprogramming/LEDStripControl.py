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

    def __init__(self, musicEvent, brightness=0.2, number_of_pixels=10, order=neopixel.GRB, delay=0.1):
        self.colour = OFF
        self.brightness = brightness

        self.__brightness_adjusted_colour = OFF
        self.__pixel_pin = board.D18
        self.__ORDER = order
        self.__num_pixels = number_of_pixels
        self.__pixels = neopixel.NeoPixel(
            self.__pixel_pin,
            self.__num_pixels,
            auto_write=False,
            pixel_order=self.__ORDER
        )

        self.__musicEvent = musicEvent
        self.__refresh_rgb_strip(self.colour, self.brightness)
        self.__delay = delay
        self.__signalAnalyser = SignalAnalyser()
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
        if not self.__musicEvent.isSet():
            print("Turning on Music")
            self.__musicEvent.set()

    def turnOffMusic(self):
        if self.__musicEvent.isSet():
            print("Turning off the music")
            self.__musicEvent.clear()

    def __musicLoop(self):
        try:
            while True:
                self.__musicEvent.wait()
                # TODO: do the boogy
                while self.__musicEvent.isSet():
                    colour_metadata = self.__signalAnalyser.get_next()
                    rgb = self.__signalAnalyser.getRGB(colour_metadata)
                    print("ColourMetaData:", colour_metadata)
                    print("rgb:", rgb)
                    self.__refresh_rgb_strip(rgb, 1.0)
                    self.show_colours()
                    time.sleep(0.2)
        finally:
            self.__signalAnalyser.terminate()
