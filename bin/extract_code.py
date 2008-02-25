"""
Extract all the code samples from a chapter.
"""

import re
import sys
from lxml import etree
from docutils.core import publish_parts

def extract_code(fname):
    parts = publish_parts(
        source = open(fname).read(),
        source_path = fname,
        writer_name = "xml",
        settings_overrides = {"xml_declaration": False}
    )
    tree = etree.fromstring(parts["whole"])
    for i, block in enumerate(tree.xpath("//literal_block")):
        print "#"
        print "# Code snippet %s %s" % (i+1, "#" * (58-len(str(i))))
        print "#"
        print
        print fix_entities(strip_tags(etree.tostring(block)))
        print
        
def strip_tags(value):
    return re.sub(r'<[^>]*?>', '', value)
    
def fix_entities(value):
    return value.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")

if __name__ == '__main__':
    extract_code(sys.argv[1])