#!/usr/bin/python
#a tool for traversing a directory structure and operating on its files
# the directory structure is a tree, where each leaf is a file (or symlink pointing to the memory address of another directory node).
# so it can be stored in memory as a tree datastructure.  


import os
import sys
import time
import filetype #for filetype (extension and mime type)
import chardet #for getting encoding
import subprocess
import random
import hashlib
import argparse
from datetime import datetime

#can we parse text out of this file or is it a libreoffice file? if so, return the contents
def attemptReadSampleFile(filepath):    
    if verbose: print('checking {}'.format(filepath))
    if os.path.isfile(filepath):
        f = open(filepath, 'rb')
        ftype = filetype.guess(filepath)
        if verbose: print('filetype: {}'.format(str(ftype)))
        if ftype != None:
            if ftype.extension in ['py', 'c', 'cc', 'h', 'hh', 'java', 'rst', 'css', 'html', 'htm', 'js', 'php', 'sh']: #don't want code in the sample data
                if verbose: print('this file is code')
                return None
            if ftype.extension == 'odt' and filepath[len(filepath)-1] != '#': #openoffice doc and not a lock file
                return cmd('odt2txt ' + filepath)
        else:
            fb = f.read() #file data (bytes) to detect encoding
            enc = str(chardet.detect(fb)['encoding'])
            if verbose: print('encoding: {}'.format(enc))
            if enc in ['ascii','utf-8']:
                return str(fb, encoding=enc)
            else:
                return None
    else: 
            if verbose: print('not file')
            return None

def getFilesRecursive(paths):
    samplefiles=[] #the paths of the individual files from which we want to grab text
    for p in paths:
            if verbose: print('path {}'.format(p))
            if os.path.isdir(p):
                    for root,dirs,files in os.walk(p):
                            if verbose: print('walk {}: {} files, {} dirs'.format(root, len(files), len(dirs)))
                            for f in files:
                                samplefiles.append(root + '/' + f)
            else:
                   samplefiles.append(p)
    return samplefiles

#returns some # of the most recently modified files in a directory, scanning recursively
def getRecentlyModifiedFiles(dir, n=10):
    fileswmodtimes = []
    for root,dirs,files in os.walk(dir):
        for f in files:
            fileswmodtimes.append( (f'{root}/{f}', os.path.getmtime(f'{root}/{f}')) )
    return sorted(fileswmodtimes, key=lambda x: x[1], reverse=True)[:n]
    #if include_time:
    #    return sorted(fileswmodtimes, key=lambda x: x[1], reverse=True)[:n]
    #else:
    #    return [f[0] for f in sorted(fileswmodtimes, key=lambda x: os.path.getmtime(x[0]), reverse=True)[:n]]

#returns duplicate files from some given lists of files
def findDuplicates(*args):
    for arg in args:
         if not isinstance(arg, str):
             raise TypeError('all arguments must be strings of file paths')
    filelists = []
    dups = [] #duplicate files found, as a list<tuple<int,int>> grouping together each file as mappings of filelist index to file index within that list. 
    for arg in args:
        if os.path.isdir(arg):
            fl = []
            for root,dirs,files in os.walk(arg):
                for f in files:
                    fl.append((f'{root}/{f}',f,os.path.getsize(f'{root}/{f}'),'')) #tuple<path, name, size, hash>
            filelists.append(fl)
        elif ':' in arg: #remote file
            tmp = arg.split(':')
            host = tmp[0]
            user = None
            if '@' in host:
                userhost = host.split('@')
                user = userhost[0]
                host = userhost[1]
            path = tmp[1]
            #TODO add remote file support
        else:
            raise ValueError('argument must be a directory or remote file path')
            
    #now we have a list of lists of files. look for duplicates via a few different approaches
    
    #union = {}
    #intersection = set(filelists[0])
    #for fl in filelists:
    #    union = union | set(fl)
    #    intersection = intersection & set(fl)


    #first, check for identical paths
    for i in range(len(filelists)):
        flist1 = filelists[i]
        for ii in range(len(flist1)):
            f1 = flist1[ii]
            for j in range(i+1, len(filelists)):
                flist2 = filelists[j]
                if flist2 != flist1:
                    for jj in range(len(flist2)):
                        f2 = flist2[jj]
                        #recall that each element of the filelist is a tuple<filepath,filename,size,hash(not-yet-calculated)>
                        if f1[0] == f2[0]: #exact same filepath, probably same file, check md5
                            if f1[2] == f2[2]: #first of all check size
                                dups.append([(i,ii),(j,jj)])
                            fb = open(f1[0],'r')
                            hash1 = hashlib.md5(fb).hexdigest()
                            fb.close()
                            fb = open(f2[0],'r')
                            hash2 = hashlib.md5(fb).hexdigest()
                            fb.close()    
    return None #todo     

def checkSimilarityOfDuplicates(dups, dir1, dir2):
    for d in dups:
        f1 = open(dir1 + '/' + d, 'rb')
        f2 = open(dir2 + '/' + d, 'rb')

#returns a list of files that are in both lists of files from each given directory
def findDuplicateFiles(dir1, dir2):
    if not (os.path.isdir(dir1) and os.path.isdir(dir2)):
         return -1
    fl1 = [] #list of file paths
    fl2 = []
    for root,dirs,files in os.walk(dir1):
        for f in files:
            fl1.append((f'{root}/{f}',f,os.path.getsize(f'{root}/{f}'),'')) #tuple<path, name, size, hash>
    for root,dirs,files in os.walk(dir2):
        for f in files:
            fl2.append((f'{root}/{f}',f,os.path.getsize(f'{root}/{f}'),'')) #tuple<path, name, size, hash>    
    
#    for i in range(len(fl1)):
 #       for j in range(i+1, len(fl2)):
  #          #TODO            

   # return list(set(l1) & set(l2))

#looks at all the files of the 2 given dirs, returns the following sets:
#   unique to 1: files that only exist in dir1
#   unique to 2: files that only exist in dir2
#   duplicates: files that exist in both dirs
#this is done by filename only, and does not take into account the full path of the files, unless the arg fullpath = True. 
#so 2 files could have the same name yet contain different data. use the function compareFileHashes() to figure out if files with same name have different contents. 
#keyword args:
#   fullpath: return the full path as opposed to just the filename
#   pretty: return formatted text. default true because this tool is primarily used in cmd line
def getDupFiles(dir1, dir2, fullpath=False, pretty=True):
    #files1 = str(cmd(f'find {dir1} -type f'), encoding='utf-8').split('\n')
    #files2 = str(cmd(f'find {dir2} -type f'), encoding='utf-8').split('\n')
    files1 = cmd(f'find {dir1} -type f').split('\n')
    files2 = cmd(f'find {dir2} -type f').split('\n')

    #make lists of filenames, without paths
    filenames1 = []
    filenames2 = []
    for fpath in files1:
        tmp=fpath.split('/')
        filenames1.append(tmp[len(tmp)-1])
    for fpath in files2:
        tmp=fpath.split('/')
        filenames2.append(tmp[len(tmp)-1])
    dupFiles = (set(filenames1) & set(filenames2)) - {' ','','.','..'}

    #TODO return fullpaths option
    if pretty:
        res = ''
        for fn in dupFiles:
            res += fn+'\n'
        print(res)
    else:
        print(dupFiles)
    return dupFiles

def getDuplicateFiles(dir1, dir2, fullpath=False, pretty=True):
    return getDupFiles(dir1, dir2, fullpath, pretty)
def getDupeFiles(dir1, dir2, fullpath=False, pretty=True):
    return getDupFiles(dir1, dir2, fullpath, pretty)


def getUniqueFiles(dir1, dir2, fullpath=False, pretty=True):
    files1 = str(cmd(f'find {dir1} -type f'), encoding='utf-8').split('\n')
    files2 = str(cmd(f'find {dir2} -type f'), encoding='utf-8').split('\n')

    #make lists of filenames, without paths, if applicable
    if not fullpath:
        filenames1 = []
        filenames2 = []
        for fpath in files1:
            tmp=fpath.split('/')
            filenames1.append(tmp[len(tmp)-1])
        for fpath in files2:
            tmp=fpath.split('/')
            filenames2.append(tmp[len(tmp)-1])
    union = (set(filenames1) | set(filenames2)) - {' ','','.','..'}
    uniq1 = union - set(filenames2)
    uniq2 = union - set(filenames1)

    if pretty:
        res = 'unique to 1:\n'
        for fn in uniq1:
            res += fn+'\n'
        res += 'unique to 2:\n'
        for fn in uniq2:
            res += fn+'\n'
        print(res)
    else:
        print(uniq1,uniq2)
    return (uniq1,uniq2)
def getUniqFiles(dir1, dir2, fullpath=False, pretty=True):
    return getUniqueFiles(dir1, dir2, fullpath, pretty)

def getDupeFilesHash(dir1, dir2, fullpath=False, pretty=True):
    filesWithHash = []
    for f in getDupFiles(dir1, dir2, fullpath=False, pretty=False):
        f1 = os.system(f'find {dir1} | grep {f}') #TODO continue work here
        f2 = os.system(f'find {dir2} | grep {f}')
        print(f1)
        #hash1 = cmd(f'md5sum {f1}')
        #hash2 = cmd(f'md5sum {f2}')
        #print(hash1+' '+hash2)
        filesWithHash.append((f,hash))
    #print(filesWithHash)
    return filesWithHash    
    



#execute a command
'''def cmd(cmdStr):
    return subprocess.run(cmdStr.join(' '), encoding='utf-8', stdout=subprocess.PIPE).stdout
'''
'''
execute a command using the python subprocess module
params:
    cmdstr (str) : the command to run
return: stdout of command
'''
def cmd(cmdstr,v=False):
    cmdarray = cmdstr.strip().split(' ')
    log(f'runcmd: {cmdstr}')
    '''if '|' in cmdarray:   #TODO handling pipe not yet working
        i = cmdarray.index('|')  
        proc0 = subprocess.check_output(cmdstr, shell=True)'''
    proc = subprocess.run(cmdarray, stdout=subprocess.PIPE)
    if proc.returncode == 0:
        res = proc.stdout
        if verbose:
            log(f'result: {res}')
    else:
        log(f'returncode = {proc.returncode}')
        res = proc.stderr
    return str(res, encoding='utf-8')

def log(msg):
    t = tnow()
    with open('filetreetool.log', 'a') as lf:
        lf.write(f'{t}: {msg}\n')
        lf.close()
    if verbose: print(f'LOG: {msg}')

def tnow():
    '''
    return: current time, formatted as %Y%m%d-%H%M%S
    ''' 
    return datetime.now().strftime('%Y%m%d-%H%M%S')

verbose=False #verbose 

def callFunc(func_name, *args, **kwargs):
    """
    Calls a function by its name if it exists in the global scope.
    
    :param func_name: (string) name of the function to call
    :param args: (List<string>) Positional arguments to pass to the function
    :param kwargs: (List<tuple<string>>) Keyword arguments to pass to the function
    :return: The result of the function call if successful, None otherwise
    """
    #TODO keep a log of called functions and cached result, to use for optimization
    if func_name in globals() and callable(globals()[func_name]):
        func = globals()[func_name]
        return func(*args, **kwargs)
    else:
        print(f'function "{func_name}" not callable')
        return None        
    

if __name__ == '__main__':
    '''
    older less-dynamic implementation
    parser = argparse.ArgumentParser(description='a tool to analyze and manage files in a directory structure')
    parser.add_argument('func', help='module function to call')
    parser.add_argument('args', nargs='*', help='function args')
    args = parser.parse_args()

    if args.func == 'compareDupesOfFiles':
        if len(args.args < 2):
            print('need (dir1, dir2)')
            sys.exit(1)
        result = compareDupesOfFiles(args.args[0], args.args[1])'''
    if len(sys.argv) == 1:
        print('a tool for traversing a directory structure and operating on its files. \
            the directory structure is a tree, where each leaf is a file (or symlink pointing to the memory address of another directory node). \
            so it can be stored in memory as a tree datastructure.  ')
        sys.exit(0)
    if len(sys.argv) == 2:
        callFunc(sys.argv[1])
    elif len(sys.argv) > 2:
        args = [] #separate out normal args and keyword args
        kwargs = []
        for a in sys.argv[2:]:
            if '=' in a:
                tmp = a.split('=')
                if len(tmp) != 2:
                    print(f'invalid: {a}')
                    sys.exit(1)
                kwargs.append([tmp[0],tmp[1]])
            else:
                args.append(a)
        #print(f'calling {sys.argv[1]}({",".join(args)}  {kwargs})')
        callFunc(sys.argv[1], *args, *kwargs)
