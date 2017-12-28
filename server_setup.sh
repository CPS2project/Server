#!/usr/bin/env bash
# File : server_setup.sh
# Description : Install the TICK stack and Mosquitto broker on a server
# Documentation : https://docs.influxdata.com/chronograf/v1.3/introduction/getting-started/

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

# Mosquitto
sudo apt-get install mosquitto
service mosquitto status

# Restart Mosquitto manually in verbose mode.
sudo service mosquitto stop
mosquitto -v

sudo apt-get install mosquitto-clients

# subscriber :
sudo apt-get install python3-pip
sudo pip3 install paho-mqtt