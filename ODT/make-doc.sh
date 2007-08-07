#!/bin/bash

# Convert *.odt to *.doc, automatically.
# This should be run from the rc1 (or whatever) directory
#
# This will probably only work on my (JKM)'s computer, but it should be
# hackable to work anywhere. The basic premise is covered here:
# http://www.xml.com/pub/a/2006/01/11/from-microsoft-to-openoffice.html?page=2
#
# For completeness, that script is:
#
#       Sub SaveAsDoc( cFile ) 
#          cURL = ConvertToURL( cFile )
#          oDoc = StarDesktop.loadComponentFromURL( cURL, "_blank", 0, (Array(MakePropertyValue( "Hidden", True ),))
#          cFile = Left( cFile, Len( cFile ) - 4 ) + ".doc"
#          cURL = ConvertToURL( cFile )
#          oDoc.storeToURL( cURL, Array(MakePropertyValue( "FilterName", "MS WinWord 6.0" ),)
#          oDoc.close( True )
#       End Sub
#       
#       Function MakePropertyValue( Optional cName As String, Optional uValue ) _
#          As com.sun.star.beans.PropertyValue
#          Dim oPropertyValue As New com.sun.star.beans.PropertyValue
#          If Not IsMissing( cName ) Then
#             oPropertyValue.Name = cName
#          EndIf
#          If Not IsMissing( uValue ) Then
#             oPropertyValue.Value = uValue
#          EndIf
#          MakePropertyValue() = oPropertyValue
#       End Function
#
#
# After making the SaveAsDoc macro detailed therein, this script will call it
# to convert stuff into .doc -- nifty, eh?
#
# On my computer, at least, NeoOffice has to be already running.

# Constants. I *think* changing these will make this work elsewhere...
OO="/Applications/NeoOffice.app/Contents/MacOS/soffice"
MACRO="Standard.Conversions.SaveAsDoc"
PWD=`pwd`

for doc in *.odt; do
    $OO -invisible "macro:///$MACRO($PWD/$doc)"
done