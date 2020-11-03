#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import threading

from gpioprogramming.LEDStripControl import StripControl
from gpioprogramming.Util \
    import TooManyModesSelectedException, InvalidTypeError, WrongValueReceived, LengthError, \
    decodeString, decodeBrightness, decodeColour

class MoodifyLogic:

    def __init__(self, manualLED=False, autoLDR=False, musicMode=False, delayTime=0.5, brightness=0.2, numberOfPixels=10):
        self.__manualLED = manualLED
        self.__autoLDR = autoLDR
        self.__musicMode = musicMode

        self.__delayTime = delayTime
        self.__value = 0  # this variable will be used to store the ldr value
        self.__ldr = 7  # ldr is connected with pin number 7
        self.__led = 11  # led is connected with pin number 11

        self.__brightness = brightness
        self.__numberOfPixels = numberOfPixels

        self.__musicEvent = threading.Event()
        self.__updateEvent = threading.Event()
        self.__colourControl = StripControl(self.__musicEvent, self.__brightness, self.__numberOfPixels)

        self.__lock = threading.Lock()
        self.__start()

    def __start(self):
        print("Starting Thread")
        threading.Thread(target=self.__mainLoop, daemon=True).start()

    def __rc_time(self):
        count = 0

        # Output on the pin for
        GPIO.setup(self.__ldr, GPIO.OUT)
        GPIO.output(self.__ldr, False)
        time.sleep(self.__delayTime)

        # Change the pin back to input
        GPIO.setup(self.__ldr, GPIO.IN)

        # Count until the pin goes high
        while GPIO.input(self.__ldr) == 0:
            count += 1

        return count

    def __manualLEDFun(self, selected):
        if selected:
            self.__colourControl.show_colours()
        else:
            self.__colourControl.turn_off()

    def __autoLDRFun(self):
        value = self.__rc_time()
        print(f"Ldr Value: {value}")
        if value >= 10000:
            print("Lights are ON")
            self.__colourControl.show_colours()
        if value < 10000:
            print("Lights are OFF")
            self.__colourControl.turn_off()

    def __musicModeFun(self, selected):
        if selected:
            self.__colourControl.turnOnMusic()
        else:
            self.__colourControl.turnOffMusic()

    def update_mode(self, code):
        with self.__lock:
            manualLED, autoLDR, musicMode = decodeString(code)
            self.__manualLED = manualLED
            self.__autoLDR = autoLDR
            self.__musicMode = musicMode
            print("Mode Values Updated")

    def update_colour(self, colour):
        with self.__lock:
            colourInTuple = decodeColour(colour)
            self.__colourControl.setColour(colourInTuple)

    def update_brightness(self, brightness):
        with self.__lock:
            newBrightness = decodeBrightness(brightness)
            self.__colourControl.setBrightness(newBrightness)

    def __mainLoop(self):
        try:
            print("Entering Forever Loop")
            while True:
                time.sleep(self.__delayTime)
                with self.__lock:
                    if self.__musicEvent.isSet() and not self.__musicMode:
                        self.__musicEvent.clear()
                    if self.__manualLED:
                        print("Manual LED")
                        self.__manualLEDFun(self.__manualLED)
                    elif self.__autoLDR:
                        print("Auto LDR")
                        self.__autoLDRFun()
                    elif self.__musicMode:
                        print("Music Mode")
                        self.__musicModeFun(self.__musicMode)
                    elif not (self.__manualLED or self.__musicMode or self.__autoLDR):
                        print("Everything OFF")
                        self.__manualLEDFun(self.__manualLED)
                        self.__musicModeFun(self.__musicMode)
                    else:
                        pass
        except KeyboardInterrupt:
            pass
        finally:
            self.terminate()

    def terminate(self):
        self.__colourControl.turn_off()
        GPIO.cleanup()
