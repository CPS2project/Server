# MongoDB Subscriber

### Description
This program is an MQTT subscriber which serves as a gateway between the client application and the objects for a scenario change.

### Features
In the MongoDB collection "scenarios" we have a document per scenario that stores scenario_id, and a set of configs for concerned objects.
When receiving a message on topic "Scenario" the program:
1. retrieves the scenario from MongoDB as a JSON object
2. parses it to get the configs array
3. for each group of objects referred as targets in this array, it publishes the new state described in the dictionary "config" and/or "fields".

### Dependencies: 
- paho.mqtt (`sudo pip3 install paho-mqtt`)
- pymongo (`sudo pip3 install pymongo`)

### Example of a scenario object stored in MongoDB
	{
		"scenario_id": 1,
		"configs": [
			["targets": {
				"building": "All",
				"floor": "All",
				"room": "All",
				"type": "All",
				"name": "All"
			},
			"config": {
				"publishing_mode": "on-demand",
				"response_latency": 0
			}],
			["targets": {
				"building": "All",
				"floor": "All",
				"room": "All",
				"type": "Lamp",
				"name": "All"
			},
			"fields": {
				"status": "OFF"
			}],
			["targets": {
				"building": "All",
				"floor": "All",
				"room": "All",
				"type": "SystemData Publisher",
				"name": "All"
			},
			"fields": {
				"status": "OFF"
			}]
		]
	}
