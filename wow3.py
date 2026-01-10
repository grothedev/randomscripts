#!/usr/bin/python3

import argparse
import sys
import time
import os
import random
import subprocess
import chardet
import filetype
import re
#Words Of Wisdom
# output some random text from some given collection of files, 
#   - primarily used to grab some random "words of wisdom" from my journals and writings
#

paths=[] #the paths to scan recursively for files from which to grab text
#samplefiles=[] #the paths of all the individual files from which we can grab text
matchpattern='' #if we want to filter the files by some text pattern that the filename must match
time_min = -1 #threshold time. dont use files that are older
v=False
exclude_patterns_default = ['.git', 'node_modules', 'vendor', '\.~lock'] #default patterns to exclude

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
    

def getSampleFiles(paths, exclude_patterns = []):
    """grab all the possible sample files (recursive files from given paths)"""
    samples = []
    
    # Compile exclusion patterns into a single regex for efficiency
    compiled_exclusions = None
    exclude_patterns = exclude_patterns + exclude_patterns_default
    # Join patterns with OR operator and compile once
    pattern = '|'.join(f'({pattern})' for pattern in exclude_patterns)
    compiled_exclusions = re.compile(pattern, re.IGNORECASE)
    
    tStart = time.time()
    for p in paths:
        if v: print('path {}'.format(p))
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                if compiled_exclusions:
                    dirs[:] = [d for d in dirs if not compiled_exclusions.search(d)]
                
                if v: print('walk {}: {} files, {} dirs'.format(root, len(files), len(dirs)))
                
                for f in files:
                    filepath = os.path.join(root, f)
                    
                    # Check if file matches any exclusion pattern
                    if compiled_exclusions and compiled_exclusions.search(f):
                        if v: print(f'excluding file: {filepath}')
                        continue
                    
                    samples.append(filepath)
        else:
            # For individual files, still check exclusion
            if compiled_exclusions and compiled_exclusions.search(os.path.basename(p)):
                if v: print(f'excluding file: {p}')
            else:
                samples.append(p)
    
    tEnd = time.time()
    tDuration = tEnd - tStart
    if v:
        print('gathered {} candidate files in {} seconds, from paths {}'.format(len(samples), tDuration, str(paths)))
    return samples
    

def getRandomFileTextContent(samplefiles):
    """pick random file until we get an acceptable one
        @return tuple(filename, textcontent)"""
    if len(samplefiles) == 0:
        return (None, None)

    fi = random.randint(0, len(samplefiles) - 1)
    if v: print('candidate file: {}'.format(samplefiles[fi]))
    t = attemptReadSampleFile(samplefiles[fi]) #check if valid file
    while t == None: #this file was invalid, try again
        del samplefiles[fi]
        if len(samplefiles) == 0: #no files are valid
            return (None, None)
        fi = random.randint(0, len(samplefiles) - 1)
        t = attemptReadSampleFile(samplefiles[fi])
    
    mt = time.ctime(os.path.getmtime(samplefiles[fi]))
    if v: print('{} ;\n       last modified {} :\n '.format(samplefiles[fi], mt))
    return (samplefiles[fi], t)

#TODO params
def getExcerpt(text):
    """grab a random excerpt from the given stringh, which is assumed to be at least one paragraph length with multiple lines """
    offset = random.randint(0,5)
    lines = text.splitlines()
    if offset >= len(lines)/2:
        return text    
    li = random.randint(offset, len(lines)-offset) #line index
    res = '\n'.join(lines[li-offset: li+offset])
    if len(res) < 7:
        res = '\n'.join(lines)
    return res


def parseArgs():
    global v
    #get args from cmd line
    parser = argparse.ArgumentParser(description='output some random text from some given collection of files')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose')
    
    parser.add_argument('-p', '--paths', type=str, required=False, help='a path to scan', action='append', default=[])
    parser.add_argument('-o', '--output', type=str, required=False, help='output file')
    parser.add_argument('-x', '--exclude', type=str, required=False, help='exclude files with pattern', action='append', default=[])
    args = parser.parse_args()

    if (args.verbose): v = True

    if len(args.paths) == 0: args.paths.append('./')

    if v: 
        print('using paths: {}'.format(args.paths))
        if args.exclude:
            print('excluding: {}'.format(str(args.exclude)))

    return args

def main():
    args = parseArgs()
    samplefiles = getSampleFiles(args.paths, args.exclude)
    chosenfile = getRandomFileTextContent(samplefiles)
    excerpt = getExcerpt(chosenfile[1])
    print(excerpt)
    print('\n - {}'.format(chosenfile[0]))


if __name__ == '__main__':
    main()
