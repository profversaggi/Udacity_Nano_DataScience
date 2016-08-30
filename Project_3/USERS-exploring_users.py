#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Filename: USERS-exploring_users.py

Course: Udacity Data Science ND -- "Data Wrangling with MongoDB"
Project: OpenStreetMap Data Case Study


@author: Matthew R. Versaggi
@Email: profversaggi@gmail.com

***************************

Description:

This program parses the OSM file and tallys the unique users who have 
contributed to the OSM area confined by the boundaries of this particular
extract. The return is a Python "Set" of uniqure user ID's.



"""



import xml.etree.cElementTree as ET
import pprint
import re


LOCAL_EXAMPLE_OSMFILE = "example.osm"
PROJECT_OSMFILE = "Minneapolis_St-Paul.osm"



def get_user(element):
    return


# This function itterates across the OSM file and takes each unique user
# who has contributed to this extract and places them in a Python "set", which
# it returns upon completion.
#
def process_map(filename):
    users = set()           # Python SET - forces Uniqueness of it's members.
    for _, element in ET.iterparse(filename):
        # print "ELEMENT: ", element.attrib
        if "user" in element.attrib:
            # print "USER: ", element.attrib["user"]
            users.add(element.attrib["user"])

    return users



# This test harnass opperates against the EXAMPLE OSM File provided in class,
# and uses a simple assert test against the known number of users who have
# contributed to this particular extract.
#
def local_example_osm_test():
    users = process_map(LOCAL_EXAMPLE_OSMFILE)
    pprint.pprint(users)
    assert len(users) == 8


# This test harnass opperates against the PROJECT OSM File from OpenStreetMap,
# and uses a simple assert test against the known number of users who have
# contributed to this particular extract.
#
def primary_test():
    users = process_map(PROJECT_OSMFILE)
    pprint.pprint(users)
    assert len(users) == 482
    
    
    

if __name__ == "__main__":
    primary_test()
    
    
    
    