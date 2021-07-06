# -*- coding: utf-8 -*-
# @Time : 2020/09/08 11:11
# @File : eastmoney_bond.py

import requests
import logging


# api请求获取可转债数据
# 可转债详情页 http://data.eastmoney.com/kzz/detail/113530.html
class Bond():
    def __init__(self):
        self.headers = {
            'User-Agent': 'User-Agent:Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'}

    def get_bond(self, code, page=1):
        # p=1&ps=8000;p是页码；ps是分页数量；上限500，这里传8000是无效的
        self.url = 'http://datacenter.eastmoney.com/api/data/get?type=RPTA_WEB_KZZ_LS&sty=ALL&source=WEB&p={}&ps=1&st=date&sr=1&filter=(zcode=%22{}%22)'.format(
            page, code[2:])
        r = self.download()
        if not r:
            return None
        ret = r.json().get('result')

        if ret:
            pages = ret.get('pages', 1)
            if pages > page:
                # 需要翻页
                return self.get_bond(code, pages)
            else:
                data = ret.get('data', {})
                if len(data) > 0:
                    return data[-1]
                else:
                    return None
        else:
            return None

    def download(self, retry=5):
        for i in range(retry):
            try:
                r = requests.get(self.url, headers=self.headers)
                if not r.text or r.status_code != 200:
                    continue
                else:
                    return r
            except Exception as e:
                logging.info(e)
                continue
        return None


if __name__ == '__main__':
    bond = Bond()
    r = bond.get_bond('sz113530')
    if r is not None:
        print(r['DATE'])
    else:
        print('错误')
