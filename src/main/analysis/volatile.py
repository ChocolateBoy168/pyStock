import datetime

import numpy as np
import pandas

from src.main.crawler.yahoo import StockHistory


def volatileAnalysis(stockNo, stockName, years=3):
    history_crawler = StockHistory.History()
    end_time = datetime.datetime.now()
    # start_time = end_time - datetime.timedelta(days=years * 365)
    start_time = end_time - datetime.timedelta(days=years * 365)
    history = history_crawler.getHistory(stockNo, start_time, end_time)
    if history is None:
        history = history_crawler.getHistory(stockNo, start_time, end_time, '.TWO')
        if history is None:
            return None
    # volatile = history['high'] - history['low']
    statistic = history['close'].describe()
    if history['close'][0] > statistic['25%'] or statistic['count'] < years * 100:
        return None

    result = {}
    result['stockNo'] = stockNo
    result['stockName'] = stockName
    result['currentPrice'] = round(history['close'][0], 2)

    high = history['high'].tolist()
    high.reverse()
    low = history['low'].tolist()
    low.reverse()
    # Log.Info("---------------------")
    print("{}({}) {}".format(stockName, stockNo, history['close'][0]))
    print(statistic)
    result['count'] = statistic['count']
    result['mean'] = round(statistic['mean'], 2)
    result['std'] = round(statistic['std'], 2)
    result['min'] = round(statistic['min'], 2)
    result['25%'] = round(statistic['25%'], 2)
    result['50%'] = round(statistic['50%'], 2)
    result['75%'] = round(statistic['75%'], 2)
    result['max'] = round(statistic['max'], 2)
    for w in range(1, 6, 1):
        volatile = []
        for i in range(len(high)):
            s = i
            e = i + w
            if e > len(high):
                break
            h = np.max(high[s:e])
            l = np.min(low[s:e])
            volatile.append(h - l)

        avg = round(np.average(volatile), 2)
        std = round(np.std(volatile), 2)
        result['day' + str(w)] = avg
        print("days:{}, volatile avg:{}, std:{}".format(w, avg, std))
    print("---------------------")

    return result


if __name__ == "__main__":
    # volatile_analysis('2353', '2353', 1)
    pick_list = {'stockNo': [],
                 'stockName': [],
                 'currentPrice': [],
                 'count': [],
                 'mean': [],
                 'std': [],
                 'min': [],
                 '25%': [],
                 '50%': [],
                 '75%': [],
                 'max': [],
                 'day1': [],
                 'day2': [],
                 'day3': [],
                 'day4': [],
                 'day5': []}

    # way = 'from_stockListCsv'
    # way = 'from_bestRevenue'
    # if way == 'from_stockListCsv':  # 來自 StockList.csv
    #     df = pandas.read_csv('StockList.csv')
    #     for stock, stockName in zip(df['代號'], df['名稱']):
    #         stock = stock[2:-1]
    #         result = volatileAnalysis(stock, stockName, 5)
    #         if result is not None:
    #             for key in result.keys():
    #                 pick_list[key].append(result[key])
    # elif way == 'from_bestRevenue':  # 來自 好營收
    #     api = ApiAiStock()
    #     result = api.listRevenueRate()
    #     print(json.dumps(result.__dict__))
    #
    #     df = pd.DataFrame([])
    #     data = result.data
    #     if MyLib.is_not_empty_array(data):
    #         # df = pd.DataFrame(data).loc[:, 'company_code', 'company_name']
    #         df = pd.DataFrame(data)
    #         for stockNo, stockName in zip(df['company_code'], df['company_name']):
    #             result = volatileAnalysis(stockNo, stockName, 5)
    #             if result is not None:
    #                 for key in result.keys():
    #                     pick_list[key].append(result[key])

    stocks = [1210, 1216, 1231, 1232, 1233, 1307, 1323, 1451, 1530, 1532, 1535, 1540, 1717, 1720, 1730
        , 1776, 1787, 1808, 1813, 2002, 2015, 2034, 2063, 2103, 2106, 2108, 2351, 2383, 2387, 2420
        , 2421, 2423, 2433, 2441, 2464, 2488, 2542, 2596, 2605, 2606, 2636, 2637, 2832, 2850, 2891
        , 2904, 2908, 2915, 3003, 3015, 3028, 3033, 3036, 3040, 3055, 3078, 3090, 3118, 3147, 3167
        , 3209, 3217, 3231, 3264, 3265, 3323, 3332, 3380, 3390, 3444, 3484, 3528, 3537, 3567, 3702
        , 4106, 4205, 4305, 4401, 4417, 4527, 4528, 4721, 5007, 5015, 5016, 5209, 5347, 5356, 5403
        , 5438, 5439, 5489, 5493, 5508, 5511, 5519, 5525, 5533, 5609, 6023, 6024, 6123, 6128, 6136
        , 6151, 6153, 6154, 6155, 6185, 6189, 6194, 6196, 6201, 6204, 6205, 6207, 6210, 6213, 6218
        , 6227, 6229, 6245, 6257, 6270, 6274, 6282, 6292, 6609, 8021, 8032, 8043, 8048, 8074, 8099
        , 8210, 8249, 8271, 8383, 8403, 8424, 8917, 8926, 9925, 9926, 9927, 9930, 9931, 9933, 9937]

    for stock in stocks:
        result = volatileAnalysis(str(stock), str(stock), 5)
        if result is not None:
            for key in result.keys():
                pick_list[key].append(result[key])
    pick_df = pandas.DataFrame(pick_list)
    date = datetime.datetime.now()
    filename = "pick_{}.csv".format(date.strftime("%Y%m%d"))
    pick_df.to_csv(filename, encoding='utf_8_sig')