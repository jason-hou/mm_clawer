# coding=utf-8
'''fetch image from specified web page'''

import os
import re
import urllib
import urllib2
import urlparse
import gzip
import argparse
import threading
import random
from bs4 import BeautifulSoup
from StringIO import StringIO
from multiprocessing.dummy import Pool
from multiprocessing import Queue, Process

__author__ = "Jason Hou"
__all__ = ['Clawer']

DEBUG = False
UseThreading = True
DEPTH = 0


def download(url, path):
    '''download file from url to path'''
    # with open(path, 'wb', -1) as f:
    # f.write(viewSource(url))
    urllib.urlretrieve(url, path)


class DownloadThread(threading.Thread):

    '''download thread'''

    def __init__(self, output, q):
        self.output = output
        self.q = q
        threading.Thread.__init__(self)

    def run(self):
        while not self.q.empty():
            url, filename = self.q.get()
            imagePath = os.path.join(self.output, '%s.%s' % (
                filename, 'jpg'))
            if not os.path.exists(imagePath):
                print('%s start downloading %s to %s' % (
                    self.name, url, imagePath))
                download(url, imagePath)
            else:
                print('%s exists, stop downloading' % filename)


class DownloadProcess(Process):
    def __init__(self, output, q):
        self.output = output
        self.q = q
        Process.__init__(self)
        
    def run(self):        
        while not self.q.empty():
            url, filename = self.q.get()
            imagePath = os.path.join(self.output, '%s.%s' % (
                filename, 'jpg'))
            if not os.path.exists(imagePath):
                print('start downloading %s to %s' % (url, imagePath))
                download(url, imagePath)
            else:
                print('%s exists, stop downloading' % filename)


class Clawer(object):

    '''clawer class'''

    def __init__(self, url, number=10, output='pics', limit=None):
        self.url = url if url.startswith('http') else 'http://{0}'.format(url)
        self.number = number
        self.output = output
        self.limit = limit
        self.links = set()
        self.source = set()
        self.queue = Queue()

    def parse(self, url):
        '''parse url, return soup object'''
        req = urllib2.Request(url)
        req.add_header('Accept-encoding', 'gzip')
        resp = urllib2.urlopen(req, timeout=5)
        if resp.info().get('Content-Encoding') == 'gzip':
            content = gzip.GzipFile(fileobj=StringIO(resp.read())).read()
        else:
            content = resp.read()
        soup = BeautifulSoup(content)
        charset = soup.original_encoding
        if charset != u'utf-8':
            soup = BeautifulSoup(content.decode(charset, 'ignore'))
        return soup

    def getLinks(self, url, depth=DEPTH):
        '''get all links in url recursively'''
        self.links.add(url)
        links = set(urlparse.urljoin(self.url, i['href'])
                    for i in self.parse(url).find_all('a', href=True)
                    if re.search(r'(htm(l)?$|/$)', i['href']))
        if depth > 0:
            for i in links:
                if i not in self.links:
                    self.getLinks(i, depth - 1)

    def getImages(self, url):
        '''get images info from url'''
        return set((urlparse.urljoin(url, i['src']), i.parent['title'])
                   for i in self.parse(url).find_all('img', src=True)
                   if i.parent.get('title') and 'logo' not in i.get('src'))

    def start(self):
        self.getLinks(self.url)
        for image in Pool().map(self.getImages, self.links):
            self.source |= image
        if self.limit:
            self.source = random.sample(self.source, self.limit)
        map(self.queue.put, self.source)
        if not os.path.exists(self.output):
            os.mkdir(self.output)
        DOWNLOAD_METHOD = DownloadThread if UseThreading else DownloadProcess
        for i in range(self.number):
            m = DOWNLOAD_METHOD(self.output, self.queue)
            m.start()

def options():
    parser = argparse.ArgumentParser(
        description='clawer image from specified url')
    parser.add_argument('url', help='url from which you want to download')
    parser.add_argument('-o', '--output', default='pics',
                        help='specified the output folder to save')
    parser.add_argument('-n', '--number', default=10, type=int,
                        help='specified threading number, default 10')
    parser.add_argument('-l', '--limit', default=None, type=int,
                        help='specified limit download amount, default No limit')
    return parser.parse_args()

if __name__ == '__main__':
    # url = r'http://www.22mm.cc'
    args = options()
    c = Clawer(
        args.url, number=args.number, output=args.output, limit=args.limit)
    c.start()
