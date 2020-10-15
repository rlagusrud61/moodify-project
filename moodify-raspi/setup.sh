#!/bin/bash
sudo apt-get update
sudo apt-get install libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev -y
sudo apt-get install bluetooth bluez-utils bluez dbus
sudo apt-get install virtualenv python-dev libdbus-1-dev libdbus-glib-1-dev python-gi
wget www.kernel.org/pub/linux/bluetooth/bluez-5.50.tar.xz
tar xvf bluez-5.50.tar.xz && cd bluez-5.50
./configure --prefix=/usr --mandir=/usr/share/man --sysconfdir=/etc --localstatedir=/var --enable-experimental
make -j4
sudo make install
cd ../
rm -f ./bluez-5.50.tar.xz
# rm -f -d -r ./bluez-5.50
systemctl daemon-reload
sudo service bluetooth restart
systemctl daemon-reload
sudo reboot now
