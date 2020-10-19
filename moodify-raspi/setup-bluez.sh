#!/bin/bash
sudo apt-get update
sudo apt-get upgrade

sudo apt-get install bluetooth bluez blueman pi-bluetooth dbus -y
sudo apt-get install libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev libglib2.0-dev -y
sudo apt-get install python-dev libdbus-glib-1-dev python-gi -y

wget www.kernel.org/pub/linux/bluetooth/bluez-5.54.tar.xz
tar xvf bluez-5.54.tar.xz && cd bluez-5.54
./configure --prefix=/usr --mandir=/usr/share/man --sysconfdir=/etc --localstatedir=/var --enable-experimental
make -j4
sudo make install
cd ../
rm -f ./bluez-5.54.tar.xz
rm -f -d -r bluez-5.54

sudo pip3 install dbus-python gobject -y
sudo systemctl daemon-reload
sudo service bluetooth restart

echo "Rebooting now!!"
sudo reboot now
