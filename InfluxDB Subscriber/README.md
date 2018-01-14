# InfluxDB Subscriber

### Description
This program is a MQTT subscriber which receives the metrics sent by the objects on the topic:
\<building>/\<floor>/\<room>/\<object_type>/\<object_name>/metrics/\<metrics_name> and the message is the value.

### Features
The topic structure allows to retrieve some metadata about the metrics. All of them are stored as tags associated with the metrics in InfluxDB. The database used is always "cps2_project" and the measurement (equivalent for table in SQL) is the object type. Thus, all the objects of a same type have their metrics in one measurement (=table) and can be easily queried.

The metrics can be visualized in the Chronograf dashboard. You can also make queries, export the data in csv, create e-mail alerts using Kapacitor, and more. See the documentation [here](https://docs.influxdata.com/chronograf/v1.4/introduction/getting-started/).

### Dependencies
- paho-mqtt (sudo pip3 install paho-mqtt)
- influxdb (sudo apt-get install python3-influxdb)

