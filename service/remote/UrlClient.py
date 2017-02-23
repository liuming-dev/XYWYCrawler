#! /usr/bin/python

from xmlrpc.client import ServerProxy


class UrlClient(object):
    @staticmethod
    def getUrls():
        with ServerProxy('http://192.168.139.32:10001/', allow_none=True) as proxy:
            urls = proxy.getUrls('liuming')
        return urls


if __name__ == '__main__':
    print(UrlClient.getUrls())
