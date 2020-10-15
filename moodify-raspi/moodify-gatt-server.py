#!/usr/bin/python3

import dbus

from pyble.advertisement import Advertisement
from pyble.service import Application, Service, Characteristic, Descriptor

GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 1000


class MoodifyAdvertisement(Advertisement):
    def __init__(self, index):
        Advertisement.__init__(self, index, "peripheral")
        self.add_local_name("Moodify")
        self.add_service_uuid("8af3d338-4048-428f-9bc1-a206d183ac38")
        self.include_tx_power = True


class ManualLightMode(Service):
    MAN_LIGHT_SVC_UUID = "953f08c4-8c8f-46f4-a48b-07c18dfb3447"

    def __init__(self, index):
        Service.__init__(self, index, self.MAN_LIGHT_SVC_UUID, True)
        self.add_characteristic(ColorCharacteristic(self))


class ColorCharacteristic(Characteristic):
    TEST_CHARACTERISTIC_UUID = "953f08c4-8c8f-46f4-a48b-07c18dfb3447"

    def __init__(self, service):
        self.notifying = False
        self._value = 'Off'

        Characteristic.__init__(
            self, self.TEST_CHARACTERISTIC_UUID,
            ["notify", "read", "write"], service)
        self.add_descriptor(ColourCharacteristicDescriptor(self))

    def get_value(self):
        return dbus.ByteArray(self._value.encode())

    def notify(self):
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": self.get_value()}, [])
        print('notified')

    def StartNotify(self):
        print('StartNotify')
        if self.notifying:
            return

        self.notifying = True

        value = self.get_value()
        self.notify()

    def WriteValue(self, value, options):
        print('WriteValue')
        self._value = ''.join([str(v) for v in value])
        print('New value:', self._value)
        if self.notifying:
            self.notify()

    def StopNotify(self):
        print('StopNotify')
        self.notifying = False

    def ReadValue(self, options):
        print('ReadValue')
        value = self.get_value()
        print('value to return:', value)
        return value


class ColourCharacteristicDescriptor(Descriptor):
    COLOUR_CHAR_UUID = "57a1524f-aab4-4162-911a-17d368696b15"
    COLOUR_DESCRIPTOR_VALUE = "This is used to set Light's Colour"

    def __init__(self, characteristic):
        Descriptor.__init__(
            self, self.COLOUR_CHAR_UUID,
            ["read"],
            characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.COLOUR_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value


if __name__ == '__main__':
    app = Application()
    app.add_service(ManualLightMode(0))
    app.register()

    adv = MoodifyAdvertisement(0)
    adv.register()

    try:
        app.run()
    except KeyboardInterrupt:
        app.quit()
