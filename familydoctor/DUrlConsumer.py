#! /usr/bin/python

import traceback
from datetime import datetime

import gevent
from gevent import monkey

from common.DBHandler import MySQL
from common.DBHandler import Redis
from common.IOHandler import FileIO
from common.IOHandler import NetworkIO

monkey.patch_all()


def getAllInfo(dbkey):
    urlPool = Redis().listUrls(dbkey, 1)
    # urlPool = ['http://club.xywy.com/familyDoctor/pay/86054846', 'http://club.xywy.com/familyDoctor/pay/43983196',
    #            'http://club.xywy.com/familyDoctor/pay/28476935']
    while 1:
        if len(urlPool) > 0:
            for url in urlPool:
                getInfo(url)
                getInfo2(url + '?info=1&page=1#name2')
                getInfo3(url + '?info=1&page=1#name2')
                getInfo4(url + '?info=2&page=1#name3')
            urlPool = Redis().listUrls(dbkey, 1)
        else:
            break


def getInfo(url):
    # http://club.xywy.com/familyDoctor/pay/43983196 对应的页面信息
    try:
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
            # 用户评分(放到用户评价界面抓取)
            # evaluateScore = html.findtext('.//span[@class="fl colClass01 fwei"]')
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
            dbInfo = (url, doctorName, doctorRank, doctorHosp.tail, medals, sendWord, serviceTypes[0], serviceTypes[1],
                      oldServiceTypes[0], oldServiceTypes[1], helpedInfo[0], helpedInfo[1], infos[0], infos[1],
                      infos[2])
            MySQL().saveDoctorInfo(dbInfo)
    except:
        doExpt('url1', url, 'url1')


def getInfo2(url):
    # http://club.xywy.com/familyDoctor/pay/43983196?info=1&page=2#name2 对应页面总的用户评价相关信息
    try:
        html = NetworkIO().requestHtml(url)
        if html is not None:
            evaluateScore = html.findtext('.//h4[@class="f30 colClass01 fWei tc"]').strip()
            evaluateStat = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
            evaluateStatBlock = html.findall('.//div[@class="HomSptop_Ri fWei f14 mt20 fl"]/span')
            for index, item in enumerate(evaluateStatBlock):
                tmptext = item.text
                evaluateStat[index] = 0 if len(tmptext) == 0 else int(tmptext[tmptext.find('（') + 1:tmptext.find('）')])
            dbInfo = (url, evaluateScore, evaluateStat[0], evaluateStat[1], evaluateStat[2], evaluateStat[3],
                      evaluateStat[4], evaluateStat[5], evaluateStat[6], evaluateStat[7])
            MySQL().saveDoctorEvaluation(dbInfo)
    except:
        doExpt('url2', url, 'url2')


def getInfo3(url):
    # http://club.xywy.com/familyDoctor/pay/43983196?info=1&page=2#name2 对应的用户评价具体内容
    try:
        # 当第一次访问页面时，除了获取评论信息，也要获取全部的评论页的总数
        html = NetworkIO().requestHtml(url)
        if html is not None:
            evaluateBlock = html.findall('.//div[@class="User_eval lh180 btn-a f14 fwei mt10"]')
            for index, block in enumerate(evaluateBlock):
                uName = block.findtext('.//span[@class="mr10 fl"]').strip()
                evalAtti = block.findtext('.//span[@class="fl colbd mr10"]').strip()
                evalScore = block.findtext('.//span[@class="colClass01 fl"]').strip()
                evalText = block.findtext('.//div[@class="pt5"]').strip()
                evalTime = block.findtext('.//span[@class="colbd f12 db pt10"]').strip()
                dbInfo = (url + '#' + str(index), uName, evalAtti, evalScore, evalText,
                          datetime.strptime(evalTime, '%Y-%m-%d %H:%M:%S'))
                MySQL().saveDoctorEvaluationText(dbInfo)
            # 评价共有多少页
            totalPageInfo = html.find('.//div[@class="mt20 HomeFen f14"]/span[@class="mr5"]')
            totalPageInfo = 1 if totalPageInfo is None else totalPageInfo.text.strip()[1:-3]
            # 目前评价页的索引值
            tmpIndex = url.find('page=') + 5
            currentPageIndex = url[tmpIndex:-6]
            # 获取当前页以后的评论页的评论信息
            if int(currentPageIndex) < int(totalPageInfo):
                for pageIndex in range(int(currentPageIndex) + 1, int(totalPageInfo) + 1):
                    url = url[:int(tmpIndex)] + str(pageIndex) + '#name2'
                    html = NetworkIO().requestHtml(url)
                    if html is not None:
                        evaluateBlock = html.findall('.//div[@class="User_eval lh180 btn-a f14 fwei mt10"]')
                        for index, block in enumerate(evaluateBlock):
                            uName = block.findtext('.//span[@class="mr10 fl"]').strip()
                            evalAtti = block.findtext('.//span[@class="fl colbd mr10"]').strip()
                            evalScore = block.findtext('.//span[@class="colClass01 fl"]').strip()
                            evalText = block.findtext('.//div[@class="pt5"]').strip()
                            evalTime = block.findtext('.//span[@class="colbd f12 db pt10"]').strip()
                            dbInfo = (url + '#' + str(index), uName, evalAtti, evalScore, evalText,
                                      datetime.strptime(evalTime, '%Y-%m-%d %H:%M:%S'))
                            MySQL().saveDoctorEvaluationText(dbInfo)
    except:
        doExpt('url3', url, 'url3')


def getInfo4(url):
    # http://club.xywy.com/familyDoctor/pay/43983196?info=2&page=2#name3 对应的服务购买信息
    try:
        html = NetworkIO().requestHtml(url)
        if html is not None:
            serviceBuyBlock = html.findall('.//div[@class="HomBone fwei f14"]')
            for index, block in enumerate(serviceBuyBlock):
                uName = block.findtext('.//span[@class="w100"]').strip()
                serviceType = 1 if '包月' in block.findtext('.//span[@class="w200 tl"]').strip() else 0
                serviceCount = block.findtext('.//span[@class="w60 tc"]').strip()
                servicePrice = block.findtext('.//span[@class="colClass01 fb w80 tc"]').strip()
                serviceStatus = block.findtext('.//span[@class="club_home_icon HomBsuc"]').strip()
                serviceTime = block.findtext('.//span[@class="col99 ml20 tc"]').strip()
                dbInfo = (url + '#' + str(index), uName, serviceType, serviceCount, servicePrice, serviceStatus,
                          serviceTime)
                MySQL().saveServiceInfo(dbInfo)
            # 评价共有多少页
            totalPageInfo = html.find('.//div[@class="mt20 HomeFen f14"]/span[@class="mr5"]')
            totalPageInfo = 1 if totalPageInfo is None else totalPageInfo.text.strip()[1:-3]
            # 目前评价页的索引值
            tmpIndex = url.find('page=') + 5
            currentPageIndex = url[tmpIndex:-6]
            # 获取当前页以后的评论页的评论信息
            if int(currentPageIndex) < int(totalPageInfo):
                for pageIndex in range(int(currentPageIndex) + 1, int(totalPageInfo) + 1):
                    url = url[:int(tmpIndex)] + str(pageIndex) + '#name3'
                    html = NetworkIO().requestHtml(url)
                    if html is not None:
                        serviceBuyBlock = html.findall('.//div[@class="HomBone fwei f14"]')
                        for index, block in enumerate(serviceBuyBlock):
                            uName = block.findtext('.//span[@class="w100"]').strip()
                            serviceType = 1 if '包月' in block.findtext('.//span[@class="w200 tl"]').strip() else 0
                            serviceCount = block.findtext('.//span[@class="w60 tc"]').strip()
                            servicePrice = block.findtext('.//span[@class="colClass01 fb w80 tc"]').strip()
                            serviceStatus = block.findtext('.//span[@class="club_home_icon HomBsuc"]').strip()
                            serviceTime = block.findtext('.//span[@class="col99 ml20 tc"]').strip()
                            dbInfo = (url + '#' + str(index), uName, serviceType, serviceCount, servicePrice,
                                      serviceStatus, serviceTime)
                            MySQL().saveServiceInfo(dbInfo)
    except:
        doExpt('url4', url, 'url4')


def doExpt(key, url, logIdentifier):
    Redis().saveUrl(key, url)
    FileIO.handleExpt(traceback.format_exc(), url, logIdentifier)


if __name__ == '__main__':
    dbkey = input('请输入医生url列表名称：')
    # threadList = []
    # for i in range(5):
    #     tmpThread = threading.Thread(target=getQPageInfo, args=(tmpYear, None if tmpPwd == '' else tmpPwd))
    #     threadList.append(tmpThread)
    # for tmpThread in threadList:
    #     tmpThread.start()
    # for tmpThread in threadList:
    #     tmpThread.join()
    jobs = []
    for i in range(5):
        jobs.append(gevent.spawn(getAllInfo, dbkey.strip()))
    gevent.joinall(jobs)
