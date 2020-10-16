#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import threading


def decodeString(code):
    print(f"Code in function decode:{code}")
    x, y, z = code[0] == "1", code[1] == "1", code[2] == "1"
    print(f"X: {x}, Y: {y}, Z:{z}")
    return x, y, z


class LEDControl:
    def __init__(self):
        self.manualLED = False
        self.autoLDR = False
        self.LEDStatus = False
        self.delayTime = 0.1
        self.value = 0  # this variable will be used to store the ldr value
        self.ldr = 7  # ldr is connected with pin number 7
        self.led = 11  # led is connected with pin number 11
        self._lock = threading.Lock()
        self.config()
        self.start()

    def start(self):
        print("Starting Thread")
        threading.Thread(target=self.mainLoop, daemon=True).start()

    def config(self):
        print("Config")
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.led, GPIO.OUT)  # as led is an output device so that’s why we set it to output.
        GPIO.output(self.led, False)  # keep led off by default

        GPIO.setup(self.led, GPIO.OUT)
        GPIO.output(self.led, False)
        time.sleep(self.delayTime)

    def rc_time(self):
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

    def autoLDRFun(self):
        # print("Before Lock: autoLDRFun")
        # with self._lock:
        #     print("After Lock: autoLDRFun")
        if self.autoLDR and not self.manualLED:
            value = self.rc_time()
            print(f"Ldr Value: {value}")
            if value >= 10000:
                print("Lights are ON")
                GPIO.output(self.led, True)
            if value < 10000:
                print("Lights are OFF")
                GPIO.output(self.led, False)

    def manualLEDFun(self, newStatus):
        # print("Before Lock: manualLEDFun")
        # with self._lock:
        #     print("After Lock: manualLEDFun")
        GPIO.output(self.led, newStatus)

    def update(self, code):
        print("Before Lock: update")
        with self._lock:
            print("After Lock: update")
            manualLED, LEDStatus, autoLDR = decodeString(code)
            self.manualLED = manualLED
            self.autoLDR = autoLDR
            self.LEDStatus = LEDStatus
            print("Values Updated")

    def mainLoop(self):
        try:
            print("Entering Forever Loop")
            while True:
                time.sleep(2*self.delayTime)
                with self._lock:
                    print(self.manualLED, self.LEDStatus, self.LEDStatus)
                    if self.manualLED:
                        print("Manual LED")
                        self.manualLEDFun(self.LEDStatus)
                    elif self.autoLDR:
                        print("Auto LDR")
                        self.autoLDRFun()
                    elif not (self.manualLED or self.LEDStatus or self.autoLDR):
                        self.manualLEDFun(self.LEDStatus)
                        print("Manual LED- OFF")
                    else:
                        pass
        except KeyboardInterrupt:
            pass
        finally:
            self.terminate()
    
    def terminate(self):
        GPIO.cleanup()
