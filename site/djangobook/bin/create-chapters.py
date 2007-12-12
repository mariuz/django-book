#!/usr/bin/env python

import sys
from djangobook.utils import create_chapters
from djangobook.models import BookVersion

try:
    vers = sys.argv[1]
    lang = sys.argv[2]
except IndexError:
    print >> sys.stderr, "Usage: %s <version> <language>" % (sys.argv[0])
    sys.exit(1)
    
try:
    book = BookVersion.objects.get(language=lang, version=vers)
except BookVersion.DoesNotExist:
    print >> sys.stderr, "No such book version."
    sys.exit(1)

create_chapters(book)