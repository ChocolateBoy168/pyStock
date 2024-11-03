import datetime

import numpy as np

from src.main.crawler.yahoo import StockHistory

def get_history(stockNo, years=1):
    history_crawler = StockHistory.History()
    end_time = datetime.datetime.now()
    # start_time = end_time - datetime.timedelta(days=years * 365)
    start_time = end_time - datetime.timedelta(days=years * 365)
    history = history_crawler.getHistory(stockNo, start_time, end_time)
    # print(history.head())

def volatileAnalysis(stockNo, stockName, years=1, enter_diff=0.5, diff=0.5, first_p=30, min_p=20):
    stockHistory = StockHistory.Class()
    end_time = datetime.datetime.now()
    # start_time = end_time - datetime.timedelta(days=years * 365)
    start_time = end_time - datetime.timedelta(days=years * 365)
    history = stockHistory.crawHistory(stockNo, start_time, end_time)
    print(history.head())
    if history is None:
        history = stockHistory.crawHistory(stockNo, start_time, end_time, '.TWO')
        if history is None:
            return None
    return history



def volatileAnalysis(history, enter_diff=0.2, diff=0.5, first_p=11, min_p=8):
    # history_crawler = StockHistory.History()
    # end_time = datetime.datetime.now()
    # # start_time = end_time - datetime.timedelta(days=years * 365)
    # start_time = end_time - datetime.timedelta(days=years * 365)
    # history = history_crawler.getHistory(stockNo, start_time, end_time)
    # # print(history.head())
    # if history is None:
    #     history = history_crawler.getHistory(stockNo, start_time, end_time, '.TWO')
    #     if history is None:
    #         return None
    # volatile = history['high'] - history['low']
    statistic = history['close'].describe()
    # if history['close'][0] > statistic['25%'] or statistic['count'] < years * 100:
    #     return None

    # result = {}
    # result['stockNo'] = stockNo
    # result['stockName'] = stockName
    # result['currentPrice'] = round(history['close'][0], 2)

    high = history['high'].tolist()
    high.reverse()
    low = history['low'].tolist()
    low.reverse()
    close = history['close'].tolist()
    close.reverse()
    open = history['open'].tolist()
    open.reverse()
    date = history['date'].tolist()
    date.reverse()
    # Log.Info("---------------------")
    # print(statistic)
    h = []
    c = 0
    max_cost = 0
    for i in range(len(high)):
        if close[i] > open[i]:
            show = len(h) > 0
            if show:
                date_str = datetime.datetime.fromtimestamp(date[i]).strftime("%Y%m%d")
                # print("{} : up h({})l({})c({})o({}), h = {}".format(date_str, high[i], low[i], close[i], open[i], h))

            # 根據最低價，看可以收多少
            while low[i] <= first_p:
                if len(h) == 0:
                    h.append(first_p)
                elif h[-1] - enter_diff >= low[i] and h[-1] > min_p:
                    h.append(h[-1] - enter_diff)
                else:
                    break
            if show:
                if max_cost < sum(h):
                    max_cost = sum(h)
                # print("buy -->cost:{}w, h{}, c = {}".format(sum(h)/10, h, c))

            # 根據最高價，看可以賣掉多少
            while len(h) > 0:
                if h[-1] <= high[i] - diff:
                    h.pop()
                    c += 1
                else:
                    break
            if show:
                if max_cost < sum(h):
                    max_cost = sum(h)
                # print("sell -->cost:{}w, h{}, c = {}".format(sum(h)/10, h, c))

            # 根據收盤價，看可以收多少
            while close[i] <= first_p:
                if len(h) == 0:
                    h.append(first_p)
                elif h[-1] - enter_diff >= close[i] and h[-1] > min_p:
                    h.append(h[-1] - enter_diff)
                else:
                    break
            if show:
                if max_cost < sum(h):
                    max_cost = sum(h)
                # print("buy -->cost:{}w, h{}, c = {}".format(sum(h) / 10, h, c))


        else:
            show = low[i] <= first_p
            if show:
                date_str = datetime.datetime.fromtimestamp(date[i]).strftime("%Y%m%d")
                # print("{}: down h({})l({})c({})o({}), h = {}".format(date_str, high[i], low[i], close[i], open[i], h))

            # 根據最高價，看可以賣掉多少
            while len(h) > 0:
                if h[-1] <= high[i] - diff:
                    h.pop()
                    c += 1
                else:
                    break
            if show:
                if max_cost < sum(h):
                    max_cost = sum(h)
                # print("sell -->cost:{}w, h{}, c = {}".format(sum(h) / 10, h, c))

            # 根據最低價，看可以收多少
            while low[i] <= first_p:
                if len(h) == 0:
                    h.append(first_p)
                elif h[-1] - enter_diff >= low[i] and h[-1] > min_p:
                    h.append(h[-1] - enter_diff)
                else:
                    break
            if show:
                if max_cost < sum(h):
                    max_cost = sum(h)
                # print("buy --> cost={}w, h{}, c = {}".format(sum(h) / 10, h, c))

            # 根據收盤價，看可以賣多少
            while len(h) > 0:
                if h[-1] <= close[i] - diff:
                    h.pop()
                    c += 1
                else:
                    break
            if show:
                if max_cost < sum(h):
                    max_cost = sum(h)
                # print("sell -->cost:{}w, h{}, c = {}".format(sum(h) / 10, h, c))

    print("max_cost = {:1f}w, count:{}".format(max_cost/10, c))

    return max_cost, c


if __name__ == '__main__':
    # volatileAnalysis('2834', '2834')

    enter_diff = [0.1, 0.2, 0.5, 1, 1.5, 2]
    earn_diff = [0.3, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5]
    max_profit = 0
    best = ""
    history = get_history('9907', 1)
    high_price = 12
    low_price = 8

    for enter in enter_diff:
        for earn in earn_diff:
            max_cost, c = volatileAnalysis(history, diff=earn, enter_diff=enter, first_p=high_price, min_p=low_price)
            profit = (c * (earn * 1000 - 40 - (high_price+earn) * 3)) / (max_cost * 1000)
            # if max_profit < profit:
            #     max_profit = profit
            best = "profit={}, enter={}, earn={}, count={}, max_cost={}w".format(profit, enter, earn, c, max_cost/10)
            print(best)

    # print(best)