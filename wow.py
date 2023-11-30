#!/usr/bin/python
#Words Of Wisdom
# output some random text from my journal

import os
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
        if enc in ['ascii','utf-8']:
            if v: print(fb)
            total_text += str(fb)
        elif ftype.extension == 'odt':
            total_text += subprocess.run(['odt2txt', filepath]).stdout
        else:
            if v: print('{} is not txt')
    else: 
            if v: print('not file')



paths=['/home/thomas/doc/j/', '/home/thomas/_poetry', '/home/thomas/doc/_journal_2019'] #the paths to scan recursively for files from which to grab text
samplefiles=[] #the individual files we want to grab text from

v=True #verbose 

for p in paths:
        if v: print('path {}'.format(p))
        if os.path.isdir(p):
                for root,dirs,files in os.walk(p):
                        if v: print('walk {}: {} files, {} dirs'.format(root, len(files), len(dirs)))
                        for f in files:
                            addSampleFileIfTxt(root + '/' + f)
        else:
               addSampleFileIfTxt(p)

print(total_text)
#for f in samplefiles:
#    print(f)




