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
                except:
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

            rename_columns = {
                              'price': '可转债价格',
                              'convert_value': '转股价值',
                              }

        df = df.rename(columns=rename_columns)
        df = df[list(rename_columns.values())]

        print(df.head())
        # 分割训练数据和测试数据
        from sklearn.model_selection import train_test_split
        value_train, value_test, premium_train, premium_test = train_test_split(df['可转债价格'], df['转股价值'], train_size=.8)

        # sklearn要求输入的特征必须是二维数组的类型
        # 将训练数据特征转换成二维数组XX行 * 1列
        value_train_2 = value_train.values.reshape(-1, 1)
        # 训练
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(value_train_2, premium_train)

        # 绘图
        import matplotlib.pyplot as plt
        # 训练数据散点图
        plt.scatter(df['可转债价格'], df['转股价值'], c='blue', cmap='训练数据')
        plt.scatter(value_train, premium_train, c='red', cmap='训练数据')
        # plt.plot(value_train, model.predict(value_train_2), c='black')
        # plt.scatter(value_test, premium_test, c='red', cmap='测试数据')
        # 图像标签
        plt.legend(loc=2)
        plt.xlabel("转股价值")
        plt.ylabel("转股价值")
        # 显示图像
        plt.show()

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
    logging.info('Start')
    obj = Jisilu()
    obj.current_data()
    # obj.history_data()


if __name__ == '__main__':
    main()
