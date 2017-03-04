#! /usr/bin/python

import pymysql
import redis
from DBUtils.PersistentDB import PersistentDB

# 设定数据库表的特定前缀和后缀
TB_PRIFIX = '20170225___2016_'

# 数据库的配置信息
DB_HOST = '192.168.139.100'
DB_PORT = 3306
DB_NAME = 'xywy'
DB_USERNAME = 'MyDataBase'
DB_PASSWORD = 'wla123456'
DB_CHARSET = 'utf8'
TB_Q_INFO = TB_PRIFIX + 'q_info'
TB_Q_REPLY = TB_PRIFIX + 'q_reply1'
TB_Q_REPLY_2 = TB_PRIFIX + 'q_reply2'


class Redis(object):
    __pool = None

    def __init__(self):
        self.__pipe = Redis.__getRedis().pipeline()

    @staticmethod
    def __getRedis():
        if Redis.__pool is None:
            Redis.__pool = redis.ConnectionPool(host='127.0.0.1', port=6379, password='9f37174731055084', db=0)
        r = redis.StrictRedis(connection_pool=Redis.__pool)
        return r

    def saveUrl(self, key, *url, backup=False):
        if backup:
            self.__pipe.lpush(key, *url).lpush(key + '+', *url).execute()
        else:
            self.__pipe.lpush(key, *url).execute()

    # 获取list类型的对象中保存的元素
    def getUrl(self, key, backup=False):
        result = self.__pipe.rpop(key).execute()
        if result[0] is not None:
            tmp = result[0].decode('utf-8')
            if not backup:
                self.__pipe.lpush((key.replace('+', '') if '+' in key else key + '+'), tmp).execute()
            return tmp
        return None

    def listUrls(self, key, count=100, backup=False):
        tmp = []
        if count == -1:
            while 1:
                result = self.getUrl(key, backup)
                if result is None:
                    break
                tmp.append(result)
        else:
            for i in range(count):
                result = self.getUrl(key, backup)
                if result is None:
                    break
                tmp.append(result)
        return tmp

    '''
    下面的两个方法用于构建代理池使用，但是实际使用效果不好，不再使用
    不好的原因可能在于：免费的代理网络拥塞比较严重，已发生丢包情况
    '''
    def saveIPs(self, key, *ips):
        self.__pipe.delete(key).sadd(key, *ips).execute()

    def getRandIP(self, key):
        ip = self.__pipe.srandmember(key).execute()[0]
        if ip is not None:
            ip = ip.decode('utf-8')
        return ip


class MySQL(object):
    def __init__(self):
        self.__conn = ConnPoolMgr().connection()

    def createTables(self):
        with open('../resource/DDL.sql', 'r', encoding='utf-8') as file:
            ddl = file.read()
        ddl = ddl.replace('q_info', TB_Q_INFO).replace('q_reply1', TB_Q_REPLY).replace('q_reply2', TB_Q_REPLY_2)
        print(ddl)
        self.__conn.cursor().execute(ddl)

    def saveQInfo(self, qInfo):
        sql = "INSERT IGNORE INTO " + TB_PRIFIX + "q_info() VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        self.__conn.cursor().execute(sql, qInfo)

    def saveReply1Info(self, reply1Info):
        sql = "INSERT IGNORE INTO " + TB_PRIFIX + "q_reply1() VALUES(%s,%s,%s,%s,%s,%s);"
        self.__conn.cursor().execute(sql, reply1Info)

    def saveReply2Info(self, reply2Info):
        sql = "INSERT IGNORE INTO " + TB_PRIFIX + "q_reply2() VALUES(%s,%s,%s,%s);"
        self.__conn.cursor().execute(sql, reply2Info)


class ConnPoolMgr(object):
    __pool = None

    def __init__(self):
        self.__conn = ConnPoolMgr.__get_conn()

    @staticmethod
    def __get_conn():
        if ConnPoolMgr.__pool is None:
            ConnPoolMgr.__pool = PersistentDB(
                creator=pymysql,
                setsession=['SET AUTOCOMMIT=1'],
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USERNAME,
                passwd=DB_PASSWORD,
                charset=DB_CHARSET,
                use_unicode=True
            )
        return ConnPoolMgr.__pool.connection()

    def connection(self):
        return self.__conn


if __name__ == '__main__':
    pass
