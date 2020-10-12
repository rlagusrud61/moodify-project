**0. Check version**

 2-1. Verify the BlueZ version by issuing the command below.

```
bluetoothctl -v
```

The result should be like this:

```shell
bluetoothctl -vbluetoothctl: 5.50
```

If the output is **different** continue with step 1, otherwise skip.

**1. Make sure you are Running bluez-5.50**

1-1. Uncompress the downloaded file.

```bash
tar xvf bluez-5.50.tar.xz
cd bluez-5.50
```

1-2. Configure.

```bash
./configure --prefix=/usr --mandir=/usr/share/man --sysconfdir=/etc --localstatedir=/var --enable-experimental 
```

1-3. Compile the source code.

```bash
make -j4
```

1-4. Install.

```shell
sudo make install
```

1-5. Reboot Raspberry Pi 3.

```shell
sudo reboot
```

**2. Verify Update**

 2-1. Verify the BlueZ version by issuing the command below.

```
bluetoothctl -v
```

The result should be like this:

```shell
bluetoothctl -vbluetoothctl: 5.50
```

**3. Test**

3-0. change directory to ble-uart-peripheral

```shell
cd ./ble-uart-peripheral
```

3-1. Run the UART service on Raspberry Pi.

```shell
python uart_peripheral.py
```

If all goes well, the output should be like this. Now, the service is  running on Raspberry Pi and it’s broadcasting BLE advertising message.
 \* See **Troubleshoot** when you get error.

You should see:

```
GATT application registered
GetAll
returning props
Advertisement registered
```

3-2. Lauch nRF Toolbox app on the smartphone and tap on “UART”.

​	[nRF Toolbox on Android](https://play.google.com/store/apps/details?id=no.nordicsemi.android.nrftoolbox&hl=en&gl=US)

​	[nRF Tooldbox for iOS](https://apps.apple.com/nl/app/nrf-toolbox/id820906058?l=en)

3-3. Tap on “CONNECT” button. Then the app will start scanning for nearby BLE devices.

3-4. Select your Raspberry Pi from the detected device list. It triggers the connection between the Raspberry Pi and the app.

\* In case of iPhone, Raspberry Pi’s host name may be displayed instead of LOCAL_NAME in the code.

3-5. Tap on “Show Log”, enter some strings and tap on “Send”.

**Troubleshoot
** If you are getting “Failed to register advertisement” error  below, it’s most likely because the advertisement wasn’t unregistered  when the script exited previously

```shell
Failed to register advertisement: org.bluez.Error.Failed: Failed to register advertisement
```

Try:

```shell
sudo systemctl restart bluetooth.service
```

**References**

[0] [Creating BLE GATT server UART service on raspberry pi](https://scribles.net/creating-ble-gatt-server-uart-service-on-raspberry-pi/) 

[1] [UART/Serial Port Emulation over BLE – Nordic Semiconductor ](https://www.nordicsemi.com/Software-and-Tools/Development-Tools/nRF-Toolbox) 

[2] [nRF Toolbox App – Nordic Semiconductor](https://www.nordicsemi.com/Software-and-Tools/Development-Tools/nRF-Toolbox) 

[3] [Turning a Raspberry Pi 3 into a Bluetooth Low Energy peripheral](https://tobiastrumm.de/2016/10/04/turning-a-raspberry-pi-3-into-a-bluetooth-low-energy-peripheral/)

