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

        # Change the publishing mode to on-demand (it is useless to publish the state of the lamp continuously)
        self.set_parameter_value("publishing_mode", "on-demand")

        # Set a default status
        self.set_field_value("status", "ON")

    def custom_mqtt_reaction(self, topic, message):
        pass

    def loop_forever(self):
        """ Publish and process MQTT messages forever. Override parent method since this class
         does not publish any data continuously """
        self.mqtt_client.loop_forever()


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
        print("Object name: Ceiling Lamp 01")
        print("MongoDB host: localhost")
        print("MongoDB port: 27017")
        print("Broker url: localhost")
        building = "EF"
        floor = "1"
        room = "1.32"
        object_type = "Lamp"
        object_name = "Ceiling Lamp 01"
        mongo_host = "localhost"
        mongo_port = 27017
        broker_url = "localhost"

    else:
        print("Usage: " + __file__ + " <building> <floor> <room> <object_type> <object_name> "
                                     "<mongo_host> <mongo_port> <broker_url>")

    # Create the object
    my_lamp = Lamp(building, floor, room, object_type, object_name, mongo_host, mongo_port, broker_url)

    # Publish and process MQTT messages forever
    my_lamp.loop_forever()