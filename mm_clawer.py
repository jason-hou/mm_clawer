#coding=utf-8
'''fetch image from specified webpage'''

import os
import urllib
import hashlib
from bs4 import BeautifulSoup

__author__ = "Jason Hou"
__all__ = ['download']

def download(url):
    '''download image from url'''
    resp = urllib.urlopen(url).read()
    soup = BeautifulSoup(resp)
    for i in soup.find_all('img'):
        if i.string:
            target = i.get('src')
            imagePath = '%s.%s' % (hashlib.sha1(target).hexdigest(),
                target.split('.')[-1])
            if not os.path.exists(imagePath):
                print('download %s to %s' % (target, imagePath))
                urllib.urlretrieve(target, imagePath)
            else:
                print('this image has been fetched')

if __name__ == '__main__':
    url = r'http://www.22mm.cc'
    download(url)

