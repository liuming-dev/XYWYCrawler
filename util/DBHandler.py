#! /usr/bin/python

import redis


class Redis(object):
    __pool = None

    def __init__(self):
        self.__pipe = Redis.__getRedis().pipeline()

    @staticmethod
    def __getRedis():
        if Redis.__pool is None:
            Redis.__pool = redis.ConnectionPool(host='192.168.139.32', port=6379, password=123456, db=0)
        r = redis.StrictRedis(connection_pool=Redis.__pool)
        return r

    def saveUrl(self, tb, url):
        self.__pipe.rpush(tb, url).execute()

    def saveUrls(self, tb, urls):
        for url in urls:
            self.saveUrl(tb, url)

    # 获取list类型的对象中保存的元素
    def getUrl(self, tb):
        result = self.__pipe.lpop(tb).execute()
        if result[0] is not None:
            tmp = result[0].decode('utf-8')
            self.__pipe.rpush((tb.replace('+', '') if '+' in tb else tb + '+'), tmp).execute()
            return tmp
        return None

    def getUrls(self, tb, count):
        tmp = []
        if count == -1:
            while 1:
                result = self.getUrl(tb)
                if result is None:
                    break
                tmp.append(result)
        else:
            for i in range(count):
                result = self.getUrl(tb)
                if result is None:
                    break
                tmp.append(result)
        return tmp


class MySQL(object):
    pass


if __name__ == '__main__':
    print(Redis().getUrls('2004', 3))
