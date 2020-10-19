#!/bin/bash
sudo apt-get update
sudo apt-get upgrade

sudo apt-get install python-smbus i2c-tools -y

sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0

sudo pi3 install --upgrade setuptools
sudo pi3 install RPI.GPIO adafruit-blinka

sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
sudo python3 -m pip install --force-reinstall adafruit-blinka

echo "Rebooting now!!"
sudo reboot now
