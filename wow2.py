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

#can we parse text out of this file or is it a libreoffice file? if so, return the contents
def attemptReadSampleFile(filepath):
    if v: print('checking {}'.format(filepath))
    if os.path.isfile(filepath):
        f = open(filepath, 'rb')
        ftype = filetype.guess(filepath)
        if v: print('filetype: {}'.format(str(ftype)))
        if ftype != None:
            if ftype.extension in ['py', 'c', 'cc', 'h', 'hh', 'java', 'rst', 'css', 'html', 'htm', 'js', 'php', 'sh']: #don't want code in the sample data
                if v: print('this file is code')
                return None
            if ftype.extension == 'odt' and filepath[len(filepath)-1] != '#': #openoffice doc and not a lock file
                subproc = subprocess.run(['odt2txt', filepath], encoding='utf-8', stdout=subprocess.PIPE)
                return subproc.stdout
        else:
            fb = f.read() #file data (bytes) to detect encoding
            enc = str(chardet.detect(fb)['encoding'])
            if v: print('encoding: {}'.format(enc))
            if enc in ['ascii','utf-8']:
                return str(fb, encoding=enc)
            else:
                return None
    else: 
            if v: print('not file')
            return None


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
                            samplefiles.append(root + '/' + f)
        else:
               samplefiles.append(p)

tEnd = time.time()
tDuration = tEnd - tStart
print('gathered {} candidate files in {} seconds, from paths {}'.format(len(samplefiles), tDuration, str(paths)))

#pick random file until we get an acceptable one
fi = random.randint(0, len(samplefiles))
t = attemptReadSampleFile(samplefiles[fi])
while t == None:
    del samplefiles[fi]
    fi = random.randint(0, len(samplefiles))
    t = attemptReadSampleFile(samplefiles[fi])

print()
print('{} : {}'.format(samplefiles[fi], t))

lines = t.splitlines()
li = random.randint(0, len(t)) #line index
#ci = random.randint(0, len(t)) #character index
res = '\n'.join(lines[li: li+7])
print(res)