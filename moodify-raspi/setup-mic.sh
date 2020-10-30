#!/bin/bash
sudo apt-get update
sudo apt-get upgrade -y

sudo apt install -y python3-scipy

sudo apt-get install libportaudio2 libportaudiocpp0 portaudio19-dev -y
sudo pip3 install pyaudio sounddevice scipy