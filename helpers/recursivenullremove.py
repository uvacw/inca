#!/usr/bin/env python

# tool to recursively remove NULL bytes
# usage: resursivebomremove /path/to/folder/withtxtfiles

import os, sys, codecs
from os import listdir, walk
from os.path import isfile, join, splitext

BUFSIZE = 4096
BOMLEN = len(codecs.BOM_UTF8)



mypath = sys.argv[1]

alleinputbestanden=[]
for path, subFolders, files in walk(mypath):
	for f in files:
		if isfile(join(path,f)) and splitext(f)[1].lower()==".txt" or splitext(f)[1].lower()==".csv":
			alleinputbestanden.append(join(path,f))

j=0
for path in alleinputbestanden:
	# print path
	fi = open(path, 'rb')
	data = fi.read()
	fi.close()
	fo = open(path, 'wb')
	fo.write(data.replace('\x00', ''))
	fo.close()
	j+=1
	
print "Done!",j,"files processed. NULL bytes have been removed, so we hhopefully ave a set of valid Unicode files now."
