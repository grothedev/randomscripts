#!/bin/python2

import requests
from bs4 import BeautifulSoup
import re
import sys
import time

###
# get images from websites
#    will probably be updated to include other data
###

#returns an array of img src urls from a 4chan thread
def pull4chImgs(url):
    result = []
    resp = requests.get(url)
    html = BeautifulSoup(resp.text, 'html.parser')
    for a in html.find_all('a'):
        if 'class' in a.attrs and 'fileThumb' in a.attrs['class']:
            url = a.get('href')
            if url[0:2] == '//':
                url = 'https:' + url
            result.append(url)
    return result

def pullVids(url):
    result = []
    resp = requests.get(url)
    html = BeautifulSoup(resp.text, 'html.parser')
    for a in html.find_all('a'):
        if '.webm' in a.get('href'):
            result.append(a.get('href'))
    return result

def pullImgs(url):
    result = []
    resp = requests.get(url)
    html = BeautifulSoup(resp.text, 'html.parser')
    for img in html.find_all('img'):
        srcURL = img.get('src')
        result.append(srcURL)
    return result

#def pullPDFs(url):
#    return pullPDFs(url, 0)

def pullPDFs(url, depth=0, alreadycrawled=[]):
    if depth > 5 or url == '' or url is None or url in alreadycrawled: 
        return [] 
    baseurl=url[0:url.find('/', 8)+1]
    result = []
    print(url)
    resp = requests.get(url)
    html = BeautifulSoup(resp.text, 'html.parser')
    alreadycrawled.append(url)
    for a in html.find_all('a'):
        url = a.get('href')
        if url is None or url == '' or url == '/':
            continue
        if baseurl not in url and 'http' in url[0:4]: #this means that the url is pointing to external site
            continue
        print('found ' + url)
        if 'http' not in url:
            url = baseurl+url
        if url.find('.pdf')>0 and os.path.isfile(url):
            result.append(url)
        else:
            time.sleep(5)
            result = result + pullPDFs(url, depth+1, alreadycrawled)
    return result

#if len(sys.argv) < 2:
#    sys.exit(0)

#for url in pull4chImgs(sys.argv[1]):
#    print(url)

