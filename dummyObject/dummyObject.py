#!/usr/bin/env python3
# File : dummyObject.py
# Description : Publish some system metrics, answer to requests and change its configuration parameters on-demand.

# Dependencies :
# 	- paho-mqtt (sudo pip3 install paho-mqtt)
# 	- psutil (sudo pip3 install psutil)
#   - pymongo (sudo pip3 install pymongo)

import json
import sys
from time import sleep
from datetime import datetime

import psutil
from paho.mqtt.client import Client
from pymongo import MongoClient


class DummyObject:
    """ simulate an object with its configuration and sensors """

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
            "metrics": {
                "label": "Metrics",
                "description": "The set of metrics that the object can collect",
                "type": "JSON",
                "values": {
                    "disk_usage": {
                        "label": "Disk usage",
                        "description": "The disk usage in percent",
                        "type": "Float",
                    },
                    "memory_usage": {
                        "label": "Memory usage",
                        "description": "The RAM usage in percent",
                        "type": "Float",
                    },
                    "cpu_usage": {
                        "label": "CPU usage",
                        "description": "The CPU usage in percent",
                        "type": "Float",
                    }
                }
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
        print("### Object information ###")
        print("(Should be sent to MongoDB)")
        print(json.dumps(self.description, indent=2))
        self.base_parameters = [self.description[item]["value"]
                               for item in ["building", "room", "floor", "object_type", "object_name"]]
        self.base_topic = "/".join(self.base_parameters)

        # Persist the object description in MongoDB
        print("Connecting to MongoDB.")
        self.mongo_client = MongoClient(mongodb_host, mongodb_port)
        print("Persisting the object description in the collection \"objects\" of the database "
              "\"cps2_project\" in MongoDB.")
        self.mongo_id = self.mongo_client\
            .cps2_project\
            .objects\
            .insert_one(self.description)\
            .inserted_id

        # Initialize the MQTT client
        self.init_mqtt_client(broker_url)

    def init_mqtt_client(self, host):
        """ initialize the MQTT client with the topics to subscribe to
        and the function to manage the received messages
        """
        self.mqtt_client = Client()  # create client object
        print("Connecting to the MQTT broker", host, ".")
        self.mqtt_client.connect(host)

        def on_message(client, userdata, msg):
            message = str(msg.payload.decode("utf-8"))
            print("received message on topic " + msg.topic + ": " + message)

            message_type = msg.topic.split("/")[-1]

            if message_type == "config":
                key, value = message.split("=")
                if key in self.get_parameters_list():
                    self.set_parameter(key, value)

            elif message_type == "request":
                    request_type, parameter, client_id = message.split(",")

                    # Fake latency
                    sleep(float(self.get_parameter("response_latency")) / 1000)

                    # ask for a configuration parameter
                    if request_type == "config":
                        print("request for a configuration parameter")
                        if parameter in self.get_parameters_list():
                            self.mqtt_client.publish(self.base_topic + "/answer/" + client_id,
                                                     self.get_parameter(parameter))
                        else:
                            self.mqtt_client.publish(self.base_topic + "/answer/" + client_id,
                                                "no such parameter")

                    # ask for a measure
                    elif request_type == "measure":
                        print("request for metrics")
                        if parameter in self.get_metrics_list():
                            client.publish(self.base_topic + "/answer/" + client_id,
                                           self.get_metrics(parameter))
                        else:
                            self.mqtt_client.publish(self.base_topic + "/answer/" + client_id,
                                                "no such metrics")

        self.mqtt_client.on_message = on_message  # bind function to callback

        building, room, floor, type, name = self.base_parameters

        topics = [
            building + "/" + floor + "/" + room + "/" + type + "/" + name + "/+",
            building + "/" + floor + "/" + room + "/" + type + "/All/+",
            building + "/" + floor + "/" + room + "/All/All/+",
            building + "/" + floor + "/All/" + type + "/All/+",
            building + "/" + floor + "/All/All/All/+",
            building + "/All/All/" + type + "/All/+",
            building + "/All/All/All/All/+",
        ]
        for topic in topics:
            print("Subscribing to the topic " + topic)
            self.mqtt_client.subscribe(topic)

        self.mqtt_client.loop_start()  # start loop to process received messages

    def get_parameters_list(self):
        """ return the list of the configuration parameters """
        return self.description["config"]["values"].keys()

    def get_parameter(self, parameter):
        """ return the current value of a configuration parameter """
        return self.description["config"]["values"][parameter]["value"]

    def set_parameter(self, parameter, new_value):
        """ change the value of a configuration parameter """
        self.description["config"]["values"][parameter]["value"] = new_value
        self.mongo_client.cps2_project.objects.update_one(
            {"_id": self.mongo_id},
            {"$set": {"config.values." + parameter + ".value": new_value,
                      "last_modified.value": str(datetime.utcnow())}
             }
        )
        print("Switched the parameter " + parameter + " to " + new_value + " and updated MongoDB.")

    def get_metrics_list(self):
        """ return the list of the available metrics """
        return self.description["metrics"]["values"].keys()

    @staticmethod
    def get_metrics(name):
        """ return the current value of metrics """
        if name in ["disk_usage", "memory_usage", "cpu_usage"]:
            return {
                "disk_usage": psutil.disk_usage('/').percent,
                "memory_usage": psutil.virtual_memory().percent,
                "cpu_usage": psutil.cpu_percent(interval=None)
            }[name]
        else:
            return "No function defined for this parameter"

    def add_metrics_field(self, name, label, description, type):
        """ add a metrics field in the description of the object """
        new_field = {
            "label": label,
            "description": description,
            "type": type
        }
        self.description["metrics"]["values"][name] = new_field

        # update MongoDB
        self.mongo_client.cps2_project.objects.update_one(
            {"_id": self.mongo_id},
            {"$set": {"metrics.values." + name: new_field,
                      "last_modified.value": str(datetime.utcnow())}
             }
        )
        print("Added a new metrics field called \"" + name + "\" and updated MongoDB.")

    def loop_forever(self):
        while True:
            if self.get_parameter("publishing_mode") == "continuous":
                self.mqtt_client.publish(self.base_topic + "/disk_usage", self.get_metrics("disk_usage"))
                self.mqtt_client.publish(self.base_topic + "/memory_usage", self.get_metrics("memory_usage"))
                self.mqtt_client.publish(self.base_topic + "/cpu_usage", self.get_metrics("cpu_usage"))
                sleep(float(self.get_parameter("publishing_period")) / 1000)


if __name__ == '__main__':
    if len(sys.argv) == 9:
        building, ground_level, room, object_type, object_name, mongo_host, mongo_port, broker_url = sys.argv[1:]
        mongo_port = int(mongo_port)

    elif len(sys.argv) == 1:
        print("Creating example object with values : ")
        print("Building: EF")
        print("Ground level: 1")
        print("Room: 1.32")
        print("Object type: Dummy Object")
        print("Object name: obj01")
        print("MongoDB host: localhost")
        print("MongoDB port: 27017")
        print("Broker url: localhost")
        building = "EF"
        ground_level = "1"
        room = "1.32"
        object_type = "Dummy Object"
        object_name = "obj01"
        mongo_host = "localhost"
        mongo_port = 27017
        broker_url = "localhost"

    else:
        print("Usage: " + __file__ + " <building> <groundLevel> <room> <objectType> <objectName> "
                                     "<mongoHost> <mongoPort> <broker_url>")

    ### Create the object
    dummy_object = DummyObject(building, ground_level, room, object_type, object_name, mongo_host, mongo_port, broker_url)

    ### Test some fonctionnalities
    sleep(3)
    print("\nTest 1")
    # Test the functionnality to change a configuration parameter
    print("Publishing mode:", dummy_object.get_parameter("publishing_mode"))
    dummy_object.set_parameter("publishing_mode", "on-demand")
    print("Publishing mode:", dummy_object.get_parameter("publishing_mode"))

    sleep(1)
    print("\nTest 2")
    # Test the functionnality to add metrics on the fly
    print("Metrics list :", dummy_object.get_metrics_list())
    dummy_object.add_metrics_field(
        "new_metrics_name",
        "new_metrics_label",
        "new_metrics_description",
        "new_metrics_type"
    )
    print("Metrics list :", dummy_object.get_metrics_list())

    # Publish MQTT messages forever
    dummy_object.loop_forever()
