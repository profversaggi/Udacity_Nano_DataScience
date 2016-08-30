#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Filename: DATA-prepare_for_mongodb_insertion.py

Course: Udacity Data Science ND -- "Data Wrangling with MongoDB"
Project: OpenStreetMap Data Case Study

Description:


@author: Matthew R. Versaggi
@Email: profversaggi@gmail.com


***************************

Description:

This program parses the OSM file and transforms the SHAPE of the data into a 
python list of dictionary in preparation for output in JSON format with the 
intention of being directly able to import into a local MongoDB instance.

The dictionary form discussed above should be something like the following:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}


In particular the following things will happen:

- the only 2 types of top level tags are: "node" and "way"
- all attributes of "node" and "way" are turned into regular key/value pairs, except:
    - attributes in the CREATED array are added under a key "created"
    - attributes for latitude and longitude are added to a "pos" array,
      for use in geospacial indexing, the values inside "pos" array are floats and not strings. 
- if the second level tag "k" value contains problematic characters, it is ignored
- if the second level tag "k" value starts with "addr:", it is added to a dictionary "address"
- if the second level tag "k" value does not start with "addr:", but contains ":", it is processed
  in an intuitive way
- if there is a second ":" that separates the type/direction of a street, the tag is ignored, 
  for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  will be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

will be turned into
"node_refs": ["305896090", "1719825889"]


"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint
import re
import codecs
import json


LOCAL_EXAMPLE_OSMFILE = "example.osm"
PROJECT_OSMFILE = "Minneapolis_St-Paul.osm"


# RegEx expressions (compiled) to ferret out patterns of interest
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# RegEx expressions (compiled) to ferret out the street acronyms.
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


# Created list:
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


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
            

# This function takes in a postal code and trims it down to only 5 characters
def trim_postalcodes(code):
    postalcode = ''
    for character in code:
        if character.isdigit():
            postalcode += character
        if len(postalcode) == 5:
            break
    return postalcode




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



# Boolean Test: If the element is an address of the pattern "addr:" , then 
# return TRUE
#
def is_address(elem):
    if elem.attrib['k'][:5] == "addr:":
        return True

        
# This function takes an XML construct as input and returns a cleaned and 
# returns a Python Dictionary comprising a cleaned and reshaped JSON Data Model
# useful as input to a local MongoDB instance. If any elements of the XML
# construct contain an abreviated street name, it will transform it into the 
# full street name.
#
def shape_element(element):
    node = {}
    # if the tag is "node" or "way":
    if element.tag == "node" or element.tag == "way" :
        address_info = {}
        nd_info = []
        
        #pprint.pprint(element.attrib)
        node["type"] = element.tag
        node["id"] = element.attrib["id"]
        
        # If 'visible' attribute is present in element - add it to the node
        if "visible" in element.attrib.keys():
            node["visible"] = element.attrib["visible"]
        
        # If 'lat' attribute is present in element - add it to the node 
        if "lat" in element.attrib.keys():
            node["pos"] = [float(element.attrib['lat']), float(element.attrib['lon'])]
        
        # Construct the node[created] dictionary using the 5 attributes of concern    
        node["created"] = {"version": element.attrib['version'],
                            "changeset": element.attrib['changeset'],
                            "timestamp": element.attrib['timestamp'],
                            "uid": element.attrib['uid'],
                            "user": element.attrib['user']}
        # If the tag is "tag":                    
        for tag in element.iter("tag"):
            # print tag.attrib
            p = problemchars.search(tag.attrib['k']) # Find the problem Chars
            if p:
                # print "PROBLEM:", p.group() # If its a problem char - ignore
                continue
            elif is_address(tag):    # if it's an address - ignore the ":"s.
                if ":" in tag.attrib['k'][5:]:
                    # print "Bad Address:", tag.attrib['k'], "--", tag.attrib['v']
                    continue
                else:
                    address_info[tag.attrib['k'][5:]] = tag.attrib['v']
                    # print "Good Address:", tag.attrib['k'], "--", tag.attrib['v']
            else:
                node[tag.attrib['k']] = tag.attrib['v']
                # print "Outside:", tag.attrib['k'], "--", tag.attrib['v']
                
        # Trim the postalcodes to only 5 characters.        
        if (address_info != {}) and ("postcode" in address_info):
            # print "address_info[postcode]: ", address_info["postcode"]
            #print "address_info[FIXED]: ", trim_postalcodes(address_info["postcode"])
            address_info["postcode"] = trim_postalcodes(address_info["postcode"])
            
        # If dict address_info not empty and has key of "street":
        if (address_info != {}) and ("street" in address_info):
               # print "ADDRESS INFO[street]: ", address_info["street"]
               # Expand street name to full form
               address_info["street"] = update_name(address_info["street"], mapping)
               node['address'] = address_info   # populate node['address']
        elif address_info != {}:           
            # print_street_name(address_info)
            node['address'] = address_info   # populate node['address']  
            
        for tag2 in element.iter("nd"):
            nd_info.append(tag2.attrib['ref'])  # append the ref attribute
            # print tag2.attrib['ref']
        
        if nd_info != []:                       # If nd info not empty:
            node['node_refs'] = nd_info     # populate node['node_refs']
        return node
    else:
        return None




# This function manages the processing of the OSM (map) file, invokes the 
# reshaping function for the various elements, and then outputs the result into
# a JSON to a file for input to the local MongoDB instance.
#
def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data




# This test harnass opperates against the EXAMPLE OSM File provided in class.
# It processes the OSM file and then executes a few assertions to check the
# correctness of the data based uopn known records in that particular dataset.
#
def local_example_osm_test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.

    data = process_map(LOCAL_EXAMPLE_OSMFILE, True)
    #pprint.pprint(data)
    
    # Create a dictionary to contain the known first element of the OSM File
    correct_first_elem = {
        "id": "261114295", 
        "visible": "true", 
        "type": "node", 
        "pos": [41.9730791, -87.6866303], 
        "created": {
            "changeset": "11129782", 
            "user": "bbmiller", 
            "version": "7", 
            "uid": "451048", 
            "timestamp": "2012-03-28T18:31:23Z"
        }
    }
    assert data[0] == correct_first_elem    # Check to see if it is present
    
    # Check assertions of other combinations of various data that is known to 
    # exist in OSM file.
    assert data[-1]["address"] == {
                                    "street": "West Lexington St.", 
                                    "housenumber": "1412"
                                      }
                                      
    assert data[-1]["node_refs"] == [ "2199822281", "2199822390",  "2199822392", "2199822369", 
                                    "2199822370", "2199822284", "2199822281"]




# This test harnass opperates against the PROJECT OSM File from OpenStreetMap.
# It processes the OSM file and then executes a few assertions to check the
# correctness of the data based uopn known records in that particular dataset.
#
def primary_test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.

    data = process_map(PROJECT_OSMFILE, False)
    #pprint.pprint(data)
    
    # Create a dictionary to contain the known first element of the OSM File
    correct_first_elem = {'created': {'changeset': '32418946',
                                      'timestamp': '2015-07-05T06:34:35Z',
                                      'uid': '992965',
                                      'user': 'lizzz_msp',
                                      'version': '7'},
                                      'highway': 'traffic_signals',
                                      'id': '33295121',
                                      'pos': [44.9748235, -93.2610554],
                                      'railway': 'level_crossing',
                                      'type': 'node'}

    correct_last_elem = {'created': {'changeset': '41418301',
                                     'timestamp': '2016-08-12T20:30:51Z',
                                     'uid': '175702',
                                     'user': 'AxelBoldt',
                                     'version': '1'},
                                     'highway': 'service',
                                     'id': '436942494',
                                     'node_refs': ['4347889717', '4347889718'],
                                     'type': 'way'}


    assert data[0] == correct_first_elem    # Check to see if it is present
    assert data[-1] == correct_last_elem    # Check to see if it is present
    
    # Check assertions of other combinations of various data that is known to 
    # exist in OSM file.
    assert data[12336]["address"] == {'housenumber': '65',
                                     'postcode': '55101',
                                     'state': 'MN',
                                     'street': 'East 10th Street'}
                                
    assert data[334078]["address"] == {'city': 'Minneapolis',
                                     'country': 'US',
                                     'housenumber': '16',
                                     'postcode': '55403',
                                     'state': 'MN',
                                     'street': '11th Ave South East'}

                                      
    assert data[-10]["node_refs"] == [ "4346218645", "4346218646", 
                                    "4346218647", "4346218648", "4346218645"]
                                    
                                    

if __name__ == "__main__":
    primary_test()
    
    
    
    
    