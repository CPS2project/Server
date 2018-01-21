#!/usr/bin/env python3
#
# File: dummyObject.py
#
# Description: Top level dummy object. It is not implementable as is (like abstract classes in java)
# so it should have children classes.
#
# Features: manage basic behaviour such as answers to requests from MQTT messages,
# configuration parameters read / write, and write operations in MongoDB.
#
# Dependencies:
# 	- paho-mqtt (sudo pip3 install paho-mqtt)
#   - pymongo (sudo pip3 install pymongo)
#
####################################################################################################

import json
import sys
from datetime import datetime
from time import sleep
from abc import ABCMeta, abstractmethod

from paho.mqtt.client import Client
from pymongo import MongoClient


class DummyObject:
    """ simulate an object with its configuration and sensors """
    __metaclass__ = ABCMeta

    def __init__(self, building, floor, room, object_type, object_name, mongodb_host, mongodb_port, broker_url):
        """ initialize the object """

        # The following variable contains all the information about the object with
        # its location, configuration and the metrics it can collect.
        # These information should be persisted in MongoDB to be accessible for the clients.
        #
        # Each field has a label and a description to be displayed on a GUI
        # and a type to know how to display its value.
        #
        # The configuration parameters also have the list of possible values
        # to enable a client to send valid values if they want to change them.
        self.description = {
            "building": {
                "label": "Building",
                "description": "The building where the object is located",
                "type": "String",
                "value": building
            },
            "floor": {
                "label": "Floor",
                "description": "The floor where the object is located",
                "type": "String",
                "value": floor
            },
            "room": {
                "label": "Room",
                "description": "The room where the object is located",
                "type": "String",
                "value": room
            },
            "object_type": {
                "label": "Object type",
                "description": "The type of the object",
                "type": "String",
                "value": object_type
            },
            "object_name": {
                "label": "Object name",
                "description": "The name of the object",
                "type": "String",
                "value": object_name
            },
            "config": {
                "label": "Configuration",
                "description": "The set of parameters which define the object behaviour",
                "type": "JSON",
                "values": {
                    "publishing_mode": {
                        "label": "Publishing mode",
                        "description": "The way the object publishes its data",
                        "type": "String",
                        "possible_values": ["continuous", "on-demand"],
                        "value": "continuous"
                    },
                    "publishing_period": {
                        "label": "Publishing period",
                        "description": "The duration in milliseconds between two batches of data in continuous mode",
                        "type": "Integer",
                        "possible_values": "positive",
                        "value": 2000
                    },
                    "response_latency": {
                        "label": "Response latency",
                        "description": "The delay in milliseconds between the reception of a request "
                                       "and the sending of the answer",
                        "type": "Integer",
                        "possible_values": "positive",
                        "value": 0
                    },
                }
            },
            "fields": {
                "label": "Fields",
                "description": "A set of fields such as metrics that the object can collect,"
                               "or a status, etc.",
                "type": "JSON",
                "values": {}
            },
            "creation_date": {
                "label": "Creation date",
                "description": "The date when the object was created",
                "type": "String",
                "value": str(datetime.utcnow())
            },
            "last_modified": {
                "label": "Last modification date",
                "description": "The date when the object was last modified",
                "type": "String",
                "value": str(datetime.utcnow())
            }
        }

        # Container for the values of the fields (either functions or static values)
        # Should be filled by the "add_field" function called in the children classes
        self.fields = {}

        # Base parameters such as the location and the type of the object
        self.base_parameters = {
            "building": self.description["building"]["value"],
            "floor": self.description["floor"]["value"],
            "room": self.description["room"]["value"],
            "object_type": self.description["object_type"]["value"],
            "object_name": self.description["object_name"]["value"]
        }

        # Base topic for the MQTT messages
        self.base_topic = "/".join(self.base_parameters.values())

        print("")
        print("### Object information ###")
        print("(Should be sent to MongoDB)")
        print(json.dumps(self.description, indent=2))

        # Persist the object description in MongoDB
        print("Connecting to MongoDB.")
        self.mongo_client = MongoClient("192.168.43.48")
        print("Persisting the object description in the collection \"objects\" of the database "
              "\"cps2_project\" in MongoDB.")
        self.mongo_id = self.mongo_client\
            .cps2_project\
            .objects\
            .insert_one(self.description)\
            .inserted_id

        # Initialize the MQTT client
        self.init_mqtt_client(broker_url)

    @abstractmethod
    def custom_mqtt_reaction(self, topic, message):
        """ Any reaction to a MQTT message other than configuration change or request.
         This behaviour depends on the object and thus should be defined in children classes.
         """
        raise NotImplementedError("Must override method custom_mqtt_reaction")

    def init_mqtt_client(self, host):
        """ initialize the MQTT client with the topics to subscribe to
        and the function to manage the received messages
        """
        self.mqtt_client = Client()  # create client object
        print("Connecting to the MQTT broker", host, ".")
        self.mqtt_client.connect(host)

        def on_message(client, userdata, msg):
            """ callback function to process mqtt messages """
            message_type = msg.topic.split("/")[-1]
            message = str(msg.payload.decode("utf-8"))
            print("\nreceived message on topic " + msg.topic + ": " + message)

            # The message should contain 3 things:
            # either <field/config>, parameter_name, new_value
            # or <field/config>, parameter_name, client_id
            if len(message.split(",")) != 3:
                print("Bad message structure")
                return 0

            # React to custom topics. Should be implemented in a concrete class depending on the behaviour to simulate.
            self.custom_mqtt_reaction(msg.topic, message)

            # The client wants to change the value of a parameter
            if message_type == "change":
                request_type, parameter_name, new_value = message.split(",")
                if request_type == "config" and parameter_name in self.get_parameters_list():
                    self.set_parameter_value(parameter_name, new_value)
                elif request_type == "field" and parameter_name in self.get_fields_list():
                    self.set_field_value(parameter_name, new_value)

            # The client requests the value of a parameter
            elif message_type == "request":
                    request_type, parameter_name, client_id = message.split(",")

                    # Fake latency
                    sleep(float(self.get_parameter_value("response_latency")) / 1000)

                    # ask for a configuration parameter
                    if request_type == "config":
                        print("request for a configuration parameter")
                        if parameter_name in self.get_parameters_list():
                            self.mqtt_client.publish(self.base_topic + "/answer/" + client_id,
                                                     self.get_parameter_value(parameter))
                        else:
                            self.mqtt_client.publish(self.base_topic + "/answer/" + client_id,
                                                     "no such parameter")

                    # ask for a field
                    elif request_type == "field":
                        print("request for a field")
                        if parameter_name in self.get_fields_list():
                            client.publish(self.base_topic + "/answer/" + client_id,
                                           self.get_field_value(parameter_name))
                        else:
                            self.mqtt_client.publish(self.base_topic + "/answer/" + client_id,
                                                     "no such field")

        self.mqtt_client.on_message = on_message  # bind function to callback

        building, floor, room, type, name = self.base_parameters.values()

        topics = [
            building + "/" + floor + "/" + room + "/" + type + "/" + name + "/+",
            building + "/" + floor + "/" + room + "/" + type + "/All/+",
            building + "/" + floor + "/" + room + "/All/All/+",
            building + "/" + floor + "/All/" + type + "/All/+",
            building + "/" + floor + "/All/All/All/+",
            building + "/All/All/" + type + "/All/+",
            building + "/All/All/All/All/+",
            "All/All/All/" + type + "/All/+",
            "All/All/All/All/All/+"
        ]
        for topic in topics:
            print("Subscribing to the topic " + topic)
            self.mqtt_client.subscribe(topic)

        self.mqtt_client.loop_start()  # start loop to process received messages

    def get_parameters_list(self):
        """ return the list of the configuration parameters """
        return self.description["config"]["values"].keys()

    def get_parameter_value(self, parameter_name):
        """ return the current value of a configuration parameter """
        if parameter_name in self.description["config"]["values"].keys():
            return self.description["config"]["values"][parameter_name]["value"]
        else:
            return "No such parameter"

    def set_parameter_value(self, parameter_name, new_value):
        """ change the value of a configuration parameter """
        self.description["config"]["values"][parameter_name]["value"] = new_value
        # Update MongoDB
        self.mongo_client.cps2_project.objects.update_one(
            {"_id": self.mongo_id},
            {"$set": {"config.values." + parameter_name + ".value": new_value,
                      "last_modified.value": str(datetime.utcnow())}
            }
        )
        print("Switched the parameter " + parameter_name + " to " + new_value + " and updated MongoDB.")

    def get_fields_list(self):
        """ return the list of the available fields """
        return self.description["fields"]["values"].keys()

    def get_field_value(self, field_name):
        """ return the current value of a field. """
        if field_name in self.fields.keys():
            # the value of the field is given either by a function or the system
            if self.description["fields"]["values"][field_name]["source"] == "function":
                return self.fields[field_name]()
            elif self.description["fields"]["values"][field_name]["source"] == "system":
                return self.fields[field_name]
        else:
            return "No such field"

    def set_field_value(self, field_name, new_value):
        """ change the value of a field """
        new_value = str(new_value)
        self.fields[field_name] = new_value
        # Send the new value to InfluxDB
        self.mqtt_client.publish(self.base_topic + "/metrics/" + field_name,
                                             self.get_field_value(field_name))
        print("Switched the field " + field_name + " to " + new_value + " and sent the new value to InfluxDB.")

    def add_field(self, field_name, label, description, type, function=None):
        """ add a field in the description of the object.
         The value of the field is either given by a function, or updated by the system. """
        new_field = {
            "label": label,
            "description": description,
            "type": type,
        }
        if function is not None:
            new_field["source"] = "function"
            self.fields[field_name] = function
        else:
            new_field["source"] = "system"
            self.fields[field_name] = "No value"
        self.description["fields"]["values"][field_name] = new_field

        # update MongoDB
        self.mongo_client.cps2_project.objects.update_one(
            {"_id": self.mongo_id},
            {"$set": {"fields.values." + field_name: new_field,
                      "last_modified.value": str(datetime.utcnow())}
             }
        )
        print("Added a new field called \"" + field_name + "\" and updated MongoDB.")

    def loop_forever(self):
        """ Publish and process MQTT messages forever """
        while True:
            if self.get_parameter_value("publishing_mode") == "continuous":
                for field_name in self.get_fields_list():
                    self.mqtt_client.publish(self.base_topic + "/metrics/" + field_name,
                                             self.get_field_value(field_name))
                sleep(float(self.get_parameter_value("publishing_period")) / 1000)


if __name__ == '__main__':
    if len(sys.argv) == 9:
        building, floor, room, object_type, object_name, mongo_host, mongo_port, broker_url = sys.argv[1:]
        mongo_port = int(mongo_port)

    elif len(sys.argv) == 1:
        print("Creating example object with values : ")
        print("Building: EF")
        print("Floor: 1")
        print("Room: 1.32")
        print("Object type: Dummy Object")
        print("Object name: obj01")
        print("MongoDB host: localhost")
        print("MongoDB port: 27017")
        print("Broker url: localhost")
        building = "EF"
        floor = "1"
        room = "1.32"
        object_type = "Dummy Object"
        object_name = "obj01"
        mongo_host = "localhost"
        mongo_port = 27017
        broker_url = "localhost"

    else:
        print("Usage: " + __file__ + " <building> <floor> <room> <object_type> <object_name> "
                                     "<mongo_host> <mongo_port> <broker_url>")

    ### Create the object
    dummy_object = DummyObject(building, floor, room, object_type, object_name, mongo_host, mongo_port, broker_url)

    ### Test some fonctionnalities
    sleep(3)
    print("\nTest 1")
    # Test the functionnality to change a configuration parameter
    print("Publishing mode:", dummy_object.get_parameter_value("publishing_mode"))
    dummy_object.set_parameter_value("publishing_mode", "on-demand")
    print("Publishing mode:", dummy_object.get_parameter_value("publishing_mode"))

    sleep(1)
    print("\nTest 2")
    # Test the functionnality to add metrics on the fly
    print("Metrics list :", dummy_object.get_fields_list())
    dummy_object.add_field(
        "new_metrics_name",
        "new_metrics_label",
        "new_metrics_description",
        "new_metrics_type"
    )
    print("Metrics list :", dummy_object.get_fields_list())

    # Publish and process MQTT messages forever
    dummy_object.loop_forever()
