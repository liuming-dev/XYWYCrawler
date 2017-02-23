#! /usr/bin/python

from xmlrpc.server import SimpleXMLRPCServer

from util.DBHandler import Redis


class UrlServer(object):
    __method = ['getUrls']

    def __init__(self, address, tb):
        self.address = address
        self.__server = SimpleXMLRPCServer(address, allow_none=True)
        self.tb = tb
        for name in self.__method:
            self.__server.register_function(getattr(self, name))
        self.__server_forever()

    def getUrls(self, username):
        if username == 'liuming':
            return Redis().getUrls(self.tb, 200)
        return None

    def __server_forever(self):
        print('RPC server is running ...')
        self.__server.serve_forever()


if __name__ == '__main__':
    table = input('请输入需要查询到表名:')
    server = UrlServer(('', 10001), table.strip())
