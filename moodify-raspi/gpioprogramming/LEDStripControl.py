import time
import math
import threading

import board
import neopixel

OFF = (0, 0, 0)


def brightnessAdjustedColour(colour, brightness):
    return tuple(math.floor(brightness * colour) for colour in colour)


class StripControl:
    colour: tuple[int, int, int]
    brightness: float

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

        self.__lock = threading.Lock()
        self.__e = e

        self.__refresh_rgb_strip()
        self.__delay = 0.5
        self.__start()

        self.turn_off()

    def show_colours(self):
        with self.__lock:
            self.__pixels.show()
            time.sleep(self.__delay)

    def turn_off(self):
        with self.__lock:
            self.__pixels.fill(OFF)
            self.show_colours()

    def setColour(self, newColour: tuple[int, int, int]):
        with self.__lock:
            self.colour = newColour
            self.__refresh_rgb_strip()

    def setBrightness(self, newBrightness: float):
        with self.__lock:
            self.brightness = newBrightness
            self.__refresh_rgb_strip()

    def __refresh_rgb_strip(self):
        self.__brightness_adjusted_colour = brightnessAdjustedColour(self.colour, self.brightness)
        self.__pixels.fill(self.__brightness_adjusted_colour)

    def __start(self):
        print("Starting Thread")
        threading.Thread(target=self.__musicLoop, daemon=True).start()

    def turnOnMusic(self):
        if not self.__e.isSet():
            self.__e.set()

    def turnOffMusic(self):
        if self.__e.isSet():
            self.__e.clear()

    def __musicLoop(self):
        while True:
            self.__e.wait()
            # TODO: do the boogy
            # While in this loop use local colour/brightness declaration not the self.colour, self.brightness
            # Use brightnessAdjustedColour for proper values if needed.
            pass
