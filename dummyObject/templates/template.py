#!/usr/bin/env python3
#
# File: template.py
#
# Description: an example object that inherits the DummyObject class which is the top level.
#
# Features: explain how to define an object
#
#
####################################################################################################

import sys

from dummyObject import DummyObject


class Template(DummyObject):
    """ Example object """

    def __init__(self, building, floor, room, object_type, object_name, mongodb_host, mongodb_port, broker_url):
        """ initialize the object """
        super().__init__(building, floor, room, object_type, object_name, mongodb_host, mongodb_port, broker_url)

        # add the fields that define what the object can measure
        self.add_field(
            field_name="field1",
            label="field label (how the name is displayed on a GUI)",
            description="description of the field (still on a GUI)",
            type="the type of the field (String, Float, Int,...",
            function=lambda: "function which return the value of the field (optional)"
        )
        self.add_field(
            field_name="field2",
            label="Field 2",
            description="This field does not have any function, its value is updated "
                        "in the code itself (in the loop_forever function most possibly)",
            type="Float",
        )

    def custom_mqtt_reaction(self, topic, message):
        """ Any reaction to a MQTT message other than configuration change or request.
         This behaviour depends on the object and thus should be defined in children classes of DummyObject.
         """
        if topic.split("/")[-1] == "custom_topic":
            print("launching custom behaviour")

    def loop_forever(self):
        """ This method runs forever so it defines the behaviour of the object.
         The default function defined in the parent class publishes all the fields continuously
         if the publishing mode is set to continuous.
         You can override the method or keep the default one if it meets your needs.
         """
        super().loop_forever()


if __name__ == '__main__':
    if len(sys.argv) == 9:
        building, floor, room, object_type, object_name, mongo_host, mongo_port, broker_url = sys.argv[1:]
        mongo_port = int(mongo_port)

    elif len(sys.argv) == 1:
        print("Creating example object with values : ")
        print("Building: building")
        print("Floor: floor")
        print("Room: room")
        print("Object type: object_type")
        print("Object name: object_name")
        print("MongoDB host: localhost")
        print("MongoDB port: 27017")
        print("Broker url: localhost")
        building = "building"
        floor = "floor"
        room = "room"
        object_type = "object_type"
        object_name = "object_name"
        mongo_host = "localhost"
        mongo_port = 27017
        broker_url = "localhost"

    else:
        print("Usage: " + __file__ + " <building> <floor> <room> <object_type> <object_name> "
                                     "<mongo_host> <mongo_port> <broker_url>")

    # Create the object
    template_object = Template(building, floor, room, object_type, object_name, mongo_host, mongo_port, broker_url)

    # Publish and process MQTT messages forever
    template_object.loop_forever()