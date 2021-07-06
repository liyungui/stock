# -*-coding=utf-8-*-
__author__ = 'conglinfeng'

from futu import *
import time
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret1, data1 = quote_ctx.get_option_expiration_date(code='HK.00700')
if ret1 == RET_OK:
    expiration_date_list = data1['strike_time'].values.tolist()
    for date in expiration_date_list:
        ret2, data2 = quote_ctx.get_option_chain(code='HK.00700', start=date, end=date)
        if ret2 == RET_OK:
            print(data2)
            print(data2['code'][0])  # 取第一条的股票代码
            print(data2['code'].values.tolist())  # 转为 list
        else:
            print('error:', data2)
        time.sleep(3)
else:
    print('error:', data1)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽

