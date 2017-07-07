# -*- coding: utf-8 -*-
"""
Created on Mon Jul 03 15:40:54 2017

@author: lyuyang
"""

import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):
        # YOUR CODE HERE
    elem_dict = {}
    for  event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag in elem_dict:
            elem_dict[elem.tag] += 1
        else:
            elem_dict[elem.tag] = 1
    return elem_dict

def test():

    tags = count_tags('las-vegas.osm')
    pprint.pprint(tags)
    

if __name__ == "__main__":
    test()