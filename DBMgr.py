#! /usr/bin/python

import traceback

import pymysql
from DBUtils.PersistentDB import PersistentDB

# 数据库的配置信息
DB_HOST = '192.168.139.100'
DB_PORT = 3306
DB_NAME = 'xywy'
DB_USERNAME = 'MyDataBase'
DB_PASSWORD = 'wla123456'
DB_CHARSET = 'utf8'


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


def insert_q_info(conn, q_info):
    try:
        sql = "INSERT INTO 2016_q_info() VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        conn.cursor().execute(sql, q_info)
    except:
        import Crawler
        Crawler.write_to_log(q_info[0])
        print('Exception: ' + traceback.format_exc())


def insert_q_reply(conn, reply1_list, reply2_list):
    try:
        # 一级回复
        for item in reply1_list:
            sql = "INSERT INTO 2016_q_reply() VALUES(%s,%s,%s,%s,%s,%s,%s,%s);"
            conn.cursor().execute(sql, item)
        # 二级回复
        for items in reply2_list:
            for item in items:
                sql = "INSERT INTO 2016_q_reply_2() VALUES(%s,%s,%s,%s,%s,%s);"
                conn.cursor().execute(sql, item)
    except:
        print('Exception: ' + traceback.format_exc())
