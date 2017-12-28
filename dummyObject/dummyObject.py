#!/usr/bin/env python3
# File : dummyObject.py
# Description : Publish some system metrics, answer to requests and change its configuration parameters on-demand.

# Dependencies :
# 	- paho-mqtt (sudo pip3 install paho-mqtt)
# 	- psutil (sudo pip3 install psutil)

from paho.mqtt.client import Client
from time import sleep
import psutil
import sys
import json


class DummyObject:
    """ simulate an object with its configuration and sensors """

    def __init__(self, building, floor, room, object_type, object_name):
        """ initialize the object properties """

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
            }
        }
        print("### Object information ###")
        print("(Should be sent to MongoDB)")
        print(json.dumps(self.description, indent=2))
        self.base_parameters = [self.description[item]["value"]
                               for item in ["building", "room", "floor", "object_type", "object_name"]]
        self.base_topic = "/".join(self.base_parameters)

    def init_mqtt_client(self, host):
        """ initialize the MQTT client with the topics to subscribe to
        and the function to manage the received messages
        """
        self.client = Client()  # create client object
        print("connecting to the broker", host)
        self.client.connect(host)

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
                            self.client.publish(self.base_topic + "/answer/" + client_id,
                                                self.get_parameter(parameter))
                        else:
                            self.client.publish(self.base_topic + "/answer/" + client_id,
                                                "no such parameter")

                    # ask for a measure
                    elif request_type == "measure":
                        print("request for metrics")
                        if parameter in self.get_metrics_list():
                            client.publish(self.base_topic + "/answer/" + client_id,
                                           self.get_metrics(parameter))
                        else:
                            self.client.publish(self.base_topic + "/answer/" + client_id,
                                                "no such metrics")

        self.client.on_message = on_message  # bind function to callback

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
            self.client.subscribe(topic)

        self.client.loop_start()  # start loop to process received messages

    def get_parameters_list(self):
        """ return the list of the configuration parameters """
        return self.description["config"]["values"].keys()

    def get_metrics_list(self):
        """ return the list of the available metrics """
        return self.description["metrics"]["values"].keys()

    @staticmethod
    def get_metrics(name):
        """ return the current value of metrics """
        return {
            "disk_usage": psutil.disk_usage('/').percent,
            "memory_usage": psutil.virtual_memory().percent,
            "cpu_usage": psutil.cpu_percent(interval=None)
        }[name]

    def get_parameter(self, parameter):
        """ return the current value of a configuration parameter """
        return self.description["config"]["values"][parameter]["value"]

    def set_parameter(self, parameter, new_value):
        """ change the value of a configuration parameter """
        self.description["config"]["values"][parameter]["value"] = new_value
        print("Switched the parameter " + parameter + " to " + new_value)

    def loop_forever(self):
        while True:
            if self.get_parameter("publishing_mode") == "continuous":
                self.client.publish(self.base_topic + "/disk_usage", self.get_metrics("disk_usage"))
                self.client.publish(self.base_topic + "/memory_usage", self.get_metrics("memory_usage"))
                self.client.publish(self.base_topic + "/cpu_usage", self.get_metrics("cpu_usage"))
                sleep(float(self.get_parameter("publishing_period")) / 1000)


if __name__ == '__main__':
    if len(sys.argv) != 6:
        print("Usage : " + __file__ + " <building> <groundLevel> <room> <objectType> <objectName>")
        sys.exit(2)

    # general information
    broker = "localhost"
    building, ground_level, room, object_type, object_name = sys.argv[1:]

    dummy_object = DummyObject(building, ground_level, room, object_type, object_name)
    dummy_object.init_mqtt_client(broker)
    dummy_object.loop_forever()
