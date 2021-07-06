# -*- encoding=utf8 -*-
__author__ = 'conglinfeng'

from sqlalchemy import create_engine


def get_engine(db_name):
    """
    方法用于
    """
    return create_engine('mysql+mysqlconnector://root:dbroot@quanlist2018@localhost:3306/{}'.format(db_name))


def is_holiday():
    """
    方法用于
    """
    pass


def get_mysql_conn(db_name, host):
    """
    方法用于
    """
    pass
