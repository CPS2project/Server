#!/usr/bin/env python3
#
# File: empty_influxdb.py
#
# Description: Empty the InfluxDB database
#
# Dependencies:
#   - influxdb (sudo apt-get install python3-influxdb)
#
####################################################################################################

from influxdb import InfluxDBClient

dbclient = InfluxDBClient('localhost', 8086, '', '', 'cps2_project')
print("Drop database: cps2_project")
dbclient.drop_database("cps2_project")