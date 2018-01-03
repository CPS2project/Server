# Dummy Object

Simulate a connected object with its configuration and sensors. It can publish a few system metrics, answer to requests from a client and change its configuration parameters on-demand. The object description is stored in a MongoDB database and is updated after each change.

Usage:

    python3 dummyObject.py <building> <groundLevel> <room> <objectType> <objectName> <mongoHost> <mongoPort> <broker_url>
or

    python3 dummyObject.py
will run the program with default values.

Dependencies: 
- paho.mqtt (`sudo pip3 install paho-mqtt`)
- psutil (`sudo pip3 install psutil`)
- pymongo (`sudo pip3 install pymongo`)
    
## Getting Started
Prerequisites : 
- you must have a MQTT broker installed. For example, Mosquitto (`sudo apt-get install mosquitto` then `sudo apt-get install mosquitto-clients`)
- the object description is stored in MongoDB so you need to install a server (doc: https://docs.mongodb.com/manual/administration/install-community/)
You can then use the program by following these steps.

1. Start a root subscriber to see all the MQTT messages:
```
mosquitto_sub -t "#" -v
```
2. In another terminal or an IDE, launch the program with all its parameters, or without parameters to use the default values:
```
python3 dummyObject.py EF 1 "Espace élèves" printer MyPrinter
```
You should see a big JSON string containing all the information about the object as well as some other logs.

3. In another terminal, try the following commands to understand the basic functionnalities:
```
# Switch the parameter "publishing_mode" from its default value "continuous" to "on-demand". The object will stop sending metrics.
mosquitto_pub -t "EF/1/Espace élèves/printer/MyPrinter/config" -m "publishing_mode=on-demand"

# Request a measure (memory usage)
mosquitto_pub -t "EF/1/Espace élèves/printer/MyPrinter/request" -m "measure,memory_usage,client01"

# Request a configuration parameter (response latency)
mosquitto_pub -t "EF/1/Espace élèves/printer/MyPrinter/request" -m "config,response_latency,client01"

# Change a configuration parameter
mosquitto_pub -t "EF/1/Espace élèves/printer/MyPrinter/config" -m "response_latency=300"

# Verify the new value of the parameter
mosquitto_pub -t "EF/1/Espace élèves/printer/MyPrinter/request" -m "config,response_latency,client01"

# Request another metrics: there should be latency now
mosquitto_pub -t "EF/1/Espace élèves/printer/MyPrinter/request" -m "measure,cpu_usage,client01"

# Request something that is not in the object properties
mosquitto_pub -t "EF/1/Espace élèves/printer/MyPrinter/request" -m "measure,wrong_name,client01"
```
### Screenshot
This is a view of the program (bottom), the root subscriber (top right) and the publisher (top left)
![alt](https://github.com/CPS2project/Server/blob/master/dummyObject/img/consoles.png)

### MongoDB Compass
MongoDB Compass is a GUI for MongoDB. This is useful to have a look on the documents (i.e. the objects) that are stored in the database. You can install it by following these instructions: https://docs.mongodb.com/compass/current/install/

Then when you run Compass (`DEBUG=* mongodb-compass` on Unbuntu), you can see the object stored. You can check that the creation\_date and the last\_modified are different since a few test were made in the program.

![alt](https://github.com/CPS2project/Server/blob/master/dummyObject/img/mongodb_compass.png)
