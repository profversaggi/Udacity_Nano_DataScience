#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Filename: TAGS-tag_types.py

Course: Udacity Data Science ND -- "Data Wrangling with MongoDB"
Project: OpenStreetMap Data Case Study

@author: Matthew R. Versaggi
@Email: profversaggi@gmail.com


***************************

Description:

This program parses the OSM file and checks the "K" values of each <tag> to see 
if there are any potential problems and report a count of four potential 
problem tag categories returned as a dictionary for interrogation. 

Those are:

  "lower", for tags that contain only lowercase letters and are valid,
  "lower_colon", for otherwise valid tags with a colon in their names,
  "problemchars", for tags with problematic characters, and
  "other", for other tags that do not fall into the other three categories.

Additionally, the data model is expanded to address the "addr:street" type of 
keys to a returned dictionary in the following format:

{"address": {"street": "Some value"}}


"""

import xml.etree.cElementTree as ET
import pprint
import re

''
LOCAL_EXAMPLE_OSMFILE = "example.osm"
PROJECT_OSMFILE = "Minneapolis_St-Paul.osm"


# Regex expressions to ferret out 3 key problems w/the tags.
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    if element.tag == "tag":
        for tag in element.iter("tag"):                
            # print "InnerTAG: ", tag.tag
            # print "InnerTAGattr: ", tag.attrib  # This is a DICTIONARY
            if "k" in tag.attrib:  # Check to see if "K" is a key in the DICT
                # print "KEY VALUE: ", tag.attrib["k"]   # value of the "K" key
                k_value = tag.attrib["k"]
                # Process Regex's:
                if lower.search(k_value) is not None:
                    # print "Lower Tags"
                    keys["lower"] +=1
                elif lower_colon.search(k_value) is not None:
                    # print "Lower Tags w/Colon"
                    keys["lower_colon"] +=1
                elif problemchars.search(k_value) is not None:
                    # print "Tags w/Problem Chars"
                    keys["problemchars"] +=1
                else:
                    # print "Other Tags"
                    keys["other"] +=1
    # print "KEYS DICT: ", keys
    return keys


# This function reads in the OSM file, creates the return dictionary, and for 
# each element that iterparse returns, it processes the element and key dict.
def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys


# This test harnass opperates against the EXAMPLE OSM File provided in class,
# and uses a simple assert test against the known number of each <tag> concern
# aggregation.
#
def local_example_osm_test():
    keys = process_map(LOCAL_EXAMPLE_OSMFILE)
    pprint.pprint(keys)
    assert keys == {'lower': 21, 'lower_colon': 18, 'other': 3, 'problemchars': 0}


# This test harnass opperates against the PROJECT OSM File from OpenStreetMap,
# and uses a simple assert test against the known number of each <tag> concern
# aggregation.
#
def primary_test():
    keys = process_map(PROJECT_OSMFILE)
    pprint.pprint(keys)
    assert keys == {'lower': 122547, 'lower_colon': 67819, 'other': 2698, 'problemchars': 0}
    
    

if __name__ == "__main__":
    primary_test()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    