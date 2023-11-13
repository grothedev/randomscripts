#!/bin/python

#some useful web-related scripts, such as crawling, searching for, downloading certain data

import requests
from bs4 import BeautifulSoup
import re
import sys
import time

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


#i used this for downloading a bunch of pdfs from some prepper website
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

#return a list of strings of all the links on the given webpage (<a> elements) whose href contains the given search string
def getLinksContainingStr(url, s):
    result = []
    resp = requests.get(url)
    html = BeautifulSoup(resp.text, 'html.parser')
    for link in html.find_all('a'):
        if link == None:
            print('non')
            continue
        h = link.get('href')
        if h and s in h:
            result.append(url + '/' + h)
    return result

#write each element of list l to file of path p
def writeListToFile(l, path):
    f = open(path, 'w')
    for e in l:
        f.write(str(e))
        f.write('\n')
    f.close()
    


#if len(sys.argv) < 2:
#    sys.exit(0)

#for url in pull4chImgs(sys.argv[1]):
#    print(url)

