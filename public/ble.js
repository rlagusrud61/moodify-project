var filters = [],
    myDevice, myServer, myService, myChars, modeCharacteristic, colourCharacteristic, brightnessCharacteristic,
    myServiceUUID = '953f08c4-8c8f-46f4-a48b-07c18dfb3447',
    flag = '000',
    modeCharUUID = '58590b45-241a-4230-b020-700ac827a8fb',
    colourCharUUID = '2f59ede8-dd70-4748-94a3-3ca4f6663a42',
    brightnessCharUUID = 'c0cf5135-aae3-4a8e-ad4c-e33614753037',
    uint8array = new TextEncoder(),
    string = new TextDecoder();

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

// subscribe to changes from the meter:
function subscribeToChanges(characteristic) {
    characteristic.oncharacteristicvaluechanged = handleData;
}

function handleData(event) {
    // get the data buffer from the meter:
    const buf = new Uint8Array(event.target.value);
    console.log(string.decode(buf));
}

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

function bleDisconnect() {
    if (myDevice) {
        myDevice.gatt.disconnect();
    }
}
