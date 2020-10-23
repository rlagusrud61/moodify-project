import time
import math
import threading

import board
import neopixel

OFF = (0, 0, 0)


def brightnessAdjustedColour(colour, brightness):
    return tuple(math.floor(brightness * colour) for colour in colour)


class StripControl:

    def __init__(self, e):
        self.colour = OFF
        self.brightness = 1.0

        self.__brightness_adjusted_colour = OFF
        self.__pixel_pin = board.D18
        self.__ORDER = neopixel.GRB
        self.__num_pixels = 5
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

    def __musicLoop(self):
        while True:
            self.__e.wait()
            # TODO: do the boogy
            # While in this loop use local colour/brightness declaration not the self.colour, self.brightness
            # Use brightnessAdjustedColour for proper values if needed.
            print("Playing music on the lights")
            time.sleep(1)
            pass
