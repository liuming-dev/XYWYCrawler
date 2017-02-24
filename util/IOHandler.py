#! /usr/bin/python

import random
import time

import requests
from lxml import etree


class NetworkIO(object):
    def __init__(self):
        self.__userAgents = [
            ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
             'Chrome/55.0.2883.87 Safari/537.36'),
            ('Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
             'Chrome/56.0.2924.87 Safari/537.36'),
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; Trident/7.0; .NET4.0C; .NET4.0E)',
            'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        ]
        self.__reqHeaders = {
            'Accept-Encoding': 'gzip, deflate, sdch',
            'User-Agent': self.__userAgents[random.randint(0, 3)]
        }

    def getHtmlByRequests(self, url):
        resp = requests.get(url, headers=self.__reqHeaders, timeout=30)
        if resp.status_code == 200:
            resp.encoding = 'gb2312'
            return etree.HTML(resp.text)
        else:
            return None


class FileIO(object):
    @staticmethod
    def __writeToFile(text, filename):
        file = open('./' + filename, 'a', encoding='utf-8')
        file.write(text + '\n')
        file.close()

    @staticmethod
    def handleExpt(exptMsg, url, identifier):
        FileIO.__writeToFile('[' + time.strftime('%Y-%y-%d %X', time.localtime()) + ']: ' + (url if url else '') + '\n'
                             + exptMsg + '\n', '../../resource/error_log_' + identifier)
