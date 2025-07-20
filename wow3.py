#!/usr/bin/python3

import argparse
import sys
import time
import os
#Words Of Wisdom
# output some random text from some given collection of files, 
#   - primarily used to grab some random "words of wisdom" from my journals and writings

paths=[] #the paths to scan recursively for files from which to grab text
samplefiles=[] #the paths of the individual files from which we want to grab text
matchpattern='' #if we want to filter the files by some text pattern that the filename must match
time_min = -1 #threshold time. dont use files that are older
v=False
def attemptReadSampleFile(filepath):
    if v: print('checking {}'.format(filepath))
    if os.path.isfile(filepath):
        try:
            with open(filepath, 'rb') as f:
                ftype = filetype.guess(filepath)
                if v: print('filetype: {}'.format(str(ftype)))
                if ftype is not None:
                    if ftype.extension in ['py', 'c', 'cc', 'h', 'hh', 'java', 'rst', 'css', 'html', 'htm', 'js', 'php', 'sh']: #don't want code in the sample data
                        if v: print('this file is code')
                        return None
                    if ftype.extension == 'odt' and filepath[-1] != '#': #openoffice doc and not a lock file
                        subproc = subprocess.run(['odt2txt', filepath], encoding='utf-8', stdout=subprocess.PIPE)
                        return subproc.stdout
                    if ftype.extension == 'txt':
                        return str(f.read(), encoding='utf-8')
                else:
                    fb = f.read() #file data (bytes) to detect encoding
                    enc = str(chardet.detect(fb)['encoding'])
                    if v: print('encoding: {}'.format(enc))
                    if enc in ['ascii', 'utf-8']:
                        return str(fb, encoding=enc)
                    else:
                        return None
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            return None
    else: 
        if v: print('not a file')
        return None

def parseArgs():
    parser = argparse.ArgumentParser(description='output some random text from some given collection of files')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose')
    
    parser.add_argument('-p', '--path', type=str, required=False, help='a path to scan', action='append', default=['~/doc'])
    parser.add_argument('-o', '--output', type=str, required=False, help='output file')
    args = parser.parse_args()
    return args

def main():
    args = parseArgs()
    if args.verbose:
        print(f"Input file: {args.input}")
        if args.output:
            print(f"Output file: {args.output}")
    
    if args.path:
        paths.append(args.path)
    

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
    
    mt = time.ctime(os.path.getmtime(samplefiles[fi]))
    print('{} ;\n       last modified {} :\n  {}'.format(samplefiles[fi], mt, t))

    lines = t.splitlines()
    li = random.randint(0, len(t)) #line index
    #ci = random.randint(0, len(t)) #character index
    res = '\n'.join(lines[li: li+7])
    print(res)

if __name__ == '__main__':
    main()