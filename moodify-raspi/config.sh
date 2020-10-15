#!/bin/bash
echo Starting...
sudo systemctl daemon-reload
sleep 0.2
sudo service bluetooth restart
sleep 0.2
sudo hciconfig
sudo hciconfig hci0 up

sudo bluetoothctl -- power on & sudo bluetoothctl -- advertise on & sudo bluetoothctl -- discoverable on &
sleep 0.2
sudo python3 moodify-gatt-server.py
sleep 0.2
sudo bluetoothctl -- advertise off & sudo bluetoothctl -- discoverable off & sudo bluetoothctl -- power off &
echo Completed...
