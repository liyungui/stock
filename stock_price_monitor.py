# -*-coding=utf-8-*-
__author__ = 'conglinfeng'

import datetime

import easyquotation
import numpy as np
from apscheduler.schedulers.blocking import BlockingScheduler

import notification


class MonitorHK(object):
    '''
    港股价格监控
    使用了 easyquotation(github 开源项目)
    '''

    def __init__(self, monitors):
        monitors = np.asarray(monitors)
        self.notification = notification.Notification()
        self.monitors = monitors
        self.code = self.monitors[..., 0].tolist()

    def monitor(self):
        quotation = easyquotation.use("hkquote")
        data = quotation.real(self.code)
        self.parse(data)

    def parse(self, data):
        # print(data)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M %S.%f"))
        for i in range(0, self.code.__len__()):
            stock_price = data.get(self.code[i]).get('price')
            stock_name = data.get(self.code[i]).get('name')
            monitor_low = float(self.monitors[i, 1])
            monitor_high = float(self.monitors[i, 2])
            if stock_price <= monitor_low:
                content = f'现价 {stock_price} 低于 {monitor_low}'
                print(stock_name + " " + content)
                self.notification.show(stock_name, content, None)
            elif stock_price >= monitor_high:
                content = f'现价 {stock_price} 高于 {monitor_high}'
                print(stock_name + " " + content)
                self.notification.show(stock_name, content, None)
            else:
                print(stock_name + f' 现价 {stock_price}')


class MonitorCH(object):
    '''
    A股价格监控
    使用了 easyquotation(github 开源项目)
    '''

    def __init__(self, monitors):
        monitors = np.asarray(monitors)
        self.notification = notification.Notification()
        self.monitors = monitors
        self.code = self.monitors[..., 0].tolist()

    def monitor(self):
        quotation = easyquotation.use("tencent")
        data = quotation.real(self.code)
        self.parse(data)

    def parse(self, data):
        # print(data)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M %S.%f"))
        for i in range(0, self.code.__len__()):
            stock_price = data.get(self.code[i]).get('now')
            stock_name = data.get(self.code[i]).get('name')
            monitor_low = float(self.monitors[i, 1])
            monitor_high = float(self.monitors[i, 2])
            if stock_price <= monitor_low:
                content = f'现价 {stock_price} 低于 {monitor_low}'
                print(stock_name + " " + content)
                self.notification.show(stock_name, content, None)
            elif stock_price >= monitor_high:
                content = f'现价 {stock_price} 高于 {monitor_high}'
                print(stock_name + " " + content)
                self.notification.show(stock_name, content, None)
            else:
                print(stock_name + f' 现价 {stock_price}')


def monitor():
    localtime = datetime.datetime.now()
    hour = localtime.hour
    minute = localtime.minute
    morningOpen = hour > 9 or hour == 9 and minute >= 30
    morningClose = hour > 11 or hour == 11 and minute >= 30
    morningHKClose = hour >= 12
    afternoonOpen = hour >= 13
    afternoonClose = hour >= 15
    afternoonHKClose = hour >= 16

    if (morningOpen and not morningHKClose) or (afternoonOpen and not afternoonHKClose):
        monitorsHK = [
            # ('01810', 21, 33),  # 小米
            # ('03690', 190, 330),  # 美团
            ('00700', 265, 365),  # 腾讯
            ('02318', 37.5, 55),  # 中国平安
        ]

        objHK = MonitorHK(monitorsHK)
        objHK.monitor()
    else:
        print(f"HK market closed {hour}:{minute}")

    if (morningOpen and not morningClose) or (afternoonOpen and not afternoonClose):
        monitorsCH = [
            # ('000597', 4.93, 5.5),  # 东北制药
            # ('000983', 10, 11),  # 山西焦煤
            # ('688680', 230, 300),  # 海优新材
            # ('300003', 20, 29),  # 乐普医疗
            # ('300079', 8, 9),  # 数码视讯
            # ('600740', 10.4, 11.1),  # 山西焦化
            # ('600722', 8.0, 8.1),  # 金牛化工
            # ('600732', 17, 20),  # 爱旭股份
            # ('300582', 23, 27.1),  # 英飞特
            # ('601600', 5, 7),  # 中国中铝
            # ('600276', 52.5, 52.8),  # 恒瑞医药
            # ('300871', 26.01, 31.1),  # 回盛生物
            # ('688212', 30.56, 32),  # 澳华内镜
            # ('300207', 36.40, 50),  # 欣旺达
            # ('601888', 180, 240),  # 中国中免
            # ('002221', 12.04, 13.80),  # 东华能源
            # ('123128', 105, 120),  # 首华转债
            # ('301071', 270, 300),  # 力量钻石
            # ('603358', 18, 25),  # 华达科技
            # ('300618', 72.1, 100),  # 寒锐钴业
            # ('300489', 24.01, 30),  # 光智科技
            # ('688212', 31.56, 43),  # 澳华内镜
            # ('600075', 7.6, 8.4),  # 新疆天业
            # ('601919', 17.11, 20.1),  # 中远海控
            # ('002989', 22.93, 30),  # 中天精装
            # ('603122', 22, 30),  # 合富中国
            # ('603056', 12.85, 30),  # 德邦股份 13.15元全面要约（目标退市），已出报告书，要约时间2022.8.2-2022.8.31
            # ('600283', 11.09, 30),  # 钱江水利，11.09元全面要约，已出摘要。
            # ('600865', 10.1, 30),  # 百大集团，11.59元部分要约8.5%，已出摘要。
            # ('601177', 7.13, 30),  # 杭齿前进，8.13元部分要约19.99%，已出报告书，要约时间2022.4.7-2022.5.6
            # ('002813', 21.7, 30),  # 路畅科技，21.67元部分要约23.83%，已出报告书，要约时间2022.3.31-2022.4.29
            # ('002088', 19.4, 30),  # 鲁阳节能，21.73元部分要约24.86%，已出报告书，要约时间2022.5.24-2022.6.22
            # ('002088', 5.5, 30),  # 东风汽车，5.6元部分要约25.1%，未出摘要
            # ('113057', 109, 122.0),  # 中银转债
            # ('000881', 8.65, 9.95),  # 中广核技
            # ('600260', 2.5, 3.9),  # st凯乐
            # ('600122', 1.8, 2.26),  # st宏图
            # ('002122', 2.1, 2.44),  # st天马
            ('002366', 5.35, 6.38),  # st海核
            ('002316', 3.0, 6.38),  # st亚联
            # ('000564', 0.94, 1.33),  # st大集
            # ('600781', 2.6, 3.44),  # st辅仁
            # ('603603', 6.1, 8.34),  # st博天
            # ('000150', 1.4, 1.85),  # st宜康
            # ('002482', 2.1, 2.45),  # st广田
            # ('002113', 1.5, 2.45),  # st天润
            # ('118012', 134.8, 136),  # 微芯转债
            # ('002404', 7.26, 7.27),  # 嘉欣丝绸
            # ('000599', 5.0, 6.0),  # 青岛双星
            # ('111005', 125, 129),  # 富春转债
            # ('000736', 28.25, 32.26),  # 中交地产
            # ('000722', 23.29, 25.30),  # 湖南发展
            # ('000722', 21.0, 25.30),  # 湖南发展
            # ('688655', 20.8, 30),  # 迅捷兴
            # ('113052', 108, 130),  # 兴业转债
            # ('128114', 99.5, 130),  # 正邦转债
        ]

        objCH = MonitorCH(monitorsCH)
        objCH.monitor()
    else:
        print(f"CN market closed {hour}:{minute}")


def main():
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(monitor, 'interval', seconds=5)
    scheduler.start()


def timeTest():
    monitor(datetime.time(8, 59))
    monitor(datetime.time(9, 0))
    monitor(datetime.time(9, 29))
    monitor(datetime.time(9, 30))
    monitor(datetime.time(10, 59))
    monitor(datetime.time(11, 30))
    monitor(datetime.time(12, 0))
    monitor(datetime.time(13, 0))
    monitor(datetime.time(13, 1))
    monitor(datetime.time(15, 0))
    monitor(datetime.time(15, 1))
    monitor(datetime.time(16, 0))


if __name__ == '__main__':
    main()
    # timeTest()
