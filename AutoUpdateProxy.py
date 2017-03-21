import json
import time
import traceback

import requests
from lxml import etree


def updateProxy():
    with open('F:\liuming\Shadowsocks\gui-config.json', encoding='utf-8', mode='r') as file:
        proxyInfo = json.load(file)
    while 1:
        requestHeaders = {
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'DNT': '1',
            'Host': 'doub.io',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'hrome/56.0.2924.87 Safari/537.36',
        }
        resp = requests.get('https://doub.io/sszhfx/', headers=requestHeaders)
        if resp.status_code == 200:
            html = etree.HTML(resp.text)
            trs = html.findall('.//table[@width="100%"]/tbody/tr')
            if len(trs) > 0:
                skipped = True  # 用于控制跳过表格汇总的标题行
                for index, tr in enumerate(trs):
                    if not skipped:
                        skipped = False
                        continue
                    tds = tr.findall('./td')
                    if len(tds) == 7 and tds[1].text is not None:
                        tmpIP = tds[1].text
                        existed = False  # 用于标识代理是否已经存在
                        # 遍历已有代理信息，查看目标代理是否存在
                        for ind, ip in enumerate(proxyInfo['configs']):
                            if ip['server'] in tmpIP:
                                existed = True
                                # 存在则更新设置
                                proxyInfo['configs'][ind]['server_port'] = tds[2].text
                                proxyInfo['configs'][ind]['password'] = tds[3].text
                                proxyInfo['configs'][ind]['method'] = tds[4].text
                                proxyInfo['configs'][ind]['remarks'] = 'doub.io-' + str(index)
                        if not existed:
                            # 不存在，则新建添加
                            proxy = {
                                "server": tmpIP,
                                "server_port": tds[2].text,
                                "password": tds[3].text,
                                "method": tds[4].text,
                                "remarks": 'doub.io-' + str(index),
                                "auth": False
                            }
                            proxyInfo['configs'].append(proxy)
            with open('F:\liuming\Shadowsocks\gui-config.json', encoding='utf-8', mode='w') as file:
                print(proxyInfo)
                json.dump(proxyInfo, file, ensure_ascii=False)
            break
        time.sleep(60)  # 如果请求页面失败，一分钟后再次请求


if __name__ == '__main__':
    try:
        while 1:
            updateProxy()
            time.sleep(3600)  # 控制每隔一个小时，更新一下代理信息
    except:
        print(traceback.format_exc())
