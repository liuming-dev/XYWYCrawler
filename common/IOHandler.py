#! /usr/bin/python

import time

import requests
from lxml import etree

from common import ReqConfig


class NetworkIO(object):
    def __init__(self):
        self.__headers = {
            'Accept-Encoding': 'gzip, deflate, sdch',
            'User-Agent': ReqConfig.getUserAgent()
        }

    def requestHtml(self, url, encoding='gb2312'):
        result = None
        resp = requests.get(url, headers=self.__headers, timeout=(10, 30))
        if resp.status_code == 200:
            resp.encoding = encoding
            result = etree.HTML(resp.text)
        return result


class FileIO(object):
    @staticmethod
    def __writeToFile(text, filename):
        file = open('./' + filename, 'a', encoding='utf-8')
        file.write(text + '\n')
        file.close()

    @staticmethod
    def handleExpt(exptMsg, url, identifier):
        FileIO.__writeToFile('[' + time.strftime('%Y-%y-%d %X', time.localtime()) + ']: ' + (url if url else '') + '\n'
                             + exptMsg + '\n', '../log/error_log_' + identifier)


if __name__ == '__main__':
    pass
