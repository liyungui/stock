# -*-coding=utf-8-*-
__author__ = 'conglinfeng'

import logging

'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
import re
import time
import datetime
import requests
import pandas as pd
from settings import get_engine, get_mysql_conn
from sqlalchemy import VARCHAR
from eastmoney_bond_api import Bond
import matplotlib.pyplot as plt

engine = get_engine('db_jisilu')


# 爬取集思录 可转债的数据
class Jisilu(object):
    def __init__(self):

        self.date = datetime.datetime.now().strftime('%Y-%m-%d')

        self.timestamp = int(time.time() * 1000)
        self.headers = {
            'User-Agent': 'User-Agent:Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'}

        self.url = 'https://www.jisilu.cn/data/cbnew/cb_list/?___jsl=LST___t={}'.format(self.timestamp)
        self.pre_release_url = 'https://www.jisilu.cn/data/cbnew/pre_list/?___jsl=LST___t={}'.format(self.timestamp)
        self.east_money_bond = Bond()

    def download(self, url, data, retry=5):
        for i in range(retry):
            try:
                r = requests.post(url, headers=self.headers, data=data)
                if not r.text or r.status_code != 200:
                    continue
                else:
                    return r
            except Exception as e:
                logging.info(e)
                continue
        return None

    def current_data(self, adjust_no_use=True):
        post_data = {
            'btype': 'C',
            'listed': 'Y',
            'rp': '50',
            'is_search': 'N',
        }
        js = self.download(self.url, data=post_data)
        if not js:
            return None
        ret = js.json()
        bond_list = ret.get('rows', {})
        cell_list = []
        for item in bond_list:
            cell_list.append(pd.Series(item.get('cell')))
        df = pd.DataFrame(cell_list)

        # 类型转换 部分含有%；剔除暂时不需要数据
        if adjust_no_use:

            def convert_float(x):
                try:
                    ret_float = float(x)
                except Exception as ef:
                    logging.error('转换失败{}'.format(ef))
                    ret_float = None
                return ret_float

            def convert_percent(x):
                try:
                    ret = float(x) * 100
                except:
                    ret = None
                return ret

            def remove_percent(x):
                try:
                    ret = x.replace(r'%', '')
                    ret = float(ret)
                except Exception as e:
                    ret = None

                return ret

            def remove_yuan(x):
                try:
                    ret = x.replace(r'元', '')
                    ret = float(ret)
                except Exception as e:
                    ret = None

                return ret

            def get_bond_value(x):
                try:
                    ret = self.east_money_bond.get_bond()
                    ret = float(ret)
                except Exception as e:
                    ret = None

                return ret

            df['put_convert_price'] = df['put_convert_price'].map(convert_float)
            df['price'] = df['price'].map(convert_float)
            df['sprice'] = df['sprice'].map(convert_float)
            df['convert_price'] = df['convert_price'].map(convert_float)
            df['convert_value'] = df['convert_value'].map(convert_float)
            df['redeem_price'] = df['redeem_price'].map(convert_float)
            df['ration'] = df['ration'].map(convert_float)
            df['volume'] = df['volume'].map(convert_float)
            df['premium_rt'] = df['premium_rt'].map(remove_percent)
            df['ytm_rt'] = df['ytm_rt'].map(remove_percent)
            df['convert_amt_ratio'] = df['convert_amt_ratio'].map(remove_percent)
            df['ration_rt'] = df['ration_rt'].map(convert_float)
            df['increase_rt'] = df['increase_rt'].map(remove_percent)
            df['sincrease_rt'] = df['sincrease_rt'].map(remove_percent)

            rename_columns = {'pre_bond_id': '可转债代码',
                              'bond_nm': '可转债名称',
                              'price': '可转债价格',
                              'stock_nm': '正股名称',
                              'sprice': '正股现价',
                              'convert_price': '最新转股价',
                              'convert_value': '转股价值',
                              'premium_rt': '溢价率',
                              'ytm_rt': '到期税前收益率',
                              'increase_rt': '可转债涨幅',
                              'sincrease_rt': '正股涨幅',
                              'volume': '成交额万元',
                              'turnover_rt': '可转债换手率',
                              'put_convert_price': '回售触发价',
                              'put_price': '回售价格',
                              'force_redeem_price': '强赎触发价格',
                              'redeem_price': '赎回价格',
                              'rating_cd': '评级',
                              'pb': 'PB',
                              'year_left': '剩余时间',
                              'maturity_dt': '到期时间',
                              'next_put_dt': '回售起始日',
                              'convert_dt': '转股起始日',
                              'redeem_flag': '赎回标识',
                              'pb_flag': 'PB标识',
                              'guarantor': '担保',
                              'adjust_tip': '下修提示',
                              'margin_flg': '股票标识',
                              'adj_cnt': '下调次数',
                              # 'ration': '配债价格',
                              'convert_amt_ratio': '转债剩余占总市值比',
                              'curr_iss_amt': '剩余规模',
                              'orig_iss_amt': '发行规模',
                              # 'ration_rt': '股东配售率',
                              'stock_cd': '正股代码',
                              # 'apply_cd': '申购代码',
                              # 'ration_cd': '配债代码',
                              'dblow': '双低指数',
                              'btype': 'btype',
                              }

        df = df.rename(columns=rename_columns)
        df = df[list(rename_columns.values())]
        df['更新日期'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

        # # 纯债价值
        # bond_value_list = []
        # # 纯债价值溢价率
        # bond_value_or_list = []
        # for code in df['可转债代码']:
        #     item = self.east_money_bond.get_bond(code)
        #     if item:
        #         bond_value_list.append(round(item['PUREBONDVALUE'], 2))
        #         bond_value_or_list.append(round(item['PUREBONDOR'], 2))
        #     else:
        #         bond_value_list.append(0)
        #         bond_value_or_list.append(0)
        # df.insert(8, '纯债价值', bond_value_list)
        # df.insert(9, '纯债溢价率', bond_value_or_list)
        # df['纯债价值'] = df['纯债价值'].map(convert_float)
        # df['纯债溢价率'] = df['纯债溢价率'].map(convert_float)

        df = df.set_index('可转债代码', drop=True)

        df.plot.scatter(x='可转债价格', y='转股价值')
        plt.show()

        try:
            df.to_sql('tb_jsl_{}'.format(self.date), engine, if_exists='replace', dtype={'可转债代码': VARCHAR(10)})
        except Exception as e:
            logging.error(e)

    # 这个数据最好晚上10点执行
    def history_data(self):
        conn = get_mysql_conn('db_stock', local='local')
        cursor = conn.cursor()

        check_table = '''
            create table if not exists tb_bond_release (
            可转债代码 varchar(10),
            可转债名称 varchar(10),
            集思录建议 varchar(500),
            包销比例 float(6,3),
            中签率 float(6,3),
            上市日期 varchar(20),
            申购户数（万户） int,
            单账户中签（顶格） float(6,3),
            股东配售率 float(6,3),
            评级 varchar(8),
            现价比转股价 float(6,3),
            抓取时间 datetime
            );
            '''
        try:
            cursor.execute(check_table)
            conn.commit()
        except Exception as e:

            logging.error('创建数据库失败{}'.format(e))

        post_data = {'cb_type_Y': 'Y',
                     'progress': '',
                     'rp': 22,
                     }
        r = self.download(url=self.pre_release_url, data=post_data)
        # print(r.json())
        js_data = r.json()
        rows = js_data.get('rows')
        for items in rows:
            item = items.get('cell')
            single_draw = item.get('single_draw')
            if single_draw:
                jsl_advise_text = item.get('jsl_advise_text')  # 集思录建议
                underwriter_rt = self.convert_float(item.get('underwriter_rt'))  # 包销比例
                bond_nm = item.get('bond_nm')
                lucky_draw_rt = self.convert_float(item.get('lucky_draw_rt'))  # 中签率
                if lucky_draw_rt:
                    lucky_draw_rt = lucky_draw_rt * 100
                list_date = item.get('list_date')
                valid_apply = self.convert_float(item.get('valid_apply'))  # 申购户数（万户）
                single_draw = self.convert_float(item.get('single_draw'))  # 单账户中签（顶格）
                ration_rt = self.convert_float(item.get('ration_rt'))  # 股东配售率
                rating_cd = item.get('rating_cd')  # 评级
                bond_id = item.get('bond_id')  # 可转债代码
                pma_rt = self.convert_float(item.get('pma_rt'))  # 现价比转股价
                update_time = datetime.datetime.now()

                check_exist = '''
                    select * from tb_bond_release where 可转债代码=%s
                    '''
                try:
                    cursor.execute(check_exist, (bond_id))
                except Exception as e:
                    logging.error('查询重复数据错误 {}'.format(e))

                else:
                    ret = cursor.fetchall()
                    # 存在则更新
                    if ret:

                        check_update = '''
                                            select * from tb_bond_release where 可转债代码=%s and 包销比例 is null
                                            '''
                        try:
                            cursor.execute(check_update, (bond_id))
                        except Exception as e:
                            logging.error('查询重复数据错误 {}'.format(e))

                        else:
                            ret = cursor.fetchall()
                            if not ret:
                                continue
                            # 更新
                            else:

                                update_sql = '''
                                    update tb_bond_release set 包销比例=%s , 上市日期=%s ,抓取时间=%s where 可转债代码 = %s
                                    '''
                                try:
                                    update_v = (underwriter_rt, list_date, update_time, bond_id)
                                    cursor.execute(update_sql, update_v)
                                    conn.commit()
                                except Exception as e:
                                    logging.error(e)

                    # 插入
                    else:
                        insert_sql = '''
                                            insert into tb_bond_release (可转债代码 , 可转债名称 , 集思录建议 , 包销比例 , 中签率 ,上市日期 ,申购户数（万户）, 单账户中签（顶格）, 股东配售率 ,评级 ,  现价比转股价,抓取时间) 
                                            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                            '''
                        v = (bond_id, bond_nm, jsl_advise_text, underwriter_rt, lucky_draw_rt, list_date, valid_apply,
                             single_draw, ration_rt, rating_cd, pma_rt, update_time)
                        try:
                            cursor.execute(insert_sql, v)
                            conn.commit()
                        except Exception as e:
                            logging.error(e)
                            conn.rollback()

    def convert_float(self, x):
        if not x:
            return None

        if '%' in x:
            ration = 100
        else:
            ration = 1

        x = re.sub('%', '', x)
        try:
            ret = float(x) * ration
        except Exception as e:
            logging.error('转换失败{}'.format(e))
            ret = None

        return ret


#
def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Start')
    obj = Jisilu()
    obj.current_data()
    # obj.history_data()


if __name__ == '__main__':
    main()
