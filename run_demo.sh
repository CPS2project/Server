#!/usr/bin/env bash
# File: run_demo.sh
# Description: Run a demo for the CPS2 project.
#
# Steps:
# - Delete all the documents in MongoDB
# - Store new scenarios in MongoDB
# - Delete the database in InfluxDB
# - Add scenarios in MongoDB
# - Launch InfluxDB and MongoDB subscribers
# - Launch several object instances in terminals

sudo service mongod start

python3 "DB utils/empty_objects.py" 
python3 "DB utils/empty_scenarios.py"
python3 "DB Utils/empty_influxdb.py"
python3 "DB utils/add_scenarios.py"

gnome-terminal -- sh -c "python3 \"MongoDB Subscriber/mongoSubscriber.py\"; exec bash"
sleep 3
gnome-terminal -- sh -c "python3 \"InfluxDB Subscriber/influxdb_subscriber.py\"; exec bash"
sleep 3

gnome-terminal -- sh -c "python3 \"dummyObject/templates/lamp.py\"; exec bash"
sleep 3
gnome-terminal -- sh -c "python3 \"dummyObject/templates/systemDataPublisher.py\"; exec bash"
sleep 3
gnome-terminal -- sh -c "python3 \"dummyObject/templates/smoke_detector.py\"; exec bash"
sleep 3