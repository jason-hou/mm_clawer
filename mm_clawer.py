#coding=utf-8
'''fetch image from specified webpage'''

import os
import urllib
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool

__author__ = "Jason Hou"
__all__ = ['download']

def fetch(source):
    '''fetch image from url'''
    assert len(source)==2
    url, filename = source
    imagePath = '%s.%s' % (filename, url.split('.')[-1])
    if not os.path.exists(imagePath):
        print('download %s to %s' % (url, imagePath))
        urllib.urlretrieve(url, imagePath)
    else:
        print('%s has been fetched' % imagePath)

def download(url):
    '''download images from url'''
    resp = urllib.urlopen(url).read()
    soup = BeautifulSoup(resp)
    target = ((i['src'],i.parent['title']) 
        for i in soup.find_all('img',src=True)
        if i.parent.get('title') and '.gif' not in i.get('src'))
    pool = Pool()
    pool.map(fetch,target)
    pool.close()
    pool.join()

if __name__ == '__main__':
    url = r'http://www.22mm.cc'
    download(url)

