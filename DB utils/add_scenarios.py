#!/usr/bin/env python3
#
# File: add_scenarios.py
#
# Description: Create scenario documents and send them to MongoDB
#
# Dependencies:
#   - pymongo (sudo pip3 install pymongo)
#
####################################################################################################

from pymongo import MongoClient

print("Connecting to MongoDB.")

mongo_client = MongoClient("192.168.43.48", 27017)

print("Persisting new scenarios in the collection \"scenarios\" of the database "
	"\"cps2_project\" in MongoDB...")

mongo_client.cps2_project.scenarios.insert_many([
{
	"scenario_id": 1,
	"scenario_name": "shutdown",
	"configs": [
		{"targets": {
			"building": "All",
			"floor": "All",
			"room": "All",
			"type": "All",
			"name": "All"
		},
		"config": {
			"publishing_mode": "on-demand",
			"response_latency": 0
		}},
		{"targets": {
			"building": "All",
			"floor": "All",
			"room": "All",
			"type": "Lamp",
			"name": "All"
		},
		"fields": {
			"status": "OFF",
			"brightness": 0
		}},
		{"targets": {
			"building": "All",
			"floor": "All",
			"room": "All",
			"type": "SystemData Publisher",
			"name": "All"
		},
		"fields": {
			"status": "OFF"
		}}
	]
}, 

{
	"scenario_id": 2,
	"scenario_name": "christmas",
	"configs": [
		{"targets": {
			"building": "All",
			"floor": "All",
			"room": "All",
			"type": "Lamp",
			"name": "All"
		},
		"fields": {
			"status": "ON",
			"brightness": 255
		}}
	]
}, 

{
	"scenario_id": 3,
	"scenario_name": "evacuation",
	"configs": [
		{"targets": {
			"building": "EF",
			"floor": "All",
			"room": "All",
			"type": "Door",
			"name": "All"
		},
		"fields": {
			"status": "Open"
		}},
		{"targets": {
			"building": "EF",
			"floor": "All",
			"room": "All",
			"type": "Ringer",
			"name": "All"
		},
		"fields": {
			"status": "ON"
		}}
	]
}, 

{
	"scenario_id": 4,
	"scenario_name": "verbose",
	"configs": [
		{"targets": {
			"building": "All",
			"floor": "All",
			"room": "All",
			"type": "All",
			"name": "All"
		},
		"config": {
			"publishing_mode": "continuous",
			"publishing_period": 1000
		}}
	]
}
])

print("Done.")