#!/usr/bin/env python3
#
# File: influxdb_subscriber.py
#
# ### Description
# This program is a MQTT subscriber which receives the metrics sent by the objects on the topic:
# <building>/<floor>/<room>/<object_type>/<object_name>/metrics/<metrics_name> and the message is the value.
#
# ### Features
# The topic structure allows to retrieve some metadata about the metrics. All of them are stored as tags associated with the metrics in 
# InfluxDB. The database used is always "cps2_project" and the measurement (equivalent for table in SQL) is the object type. Thus, all the 
# objects of a same type have their metrics in one measurement (=table) and can be easily queried.
#
# The metrics can be visualized in the Chronograf dashboard. You can also make queries, export the data in csv, create e-mail alerts using 
# Kapacitor, and more. See the documentation [here](https://docs.influxdata.com/chronograf/v1.4/introduction/getting-started/).
#
# ### Dependencies
# - paho-mqtt (sudo pip3 install paho-mqtt)
# - influxdb (sudo apt-get install python3-influxdb)
#
####################################################################################################

import paho.mqtt.client as mqtt
import datetime
import time

from influxdb import InfluxDBClient


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
        data_type = "numericValue"
    except:
        # The message is not a float, this is not a problem
        data_type = "textValue"

    print(str(receiveTime) + ": " + msg.topic + " " + str(message))

    json_body = [
        {
            "measurement": object_type,
            "fields": {
                data_type: message
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


def on_log(mqttc, obj, level, string):
    print(string)


# Set up a client for InfluxDB
print("### InfluxDB Client  ###")
dbclient = InfluxDBClient('localhost', 8086, '', '', 'cps2_project')
dbclient.create_database('cps2_project')

mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_publish = on_publish

# Uncomment to enable debug messages
# mqttc.on_log = on_log
mqttc.connect("localhost", 1883)
mqttc.subscribe("+/+/+/+/+/metrics/+")

mqttc.loop_forever()
