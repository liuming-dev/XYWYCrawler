#! /usr/bin/python

from xmlrpc.client import ServerProxy


class UrlClient(object):
    @staticmethod
    def getUrls(password):
        with ServerProxy('http://192.168.139.32:10001/', allow_none=True) as proxy:
            return proxy.getUrls(password)

    @staticmethod
    def saveUrl(password, tb, url):
        with ServerProxy('http://192.168.139.32:10001/', allow_none=True) as proxy:
            proxy.saveUrl(password, tb, url)

    @staticmethod
    def getIP(password):
        with ServerProxy('http://192.168.139.32:10001/', allow_none=True) as proxy:
            return proxy.getIP(password)


if __name__ == '__main__':
    pass
