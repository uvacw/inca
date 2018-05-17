#!/usr/bin/env python

# tool to recursively removes the first x lines from files
# usage: resursivefirstxlinesreove 22 /path/to/folder/withtxtfiles

import os, sys, codecs
from os import listdir, walk
from os.path import isfile, join, splitext



mypath = sys.argv[2]

alleinputbestanden=[]
for path, subFolders, files in walk(mypath):
	for f in files:
		if isfile(join(path,f)) and splitext(f)[1].lower()==".txt":
			alleinputbestanden.append(join(path,f))

i=0
for path in alleinputbestanden:
	print path
	with open(path) as inp:
                wholetext=inp.readlines()
                skip=int(sys.argv[1])
                if len(wholetext)>skip:
                        txt = wholetext[skip:]
                else:
                        txt=wholetext
	with open(path, 'w') as out:
		out.writelines(txt)
	i+=1
	
print "Done!",i,"files processed. The first",sys.argv[1],"lines have been removed"
