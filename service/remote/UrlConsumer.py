#! /usr/bin/python

import socket
import threading
import traceback
from datetime import datetime

from util.DBHandler import MySQL
from util.DBHandler import Redis
from util.IOHandler import FileIO
from util.IOHandler import NetworkIO


def getQPageInfo(year):
    urlPool = Redis().getUrls(year, 200)
    # urlPool=['http://club.xywy.com/static/20170223/126671067.htm',
    #          'http://club.xywy.com/static/20170223/126671066.htm',
    #          'http://club.xywy.com/static/20170223/126671065.htm',
    #          'http://club.xywy.com/static/20170223/126671064.htm',
    #          'http://club.xywy.com/static/20170223/126671063.htm']
    while 1:
        if len(urlPool) > 0:
            for url in urlPool:
                try:
                    html = NetworkIO().getHtmlByRequests(url)
                    if html is not None:
                        # 获取问题信息
                        qInfoBlock = html.xpath('//div[@class="w980 clearfix bc f12 btn-a pr"]')
                        if len(qInfoBlock) > 0:
                            getQInfo(url, qInfoBlock[0])
                        # 获取关于问题的回复信息
                        replyInfoBlock = html.xpath('//div[@class="Doc_con clearfix pr mt5 "]')
                        if len(replyInfoBlock) > 0:
                            getReplyInfo(url, replyInfoBlock[0])
                except:
                    # print('>>>Exception: ' + traceback.format_exc())
                    doExpt(year + '-', url, '1')
            urlPool = Redis().getUrls(year, 200)
        else:
            break


def getQInfo(url, elem):
    sectionBlock = elem.findall('./p[@class="pt10 pb10 lh180 znblue normal-a"]/a')
    # 一级科室
    keshi1 = getPureText(sectionBlock[2].text)
    # 二级科室
    keshi2 = None
    if len(sectionBlock) >= 4:
        keshi2 = getPureText(sectionBlock[3].text)
    qInfoBlock = elem.find('./div/div[@class="User_askcon clearfix pr"]')
    # 问题题目
    qTitle = getPureText(qInfoBlock.find('.//p[@class="fl dib fb"]').text)
    userInfoBlock = qInfoBlock.findall('./div[@class="f12 graydeep Userinfo clearfix pl29"]/span')
    # 提问者姓名
    uName = None
    # 提问者性别
    uSex = None
    # 提问者年龄
    uAge = None
    # 问题发表时间
    qDatetime = None
    if len(userInfoBlock) >= 7:
        uName = getPureText(userInfoBlock[0].text)
        uSex = getPureText(userInfoBlock[2].text)
        uAge = getPureText(userInfoBlock[4].text)
        qDatetime = getPureText(userInfoBlock[6].text)
        qDatetime = (datetime.strptime(qDatetime, '%Y-%m-%d %H:%M:%S') if qDatetime is not None
                     else datetime.strptime('2000-01-01 00:00', '%Y-%m-%d %H:%M:%S'))
    # 问题内容
    qBodyBlock = qInfoBlock.find('./div/div[@id="qdetailc"]')
    qBody = ''
    for tmpText in qBodyBlock.itertext():
        subText = getPureText(tmpText)
        qBody = qBody + subText if subText is not None else ''
    MySQL().saveQInfo((url, qTitle, qBody, qDatetime, keshi1, keshi2, uName, uSex, uAge))


def getReplyInfo(url, elem):
    # 医生回复是否被采纳：0--未采纳；1--采纳
    accepted = elem.find('./div[@class="t9999 questnew_icon Quest_askh2 pa"]')
    accepted = getPureText(accepted.text) if accepted is not None else None
    accepted = 1 if accepted == '最佳答案' else 0
    # reply1Block = None
    if accepted:
        reply1Block = elem.findall('./div[@class="docall clearfix Bestbg"]')
    else:
        reply1Block = elem.findall('./div[@class="docall clearfix "]')
    reply1Index = 1
    for block in reply1Block:
        # 回复医生的个人url
        doctorUrl = block.find('.//a[@class="f14 fb Doc_bla"]')
        doctorUrl = doctorUrl.get('href') if doctorUrl is not None else None
        # 医生回复的具体内容
        reply1Body = block.find('.//div[@class="pt15 f14 graydeep  pl20 pr20"]')
        reply1Body = getAllText(reply1Body) if reply1Body is not None else None
        # 回复的时间
        reply1Datetime = block.find('.//p[@class="col99 tr clearfix pr20"]/span')
        reply1Datetime = getPureText(reply1Datetime.text)
        reply1Datetime = (datetime.strptime(reply1Datetime, '%Y-%m-%d %H:%M:%S') if reply1Datetime is not None
                          else datetime.strptime('2000-01-01 00:00', '%Y-%m-%d %H:%M:%S'))
        if accepted:
            puIndex = block.find('.//div[@class="clearfix pb10  pl20 pr20 ballc"]//b[@class="gratenum"]')
        else:
            puIndex = block.find('.//div[@class="clearfix pb10  pl20 pr20 ballc pr"]//b[@class="gratenum"]')
        puIndex = getPureText(puIndex.text) if puIndex is not None else None
        reply1Id = url + '#' + str(reply1Index)
        reply1Index += 1
        MySQL().saveReply1Info((reply1Id, doctorUrl, reply1Body, reply1Datetime, puIndex, accepted))

        # 获取二级回复信息
        reply2InfoBlock = block.findall('.//div[@class="appdoc appxian ml20 mr20 mt15 pb10 clearfix f14"]'
                                        '/div[@class="usezw pt10 clearfix"]')
        getReply2Info(reply1Id, reply2InfoBlock)


def getReply2Info(reply1Id, elems):
    reply2Index = 1
    for reply2InfoBlock in elems:
        # 二级回复中，是哪一方在回复:值为0表示提问者追问，值为1表示医生回复
        whoReply = reply2InfoBlock.find('.//span[@class="fl dib fb Doc_bla"]')
        whoReply = getPureText(whoReply.text if whoReply is not None else None)
        if whoReply is not None:
            if '追问' in whoReply:
                whoReply = 0
            else:
                whoReply = 1
        # 二级回复的内容
        reply2Body = reply2InfoBlock.find('.//*[@class="fl w390"]')
        reply2Body = getPureText(reply2Body.text)
        # 二级回复的时间
        reply2Datetime = reply2InfoBlock.find('./p[@class="tr col99 f12"]/span')
        reply2Datetime = getPureText(reply2Datetime.text)
        reply2Datetime = (datetime.strptime(reply2Datetime, '%Y-%m-%d %H:%M:%S') if reply2Datetime is not None
                          else datetime.strptime('2000-01-01 00:00', '%Y-%m-%d %H:%M:%S'))
        reply2Id = reply1Id + '_' + str(reply2Index)
        reply2Index += 1
        MySQL().saveReply2Info((reply2Id, reply2Body, whoReply, reply2Datetime))


def getAllText(reply1BodyBlock):
    tmp = ''
    for tmpText in reply1BodyBlock.itertext():
        subText = getPureText(tmpText)
        tmp = tmp + subText if subText is not None else ''
    return tmp


def getPureText(rawText):
    if rawText is not None:
        rawText = rawText.strip()
        if rawText == '':
            rawText = None
    return rawText


def doExpt(tb, url, logIdentifier):
    Redis().saveUrl(tb, url)
    FileIO.handleExpt(traceback.format_exc(), url, logIdentifier)


if __name__ == '__main__':
    socket.setdefaulttimeout(60)
    tmpYear = input('请输入数据所归属的年份:')
    MySQL().createTables()
    print('数据库中相应数据表已准备完成...')
    threadList = []
    for i in range(5):
        tmpThread = threading.Thread(target=getQPageInfo, args=(tmpYear.strip(),))
        threadList.append(tmpThread)
    for tmpThread in threadList:
        tmpThread.start()
    for tmpThread in threadList:
        tmpThread.join()
