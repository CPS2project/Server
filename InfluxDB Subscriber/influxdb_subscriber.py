#!/usr/bin/env python3
#
# File: influxdb_subscriber.py
#
# Description: MQTT subscriber which receives the metrics sent by the objects on the topic:
# <building>/<floor>/<room>/<object_type>/<object_name>/metrics/<metrics_name>
# and the message is the value.
#
# Features: The topic structure allows to retrieve some metadata about the metrics. All of them are stored as tags associated with the metrics
# in InfluxDB. The database used is always "cps2_project" and the Measurement (equivalent for table in SQL) is the object type. Thus, all the 
# objects of a same type have their metrics in one Measurement (=table) and can be easily queried. 
#
# Dependencies:
#   - paho-mqtt (sudo pip3 install paho-mqtt)
#   - influxdb (sudo apt-get install python3-influxdb)
#
####################################################################################################

import paho.mqtt.client as mqtt
import datetime
import time

from influxdb import InfluxDBClient

def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def on_message(client, userdata, msg):
    # Use utc as timestamp
    receiveTime = datetime.datetime.utcnow()
    message = msg.payload.decode("utf-8")
    try:
        metadata = msg.topic.split("/")
        building, floor, room, object_type, object_name = metadata[:5]
        metrics_name = metadata[6]
    except:
        # bad topic structure. End the function
        return

    try:
        # Convert the string to a float so that it is stored as a number and not a string in the database
        message = float(message)
    except:
        # The message is not a float, this is not a problem
        pass

    print(str(receiveTime) + ": " + msg.topic + " " + str(message))

    json_body = [
        {
            "measurement": object_type,
            "fields": {
                "value": message
            },
            "tags": {
                "building": building,
                "floor": floor,
                "room": room,
                "object_name": object_name,
                "field_name": metrics_name
            }
        }
    ]
    dbclient.write_points(json_body)


def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)


# Set up a client for InfluxDB
dbclient = InfluxDBClient('localhost', 8086, '', '', 'cps2_project')
dbclient.create_database('cps2_project')

mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

# Uncomment to enable debug messages
# mqttc.on_log = on_log
mqttc.connect("localhost", 1883)
mqttc.subscribe("+/+/+/+/+/metrics/+")

mqttc.loop_forever()
