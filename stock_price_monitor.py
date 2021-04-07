# -*-coding=utf-8-*-
__author__ = 'conglinfeng'

import datetime

import easyquotation
import numpy as np
from apscheduler.schedulers.blocking import BlockingScheduler

import notification


class Monitor(object):
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


def monitor():
    monitors = [
        ('01810', 21, 30),  # 小米
        ('03690', 280, 330),  # 美团
        ('00700', 600, 660)  # 腾讯
    ]

    obj = Monitor(monitors)
    obj.monitor()


def main():
    scheduler = BlockingScheduler()
    scheduler.add_job(monitor, 'interval', seconds=5)
    scheduler.start()


if __name__ == '__main__':
    main()
