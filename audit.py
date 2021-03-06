#!/usr/bin/python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "las-vegas.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons","Apache"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "AVE": "Avenue",
            "ave": "Avenue",
            "apache" : "Apache",
            "Ave.": "Avenue",
            "Blvd":"Boulevard",
            "Blvd.":"Boulevard",
            "blvd":"Boulevard",
            "Rd5" :"Road",
            "Rd": "Road",
            "Rd.": "Road",
            "Cir":"Circle",
            "Dr":"Drive",
            "Ln":"Lane",
            "Ln.":"Lane",
            "ln":"Lane",
            "parkway":"Parkway",
            "Pkwy":"Parkway",
            "S.":"South",
            "S":"South"
            }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name, mapping):

    # YOUR CODE HERE
    m = street_type_re.search(name)
    street_type = m.group()
    if street_type not in expected:
        if street_type in mapping:
            name=name.replace(street_type,mapping[street_type])
    return name

def is_zip_code(elem):
    return (elem.attrib['k'] == "addr:postcode")

def audit_zip(osmfile):
    osm_file = open(osmfile, "r")
    prob_zip = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_zip_code(tag):

                    if len(tag.attrib['v']) != 5:
                        prob_zip.add(tag.attrib['v'])
                    elif tag.attrib['v'][0:2] != '89':
                        prob_zip.add(tag.attrib['v'])
    osm_file.close()
    return prob_zip


def test():
    st_types = audit_zip(OSMFILE)
    pprint.pprint(st_types)
    
  #  for st_type, ways in st_types.iteritems():
  #      for name in ways:
  #          better_name = update_name(name, mapping)
  #          print name, "=>", better_name


if __name__ == '__main__':
    test()