#!/bin/bash
echo Starting...
sudo systemctl daemon-reload
sleep 0.2
sudo service bluetooth restart
sleep 0.2
sudo hciconfig
sudo hciconfig hci0 up

sudo python3 moodify-gatt-server.py
sleep 0.2
sudo bluetoothctl -- advertise on
sudo bluetoothctl -- discoverable on
sleep 0.2
echo Completed...
