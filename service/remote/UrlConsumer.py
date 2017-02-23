#! /usr/bin/python

from service.remote.UrlClient import UrlClient
from util.IOHandler import NetworkIO


def getQPageInfo():
    # urlPool = UrlClient.getUrls()
    urlPool = ['http://club.xywy.com/static/20161228/124462978.htm']
    while 1:
        if len(urlPool) > 0:
            for url in urlPool:
                print(url)
                html = NetworkIO().getHtmlByRequests(url)
                if html is not None:
                    targetBlock = html.xpath('//div[@class="w980 clearfix bc f12 btn-a pr"]')
                    getQInfo(targetBlock[0])

            urlPool = UrlClient.getUrls()
        else:
            break


def getQInfo(elem):
    sectionBlock = elem.findall('./p[@class="pt10 pb10 lh180 znblue normal-a"]/a')
    keshi1 = sectionBlock[2].text
    if len(sectionBlock) == 4:
        keshi2 = sectionBlock[3].text
    else:
        keshi2 = None
    qInfoBlock = elem.find('./div/div[@class="User_askcon clearfix pr"]')
    qTitle = qInfoBlock.find('.//p[@class="fl dib fb"]').text
    print(qTitle)


if __name__ == '__main__':
    getQPageInfo()
