# -*-coding=utf-8-*-
__author__ = 'conglinfeng'

from datetime import *


def getWeekDay(day=date.today(), accuracy=None):
    '''
    获取工作日(周一到周五)
    :param day:
    :param accuracy: 当前日期不是工作日，递增取还是递减取。可取 'add'和'minus'
    :return:
    '''
    if day.isoweekday() in set((6, 7)):
        if accuracy == 'add':
            day += timedelta(days=8 - day.isoweekday())
        elif accuracy == 'minus':
            day -= timedelta(days=day.isoweekday() - 5)
    return day


def test():
    for i in range(8):
        day = date.today() + timedelta(days=i)
        start_day = getWeekDay(day, 'minus')
        end_day = getWeekDay(day, 'add')
        print(f'{day} {start_day} {end_day}')


if __name__ == '__main__':
    test()
