# -*- encoding=utf8 -*-
__author__ = 'conglinfeng'

import math
from scipy import stats
import numpy as np

'''
期权定价模型
s:标的价格
k:行权价格
r:无风险利率
t:剩余期限
cp:1为call ，-1为put
sigma:股价的波动率
'''

def d(s, k, r, T, sigma):
    d1 = (np.log(s / k) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2


def delta(s, k, r, T, sigma, n):
    '''
    认购期权的n为1
    认沽期权的n为-1
    '''
    d1 = d(s, k, r, T, sigma)[0]
    delta = n * stats.norm.cdf(n * d1)
    return delta


def gamma(s, k, r, T, sigma):
    d1 = d(s, k, r, T, sigma)[0]
    gamma = stats.norm.pdf(d1) / (s * sigma * np.sqrt(T))
    return gamma


def vega(s, k, r, T, sigma):
    d1 = d(s, k, r, T, sigma)[0]
    vega = (s * stats.norm.pdf(d1) * np.sqrt(T)) / 100
    return vega


def theta(s, k, r, T, sigma, n):
    '''
    认购期权的n为1
    认沽期权的n为-1
    '''
    d1 = d(s, k, r, T, sigma)[0]
    d2 = d(s, k, r, T, sigma)[1]

    theta = (-1 * (s * stats.norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - n * r * k * np.exp(-r * T) * stats.norm.cdf(
        n * d2)) / 365
    return theta


# 根据BS公式计算欧式期权价格
def caculateBSM(s, k, r, t, v, cp):
    """
        s:标的价格
        k:行权价格
        r:无风险利率
        t:剩余期限
        v:波动率
        cp:1为call ，-1为put
    """
    d1 = (math.log(s / k) + (r + v ** 2 / 2) * t) / v * t ** 0.5
    d2 = d1 - v * t ** 0.5
    price = cp * s * stats.norm.cdf(cp * d1) - cp * k * math.exp(-r * t) * stats.norm.cdf(cp * d2)
    return round(price, 4)


# 根据牛顿法计算期权隐含波动率
def caculateIV_Newton(price, s, k, r, t, cp):
    """
        price:期权市场价格
        s:标的价格
        k:行权价格
        r:无风险利率
        t:剩余期限
        cp:1为call ，-1为put
    """
    v = 0.3
    for i in range(200):
        Theory = caculateBSM(s, k, r, t, v, cp)
        d1 = (math.log(s / k) + (r + v ** 2 / 2) * t) / v * t ** 0.5
        vega = s * stats.norm.pdf(d1) * t ** 0.5
        dx = (price - Theory) / vega
        v += dx
        if abs(dx) <= 1e-5:
            break
    return round(v, 4)


def caculateIV_Dichotomy(price, s, k, r, t, cp):
    """
        price:期权市场价格
        s:标的价格
        k:行权价格
        r:无风险利率
        t:剩余期限
        cp:1为call ，-1为put
    """
    Theory, up, down = 0, 1, 0
    v = (down + up) / 2
    for i in range(5000):
        Theory = caculateBSM(s, k, r, t, v, cp)
        if price - Theory > 0:  # f(x)>0
            down = v
            v = (v + up) / 2
        else:
            up = v
            v = (v + down) / 2
        if abs(price - Theory) < 1e-5:
            # print('二分法收敛')
            return round(v, 4)
    return '二分法没有收敛，请用牛顿法'
    # return round(v,4)


if __name__ == "__main__":
    p1 = caculateIV_Newton(2, 10, 10, 0.03, 30 / 365, 1)
    p2 = caculateIV_Dichotomy(2, 10, 10, 0.03, 30 / 365, 1)
    p = caculateBSM(10, 10, 0.03, 30 / 365, 1.811, 1)
    print(p1, p2, p)
    pass
