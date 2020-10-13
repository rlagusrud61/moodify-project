#!/usr/bin/env python3

import logging

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

from ble import (
    Advertisement,
    Characteristic,
    Service,
    Application,
    find_adapter,
    Descriptor,
    Agent,
)

import struct
import requests
import array
from enum import Enum

import sys

MainLoop = None
try:
    from gi.repository import GLib

    MainLoop = GLib.MainLoop
except ImportError:
    import gobject as GObject

    MainLoop = GObject.MainLoop

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logHandler = logging.StreamHandler()
filelogHandler = logging.FileHandler("logs.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logHandler.setFormatter(formatter)
filelogHandler.setFormatter(formatter)
logger.addHandler(filelogHandler)
logger.addHandler(logHandler)

MoodifyBaseUrl = "https://team8.utwente.io/moodify/"

mainloop = None

BLUEZ_SERVICE_NAME = "org.bluez"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"
LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"
LE_ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"


class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.freedesktop.DBus.Error.InvalidArgs"


class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.NotSupported"


class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.NotPermitted"


class InvalidValueLengthException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.InvalidValueLength"


class FailedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.Failed"


def register_app_cb():
    logger.info("GATT application registered")


def register_app_error_cb(error):
    logger.critical("Failed to register application: " + str(error))
    mainloop.quit()


class MoodifyLightModeService(Service):
    MOODIFY_LIGHT_MODE_SVC_UUID = "a20d4a98-1d52-4335-aea6-fb1d3f16b9db"

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.MOODIFY_LIGHT_MODE_SVC_UUID, True)
        self.add_characteristic(LightIntensityControlCharacteristic(bus, 0, self))
        self.add_characteristic(AlarmCharacteristic(bus, 1, self))


class MoodifyManualModeService(Service):
    MOODIFY_MANUAL_MODE_SVC_UUID = "4c0d6577-01c1-49bb-b858-d4d3bd67862a"

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.MOODIFY_LIGHT_MODE_SVC_UUID, True)
        self.add_characteristic(ColourControlCharacteristic(bus, 0, self))


# TODO: When we do music mode.
# class MoodifyMusicModeService(Service):
#     MOODIFY_MANUAL_MODE_SVC_UUID = "1fa8c75e-294d-48e7-8073-54266ece9ec5"
#
#     def __init__(self, bus, index):
#         Service.__init__(self, bus, index, self.MOODIFY_LIGHT_MODE_SVC_UUID, True)
#         self.add_characteristic(MusicModeToggleCharacteristic(bus, 0, self))
#         self.add_characteristic(AutoShutdownCharacteristic(bus, 0, self))


class ColourControlCharacteristic(Characteristic):
    uuid = "105a923c-cd2d-4233-ad3c-124419004741"
    description = b"Get/set lamp colour state {}"

    # TODO: add better description

    class Colour(Enum):
        red = "red"
        blue = "blue"
        unknown = "UNKNOWN"

        @classmethod
        def has_value(cls, value):
            return value in cls._value2member_map_

    colour_options = {"red", "blue", "UNKNOWN"}

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index, self.uuid, ["encrypt-read", "encrypt-write"], service,
        )

        self.value = [0xFF]
        self.add_descriptor(CharacteristicUserDescriptionDescriptor(bus, 1, self))

    def ReadValue(self, options):
        logger.debug("moodify read: " + repr(self.value))
        res = None
        try:
            res = 0  # TODO: read value
            self.value = bytearray(f"{res}", encoding="utf8")
        except Exception as e:
            logger.error(f"Error getting status {e}")
            self.value = bytearray(self.Colour.unknown, encoding="utf8")

        return self.value

    def WriteValue(self, value, options):
        logger.debug("power Write: " + repr(value))
        colour = bytes(value).decode("utf-8")
        if self.Colour.has_value(colour):
            # write it to machine
            logger.info(f"setting colour to: {colour}")
            data = {"colour": colour.lower()}
            try:
                # TODO: make LED of colour
                pass
            except Exceptions as e:
                logger.error(f"Error updating moodify state: {e}")
        else:
            logger.info(f"invalid state written {colour}")
            raise NotPermittedException

        self.value = value


class LightIntensityControlCharacteristic(Characteristic):
    uuid = "ad3e02a1-b72b-4d17-ac48-b5978e60735d"
    description = b"Get/set light intensity of the moodify"

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index, self.uuid, ["encrypt-read", "encrypt-write"], service,
        )

        self.value = []
        self.add_descriptor(CharacteristicUserDescriptionDescriptor(bus, 1, self))

    def ReadValue(self, options):
        logger.info("moodify read: " + repr(self.value))
        res = None
        try:
            res = 0  # TODO: read light intensity value.
            self.value = res
        except Exception as e:
            logger.error(f"Error getting status {e}")

        return self.value

    def WriteValue(self, value, options):
        logger.info("moodify write: " + repr(value))
        cmd = bytes(value).decode("utf-8")

        # write it to machine
        logger.info(f"writing {cmd} to machine")
        data = {"cmd": "setLightIntensity", "state": cmd.lower()}
        try:
            res = data  # TODO: set light intensity.
            logger.info(res)
        except Exceptions as e:
            logger.error(f"Error updating moodify state: {e}")
            raise


class AlarmCharacteristic(Characteristic):
    uuid = "2b8f6a21-d667-48c6-be92-e502311531ac"
    description = b"Get/set alarm for given time."

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index, self.uuid, ["encrypt-read", "encrypt-write"], service,
        )

        self.value = []
        self.add_descriptor(CharacteristicUserDescriptionDescriptor(bus, 1, self))

    def ReadValue(self, options):
        logger.info("alarm read: " + repr(self.value))
        res = None
        try:
            res = 0  # TODO: read from place where alarm timing are stored.
            self.value = res
        except Exception as e:
            logger.error(f"Error getting status {e}")

        return self.value

    def WriteValue(self, value, options):
        logger.info("alarm write: " + repr(value))
        cmd = bytes(value)

        # write it to machine
        logger.info(f"writing {cmd} to moodify")
        data = {"cmd": "alarm", "time": cmd}
        try:
            res = data  # TODO: write to file of alarm.
            logger.info(res)
        except Exceptions as e:
            logger.error(f"Error updating machine state: {e}")
            raise


class CharacteristicUserDescriptionDescriptor(Descriptor):
    """
    Writable CUD descriptor.
    """

    CUD_UUID = "2901"

    def __init__(
            self, bus, index, characteristic,
    ):
        self.value = array.array("B", characteristic.description)
        self.value = self.value.tolist()
        Descriptor.__init__(self, bus, index, self.CUD_UUID, ["read"], characteristic)

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        if not self.writable:
            raise NotPermittedException()
        self.value = value


class MoodifyAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, "peripheral")
        self.add_manufacturer_data(
            0xFFFF, [0x26, 0x08],
        )
        self.add_service_uuid(MoodifyLightModeService.MOODIFY_LIGHT_MODE_SVC_UUID)
        self.add_service_uuid(MoodifyManualModeService.MOODIFY_MANUAL_MODE_SVC_UUID)
        # self.add_service_uuid(MoodifyMusicModeService.MOODIFY_MUSIC_MODE_SVC_UUID)

        self.add_local_name("Moodify")
        self.include_tx_power = True


def register_ad_cb():
    logger.info("Advertisement registered")


def register_ad_error_cb(error):
    logger.critical("Failed to register advertisement: " + str(error))
    mainloop.quit()


AGENT_PATH = "/com/moodify/agent"


def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    # get the system bus
    bus = dbus.SystemBus()
    # get the ble controller
    adapter = find_adapter(bus)

    if not adapter:
        logger.critical("GattManager1 interface not found")
        return

    adapter_obj = bus.get_object(BLUEZ_SERVICE_NAME, adapter)

    adapter_props = dbus.Interface(adapter_obj, "org.freedesktop.DBus.Properties")

    # powered property on the controller to on
    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

    # Get manager objs
    service_manager = dbus.Interface(adapter_obj, GATT_MANAGER_IFACE)
    ad_manager = dbus.Interface(adapter_obj, LE_ADVERTISING_MANAGER_IFACE)

    advertisement = MoodifyAdvertisement(bus, 0)
    obj = bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez")

    agent = Agent(bus, AGENT_PATH)

    app = Application(bus)
    app.add_service(MoodifyLightModeService(bus, 2))
    app.add_service(MoodifyManualModeService(bus, 3))

    #  TODO: when we do music mode

    # app.add_service(MoodifyMusicModeService(bus, 4))

    mainloop = MainLoop()

    agent_manager = dbus.Interface(obj, "org.bluez.AgentManager1")
    agent_manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")

    ad_manager.RegisterAdvertisement(
        advertisement.get_path(),
        {},
        reply_handler=register_ad_cb,
        error_handler=register_ad_error_cb,
    )

    logger.info("Registering GATT application...")

    service_manager.RegisterApplication(
        app.get_path(),
        {},
        reply_handler=register_app_cb,
        error_handler=[register_app_error_cb],
    )

    agent_manager.RequestDefaultAgent(AGENT_PATH)

    mainloop.run()
    # ad_manager.UnregisterAdvertisement(advertisement)
    # dbus.service.Object.remove_from_connection(advertisement)


if __name__ == "__main__":
    main()
