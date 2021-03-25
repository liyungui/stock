# -*-coding=utf-8-*-
__author__ = 'conglinfeng'

import random

# 10张牌。代表风报比。1表示投入1块钱赢1块钱，-1表示投入1块钱输1块钱
profit = [1, 2, 2, 4, -1, -1, -1, -1, -1, -1]
# 重复次数
repeat = 100
# 每次的收益
process = []
# 负收益的次数
loss = 0
for i in range(repeat):
    num = random.choice(profit)
    if num < 0:
        loss = loss + 1
    process.append(num)

# 输出每次的收益
print(process)
# 输出总收益
print(sum(process))
# 输出负收益比率
print(loss / repeat)
