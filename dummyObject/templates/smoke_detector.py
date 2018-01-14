#!/usr/bin/env python3
#
# File: smoke_detector.py
#
# Description: a smoke detector object that inherits the DummyObject class which is the top level.
#
# Features: the simplest object possible, just have one field which is its status
#
####################################################################################################

import sys
from time import time

from dummyObject import DummyObject


class SmokeDetector(DummyObject):
    """ A smoke detector with a status """

    def __init__(self, building, floor, room, object_type, object_name, mongodb_host, mongodb_port, broker_url):
        """ initialize the object """
        super().__init__(building, floor, room, object_type, object_name, mongodb_host, mongodb_port, broker_url)

        # add the fields that define what the object can measure
        self.add_field(
            field_name="status",
            label="Status",
            description="The status of the detector (ON/OFF)",
            type="String",
        )

        # Change the publishing mode to on-demand (it is useless to publish the state of the detector continuously)
        self.set_parameter_value("publishing_mode", "on-demand")

        # Set a default fields value
        self.set_field_value("status", "OFF")

    def custom_mqtt_reaction(self, topic, message):
        pass

    def set_field_value(self, field_name, new_value):
        super().set_field_value(field_name, new_value)
        # Trigger the scenario 2 when detecting some smoke
        if field_name == "status" and new_value == "ON":
            self.mqtt_client.publish("Scenario", "2")

    def loop_forever(self):
        """ Publish and process MQTT messages forever. 
        Artificially switch its status after 10 seconds for testing purpose.
        """
        while True:
            if time() - start > 10:
                self.set_field_value("status", "ON")
                exit()


if __name__ == '__main__':
    if len(sys.argv) == 9:
        building, floor, room, object_type, object_name, mongo_host, mongo_port, broker_url = sys.argv[1:]
        mongo_port = int(mongo_port)

    elif len(sys.argv) == 1:
        print("Creating example object with values : ")
        print("Building: EF")
        print("Floor: 4")
        print("Room: 4.21")
        print("Object type: Smoke Detector")
        print("Object name: Corridor smoke detector")
        print("MongoDB host: localhost")
        print("MongoDB port: 27017")
        print("Broker url: localhost")
        building = "EF"
        floor = "4"
        room = "4.21"
        object_type = "Smoke Detector"
        object_name = "Corridor smoke detector "
        mongo_host = "localhost"
        mongo_port = 27017
        broker_url = "localhost"

    else:
        print("Usage: " + __file__ + " <building> <floor> <room> <object_type> <object_name> "
                                     "<mongo_host> <mongo_port> <broker_url>")

    # Create the object
    smoke = SmokeDetector(building, floor, room, object_type, object_name, mongo_host, mongo_port, broker_url)
    start = time()
    # Publish and process MQTT messages forever
    smoke.loop_forever()