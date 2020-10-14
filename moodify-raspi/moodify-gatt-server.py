#!/usr/bin/env python3
import datetime

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

import array
try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject
import sys

from random import randint

mainloop = None

BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
DBUS_OM_IFACE =      'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE =    'org.freedesktop.DBus.Properties'

GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE =    'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE =    'org.bluez.GattDescriptor1'

class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'

class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotSupported'

class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotPermitted'

class InvalidValueLengthException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.InvalidValueLength'

class FailedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.Failed'


class Application(dbus.service.Object):
    """
    org.bluez.GattApplication1 interface implementation
    """
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        self.add_service(MoodLightingMode(bus, 0))
        self.add_service(ManualLightModeService(bus, 1))

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        print('GetManagedObjects')

        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()

        return response


class Service(dbus.service.Object):
    """
    org.bluez.GattService1 interface implementation
    """
    PATH_BASE = '/org/bluez/example/service'

    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_SERVICE_IFACE: {
                        'UUID': self.uuid,
                        'Primary': self.primary,
                        'Characteristics': dbus.Array(
                                self.get_characteristic_paths(),
                                signature='o')
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    def get_characteristics(self):
        return self.characteristics

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_SERVICE_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_SERVICE_IFACE]


class Characteristic(dbus.service.Object):
    """
    org.bluez.GattCharacteristic1 interface implementation
    """
    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.path + '/char' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_CHRC_IFACE: {
                        'Service': self.service.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                        'Descriptors': dbus.Array(
                                self.get_descriptor_paths(),
                                signature='o')
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        return self.descriptors

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE,
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        print('Default ReadValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        print('Default StartNotify called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        print('Default StopNotify called, returning error')
        raise NotSupportedException()

    @dbus.service.signal(DBUS_PROP_IFACE,
                         signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass


class Descriptor(dbus.service.Object):
    """
    org.bluez.GattDescriptor1 interface implementation
    """
    def __init__(self, bus, index, uuid, flags, characteristic):
        self.path = characteristic.path + '/desc' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.chrc = characteristic
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_DESC_IFACE: {
                        'Characteristic': self.chrc.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_DESC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_DESC_IFACE]

    @dbus.service.method(GATT_DESC_IFACE,
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        print ('Default ReadValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_DESC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise NotSupportedException()


class MoodLightingMode(Service):
    MLM_UUID = 'a9a23424-73cc-4140-80ea-b2eecc335760'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.MLM_UUID, True)
        self.add_characteristic(ChangeLightIntensityCharacteristic(bus, 0, self))
        self.add_characteristic(ChangeAlarmSettingCharacteristic(bus, 1, self))


class ChangeLightIntensityCharacteristic(Characteristic):
    CLI_UUID = '9de2dcc7-f9e4-4372-a559-05c41e37914e'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CLI_UUID,
                ['read', 'write'],
                service)
        self.notifying = False
        self.value = 0

    def ReadValue(self, options):
        print("moodify read: " + repr(self.value))
        res = None
        try:
            res = "0"  # TODO: read light intensity value.
            self.value = res
        except Exception as e:
            print(f"Error getting status {e}")

        return bytearray(self.value, encoding='utf8')

    def WriteValue(self, value, options):
        print("moodify write: " + repr(value))
        intensity = bytes(value).decode("utf8")

        if 0 < int(intensity) < 100:
            # write it to machine
            print(f"writing {intensity} to machine")
            try:
                res = intensity  # TODO: set light intensity.
                self.value = res
            except Exception as e:
                print(f"Error updating moodify state: {e}")
        else:
            print(f"invalid state written: {intensity}")
            raise NotPermittedException


class ChangeAlarmSettingCharacteristic(Characteristic):
    CASC_UUID = 'bb2d7591-b7e4-4fc3-ae11-66a1cb637153'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CASC_UUID,
                ['read', 'write'],
                service)

    def ReadValue(self, options):
        print("moodify read: " + repr(self.value))
        res = None
        try:
            res = "0"  # TODO: read alarm value.
            self.value = res
        except Exception as e:
            print(f"Error getting status {e}")

        return bytearray(self.value, encoding='utf8')

    def WriteValue(self, value, options):
        print("moodify write: " + repr(value))
        date_time_str = bytes(value).decode("utf8")

        if datetime.datetime.now() < datetime.datetime.strptime(date_time_str, '%b %d %Y %I:%M%p'):
            # write it to machine
            print(f"writing {date_time_str} to machine")
            try:
                res = date_time_str  # TODO: set alarm.
                self.value = res
            except Exception as e:
                print(f"Error updating moodify Alarm: {e}")
        else:
            print(f"invalid state written: {date_time_str}")
            raise NotPermittedException


class ManualLightModeService(Service):
    ML_UUID = '953f08c4-8c8f-46f4-a48b-07c18dfb3447'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.ML_UUID, True)
        self.add_characteristic(ChangeColourCharacteristic(bus, 0, self))


class ChangeColourCharacteristic(Characteristic):
    CCC_UUID = '92915619-d075-499e-a072-0da6f7325d37'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CCC_UUID,
                ['write', 'read'],
                service)
        self.value = "Off"

    def ReadValue(self, options):
        print("moodify read: " + repr(self.value))
        res = None
        try:
            res = "0"  # TODO: read value
            self.value = res
        except Exception as e:
            print(f"Error getting status {e}")

        return bytearray(self.value, encoding='utf8')

    def WriteValue(self, value, options):
        print("moodify write: " + repr(value))
        colour = bytes(value).decode("utf-8")
        if colour in self.colour_options:
            print(f"setting colour to: {colour}")
            data = {"colour": colour.lower()}
            try:
                # TODO: make LED of colour
                self.value = value
            except Exception as e:
                print(f"Error updating moodify state: {e}")
        else:
            print(f"invalid state written {colour}")
            raise NotPermittedException


class CharacteristicUserDescriptionDescriptor(Descriptor):
    """
    Writable CUD descriptor.

    """
    CUD_UUID = '2901'

    def __init__(self, bus, index, characteristic):
        self.writable = 'writable-auxiliaries' in characteristic.flags
        self.value = array.array('B', b'This is a characteristic for testing')
        self.value = self.value.tolist()
        Descriptor.__init__(
                self, bus, index,
                self.CUD_UUID,
                ['read', 'write'],
                characteristic)

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        if not self.writable:
            raise NotPermittedException()
        self.value = value


def register_app_cb():
    print('GATT application registered')


def register_app_error_cb(error):
    print('Failed to register application: ' + str(error))
    mainloop.quit()


def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if GATT_MANAGER_IFACE in props.keys():
            return o

    return None

def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    adapter = find_adapter(bus)
    if not adapter:
        print('GattManager1 interface not found')
        return

    service_manager = dbus.Interface(
            bus.get_object(BLUEZ_SERVICE_NAME, adapter),
            GATT_MANAGER_IFACE)

    app = Application(bus)

    mainloop = GObject.MainLoop()

    print('Registering GATT application...')

    service_manager.RegisterApplication(app.get_path(), {},
                                    reply_handler=register_app_cb,
                                    error_handler=register_app_error_cb)

    mainloop.run()

if __name__ == '__main__':
    main()
