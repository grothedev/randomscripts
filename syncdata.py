#!/bin/python

#on local: gather list of all files and their associated modified-times (using filetreetool)
#send this to remote
#on remote: iterate through list, for each check if remote exists and is older or newer. 
#remote sends back a list of all the files that need to be updated (including non-existent-on-remote), and files that are newer on remote.

#user of program can configure whether to automatically download newer remote files for review, or to auto overwrite remote even if newer. 

