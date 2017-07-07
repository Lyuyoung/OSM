# -*- coding: utf-8 -*-
import csv
import codecs
import re
import xml.etree.cElementTree as ET



OSM_PATH = "las-vegas.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Apache"]
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

def update_name(name, mapping):

    m = street_type_re.search(name)
    if m not in expected:
        if m in mapping:
            name=name.replace(m,mapping[m])
    return name

    # Fix Zip Codes:

def is_zip_code(elem):
    return (elem.attrib['k'] == "addr:postcode")
        
def update_zip(elem):

    if elem.tag == "node" or elem.tag == "way":
        for tag in elem.iter("tag"):
            if is_zip_code(tag):
                if len(tag.attrib['v']) != 5:
                    if tag.attrib['v'][0:2] == '89':
                        tag.attrib['v'] = tag.attrib['v'][0:5]
                    else:
                        tag.attrib['v'] = tag.attrib['v'][-5:]

def shape_tag(el, tag): 
    if PROBLEMCHARS.search(tag.attrib['k']): return None
    
    update_zip(el)
    updated = update_name(tag.attrib['v'], mapping)
                          
    tag = {
        'id'   : el.attrib['id'],
        'key'  : tag.attrib['k'],
        'value': updated,
        'type' : 'regular'
    }
    
    if LOWER_COLON.match(tag['key']):
        tag['type'], _, tag['key'] = tag['key'].partition(':')
        
    return tag
    
def shape_way_node(el, i, nd):
    return {
        'id'       : el.attrib['id'],
        'node_id'  : nd.attrib['ref'],
        'position' : i
    }

def shape_element(el, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    tags = [shape_tag(el, t) for t in el.iter('tag')]

    if el.tag == 'node':
        node_attribs = {f: el.attrib[f] for f in node_attr_fields}
        
        return {'node': node_attribs, 'node_tags': tags}
        
    elif el.tag == 'way':
        way_attribs = {f: el.attrib[f] for f in way_attr_fields}
        
        way_nodes = [shape_way_node(el, i, nd) 
                     for i, nd 
                     in enumerate(el.iter('nd'))]
   
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()



class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()



        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)
