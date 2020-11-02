var filters = [],
    myDevice, myServer, myService, myChars, modeCharacteristic, colourCharacteristic, brightnessCharacteristic,
    myServiceUUID = '953f08c4-8c8f-46f4-a48b-07c18dfb3447',
    flag = '000',
    modeCharUUID = '58590b45-241a-4230-b020-700ac827a8fb',
    colourCharUUID = '2f59ede8-dd70-4748-94a3-3ca4f6663a42',
    brightnessCharUUID = 'c0cf5135-aae3-4a8e-ad4c-e33614753037',
    uint8array = new TextEncoder(),
    string = new TextDecoder();

/**
    This method is used to get the Raspberry Pi, which is the Bluetooth device.
*/
async function getDevice() {
    let services = [myServiceUUID];
    if (services) {
        filters.push({services: services});
    }

    let filterName = 'Moodify';
    if (filterName) {
        filters.push({name: filterName});
    }

    let options = {};
    options.filters = filters;

    console.log('Requesting Bluetooth Device...');
    console.log('with ' + JSON.stringify(options));
    try {
        console.log('Requesting Bluetooth Device...');
        console.log('with ' + JSON.stringify(options));
        myDevice = await navigator.bluetooth.requestDevice(options);
        console.log('> Name:             ' + myDevice.name);
        console.log('> Id:               ' + myDevice.id);
        console.log('> Connected:        ' + myDevice.gatt.connected);
        enableRadioButtons();
        await establishConnection()
    } catch(error)  {
        console.log('Argh! ' + error);
    }
}

/**
    This method gets the BLE GATT server hosted on the Raspberry Pi.
*/
async function getServer() {
    try {
        if (myDevice === undefined) {
            await getDevice()
        }
        myServer = await myDevice.gatt.connect();
    } catch (error) {
        console.log('Argh! ' + error)
    }
}

/**
    This  method gets the Moodify Service that is provided by the BLE GATT server.
*/
async function getService() {
    try {
        if (myServer === undefined) {
            await getServer()
        }
        myService = await myServer.getPrimaryService(myServiceUUID);
    } catch (error) {
        console.log('Argh! ' + error)
    }
}

/**
    This method gets all the Characteristics of the Moodify service.
*/
async function getChars() {
    try {
        if (myService === undefined) {
            await getService()
        }
        myChars = await myService.getCharacteristics();
    } catch (error) {
        console.log('Argh! ' + error)
    }
}

/**
    This method gets a specific Characteristic of the Moodify service.
*/
async function getChar() {
    try {
        if (myChars === undefined) {
            await getChars()
        }
        myChars.forEach(function (char) {
            if (modeCharUUID === char.uuid) {
                modeCharacteristic = char
            } else if (colourCharUUID === char.uuid) {
                colourCharacteristic = char
            } else if (brightnessCharUUID === char.uuid) {
                brightnessCharacteristic = char
            }
        });
        modeCharacteristic.startNotifications().then(subscribeToChanges)
    } catch (error) {
        console.log('Argh! ' + error)
    }
}

/**
    This method is used to connect the web interface to the Raspberry Pi via Bluetooth.
*/
async function establishConnection() {
    if (myDevice === undefined) {
        await getDevice()
    }
    await getServer();
    await getService();
    await getChars();
    await getChar();
    console.log(myDevice)
    console.log(myServer)
    console.log(myService)
    console.log(myChars)
    console.log(modeCharacteristic)
}

/**
    This method is used to send changes made in the Raspberry Pi to the web interface via Bluetooth.
*/
function subscribeToChanges(characteristic) {
    characteristic.oncharacteristicvaluechanged = handleData;
}

/**
    This method converts the data received from the Raspberry Pi to a human-readable format.
*/
function handleData(event) {
    // get the data buffer from the meter:
    const buf = new Uint8Array(event.target.value);
    console.log(string.decode(buf));
}

/**
    This method is no longer used.
*/
async function getCurrentValue() {
    try {
        if (modeCharacteristic === undefined) {
            await getChar();
        }
        let value = await modeCharacteristic.readValue()
        flag = string.decode(value)
        console.log(flag)
    } catch (error) {
        console.log('Argh! ' + error)
    }
}

/**
    This method writes the new mode to the mode characteristic and sends it to the Raspberry Pi.
*/
async function writeVal(newFlag) {
    if (modeCharacteristic === undefined) {
        await getChar();
    }

    let commandValue = new Uint8Array(uint8array.encode(newFlag));

    try {
        let some = await modeCharacteristic.writeValue(commandValue);
        console.log({some})
    } catch (error) {
        console.log('Argh! ' + error)
    }
}

/**
    This method writes the new colour to the colour characteristic and sends it to the Raspberry Pi.
*/
async function writeColour(colour) {
    if (colourCharacteristic === undefined) {
        await getChar();
    }

    let commandValue = new Uint8Array(uint8array.encode(colour));

    try {
        await colourCharacteristic.writeValue(commandValue);
    } catch (error) {
        console.log('Argh! ' + error)
    }
    console.log({colour})
}

/**
    This method writes the brightness as detected by the slider to the brightness characteristic
    and sends it to the Raspberry Pi.
*/
async function writeBrightness(brightness) {
    if (brightnessCharacteristic === undefined) {
        await getChar();
    }

    let commandValue = new Uint8Array(uint8array.encode(brightness));

    try {
        await brightnessCharacteristic.writeValue(commandValue);
    } catch (error) {
        console.log('Argh! ' + error)
    }
    console.log({ brightness })
}

/**
    This method is used to disconnect the web interface from the Raspberry Pi.
*/
function bleDisconnect() {
    if (myDevice) {
        myDevice.gatt.disconnect();
    }
}
