#!/usr/bin/env python3
#
# File: mongoSubscriber.py
#
# ### Description
# This program is an MQTT subscriber which serves as a gateway between the client application and the objects for a scenario change.
#
# ### Features
# In the MongoDB collection "scenarios" we have a document per scenario that stores scenario_id, and a set of configs for concerned objects.
# When receiving a message on topic "Scenario" the program:
# 1- retrieves the scenario from MongoDB as a JSON object
# 2- parses it to get the configs array
# 3- for each group of objects referred as targets in this array, it publishes the new state described in the dictionary "config" and/or "fields".
#
# ### Dependencies: 
# - paho.mqtt (`sudo pip3 install paho-mqtt`)
# - pymongo (`sudo pip3 install pymongo`)
#
####################################################################################################

import time
import json
import sys
from datetime import datetime
from abc import ABCMeta, abstractmethod
from pymongo import MongoClient
from paho.mqtt.client import Client

class MongoSubscriber:
	def __init__(self):
		print("### MongoDB Client ###")
		self.Mclient = MongoClient("192.168.43.48")
		self.init_mqtt_client("192.168.43.48")
		#self.test("2")
		
	#initiate connction to MQTT
	def init_mqtt_client(self, host):
		self.mqtt_client = Client()
		self.mqtt_client.connect(host)
		def on_message(client, userdata, msg):
			message_body=msg.payload.decode("utf-8")
			scenario=self.get_scenario(message_body)
			if scenario:
				self.apply_scenario(scenario)
			else:
				print("unable to retrieve scenario:" +message_body)
		self.mqtt_client.on_message = on_message
		topic="Scenario"
		self.mqtt_client.subscribe(topic)
		self.mqtt_client.loop_forever()
	# retrive a scenario from MongoDB by scenario_id
	def get_scenario(self,scenario_id):
		id = int(scenario_id)
		return self.Mclient.cps2_project.scenarios.find_one({'scenario_id': id})
		
	# send mqtt message to set specific config 	
	def set_config(self,building,level,room,type,name,newConfig):
		obj_topic=building + "/" + level + "/" + room + "/" + type + "/" + name + "/change"
		self.mqtt_client.publish(obj_topic, newConfig)
		print("sent MQTT to "+obj_topic +" message: "+ newConfig)
		
	# parse scenario document to topics and configs then call set_configs to each one
	def apply_scenario(self,scenario):
		if 'configs' in scenario.keys():
			for obj in scenario['configs']:
				if 'targets' in obj.keys():
					targets=obj['targets']
					if 'config' in obj.keys():
						conf=obj['config']
						for key in conf.keys():
							body = "config," + key + "," + str(conf[key])
							self.set_config(targets['building'],targets['floor'],targets['room'],targets['type'],targets['name'],body)
					if 'fields' in obj.keys():
						fields=obj['fields']
						for key in fields.keys():
							body = "field," + key + "," + str(fields[key])
							self.set_config(targets['building'],targets['floor'],targets['room'],targets['type'],targets['name'],body)
				else:
					print("no targets to publish")
		else:
			print("no configs in scenario")
				
				
					
	def test(self, msg):
			
			scenario=self.get_scenario(msg)
			if scenario:
				self.apply_scenario(scenario)
			else:
				print("unable to retrieve scenario:" +msg)
			
		
if __name__ == '__main__':
    mongo_port = MongoSubscriber()