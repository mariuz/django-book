#!/bin/bash

# Convert all the .txt documents in the cwd to ODF.

RST2ODT="`dirname $0`/rst2odt.py"

mkdir -p ODT
for doc in *.txt; do
    $RST2ODT --strip-comments $doc ODT/${doc/%.txt/.odt}
done