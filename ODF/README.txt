What's this?
============

This directory has tools for converting the Django Book into Open Office
documents.

There's a patch against the docutils ODF converter (see the "OpenDocument"
directory in the sandbox). You'll need to apply the patch and then install the
writer using the included setup.py in that directory.

There's also a styles.xml here you should point to using rst2odt's
--stylesheet-path option.