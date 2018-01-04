#!/usr/bin/env python3
#
# File: systemDataPublisher.py
#
# Description: a simple object that inherits the DummyObject class which is the top level.
#
# Features: published some metrics from the system it is running on
#
# Dependencies:
# 	- psutil (sudo pip3 install psutil)
#
####################################################################################################

import psutil
import sys

from dummyObject import DummyObject


class SystemDataPublisher(DummyObject):
    """ Simple object that publishes some metrics from the system it is running on """

    def __init__(self, building, floor, room, object_type, object_name, mongodb_host, mongodb_port, broker_url):
        """ initialize the object """
        super().__init__(building, floor, room, object_type, object_name, mongodb_host, mongodb_port, broker_url)

        # add the fields that define what the object can measure
        self.add_field(
            field_name="disk_usage",
            label="Disk usage",
            description="The disk usage in percent",
            type="Float",
            function=lambda: psutil.disk_usage('/').percent
        )
        self.add_field(
            field_name="memory_usage",
            label="Memory usage",
            description="The RAM usage in percent",
            type="Float",
            function=lambda: psutil.virtual_memory().percent
        )
        self.add_field(
            field_name="cpu_usage",
            label="CPU usage",
            description="The CPU usage in percent",
            type="Float",
            function=lambda: psutil.cpu_percent(interval=None)
        )

    def custom_mqtt_reaction(self, topic, message):
        pass


if __name__ == '__main__':
    if len(sys.argv) == 9:
        building, floor, room, object_type, object_name, mongo_host, mongo_port, broker_url = sys.argv[1:]
        mongo_port = int(mongo_port)

    elif len(sys.argv) == 1:
        print("Creating example object with values : ")
        print("Building: EF")
        print("Floor: 1")
        print("Room: 1.32")
        print("Object type: systemData Publisher")
        print("Object name: Computer 01")
        print("MongoDB host: localhost")
        print("MongoDB port: 27017")
        print("Broker url: localhost")
        building = "EF"
        floor = "1"
        room = "1.32"
        object_type = "systemData Publisher"
        object_name = "Computer 01"
        mongo_host = "localhost"
        mongo_port = 27017
        broker_url = "localhost"

    else:
        print("Usage: " + __file__ + " <building> <floor> <room> <object_type> <object_name> "
                                     "<mongo_host> <mongo_port> <broker_url>")

    # Create the object
    my_publisher = SystemDataPublisher(building, floor, room, object_type, object_name, mongo_host, mongo_port, broker_url)

    # Publish and process MQTT messages forever
    my_publisher.loop_forever()