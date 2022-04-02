#!/usr/bin/python2

import json
import requests
import sqlite3
import sys
from wwwimgpull import *


def processCatalog(catalog, b):

    for i in range(0, len(catalog)): #each page of the board
        for j in range(0, len(catalog[i]['threads'])): #each OP on the page
            if not 'com' in catalog[i]['threads'][j]:
                continue
            url = "https://boards.4channel.org/"+b+"/thread/"+str(catalog[i]['threads'][j]['no'])
            if wod == "*" or wod == "" or wod.lower() in catalog[i]['threads'][j]['com'].lower():
                results_url.append(url)
                results_content.append(catalog[i]['threads'][j]['com'])
                for imgurl in pull4chImgs(url):
                    results_img.append(imgurl)
            if not 'last_replies' in catalog[i]['threads'][j]:
                continue
            for k in range(0, len(catalog[i]['threads'][j]['last_replies'])): #each comment on the OP
                r = catalog[i]['threads'][j]['last_replies'][k]
                if not 'com' in r:
                        continue
                if wod.lower() in r['com'].lower():
                    results_url.append(url+"#p"+str(catalog[i]['threads'][j]['last_replies'][k]['no']))
                    results_content.append(catalog[i]['threads'][j]['last_replies'][k]['com'])
                    #imgs were already retrieved from OP grab

def repliesSort(catalog):
    result = []
    for i in range(0, len(catalog)):
        for j in range(0, len(catalog[i]['threads'])):
            url = "https://boards.4channel.org/"+b+"/thread/"+str(catalog[i]['threads'][j]['no']) 
            result.append((url, catalog[i]['threads'][j]['replies']))
        
    result.sort(key=lambda v: v[1])
    return result

bods = ['a', 'c', 'w', 'm', 'cgl', 'cm', 'f', 'n', 'jp', 'vp', 'v', 'vg', 'vr', 'co', 'g', 'tv', 'k', 'o', 'an', 'tg', 'sp', 'asp', 'sci', 'int', 'out', 'toy', 'biz', 'i', 'po', 'p', 'ck', 'ic', 'wg', 'mu', 'fa', '3', 'gd', 'diy', 'wsg', 's', 'trv', 'fit', 'x', 'lit', 'adv', 'lgbt', 'mlp', 'b', 'r', 'r9k', 'pol', 'soc', 's4s']
abods = ['hc', 'hm', 'h', 'e', 'u', 'd', 'y', 't', 'hr', 'gif']


#####################################################################

r = True #just for debugging right now

if not r and (len(sys.argv) < 2 or sys.argv[1][0] == '-'):
    print('This program will give you the URLs of all 4chan posts that contain the given search word, either on the entire site or on a select board. You can also use wildcard as search word for all posts of board/site')
    print('you must provide a search word, or \"*\" for any word.')
    print('Usage: ./query.py <searchword> [board]')
    sys.exit(0)

if not r:
    wod = sys.argv[1] #the search keyword
bod = ''
if len(sys.argv) > 2:
    bod = sys.argv[2] #the board if interest, if given

results_url = [] #URLs of threads containing the keyword
results_content = [] #text of all posts and comments containing the keyword
results_img = [] #URLs of all images containing the keyword

if bod == '':
    print('searching all boards')
    repl_res = []
    for b in bods:
        res = requests.get("https://a.4cdn.org/"+b+"/catalog.json")
        repl_res.append(repliesSort(json.loads(res.text)))
        #processCatalog(json.loads(res.text), b)
    repl_res.sort(key=lambda v: v[1])
    print(repl_res)
else:
    print('searching board ' + bod)
    res = requests.get("https://a.4cdn.org/"+bod+"/catalog.json")
    print(repliesSort(json.loads(res.text)))
    processCatalog(json.loads(res.text), bod)


for url in results_url:
    print(url)
