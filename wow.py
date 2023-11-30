#!/usr/bin/python
#Words Of Wisdom
# output some random text from my journals and writings

import os
import sys
import time
import filetype #for filetype (extension and mime type)
import chardet #for getting encoding
import subprocess

total_text = ''

def addSampleFileIfTxt(filepath):
    global total_text
    if v: print('checking {}'.format(filepath))
    if os.path.isfile(filepath):
        f = open(filepath, 'rb')
        fb = f.read() #file data (bytes)
        enc = str(chardet.detect(fb)['encoding'])
        ftype = filetype.guess(filepath)
        if v: print('filetype: {}'.format(str(ftype)))
        if v: print('encoding: {}'.format(enc))
        if ftype != None:
            if ftype.extension in ['py', 'c', 'cc', 'h', 'hh', 'java']: #don't want code in the sample data
                return
            if ftype.extension == 'odt': 
                if v: print('converting odt: {}'.format(filepath))
                subproc = subprocess.run(['odt2txt', filepath], encoding='utf-8', stdout=subprocess.PIPE)
                total_text += str(subproc.stdout)
        if enc in ['ascii','utf-8']:
            if v: print(fb)
            total_text += str(fb, encoding='utf-8')            
            
        else:
            if v: print('{} is not txt')
    else: 
            if v: print('not file')


#paths=['/home/thomas/doc/fiction']
paths=['/home/thomas/doc/j/', '/home/thomas/_poetry', '/home/thomas/doc/_journal_2019'] #the paths to scan recursively for files from which to grab text
samplefiles=[] #the individual files we want to grab text from

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

#now we have all of our files of interest. so pick a random one

tEnd = time.time()
tDuration = tEnd - tStart
print('report generated in {} seconds, from paths {}'.format(tDuration, str(paths)))
print(total_text)
#for f in samplefiles:
#    print(f)




