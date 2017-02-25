#! /usr/bin/python

from xmlrpc.server import SimpleXMLRPCServer

from common.DBHandler import Redis


class UrlServer(object):
    __method = ['getUrls', 'saveUrl', 'getIP']

    def __init__(self, password, address, tb):
        self.__password = password
        self.__server = SimpleXMLRPCServer(address, allow_none=True)
        self.__tb = tb
        for name in self.__method:
            self.__server.register_function(getattr(self, name))
        self.__server_forever()

    def getUrls(self, password):
        if password == self.__password:
            return Redis().listUrls(self.__tb, 300)
        return None

    def saveUrl(self, password, tb, url):
        if password == self.__password:
            Redis().saveUrl(tb, url)

    def getIP(self, password):
        if password == self.__password:
            return Redis().getRandIP('proxy')
        return None

    def __server_forever(self):
        print('RPC server is running ...')
        self.__server.serve_forever()


if __name__ == '__main__':
    tmppwd = input('请指定一个用于认证的密码:')
    table = input('请输入需要查询的队列键名:')
    server = UrlServer(tmppwd.strip(), ('', 10001), table.strip())
