#! /usr/bin/python

import crawler

all_day_1th_page_urls = []


# 开始爬取时，获取全部已有天的病人问题列表第一页的url
def get_all_day_1th_page_url(page_count):
    url_prefix = 'http://club.xywy.com/keshi/'
    index = 1
    while index <= page_count:
        page_url = url_prefix + str(index) + '.html'
        index += 1
        html = crawler.get_html(page_url)
        if html is not None:
            # 获取此页面(page_url)中每天的问题列表中的第一页url
            urls = html.xpath('//ul[@class="club_Date clearfix"]/li/a/@href')
            for url in urls:
                if '2017' not in url:
                    all_day_1th_page_urls.append(url)


def output_urls(task_count):
    total_count = len(all_day_1th_page_urls)
    index = 0
    while index < total_count:
        with open('./task' + str(index % task_count) + '.txt', 'a') as file:
            file.write(all_day_1th_page_urls[index] + '\n')
        index += 1


if __name__ == '__main__':
    count1 = input('Input the page count: ')
    count2 = input('Input the task count: ')
    get_all_day_1th_page_url(int(count1))
    output_urls(int(count2))
    print('Finished...')
