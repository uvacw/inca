#!/usr/bin/env python

# tool to recursively convert CRLF/BOM text files (e.g., from LexisNexis) to LF/no-BOM
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
	with open(path, "r+b") as fp:
		chunk = fp.read(BUFSIZE)
		if chunk.startswith(codecs.BOM_UTF8):
			i = 0
			chunk = chunk[BOMLEN:]
			while chunk:
				fp.seek(i)
				fp.write(chunk)
				i += len(chunk)
				fp.seek(BOMLEN, os.SEEK_CUR)
				chunk = fp.read(BUFSIZE)
			fp.seek(-BOMLEN, os.SEEK_CUR)
			fp.truncate()			

	with open(path) as inp:
		txt = inp.read()
	txt = txt.replace('\r','')
	with open(path, 'w') as out:
		out.write(txt)
	j+=1
	
print "Done!",j,"files processed. BOM's and CR have been removed, so we have a set of Unicode files without BOM and with Unix-style line endings."
