#! /usr/bin/python

import socket
import traceback

import gevent
from gevent import monkey

from util.DBHandler import Redis
from util.IOHandler import FileIO
from util.IOHandler import NetworkIO

monkey.patch_all()


class QUrlProducer(object):
    '''
    问题列表页的url存放在键名形如“-2016”的列表队列中
    具体问题页的url存储在键名形如“2016”的列表队列中
    抓取流程：
    1、抓取全部的问题列表页的url入队对应的列表队列中
    2、获取（出队）全部问题列表页url，遍历病操作每一个url，获取页面中具体问题的url并存入到对应的列表队列中
        1）如果问题列表页的url处理失败（未能成功请求该页面、获取页面中具体问题的url以及存储到相应队列中），将其再次存储到相应的列表队列中，方便下次重新遍历
        2）问题列表页url列表队列中不再存在可遍历的url时，遍历结束，成功获取全部目标问题的url
    '''

    def __init__(self, startPage, endPage, rules):
        if 0 < startPage <= endPage:
            self.__startPage = startPage
            self.__endPage = endPage
            self.__rules = rules
            self.__years = set([])

    def getAllQUrl(self):
        self.__getDayUrl()
        print('需要抓取数据所属年份为：' + str(self.__years))
        for year in self.__years:
            pageUrlTask = Redis().getUrls('-' + year, -1, restore=False)
            while 1:
                if len(pageUrlTask) > 0:
                    # 全部任务分为8个小任务
                    allTask = {}
                    for i in range(8):
                        allTask[i] = []
                    for index, url in enumerate(pageUrlTask):
                        allTask[index % 8].append(url)
                    # 创建8个协程
                    jobs = []
                    for i in range(8):
                        jobs.append(gevent.spawn(QUrlProducer.__getAllQUrl, allTask[i], year))
                    gevent.joinall(jobs)

                    pageUrlTask = Redis().getUrls('-' + year, -1, restore=False)
                else:
                    break
            print(year + '的问题url获取工作已经结束...')

    def __getDayUrl(self):
        urlPrefix = 'http://club.xywy.com/keshi/'
        for pageIndex in range(self.__startPage, self.__endPage + 1):
            tmpUrl = urlPrefix + str(pageIndex) + '.html'
            html = NetworkIO().getHtmlByRequests(tmpUrl)
            if html is not None:
                dayLinkBlock = html.xpath('//ul[@class="club_Date clearfix"]//a')
                for dayLink in dayLinkBlock:
                    dayName = dayLink.text.strip('[] ')
                    if not self.__isFiltered(dayName):
                        dayUrl = dayLink.get('href')
                        # print((dayName, dayUrl))
                        year = dayName[0:4] if len(dayName) == 10 else '2000'
                        if year not in self.__years:
                            self.__years.add(year)
                        Redis().saveUrl('-' + year, dayUrl)
            print(tmpUrl + ' --> completed...')

    @staticmethod
    def __getAllQUrl(task, year):
        for url in task:
            try:
                date = url[27:37]  # 用户构造问题url
                pageBase = int(url[38:-5])
                html = NetworkIO().getHtmlByRequests(url)
                if html is not None:
                    pageCount = QUrlProducer.__getDayPageCount(html)
                    qUrls = QUrlProducer.__getPageQUrl(html)
                    Redis().saveUrls(year, qUrls)

                    if pageCount > pageBase:
                        for pageIndex in range(pageBase + 1, pageCount + 1):
                            url = 'http://club.xywy.com/keshi/' + date + '/' + str(pageIndex) + '.html'
                            html = NetworkIO().getHtmlByRequests(url)
                            if html is not None:
                                qUrls = QUrlProducer.__getPageQUrl(html)
                                Redis().saveUrls(year, qUrls)
            except:
                # print('>>>Exception: ' + traceback.format_exc())
                QUrlProducer.__doExpt('-' + year, url, '0')

    @staticmethod
    def __getDayPageCount(html):
        pageIndexBlock = html.find('.//div[@class="subFen"]')
        tmpStr = ''
        for text in pageIndexBlock.itertext():
            tmpStr = tmpStr + text
        tmpStr = tmpStr[tmpStr.rfind('共') + 1:tmpStr.rfind('页')].strip()
        return int(tmpStr)

    @staticmethod
    def __getPageQUrl(html):
        qUrls = []
        qLinkBlock = html.xpath('//div[@class="club_dic"]/h4/em/a')
        for qLink in qLinkBlock:
            qUrl = qLink.get('href')
            # qTitle = qLink.text
            qUrls.append(qUrl)
        return qUrls

    @staticmethod
    def __doExpt(tb, url, logIdentifier):
        Redis().saveUrl(tb, url)
        FileIO.handleExpt(traceback.format_exc(), url, logIdentifier)

    def __isFiltered(self, dayName):
        for rule in self.__rules:
            if rule in dayName:
                return True
        return False


if __name__ == '__main__':
    socket.setdefaulttimeout(30)
    print('请输入如下初始化参数 -->')
    startPageIndex = input('输入起始抓取页面索引值: ')
    endPageIndex = input('输入结束抓取页面索引值: ')
    filterRule = input('输入不需要抓取的天或年:')
    if len(filterRule.replace(' ', '')) == 0:
        filterRule = []
    else:
        filterRule = filterRule.split(',')
    print((int(startPageIndex), int(endPageIndex), filterRule))
    QUrlProducer(int(startPageIndex), int(endPageIndex), filterRule).getAllQUrl()
