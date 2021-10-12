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
    港股价格监控
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
    morningOpen = localtime.hour >= 9 and localtime.minute >= 30
    morningClose = localtime.hour >= 11 and localtime.minute >= 30
    morningHKClose = localtime.hour >= 12
    afternoonOpen = localtime.hour >= 13
    afternoonClose = localtime.hour >= 15
    afternoonHKClose = localtime.hour >= 16

    if (morningOpen and not morningHKClose) or (afternoonOpen and not afternoonHKClose):
        monitorsHK = [
            # ('01810', 21, 33),  # 小米
            # ('03690', 190, 330),  # 美团
            ('00700', 460, 500),  # 腾讯
            ('02318', 56, 60),  # 中国平安
        ]

        objHK = MonitorHK(monitorsHK)
        objHK.monitor()
    else:
        print(f"HK market closed {localtime.hour}:{localtime.minute}")

    if (morningOpen and not morningClose) or (afternoonOpen and not afternoonClose):
        monitorsCH = [
            # ('601888', 230, 250),  # 中国中免
            # ('000597', 4.93, 5.5),  # 东北制药
            # ('000983', 10, 11),  # 山西焦煤
            ('688680', 210, 230),  # 海优新材
            # ('300003', 25, 29),  # 乐普医疗
            # ('300079', 9, 9.8),  # 数码视讯
            # ('600740', 10.4, 11.1),  # 山西焦化
            # ('600722', 8.0, 8.1),  # 金牛化工
            ('300207', 36, 39.5),  # 欣旺达
            ('600732', 13.5, 14.6),  # 爱旭股份
            ('300582', 22.8, 24.1),  # 英飞特
        ]

        objCH = MonitorCH(monitorsCH)
        objCH.monitor()
    else:
        print(f"CN market closed {localtime.hour}:{localtime.minute}")


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
