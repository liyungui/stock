# -*-coding=utf-8-*-
__author__ = 'conglinfeng'

from decimal import Decimal

import matplotlib.pyplot as plt
import numpy as np


def draw_dot(dot_x, dot_y):
    dot_x_display = Decimal(dot_x).quantize(Decimal('0.00'))
    dot_y_display = Decimal(dot_y).quantize(Decimal('0.00'))
    # 绘制散点(dot_x, dot_y)
    plt.scatter([dot_x], [dot_y], s=15, color="red")  # s 为点的 size
    # 对(dot_x, dot_y)做标注
    plt.annotate(f'{dot_y_display}',
                 xy=(dot_x, dot_y),  # 在(dot_x, y)上做标注
                 fontsize=8,  # 设置字体大小
                 xycoords='data')  # xycoords='data' 是说基于数据的值来选位置


# 触发加仓的价位。0.8表示跌20%加仓
p = 0.8
# 加仓的比例。2表示每次翻倍加仓
r = 2
# 加仓次数上限
repeat = 20
# 每次加仓的价位
price = []
# 每次加仓的数量
num = []
# 加仓后的总成本
total_cost = 0
# 每次加仓后的损失比例
lost = []

for i in range(repeat):
    # 加仓的价位
    current_price = pow(p, i)
    price.append(current_price)
    # 加仓的数量
    current_num = pow(r, i)
    num.append(current_num)
    # 总成本
    total_cost = total_cost + current_num * current_price
    # 平均成本
    avg_cost = total_cost / sum(num)
    # 损失比例
    lost.append((avg_cost - current_price) / current_price)

# 输出每次加仓的价位
print(price)
# 每次加仓后的损失比例
print(lost)

x = np.arange(1, repeat + 1)
y_price = np.asarray(price)
y_lost = np.asarray(lost)

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

plt.figure()  # 定义一个图像窗口
plt.plot(x, y_price, color="blue", label="价格比率%")  # 绘制曲线 y1
plt.plot(x, y_lost, color="green", label="损失比率%")  # 绘制曲线 y2
plt.legend(loc="upper right")  # 添加图例
# 设置横轴精准刻度
plt.xticks(x)
# 设置纵轴精准刻度
# plt.yticks(np.arange(1.1, step=0.1))
# 设置横轴标签
plt.xlabel("加仓次数")
# 设置纵轴标签
plt.ylabel("比率%")

# 绘制点
price_dot = np.vstack((x, y_price)).T
lost_dot = np.vstack((x, y_lost)).T
for d_x in price_dot:
    draw_dot(d_x[0], d_x[1])
for d_x in lost_dot:
    draw_dot(d_x[0], d_x[1])
plt.show()
