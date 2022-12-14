"""Main script for EcoPanel BACnet add-on."""

import sys
from collections.abc import Callable
from queue import Queue
from threading import Event, Thread
from typing import Any

import uvicorn
from bacpypes.basetypes import (EventType, PropertyIdentifier,
                                PropertyReference, PropertyValue, Recipient,
                                RecipientProcess, ServicesSupported)
from bacpypes.consolelogging import ConfigArgumentParser, ConsoleLogHandler
from bacpypes.core import deferred, enable_sleeping, run, stop
from bacpypes.debugging import ModuleLogger, bacpypes_debugging
from bacpypes.local.device import LocalDeviceObject
from bacpypes.pdu import (Address, GlobalBroadcast, LocalBroadcast,
                          RemoteBroadcast)
from bacpypes.task import RecurringTask

import webAPI as api
from BACnetIOHandler import BACnetIOHandler

webserv: str = "127.0.0.1"
port = 7813

this_application = None
devices = []
rsvp = (True, None, None)

_debug = 0
_log = ModuleLogger(globals())


class uviThread(Thread):
    """Thread for Uvicorn."""

    def run(self):
        uvicorn.run(api.app, host=webserv, port=port)


class EventWatcherTask(RecurringTask):
    """Checks if event is true. When it is, do callback."""

    def __init__(self, event: Event(), callback: Callable, interval):
        RecurringTask.__init__(self, interval)
        self.event = event
        self.callback = callback

        # install it
        self.install_task()

    def process_task(self):
        if self.event.is_set():
            self.callback()
            self.event.clear()


class QueueWatcherTask(RecurringTask):
    """Checks if queue has items. When it has, do callback."""

    def __init__(self, queue: Queue(), callback: Callable, interval):
        RecurringTask.__init__(self, interval)
        self.queue = queue
        self.callback = callback

        # install it
        self.install_task()

    def process_task(self):
        if self.queue.empty():
            return
        queue_item = self.queue.get()
        self.callback(queue_item)


class RefreshDict(RecurringTask):
    """Checks if queue has items. When it has, do callback."""

    def __init__(self, interval):
        RecurringTask.__init__(self, interval)

        # install it
        self.install_task()

    def process_task(self):
        this_application.read_entire_dict()


def write_from_dict(dict_to_write: dict):
    """Write to object from a dict received by API"""
    deviceID = get_key(dict_to_write)
    for object in dict_to_write[deviceID]:
        for property in dict_to_write[deviceID][object]:
            prop_value = dict_to_write[deviceID][object].get(property)
            this_application.WriteProperty(
                object, property, prop_value, this_application.dev_id_to_addr(deviceID)
            )


def get_key(dictionary: dict) -> str:
    """Return the first key"""
    for key, value in dictionary.items():
        return key


def read_all_from_dict():
    """Read all objects from every device included in the dictionary"""
    this_application.read_entire_dict()


def main():

    args = ConfigArgumentParser(description=__doc__).parse_args()

    server = uviThread()
    server.start()

    global this_application
    global this_device

    # make a device object
    this_device = LocalDeviceObject(
        objectName=args.ini.objectname,
        objectIdentifier=int(args.ini.objectidentifier),
        maxApduLengthAccepted=int(args.ini.maxapdulengthaccepted),
        segmentationSupported=args.ini.segmentationsupported,
        vendorIdentifier=int(args.ini.vendoridentifier),
        description="BACnet Add-on for Home Assistant",
    )

    # provide max segments accepted if any kind of segmentation supported
    if args.ini.segmentationsupported != "noSegmentation":
        this_device.maxSegmentsAccepted = int(args.ini.maxsegmentsaccepted)

    # make a simple application
    this_application = BACnetIOHandler(this_device, args.ini.address)
    sys.stdout.write("Starting BACnet device on " + args.ini.address + "\n")

    # Coupling of FastAPI and BACnetIOHandler
    api.BACnetDeviceDict = this_application.BACnetDeviceDict
    api.threadingUpdateEvent = this_application.updateEvent
    who_is_watcher = EventWatcherTask(
        api.threadingWhoIsEvent, this_application.who_is, 2000
    )
    i_am_watcher = EventWatcherTask(api.threadingIAmEvent, this_application.i_am, 2000)
    read_watcher = EventWatcherTask(api.threadingReadAllEvent, read_all_from_dict, 2000)
    write_queue_watcher = QueueWatcherTask(api.writeQueue, write_from_dict, 1000)
    dict_refresher = RefreshDict(60000)

    while True:
        run()


if __name__ == "__main__":
    main()
