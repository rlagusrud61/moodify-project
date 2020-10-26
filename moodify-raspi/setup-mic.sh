#!/bin/bash
sudo apt-get update
sudo apt-get upgrade

sudo apt-get install libportaudio2 libportaudiocpp0 portaudio19-dev
sudo pip3 install pyaudio