# -*-coding=utf-8-*-
__author__ = 'conglinfeng'

import datetime
import json
import logging
import re
import pandas as pd
import requests


# 爬取cninfo公告数据
# 部署在 GitHub Actions 执行
class Cninfo(object):

    def __init__(self):
        self.url = ''

        # self.date = datetime.datetime.now().strftime('%Y-%m-%d')
        self.date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        self.nextTradeDate = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': 'JSESSIONID=D0DCD2408272960BD5E45E5FF7C861AE; insert_cookie=37836164; routeId=.uc1; _sp_ses.2141=*; _sp_id.2141=34874370-d57e-4fac-b0f1-9712d6bd1254.1593741019.81.1610091486.1610077790.c50c98d9-1acc-46ad-87e2-e050789d9320',
            'Referer': 'http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&lastPage=index'}

        self.stockList = []  # 股票列表

        self.stock_code = ''  # 当前搜索股票代码
        self.group_title = ''  # 当前组名(搜索关键字，搜索股票代码)
        self.pageNum = 1  # 当前页码
        self.content_list = []  # 结果列表
        self.content = ''  # 格式化结果

    def post(self, url, data, retry=5):
        for i in range(retry):
            try:
                r = requests.post(url, headers=self.headers, data=data)
                print(r.text)
                if not r.text or r.status_code != 200:
                    continue
                else:
                    return r
            except Exception as e:
                logging.info(e)
                continue
        return None

    def get(self, url, retry=5):
        for i in range(retry):
            try:
                r = requests.get(url, headers=self.headers)
                if not r.text or r.status_code != 200:
                    continue
                else:
                    return r
            except Exception as e:
                logging.info(e)
                continue
        return None

    def search(self):
        self.url = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'

        post_data = {
            'pageNum': self.pageNum,
            'pageSize': '30',
            'column': 'szse',
            'tabName': 'fulltext',
            'plate': '',
            'stock': self.stock_code,
            'searchkey': self.group_title,  # 多个关键字以分号分隔
            'secid': '',
            'category': '',
            'trade': '',
            'seDate': '{}~{}'.format(self.date, self.nextTradeDate),
            'sortName': '',
            'sortType': '',
            'isHLtitle': 'true'
        }
        response = self.post(self.url, data=post_data)
        if not response:
            return None
        self.parse(response)

    def parse(self, response):
        dic = json.loads(response.text)
        print(self.group_title)
        print(dic)

        if dic.get("announcements"):

            for j in range(0, dic.get("announcements").__len__()):
                item = {}
                # 确实是存在没有命名的公告的
                titles = "未命名"
                if dic.get("announcements")[j]["announcementTitle"] is not None:
                    titles = re.split('[:：]', dic.get("announcements")[j]["announcementTitle"], 1)
                if titles.__len__() == 2:
                    title = titles[1]
                else:
                    title = titles[0]
                company = dic.get("announcements")[j]["secName"]
                adjuntUrl = dic.get("announcements")[j]["adjunctUrl"]
                adjuntUrl_time = adjuntUrl.split("/")[1]

                item["title"] = title.replace('<em>', '').replace('</em>', '')
                item["company"] = company.replace('<em>', '').replace('</em>', '')
                item["time"] = adjuntUrl_time
                item["url"] = "http://static.cninfo.com.cn/" + adjuntUrl

                self.content_list.append(item)

            if dic.get("hasMore"):
                self.pageNum += 1
                self.search()
            else:
                self.build_content()
        else:
            self.build_content()

    def stock_list(self):
        self.url = 'http://www.cninfo.com.cn/new/data/szse_stock.json'

        response = self.get(self.url)
        if not response:
            print('获取股票列表失败')
            return None

        self.stockList = json.loads(response.text)['stockList']
        print(self.stockList)

    # 每人每天发送上限500条
    # 相同内容5分钟内不能重复发送，
    # 不同内容一分钟只能发送30条
    def sendWX(self):
        title = '今日份最新公告'

        # url = "https://sc.ftqq.com/SCU147801T940ef25022761a5471783a24abf7318f5ff835bfbb8c0.send?text={}&desp={}".format(
        #     title, self.content)
        # r = requests.get(url)

        # print(url)

        print(self.content)

        # self.url = "https://sc.ftqq.com/SCU147801T940ef25022761a5471783a24abf7318f5ff835bfbb8c0.send"
        self.url = "https://sctapi.ftqq.com/SCT15193TK4ooKrGEAsw0lMBMnPqaPNEC.send"
        post_data = {
            'text': title,
            'desp': self.content
        }
        response = self.post(self.url, data=post_data)
        print(response)

    def build_content(self):
        if self.content_list.__len__() > 0:
            self.content = f'{self.content}{self.group_title} 有{self.content_list.__len__()}条新公告 \n\n'
            for item in self.content_list:
                self.content = f'{self.content}{item["company"]}:{item["title"]} {item["url"]} \n\n'
            self.content_list.clear()
        # else:
        # self.content = f'{self.content}{self.group_title} 没有新公告 \n\n'

    def writeFile(self):
        f = open('README.md', 'w')
        f.write(self.content)
        f.close()


def main():
    logging.info('Start')
    keywords = [
        '要约收购', '混合所有制改革', '并购重组', '定向增发',
        # '增持', '减持',
        # '股权质押',¬
        # '发行股份',
        # '风险警示',
        # '可转换债券',
        # '停牌'
    ]

    stock_names = [
        '东方日升', '天味食品', '*ST融捷', '爱尔眼科', '阳光电源', '新城控股', '盛宏股份', '科顺股份', '金域医学', '德赛电池', '邮储银行', '兴齐眼药', '爱美客', '金龙鱼',
    ]

    stock_names = pd.unique(stock_names).tolist()

    obj = Cninfo()

    obj.stock_list()

    for keyword in keywords:
        obj.group_title = keyword
        obj.pageNum = 1
        obj.search()

    for stock_name in stock_names:
        obj.group_title = stock_name
        obj.stock_code = ''
        for stock_code in obj.stockList:
            if stock_code['zwjc'] == stock_name:
                obj.stock_code = stock_code['code'] + ',' + stock_code['orgId']
                obj.pageNum = 1
                obj.search()
                break
        if not obj.stock_code:
            print(stock_name + ' 找不到匹配的 code')

    # obj.sendWX()
    obj.writeFile()


def main2():
    import math
    for i in range(9, 35):
        print(f'<dimen name="Pad_TextSize_{i}">{math.ceil(i * 1.1)}dp</dimen>')


if __name__ == '__main__':
    main()
