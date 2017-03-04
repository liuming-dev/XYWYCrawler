#! /usr/bin/python

import traceback

import gevent
from gevent import monkey

from common.DBHandler import Redis
from common.IOHandler import FileIO
from common.IOHandler import NetworkIO

monkey.patch_all()


class DUrlProducer(object):
    def __init__(self):
        self.__initUrl = 'http://club.xywy.com/familyDoctor/jib'
        self.__threadCount = 8
        self.runCrawler()

    def __getAllSicknessUrl(self):
        html = NetworkIO().requestHtml(self.__initUrl)
        if html is not None:
            sicknessUrls = html.xpath('//a[@class="mr5"]/@href')
            tmpUrls = []
            for url in sicknessUrls:
                tmpUrls.append('http://club.xywy.com' + url + '&keyword=&page=1')
            Redis().saveUrl('sickness-url', *tmpUrls)

    def runCrawler(self):
        self.__getAllSicknessUrl()
        allTargetUrls = Redis().listUrls('sickness-url', -1)
        while 1:
            if len(allTargetUrls) > 0:
                allSubTasks = []
                for i in range(self.__threadCount):
                    allSubTasks.append([])
                for index, url in enumerate(allTargetUrls):
                    allSubTasks[index % self.__threadCount].append(url)
                # 创建5个协程
                jobs = []
                for i in range(self.__threadCount):
                    jobs.append(gevent.spawn(DUrlProducer.__getAllDUrl, allSubTasks[i]))
                gevent.joinall(jobs)
                allTargetUrls = Redis().listUrls('sickness-url', -1)
            else:
                break
        print('每个疾病的首页url获取结束...')

    @staticmethod
    def __getAllDUrl(thisTask):
        for url in thisTask:
            try:
                spiltIndex = url.rfind('page=') + 5
                urlPrefix = url[:spiltIndex]
                basePageIndex = int(url[spiltIndex:])
                html = NetworkIO().requestHtml(url)
                if html is not None:
                    doctorUrls = DUrlProducer.__getDoctorUrl(html)
                    pageCount = html.xpath('//div[@class="mt20 HomeFen f14"]/a[@class="page"]/text()')
                    pageCount = 1 if len(pageCount) == 0 else pageCount[-1]
                    pageCount = int(pageCount)
                    Redis().saveUrl('family-doctor-url', *doctorUrls, backup=True)

                    if pageCount > basePageIndex:
                        for pageIndex in range(basePageIndex + 1, pageCount + 1):
                            url = urlPrefix + str(pageIndex)
                            html = NetworkIO().requestHtml(url)
                            if html is not None:
                                doctorUrls = DUrlProducer.__getDoctorUrl(html)
                                Redis().saveUrl('family-doctor-url', *doctorUrls, backup=True)
            except:
                # print('>>>Exception: ' + traceback.format_exc())
                DUrlProducer.__doExpt('sickness-url', url, 'doctor_0')

    @staticmethod
    def __getDoctorUrl(html):
        doctorUrls = html.xpath('//div[@class="FaMSlist clearfix"]/@onclick')
        flag = 1
        if len(doctorUrls) == 0:
            doctorUrls = html.xpath('//div[@class="FaMSlist clearfix"]//div[@class="FaMpic fl mt15"]/a/@href')
            flag = 0
        return DUrlProducer.__convertToFullUrl((flag, doctorUrls))

    @staticmethod
    def __convertToFullUrl(item):
        tmpUrls = []
        for url in item[1]:
            if item[0]:
                tmpUrls.append('http://club.xywy.com' + url[24:-2])
            else:
                tmpUrls.append('http://club.xywy.com' + url)
        return tmpUrls

    @staticmethod
    def __doExpt(key, url, logIdentifier):
        Redis().saveUrl(key, url)
        FileIO.handleExpt(traceback.format_exc(), url, logIdentifier)


if __name__ == '__main__':
    DUrlProducer()
