#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import threading

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
        threading.Thread(target=self.mainLoop(), daemon=True).start()

    def config(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.led, GPIO.OUT)  # as led is an output device so that’s why we set it to output.
        GPIO.output(self.led, False)  # keep led off by default

        GPIO.setup(self.led, GPIO.OUT)
        GPIO.output(self.led, False)
        time.sleep(self.led)

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
        try:
            if self.autoLDR and not self.manualLED:
                value = self.rc_time()
                print(f"Ldr Value: {value}")
                if value >= 5000:
                    print("Lights are ON")
                    GPIO.output(self.led, True)
                if value < 5000:
                    print("Lights are OFF")
                    GPIO.output(self.led, False)
        except KeyboardInterrupt:
            pass
        finally:
            GPIO.cleanup()

    def manualLEDFun(self, newStatus):
        try:
            if self.manualLED:
                GPIO.output(self.led, newStatus)
        except KeyboardInterrupt:
            pass
        finally:
            GPIO.cleanup()

    def update(self, manualLED, autoLDR, LEDStatus):
        with self._lock:
            self.manualLED = manualLED
            self.autoLDR = autoLDR
            self.LEDStatus = LEDStatus

    def mainLoop(self):
        with self._lock:
            while True:
                if self.manualLED:
                    self.manualLEDFun(self.LEDStatus)
                elif self.autoLDR:
                    self.autoLDRFun()
                else:
                    pass
