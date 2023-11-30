#!/usr/bin/python
#Words Of Wisdom
# output some random text from my journals and writings

import os
import sys
import time
import filetype #for filetype (extension and mime type)
import chardet #for getting encoding
import subprocess
import random

total_text = ''

def addSampleFileIfTxt(filepath):
    global total_text
    if v: print('checking {}'.format(filepath))
    if os.path.isfile(filepath):
        f = open(filepath, 'rb')
        fb = f.read() #file data (bytes). unfortunately have to read the file to detect encoding
        enc = str(chardet.detect(fb)['encoding'])
        ftype = filetype.guess(filepath)
        if v: print('filetype: {}'.format(str(ftype)))
        if v: print('encoding: {}'.format(enc))
        if ftype != None:
            if ftype.extension in ['py', 'c', 'cc', 'h', 'hh', 'java']: #don't want code in the sample data
                return
            if ftype.extension == 'odt':
                samplefiles.append(filepath)
                #if v: print('converting odt: {}'.format(filepath))
                #subproc = subprocess.run(['odt2txt', filepath], encoding='utf-8', stdout=subprocess.PIPE)
                #total_text += str(subproc.stdout)
        if enc in ['ascii','utf-8']:
            if v: print(fb)
            samplefiles.append(filepath)
            #total_text += str(fb, encoding='utf-8')
        else:
            if v: print('{} is not txt')
    else: 
            if v: print('not file')


#paths=['/home/thomas/doc/fiction']
paths=['/home/thomas/doc/j/', '/home/thomas/_poetry', '/home/thomas/doc/_journal_2019'] #the paths to scan recursively for files from which to grab text
samplefiles=[] #the paths of the individual files from which we want to grab text

v=False #verbose 
tStart = time.time()
for p in paths:
        if v: print('path {}'.format(p))
        if os.path.isdir(p):
                for root,dirs,files in os.walk(p):
                        if v: print('walk {}: {} files, {} dirs'.format(root, len(files), len(dirs)))
                        for f in files:
                            addSampleFileIfTxt(root + '/' + f)
        else:
               addSampleFileIfTxt(p)

tEnd = time.time()
tDuration = tEnd - tStart
print('gathered {} acceptable files in {} seconds, from paths {}'.format(len(samplefiles), tDuration, str(paths)))

#now we have all of our files of interest. so pick a random one
fi = random.randint(0, len(samplefiles)) # file index
fc = samplefiles[fi] # the chosen one
print('chose file ' + fc)
f = open(fc, 'rb')
fb = f.read()
ftype = filetype.guess(fc)
if ftype != None and ftype.extension == 'odt':
     subproc = subprocess.run(['odt2txt', fc], encoding='utf-8', stdout=subprocess.PIPE)
     print(subproc.stdout)
else:
     print(str(f.read(), encoding='utf-8'))


#for f in samplefiles:
#    print(f)




