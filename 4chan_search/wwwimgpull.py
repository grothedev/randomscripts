import requests
from bs4 import BeautifulSoup
import re

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

def pullImgs(url):
    result = []
    resp = requests.get(url)
    html = BeautifulSoup(resp.text, 'html.parser')
    for img in html.find_all('img'):
        srcURL = img.get('src')
        result.append(srcURL)
    return result
