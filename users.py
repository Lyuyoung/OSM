# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re

def get_user(element):
    if 'uid' in element.attrib:
        return element.attrib['uid']


def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if get_user(element):
            users.add(get_user(element))

    return users


def test():

    users = process_map('las-vegas.osm')
    #pprint.pprint(users)
    print len(users)


if __name__ == "__main__":
    test()