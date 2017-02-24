#! /usr/bin/python

from xmlrpc.client import ServerProxy


class UrlClient(object):
    @staticmethod
    def getUrls(username):
        with ServerProxy('http://127.0.0.1:10001/', allow_none=True) as proxy:
            urls = proxy.getUrls(username)
        return urls

    @staticmethod
    def saveUrl(username, tb, url):
        with ServerProxy('http://192.168.139.32:10001/', allow_none=True) as proxy:
            proxy.saveUrl(username, tb, url)


if __name__ == '__main__':
    pass
