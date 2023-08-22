#!/usr/bin/python

import json
import requests
import sqlite3
import sys
from wwwimgpull import *
#####################################################################

if (len(sys.argv) < 2):
    print('This program will download all of the images on a given 4chan thread. provide URL. ')
    print('you must provide a search word, or \"*\" for any word.')
    print('Usage: ./pullimgs.py <url>')
    sys.exit(0)

url = sys.argv[1]
for imgurl in pull4chImgs(url):
    print(imgurl)
