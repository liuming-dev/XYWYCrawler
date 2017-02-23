#! /usr/bin/python

import queue
import random
import socket
import threading
import traceback
import urllib.error
import urllib.request
from datetime import datetime

from lxml import etree

import DBMgr
from DBMgr import ConnPoolMgr

task_urls = []
q_queue = queue.Queue(100)
user_agents = [
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; Trident/7.0; .NET4.0C; .NET4.0E)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    ('Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 '
     'Edge/14.14393')
]


# ------------------------------获取每个问题的url的线程类---------------------------------#
class QUrlGetter(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.day_finished = False
        self.day_url = ''

    def run(self):
        while task_urls:
            self.day_url = task_urls.pop()
            self.day_finished = False
            while not self.day_finished:
                self.get_q_url()

    def get_q_url(self):
        html = get_html(self.day_url)
        if html is not None:
            # 提取每天的问题列表中问题的url
            urls = html.xpath('//h4[@class="clearfix"]/em/a/@href')
            for url in urls:
                q_queue.put(url)
            # 同一天中下一页问题列表的url
            results = html.xpath('//div[@class="subFen"]/a[text()="[下一页]"]/@href')
            if len(results) > 0:
                self.day_url = self.day_url[0:self.day_url.rindex('/') + 1] + results[0]
            else:
                self.day_finished = True


# --------------------------------获取每个问题的信息 线程类-----------------------------------#
class QPageParser(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while 1:
            url = q_queue.get()
            self.get_page_info(url)
            q_queue.task_done()

    def get_page_info(self, url):
        html = get_html(url)
        if html is not None:
            self.get_question_info(url, html)
            self.get_reply(url, html)

    def get_question_info(self, url, html):
        try:
            a_block = html.xpath('//p[@class="pt10 pb10 lh180 znblue normal-a"]/a')
            keshi1 = a_block[2].text
            keshi2 = a_block[3].text
            # 提取病人的问题<题目>
            tmp_title = html.xpath('//p[@class="fl dib fb"]/text()')
            q_title = tmp_title[0] if tmp_title is not None and len(tmp_title) > 0 else ''
            # 提取病人的问题<内容>
            tmp_body_blocks = html.xpath('//div[@id="qdetailc"]')
            q_body_block = tmp_body_blocks[0] if tmp_body_blocks is not None and len(tmp_body_blocks) > 0 else None
            q_body = ''
            if q_body_block is not None:
                for text in q_body_block.itertext():
                    q_body = q_body + text.strip()
            # 提取问问题病人的信息
            user_info = html.xpath('//div[@class="f12 graydeep Userinfo clearfix pl29"]'
                                   '/span[not(@class="User_newbg User_fticon")]')
            u_name = ''
            u_sex = ''
            u_age = ''
            q_publish_time = ''
            if user_info is not None and len(user_info) >= 4:
                # 用户名
                u_name = user_info[0].text.strip() if user_info[0].text is not None else ''
                # 用户性别
                tmp_sex = user_info[1].text
                u_sex = tmp_sex.strip() if tmp_sex is not None else None
                # 用户年龄
                tmp_age = user_info[2].text
                u_age = tmp_age.strip() if tmp_age is not None else None
                # 问题发布时间
                tmp_datetime = user_info[3].text
                q_publish_time = (tmp_datetime.strip() if tmp_datetime is not None
                                                          and tmp_datetime is not '' else '1990-01-01 00:00:00')
            q_datetime = datetime.strptime(q_publish_time, '%Y-%m-%d %H:%M:%S')
            q_info = (
                url, q_title, q_body, q_datetime, u_name, u_sex, u_age, keshi1, keshi2, datetime.date(datetime.now()))
            # print(q_info)
            DBMgr.insert_q_info(ConnPoolMgr().connection(), q_info)
        except:
            print('Exception: ' + traceback.format_exc())

    def get_reply(self, url, html):
        try:
            q_reply_infos = html.xpath('//div[@class="docall clearfix Bestbg"]')
            self.get_reply_info(url, q_reply_infos, True)
            q_reply_infos = html.xpath('//div[@class="docall clearfix "]')
            self.get_reply_info(url, q_reply_infos, False)
        except:
            print('Exception: ' + traceback.format_exc())

    def get_reply_info(self, url, reply_infos, accepted):
        q_reply1_list = []
        q_reply2s_list = []
        index = 1
        for info in reply_infos:
            # 提取回复问题医生的url
            doctor_url_block = info.find('.//a[@class="f14 fb Doc_bla"]')
            doctor_url = doctor_url_block.get('href') if doctor_url_block is not None else ''
            # 提取回复的内容
            reply_body_part = info.find('.//div[@class="pt15 f14 graydeep  pl20 pr20"]')
            reply_body = ''
            for text in reply_body_part.itertext():
                reply_body = reply_body + text
            # 提取回复时间
            reply_datetime_str = info.find('.//span[@class="User_newbg User_time Doc_time"]').text
            reply_datetime = datetime.strptime(reply_datetime_str.strip() if reply_datetime_str is not None
                                                                             and reply_datetime_str is not ''
                                               else '1990-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
            # 提取回复的有用数
            pu_block = info.find('.//b[@class="gratenum"]')
            pu_index = pu_block.text if pu_block is not None else 0
            tmp_accepted = 1 if accepted else 0
            # 构建reply_id
            reply_id = url + '#' + str(tmp_accepted) + '_' + str(index)
            q_reply1 = (url, reply_id, doctor_url, reply_body, reply_datetime,
                        pu_index, tmp_accepted, datetime.date(datetime.now()))
            index += 1

            if q_reply1 is not None:
                q_reply1_list.append(q_reply1)
                q_reply2s = self.get_reply2(q_reply1[1], info)
                q_reply2s_list.append(q_reply2s) if q_reply2s is not None else 0

        DBMgr.insert_q_reply(ConnPoolMgr().connection(), q_reply1_list, q_reply2s_list)

    def get_reply2(self, reply_id, info):
        try:
            reply2_block = info.findall('.//div[@class="usezw pt10 clearfix"]')
            index = 1
            reply_list = []
            for reply2 in reply2_block:
                # 构造id
                reply2_id = reply_id + '_' + str(index)
                # 回复内容
                reply2_text_block = reply2.find('.//div[@class="ml10 fl"]')
                tmp_text = ''
                for text in reply2_text_block.itertext():
                    tmp_text += text.strip()
                # 哪一方回复
                who_reply = 1 if '回复' in tmp_text else 0
                # 回复时间
                reply2_datetime_str = reply2.find('.//span[@class="User_newbg User_time Doc_time"]').text
                reply2_datetime = (datetime.strptime(reply2_datetime_str.strip()
                                                     if reply2_datetime_str is not None
                                                        and reply2_datetime_str is not ''
                                                     else '1990-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'))
                q_reply2 = (reply_id, reply2_id, tmp_text, who_reply, reply2_datetime,
                            datetime.date(datetime.now()))
                reply_list.append(q_reply2)
                index += 1
            # print(reply_list)
            return reply_list
        except:
            print('Exception: ' + traceback.format_exc())
        return None


# -----------------------------发送网络请求，获取请求页面的函数--------------------------------#
def get_html(url):
    try:
        req_headers = {
            'User-Agent': user_agents[random.randint(0, 3)]
        }
        req_obj = urllib.request.Request(url, data=None, headers=req_headers)
        req = urllib.request.urlopen(req_obj)
        content = req.read().decode('gb2312', 'ignore')
        req.close()
    except socket.timeout:
        print('Exception: ' + traceback.format_exc())
        write_to_log(url)
        return None
    except:
        print('Exception: ' + traceback.format_exc())
        write_to_log(url)
        return None
    html = etree.HTML(content)
    return html


# ------------------------------请求失败的url写入日志文件---------------------------------#
def write_to_log(url):
    file = open('./failure_url.txt', 'a')
    file.write(url + '\n')
    file.close()


def init():
    file = open('./failure_url.txt', 'w')
    file.write('')
    file.close()
    # 设置socket超时时间
    socket.setdefaulttimeout(60)


# -----------------------------------------------------------------------------#
def main():
    # 读取需要爬取的页面url
    task = input('Which task to process: ')
    with open('./task' + task + '.txt', 'r') as file:
        while 1:
            line = file.readline()
            if line:
                task_urls.append(line)
            else:
                break
    # 启动线程及相关设置
    init()
    threads = []
    t0 = QUrlGetter()
    threads.append(t0)
    for ti in range(8):
        t1 = QPageParser()
        threads.append(t1)
    for thread_obj in threads:
        thread_obj.start()
    for thread_obj in threads:
        thread_obj.join()


if __name__ == '__main__':
    main()
