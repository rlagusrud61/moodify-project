let filters = [];
let myDevice;
let myServer;
let myService;
let myChars;
let myCharacteristic;
let myServiceUUID = '953f08c4-8c8f-46f4-a48b-07c18dfb3447';
let flag = '000';
let myCharacteristicUUID = '58590b45-241a-4230-b020-700ac827a8fb';
let uint8array = new TextEncoder()
let string = new TextDecoder()

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
            if (myCharacteristicUUID === char.uuid) {
                myCharacteristic = char
            }
        });
        myCharacteristic.startNotifications().then(subscribeToChanges)
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
    console.log(myCharacteristic)
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
        if (myCharacteristic === undefined) {
            await getChar();
        }
        let value = await myCharacteristic.readValue()
        flag = string.decode(value)
        console.log(flag)
    } catch (error) {
        console.log('Argh! ' + error)
    }
}

async function writeVal(newFlag) {
    if (myCharacteristic === undefined) {
        await getChar();
    }

    let commandValue = new Uint8Array(uint8array.encode(newFlag));

    try {
        let some = await myCharacteristic.writeValue(commandValue);
        console.log(some)
    } catch (error) {
        console.log('Argh! ' + error)
    }
}

function bleDisconnect() {
    if (myDevice) {
        myDevice.gatt.disconnect();
    }
}