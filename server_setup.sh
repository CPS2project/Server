#!/usr/bin/env bash
# File: server_setup.sh
# Description: Install all the programs for the server
# 
# Components:
# 	* TICK STACK 
#   Documentation: https://docs.influxdata.com/chronograf/v1.4/introduction/getting-started/
# 	
# 	* Mosquitto
#	Documentation: https://diyprojects.io/mqtt-mosquitto-communicating-connected-objects-iot/#.WkzwE3Xia00
#
#	* MongoDB
#	Documentation: 
#	general: https://docs.mongodb.com/manual/
#	Python API: https://api.mongodb.com/python/current/index.html?_ga=2.63109999.1791297804.1514988286-187034416.1514988286
###########################################################################################################################

##################
### TICK STACK ###
##################

# Telegraf
wget https://dl.influxdata.com/telegraf/releases/telegraf_1.4.4-1_amd64.deb
sudo dpkg -i telegraf_1.4.4-1_amd64.deb

# InfluxDB
wget https://dl.influxdata.com/influxdb/releases/influxdb_1.4.2_amd64.deb
sudo dpkg -i influxdb_1.4.2_amd64.deb

# Chronograf
wget https://dl.influxdata.com/chronograf/releases/chronograf_1.3.10.0_amd64.deb
sudo dpkg -i chronograf_1.3.10.0_amd64.deb

# Start the services
sudo systemctl start influxdb
sudo systemctl start telegraf
sudo systemctl start chronograf

# Check that the services are properly installed (very verbose)
# echo "influxDB databases :";
# curl "http://localhost:8086/query?q=show+databases"
#
# curl "http://localhost:8086/query?q=select+*+from+telegraf..cpu"


#################
### Mosquitto ###
#################

sudo apt-get install mosquitto
service mosquitto status

# Restart Mosquitto manually in verbose mode.
sudo service mosquitto stop
mosquitto -v &

sudo apt-get install mosquitto-clients

# subscriber :
sudo apt-get install python3-pip
sudo pip3 install paho-mqtt

###############
### MongoDB ###
###############

## MongoDB Community Server
# Import the public key used by the package management system.
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5
# Create a list file for MongoDB.
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list
# Reload local package database.
sudo apt-get update
# Install the MongoDB packages.
sudo apt-get install -y mongodb-org

## MongoDB Compass (GUI for MongoDB)
wget https://downloads.mongodb.com/compass/mongodb-compass_1.6.0_amd64.deb
sudo dpkg -i mongodb-compass_1.6.0_amd64.deb
DEBUG=* mongodb-compass &

## Python client
sudo pip3 install pymongo