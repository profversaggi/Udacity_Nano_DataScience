#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Filename: MAPPARSER-iterative_parsing.py

Course: Udacity Data Science ND -- "Data Wrangling with MongoDB"
Project: OpenStreetMap Data Case Study

@author: Matthew R. Versaggi
@Email: profversaggi@gmail.com


***************************
 
Description:

This program leverages iterative parsing to process the OSM file and determine
how many of each top level tag in the dataset exist. The result is injected 
into a dictionary with the tag names as keys and their tallys as values.



"""

import xml.etree.cElementTree as ET
import pprint

LOCAL_EXAMPLE_OSMFILE = "example.osm"
PROJECT_OSMFILE = "Minneapolis_St-Paul.osm"


# This function counts the number of tags it finds in the OSM file and returns
# a dictionary containing them.
#
def count_tags(filename):
    tag_dict = {}
    
    # Inspiration from the InMemory Tree Parsing Example
    # tree = ET.parse(filename)   # Parse article into a Tree
    # root = tree.getroot()       # from the Tree, we get the root element.
    # for elem in tree.iter():
    
    # Using the IterParser instead of inmemory tree since data is tii big.
    for event, elem in ET.iterparse(filename):
        # print elem.tag, elem.attrib
        # Check if tag is in the dictionary
        if elem.tag in tag_dict:
            tag_dict[elem.tag] += 1
        else:
            tag_dict[elem.tag] = 1
            
    return tag_dict


# This test harnass opperates against the EXAMPLE OSM File provided in class,
# and uses a simple assert test against the known number of each tag that is 
# known to exist in this particular dataset.
#
def local_example_osm_test():
    tags = count_tags(LOCAL_EXAMPLE_OSMFILE)
    pprint.pprint(tags)
    assert tags == {'bounds': 1,
                     'member': 3,
                     'nd': 11,
                     'node': 23,
                     'osm': 1,
                     'relation': 1,
                     'tag': 42,
                     'way': 2}

# This test harnass opperates against the PROJECT OSM File from OpenStreetMap,
# and uses a simple assert test against the known number of each tag that is 
# known to exist in this particular dataset.
#
def primary_test():
    tags = count_tags(PROJECT_OSMFILE)
    pprint.pprint(tags)
    assert tags == {'bounds': 1,
                    'member': 7191,
                    'nd': 407076,
                    'node': 326110,
                    'osm': 1,
                    'relation': 546,
                    'tag': 193064,
                    'way': 52036}
                     
                     
                     

if __name__ == "__main__":
    primary_test()
    
    
    
    
    
    
    
    