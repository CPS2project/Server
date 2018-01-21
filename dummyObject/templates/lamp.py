#!/usr/bin/env python3
#
# File: lamp.py
#
# Description: a lamp object that inherits the DummyObject class which is the top level.
#
# Features: the simplest object possible, just have one field which is its status
#
####################################################################################################

import sys

from dummyObject import DummyObject


class Lamp(DummyObject):
    """ A lamp with a status """

    def __init__(self, building, floor, room, object_type, object_name, mongodb_host, mongodb_port, broker_url):
        """ initialize the object """
        super().__init__(building, floor, room, object_type, object_name, mongodb_host, mongodb_port, broker_url)

        # add the fields that define what the object can measure
        self.add_field(
            field_name="status",
            label="Status",
            description="The status of the lamp (ON/OFF)",
            type="String",
        )
        self.add_field(
            field_name="brightness",
            label="brightness",
            description="The brightness of the lamp (0-255)",
            type="Integer",
        )

        # Change the publishing mode to on-demand (it is useless to publish the state of the lamp continuously)
        self.set_parameter_value("publishing_mode", "on-demand")

        # Set a default fields value
        self.set_field_value("status", "ON")
        self.set_field_value("brightness", 200)

    def custom_mqtt_reaction(self, topic, message):
        pass

    def set_field_value(self, field_name, new_value):
        """ Override a parent method to make a custom behaviour """
        super().set_field_value(field_name, new_value)
        # Change the brightness to be consistent with the status
        if field_name == "status" and new_value == "OFF":
            self.set_field_value("brightness", 0)
        elif field_name == "status" and new_value == "ON":
            self.set_field_value("brightness", 200)


if __name__ == '__main__':
    if len(sys.argv) == 9:
        building, floor, room, object_type, object_name, mongo_host, mongo_port, broker_url = sys.argv[1:]
        mongo_port = int(mongo_port)

    elif len(sys.argv) == 1:
        print("Creating example object with values : ")
        print("Building: EF")
        print("Floor: 1")
        print("Room: 1.32")
        print("Object type: Lamp")
        print("Object name: Ceiling Lamp")
        print("MongoDB host: 192.168.43.48")
        print("MongoDB port: 27017")
        print("Broker url: 192.168.43.48")
        building = "EF"
        floor = "1"
        room = "1.32"
        object_type = "Lamp"
        object_name = "Ceiling Lamp"
        mongo_host = "192.168.43.48"
        mongo_port = 27017
        broker_url = "192.168.43.48"

    else:
        print("Usage: " + __file__ + " <building> <floor> <room> <object_type> <object_name> "
                                     "<mongo_host> <mongo_port> <broker_url>")

    # Create the object
    my_lamp = Lamp(building, floor, room, object_type, object_name, mongo_host, mongo_port, broker_url)

    # Publish and process MQTT messages forever
    my_lamp.loop_forever()