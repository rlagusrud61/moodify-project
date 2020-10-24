from LEDStripControl import StripControl
import threading
import time

woo = StripControl(threading.Event())
print("compiles")

time.sleep(5)
woo.setColour((255,0,0))
woo.show_colours()
time.sleep(2)
woo.setColour((0,255,0))
woo.show_colours()
time.sleep(2)
woo.setBrightness(0.10)
woo.show_colours()
time.sleep(2)
woo.setColour((0,0,255))
woo.show_colours()
time.sleep(2)
woo.setBrightness(0.50)
woo.show_colours()
time.sleep(2)
woo.turn_off()
