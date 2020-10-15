#!/bin/bash
echo Starting...
sudo systemctl daemon-reload
sudo service bluetooth restart
sudo hciconfig
sudo hciconfig hci0 up

sudo bluetoothctl -- power on & sudo bluetoothctl -- agent on & sudo bluetoothctl -- discoverable on
sleep 1.0
sudo python3 moodify-gatt-advertisement & sudo python3 moodify-gatt-server
echo Completed...
