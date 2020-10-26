#!/usr/bin/env python3

import RPi.GPIO as GPIO
from gpioprogramming.LEDStripControl import StripControl
import time
import threading

SEP = ","
TRUE = "1"


def decodeString(code):
    print(f"Code in function decode:{code}")
    manualLED, autoLDR, musicMode = code[0] == TRUE, code[1] == TRUE, code[2] == TRUE
    print(f"manualLED: {manualLED}, autoLDR: {autoLDR}, musicMode:{musicMode}")
    return manualLED, autoLDR, musicMode


def decodeColour(colour):
    print(f"Colour: {colour}")
    return tuple(int(val) for val in colour.split(sep=SEP))


def decodeBrightness(brightness):
    print(f"Brightness: {brightness}")
    return float(brightness)


def terminate():
    GPIO.cleanup()


class MoodifyLogic:
    def __init__(self):
        self.manualLED = False
        self.autoLDR = False
        self.musicMode = False

        self.delayTime = 0.1
        self.value = 0  # this variable will be used to store the ldr value
        self.ldr = 7  # ldr is connected with pin number 7
        self.led = 11  # led is connected with pin number 11

        self.brightness = 0.2
        self.numberOfPixels = 5

        self.__e = threading.Event()
        self.colourControl = StripControl(self.__e)

        self._lock = threading.Lock()
        self.__start()

    def __start(self):
        print("Starting Thread")
        threading.Thread(target=self.__mainLoop, daemon=True).start()

    def __rc_time(self):
        count = 0

        # Output on the pin for
        GPIO.setup(self.ldr, GPIO.OUT)
        GPIO.output(self.ldr, False)
        time.sleep(self.delayTime)

        # Change the pin back to input
        GPIO.setup(self.ldr, GPIO.IN)

        # Count until the pin goes high
        while GPIO.input(self.ldr) == 0:
            count += 1

        return count

    def __manualLEDFun(self, selected):
        if selected:
            self.colourControl.show_colours()
        else:
            self.colourControl.turn_off()

    def __autoLDRFun(self):
        value = self.__rc_time()
        print(f"Ldr Value: {value}")
        if value >= 10000:
            print("Lights are ON")
            self.colourControl.show_colours()
        if value < 10000:
            print("Lights are OFF")
            self.colourControl.turn_off()

    def __musicModeFun(self, selected):
        if selected:
            self.colourControl.turnOnMusic()
        else:
            self.colourControl.turnOffMusic()

    def update_mode(self, code):
        with self._lock:
            manualLED, autoLDR, musicMode = decodeString(code)
            self.manualLED = manualLED
            self.autoLDR = autoLDR
            self.musicMode = musicMode
            print("Values Updated")

    def update_colour(self, colour):
        with self._lock:
            colourInTuple = decodeColour(colour)
            self.colourControl.setColour(colourInTuple)

    def update_brightness(self, brightness):
        with self._lock:
            newBrightness = decodeBrightness(brightness)
            self.colourControl.setBrightness(newBrightness)

    def __mainLoop(self):
        try:
            print("Entering Forever Loop")
            while True:
                time.sleep(5*self.delayTime)
                with self._lock:
                    print(self.manualLED, self.autoLDR, self.musicMode)
                    print(self.__e.isSet())
                    if (self.__e.isSet() and not self.musicMode):
                        print("shutting down music")
                        self.__e.clear()
                    
                    if self.manualLED:
                        print("Manual LED")
                        self.__manualLEDFun(self.manualLED)
                    elif self.autoLDR:
                        print("Auto LDR")
                        self.__autoLDRFun()
                    elif self.musicMode:
                        print("Music Mode")
                        self.__musicModeFun(self.musicMode)
                    elif not (self.manualLED or self.musicMode or self.autoLDR):
                        print("Everything OFF")
                        self.__manualLEDFun(self.manualLED)
                        self.__musicModeFun(self.musicMode)
                    else:
                        pass
        except KeyboardInterrupt:
            pass
        finally:
            terminate()
