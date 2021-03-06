# -*-coding=utf-8-*-
__author__ = 'conglinfeng'

import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

from cninfo import main as cninfo_main


def job():
    cninfo_main()


def test():
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M %S.%f"))


def main():
    scheduler = BlockingScheduler()
    scheduler.add_job(test, 'interval', seconds=60 * 5)
    scheduler.add_job(job, 'cron', day_of_week='1-5', hour=23, minute=59)
    scheduler.start()


if __name__ == '__main__':
    main()
