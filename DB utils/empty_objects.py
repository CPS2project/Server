#!/usr/bin/env python3
#
# File: empty_objects.py
#
# Description: Empty the objects collection in MongoDB
#
# Dependencies:
#   - pymongo (sudo pip3 install pymongo)
#
####################################################################################################

from pymongo import MongoClient

print("Connecting to MongoDB.")

mongo_client = MongoClient("192.168.43.48", 27017)

print("Deleting all the documents of the collection \"objects\" of the database "
	"\"cps2_project\" in MongoDB...")

mongo_client.cps2_project.objects.delete_many({})

print("Done.")