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
from bs4 import BeautifulSoup
from StringIO import StringIO
from multiprocessing.dummy import Pool

__author__ = "Jason Hou"
__all__ = ['viewSource', 'parse', 'Clawer']

DEBUG = False
DEPTH = 0
data = {'amount': 0,
        'source': set(),
        'output': 'pics',
        'limit': None,
        'mutex': threading.Lock()}


def download(url, path):
    '''download file from url to path'''
    # with open(path, 'wb', -1) as f:
    # f.write(viewSource(url))
    urllib.urlretrieve(url, path)


class DownloadThread(threading.Thread):

    '''download thread'''

    def run(self):
        mutex = data.get('mutex')
        limit = data.get('limit')
        while True:
            begin = False
            if mutex.acquire(1):
                if len(data.get('source')) > 0:
                    if not limit or data.get('amount') < limit:
                        url, filename = data.get('source').pop()
                        imagePath = os.path.join(data.get('output'), '%s.%s' % (
                            filename, 'jpg'))
                        data['amount'] = data.get('amount') + 1
                        if not os.path.exists(imagePath):
                            begin = True
                            print('%s start downloading %s to %s' % (
                                self.name, url, imagePath))
                        else:
                            print('%s exists, stop downloading' % filename)
                    else:
                        mutex.release()
                        break
                else:
                    mutex.release()
                    break
                mutex.release()
            if begin:
                download(url, imagePath)


class Clawer(object):

    '''clawer class'''

    def __init__(self, url, number=10, output='pics', limit=None):
        self.url = url if url.startswith('http') else 'http://{0}'.format(url)
        self.number = number
        self.output = output
        self.limit = limit
        self.links = set()

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
        data['output'] = self.output
        data['limit'] = self.limit
        for image in Pool().map(self.getImages, self.links):
            data['source'] |= image
        if not os.path.exists(self.output):
            os.mkdir(self.output)
        for i in range(self.number):
            t = DownloadThread()
            t.start()


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
