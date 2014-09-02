#coding=utf-8
'''fetch image from specified webpage'''

import os
import urllib
import threading
from bs4 import BeautifulSoup

__author__ = "Jason Hou"
__all__ = ['Clawer']

DEBUG = False
data = {'amount': 0,
        'source': set(),
        'output': 'pics',
        'limit' : None,
        'mutex' : threading.Lock()}

class DownloadThread(threading.Thread):
    '''download thread'''
    def run(self):
        mutex = data.get('mutex')
        limit = data.get('limit')
        while True:
            begin = False
            if mutex.acquire(1):
                if len(data.get('source'))>0:
                    if not limit or data.get('amount')<limit:
                        url, filename = data.get('source').pop()
                        imagePath = os.path.join(data.get('output'),'%s.%s' % (
                            filename, url.split('.')[-1]))
                        data['amount'] = data.get('amount') + 1
                        if not os.path.exists(imagePath):
                            begin = True
                            print('%s start download %s to %s' % (
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
                urllib.urlretrieve(url, imagePath)

class Clawer(object):
    '''clawer class'''
    def __init__(self, url, threads=10, output='pics', limit=None):
        self.url = url
        self.threads = threads
        self.output = output
        self.limit = limit
    
    def start(self):
        data['output'] = self.output
        data['limit'] = self.limit
        resp = urllib.urlopen(self.url).read()
        soup = BeautifulSoup(resp)
        data['source'] = set((i['src'],i.parent['title']) 
            for i in soup.find_all('img',src=True)
            if i.parent.get('title') and '.gif' not in i.get('src'))
        if not os.path.exists(self.output):
            os.mkdir(self.output)
        for i in range(self.threads):
            t=DownloadThread()
            t.start()
        
if __name__ == '__main__':
    url = r'http://www.22mm.cc'
    c=Clawer(url, threads=5, output='photo', limit=20)
    c.start()

