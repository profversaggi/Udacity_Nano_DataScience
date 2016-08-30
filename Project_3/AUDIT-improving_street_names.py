#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Filename: AUDIT-improving_street_names.py

Course: Udacity Data Science ND -- "Data Wrangling with MongoDB"
Project: OpenStreetMap Data Case Study

Description:


@author: Matthew R. Versaggi
@Email: profversaggi@gmail.com



***************************

Description:

This programs intent is to audit and fix unexpected street names as they are 
discovered in the extraction. The OSM file is parsed and the street names are 
matched with a mapping of problematic known street acronyms which we'd like to 
correct. An update function corrects the street names in question upon 
returning the result.

    
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint


LOCAL_EXAMPLE_OSMFILE = "example.osm"
PROJECT_OSMFILE = "Minneapolis_St-Paul.osm"

# RegEx expressions (compiled) to ferret out the street acronyms.
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


# This is the list of expected street names - if it's on this list it should 
# be ignored.
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

# This variable contains the mapping of questionable street acronyms to 
# corrected street names. This must be updated to reflect new observations in
# the extraction data.
#
mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "Av": "Avenue",
            "Av.": "Avenue",
            "Rd.": "Road",
            "Rd": "Road",
            "Blvd" : "Boulevard",
            "Blvd." : "Boulevard",
            "Dr" : "Drive",
            "Dr." : "Drive",
            "E" : "East",
            "E." : "East",
            "Ln" : "Lane",
            "Ln." : "Lane",
            "N" : "North",
            "N." : "North",
            "Pkwy" : "Parkway",
            "Pky" : "Parkway",
            "Pl" : "Place",
            "Pl." : "Place",
            "Rd" : "Road",
            "Rd." : "Road",
            "Rd/Pkwy" : "Road/Parkway",
            "S" : "South",
            "S." : "South",
            "S.E." : "South East",
            "SE" : "South East",
            "Terr" : "Terrace",
            "Terr." : "Terrace",
            "W" : "West",
            "W." : "West"
            }

# This function examines the street name against the list if expected street 
# names and if it is not found then it adds it to the list to be interrogated.
#
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

# Spot Check Function:
# If the "K" value of the element is equal to "addr:street", return TRUE.
#
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


# Process the OSM file and audit each street name. If it is an unexpected 
# street name, put it in the list of street_types to be interrogated later.
#
def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)   # Use this to not have to check if keys 
                                      # are in the dictionary every time.
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


# This function takes a questionable street name  and consults a Key:Value 
# mapping to transform it into a form more desirable.
#
def update_name(name, mapping):
    # print "NAME: ",name
    # print "MAPING: ", mapping
    m = street_type_re.search(name)  # Execute a compiled RegEx against the name
    if m:                            # If anything is found ....
        street_type = m.group()      # Grab the street name from the result
        # print "STREET TYPE: ", street_type
        if street_type in mapping:   # If the street name is in the mapping
            transformation = mapping[street_type]  # transform it below ...
            # print "TRANSFORMATION: ", transformation
            name_base = name.split(street_type)[0]
            # print "name_base: ", name_base
            name = name_base + transformation

    return name



# This test harnass opperates against the EXAMPLE OSM File provided in class,
# and uses a simple assert test against the known set of questionable street
# names to inspect for proper transformations.
#
def local_example_osm_test():
    st_types = audit(LOCAL_EXAMPLE_OSMFILE)
    assert len(st_types) == 3
    pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
            if name == "West Lexington St.":
                assert better_name == "West Lexington Street"
            if name == "Baldwin Rd.":
                assert better_name == "Baldwin Road"


# This test harnass opperates against the PROJECT OSM File from OpenStreetMap,
# and uses a simple assert test against the known set of questionable street
# names to inspect for proper transformations.
#
def primary_test():
    st_types = audit(PROJECT_OSMFILE)
    assert len(st_types) == 34
    pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
            if name == "5th St SE":
                assert better_name == "5th St South East"
            if name == "Walnut St SE":
                assert better_name == "Walnut St South East"




if __name__ == '__main__':
    primary_test()
    
    
    
    