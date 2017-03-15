#! /usr/bin/python

import traceback
from datetime import datetime

import gevent
from gevent import monkey

from common.DBHandler import MySQL
from common.DBHandler import Redis
from common.IOHandler import FileIO
from common.IOHandler import NetworkIO
from rpc.Client import UrlClient

monkey.patch_all()


def getAllInfo(dbkey):
    urlPool = Redis().listUrls(dbkey, 1)
    while 1:
        if len(urlPool) > 0:
            for url in urlPool:
                pass
        else:
            break


def getInfo(url):
    # http://club.xywy.com/familyDoctor/pay/43983196 对应的页面信息
    html = NetworkIO().requestHtml(url)
    if html is not None:
        # 医生姓名
        doctorName = html.findtext('.//i[@class="fwei fl"]')
        doctorName = doctorName[:-6] if doctorName is not None and len(doctorName) > 6 else None
        # 医生职称和医院科室
        doctorRankAndHosp = html.find('.//div[@class=" lh200 pt10 f14"]')
        doctorRank = doctorRankAndHosp.text
        doctorHosp = doctorRankAndHosp.find('./br')
        # 获取医生的勋章
        medalsBlock = html.findall('.//div[@class="HomePth"]/span')
        medals = ''
        for medal in medalsBlock:
            medals += medal.get('data-th') + ','
        # 医生的寄语
        sendWord = html.find('.//div[@class="f12 graydeep club_home_icon HomePj"]/span').tail
        # 医生的服务类型
        serviceTypeBlock = {0: html.find('.//div[@class="fl pr"]'), 1: None}
        if serviceTypeBlock[0] is None:
            serviceTypeBlock[1] = html.find('.//div[@class="fl f14"]')
        serviceTypes = {0: '', 1: ''}
        oldServiceTypes = {0: '', 1: ''}
        if serviceTypeBlock[0] is not None:
            serviceTypeBlock2 = serviceTypeBlock[0].findall('.//a[@cate]')
            for index, item in enumerate(serviceTypeBlock2):
                for text in item.itertext():
                    serviceTypes[index] += text.strip()
        elif serviceTypeBlock[1] is not None:
            # 各服务原始价格
            serviceTypeBlock2 = serviceTypeBlock[1].findall('.//a[@cate]')
            for index, item in enumerate(serviceTypeBlock2):
                for text in item.itertext():
                    serviceTypes[index] += text.strip()
            serviceTypeBlock2 = serviceTypeBlock[1].findall('.//span[@class="f14 col99 ml10"]')
            for index, item in enumerate(serviceTypeBlock2):
                for text in item.itertext():
                    oldServiceTypes[index] += text.strip()
        # 用户评分
        evaluateScore = html.findtext('.//span[@class="fl colClass01 fwei"]')
        # 签约家庭和帮助用户
        helpedInfo = {0: None, 1: None}
        helpedInfoBlock = html.findall('.//span[@class="fb f16 ml5"]')
        for index, item in enumerate(helpedInfoBlock):
            helpedInfo[index] = item.text
        # 擅长、简介以及荣誉
        infos = {0: '', 1: '', 2: ''}
        infoBlock = html.findall('.//div[@class="HomeJie f14 fwei pt20"]')
        for item in infoBlock:
            tmp = item.findtext('./h4')
            textblock = item.find('./div')
            tmptext = ''
            for text in textblock.itertext():
                tmptext += text.strip()
            if '擅长' in tmp:
                infos[0] = tmptext
            elif '简介' in tmp:
                infos[1] = tmptext
            elif '荣誉' in tmp:
                infos[2] = tmptext
        print(doctorName, doctorRank, doctorHosp.tail, medals, sendWord, serviceTypes, oldServiceTypes, evaluateScore,
              helpedInfo, infos)


def getInfo2(url):
    # http://club.xywy.com/familyDoctor/pay/43983196?info=1&page=2#name2 对应的页面信息
    pass


def getInfo3(url):
    # http://club.xywy.com/familyDoctor/pay/43983196?info=2&page=2#name3 对应的页面信息
    pass


def doExpt(password, tb, url, logIdentifier):
    if password is not None:
        UrlClient.saveUrl(password, tb, url)
    else:
        Redis().saveUrl(tb, url)  # 与redis在同一台主机上时
    FileIO.handleExpt(traceback.format_exc(), url, logIdentifier)


if __name__ == '__main__':
    # threadList = []
    # for i in range(5):
    #     tmpThread = threading.Thread(target=getQPageInfo, args=(tmpYear, None if tmpPwd == '' else tmpPwd))
    #     threadList.append(tmpThread)
    # for tmpThread in threadList:
    #     tmpThread.start()
    # for tmpThread in threadList:
    #     tmpThread.join()
    # jobs = []
    # for i in range(5):
    #     jobs.append(gevent.spawn(getQPageInfo, tmpYear, (None if tmpPwd == '' else tmpPwd)))
    # gevent.joinall(jobs)
    getInfo('http://club.xywy.com/familyDoctor/pay/43983196#name1')
    getInfo('http://club.xywy.com/familyDoctor/pay/28476935#name1')
