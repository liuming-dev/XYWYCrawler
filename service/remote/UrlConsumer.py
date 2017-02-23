#! /usr/bin/python

from datetime import datetime

from util.IOHandler import NetworkIO


def getQPageInfo():
    # urlPool = UrlClient.getUrls()
    urlPool = ['http://club.xywy.com/static/3/1234.htm',
               'http://club.xywy.com/static/20161207/123982687.htm',
               'http://club.xywy.com/static/20161207/123982709.htm',
               'http://club.xywy.com/static/20161207/123982714.htm',
               'http://club.xywy.com/static/20161229/124483009.htm',
               'http://club.xywy.com/static/20161228/124462978.htm']
    while 1:
        if len(urlPool) > 0:
            for url in urlPool:
                html = NetworkIO().getHtmlByRequests(url)
                if html is not None:
                    # qInfoBlock = html.xpath('//div[@class="w980 clearfix bc f12 btn-a pr"]')
                    # getQInfo(qInfoBlock[0])
                    replyInfoBlock = html.xpath('//div[@class="Doc_con clearfix pr mt5 "]')
                    getReplyInfo(replyInfoBlock[0])

                    # urlPool = UrlClient.getUrls()
        else:
            break


def getQInfo(elem):
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
    print(qTitle, qBody, qDatetime, keshi1, keshi2, uName, uSex, uAge)


def getReplyInfo(elem):
    # 医生回复是否被采纳：0--未采纳；1--采纳
    accepted = elem.find('./div[@class="t9999 questnew_icon Quest_askh2 pa"]')
    accepted = 1 if getPureText(accepted.text) == '最佳答案' else 0
    # reply1Block = None
    if accepted:
        reply1Block = elem.findall('./div[@class="docall clearfix Bestbg"]')
    else:
        reply1Block = elem.findall('./div[@class="docall clearfix "]')
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
        puIndex = getPureText(puIndex.text)
        print(doctorUrl, reply1Body, reply1Datetime, puIndex, accepted)

        # 获取二级回复信息
        reply2InfoBlock = block.findall('.//div[@class="appdoc appxian ml20 mr20 mt15 pb10 clearfix f14"]'
                                        '/div[@class="usezw pt10 clearfix"')
        getReply2Info(reply2InfoBlock)


def getReply2Info(elems):
    pass


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


if __name__ == '__main__':
    getQPageInfo()
