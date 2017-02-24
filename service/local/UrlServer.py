#! /usr/bin/python

from xmlrpc.server import SimpleXMLRPCServer

from util.DBHandler import Redis


class UrlServer(object):
    __method = ['getUrls', 'saveUrl']

    def __init__(self, username, address, tb):
        self.__username = username
        self.__server = SimpleXMLRPCServer(address, allow_none=True)
        self.__tb = tb
        for name in self.__method:
            self.__server.register_function(getattr(self, name))
        self.__server_forever()

    def getUrls(self, username):
        if username == self.__username:
            return Redis().getUrls(self.tb, 200)
        return None

    def saveUrl(self, username, tb, url):
        if username == self.__username:
            Redis().saveUrl(tb, url)

    def __server_forever(self):
        print('RPC server is running ...')
        self.__server.serve_forever()


if __name__ == '__main__':
    tmpUsername = input('请指定一个认证用户名:')
    table = input('请输入需要查询到表名:')
    server = UrlServer(tmpUsername.strip(), ('', 10001), table.strip())
