# -*-coding=utf-8-*-
__author__ = 'conglinfeng'

import datetime
import json
import logging
import re
import pandas as pd
import requests


# 爬取cninfo公告数据
class Cninfo(object):

    def __init__(self):
        self.url = ''

        # self.date = datetime.datetime.now().strftime('%Y-%m-%d')
        self.date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        self.nextTradeDate = (datetime.date.today() + datetime.timedelta(days=3)).strftime("%Y-%m-%d")

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


def main():
    logging.info('Start')
    keywords = [
        '要约收购', '混合所有制改革', '并购重组', '定向增发',
        # '增持', '减持',
        # '股权质押',
        # '发行股份',
        # '风险警示',
        # '可转换债券',
        # '停牌'
    ]

    stock_names = [
        '东方日升', '天味食品', '*ST融捷', '爱尔眼科', '阳光电源', '新城控股', '盛宏股份', '科顺股份', '金域医学', '德赛电池', '邮储银行', '兴齐眼药', '爱美客', '金龙鱼',
        '华域汽车', '伊利股份', '兴业银行', '潍柴动力', '保利地产', '格力电器', '海螺水泥', '宋城演艺', '中国平安', '华宇软件', '分众传媒', '安琪酵母', '上海机场', '伟星新材',
        '招商银行', '海康威视', '福耀玻璃', '中顺洁柔', '瀚蓝环境', '恒瑞医药', '平安银行', '万科A', '德赛电池', '中兴通讯', 'TCL科技', '美的集团''潍柴动力',
        '贵州茅台', '中国平安', '招商银行', '格力电器', '海螺水泥', '东方财富', '牧原股份', '旗滨集团', '五粮液', '恒瑞医药', '长江电力',
        '海天味业', '华域汽车', '兴业银行', '保利地产', '宋城演艺',
        '立讯精密', '药明康德', '东方财富', '万华化学', '宁德时代', '长江电力', '美的集团', '恒瑞医药', '招商银行', '中国中免', '中国平安', '五粮液', '贵州茅台', '海天味业',
        '中国重汽',
        '三一重工', '顺丰控股', '东方雨虹', '万孚生物', '片仔癀', '昭衍新药', '通威股份', '千禾味业', '隆基股份',
        '新产业', '卫星石化', '歌尔股份', '三安光电', '乐普医疗', '博腾股份', '泰格医药',
        '生物股份',
        '康泰生物'
        '汤臣倍健',
        '迈瑞医疗', '海螺水泥', '宁德时代', '海康威视', '牧原股份', '中信建投', '立讯精密', '顺丰控股', '韦尔股份',
        '伊利股份', '三一重工', '药明康德', '中公教育', '宁波银行', '万华化学', '爱尔眼科', '双汇发展', '新希望', '上海机场', '智飞生物', '闻泰科技',
        '金山办公', '长春高新', '用友网络', '隆基股份', '云南白药', '汇顶科技', '恒力石化', '兆易创新', '永辉超市', '公牛集团', '片仔癀',
        '深南电路'
    ]

    stock_names = pd.unique(stock_names).tolist()

    obj = Cninfo()

    # obj.stock_list()

    # for keyword in keywords:
    #     obj.group_title = keyword
    #     obj.pageNum = 1
    #     obj.search()
    #
    # for stock_name in stock_names:
    #     obj.group_title = stock_name
    #     obj.stock_code = ''
    #     for stock_code in obj.stockList:
    #         if stock_code['zwjc'] == stock_name:
    #             obj.stock_code = stock_code['code'] + ',' + stock_code['orgId']
    #             obj.pageNum = 1
    #             obj.search()
    #             break
    #     if not obj.stock_code:
    #         print(stock_name + ' 找不到匹配的 code')

    obj.sendWX()


if __name__ == '__main__':
    main()
