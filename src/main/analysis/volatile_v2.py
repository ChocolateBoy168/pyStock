import datetime

import numpy as np

from src.main.crawler.yahoo import StockHistory


def volatileAnalysis_v2(stockNo,  months=12, sdPercent='25%'):
	stockHistory = StockHistory.Class()
	end_time = datetime.datetime.now()
	start_time = end_time - datetime.timedelta(
		days=months * 30)  # todo  https://stackoverflow.com/questions/4130922/how-to-increment-datetime-by-custom-months-in-python-without-using-library
	history = stockHistory.crawHistory(stockNo, start_time, end_time)
	if history is None:
		history = stockHistory.crawHistory(stockNo, start_time, end_time, '.TWO')
		if history is None:
			return None
	# volatile = history['high'] - history['low']
	statistic = history['close'].describe()
	if history['close'][0] > statistic[sdPercent] or statistic['count'] < months / 12 * 100:
		return None

	result = {}
	result['stockNo'] = stockNo
	result['currentPrice'] = round(history['close'][0], 2)

	high = history['high'].tolist()
	high.reverse()
	low = history['low'].tolist()
	low.reverse()
	# Log.Info("---------------------")
	print("股號{} 收盤價{}".format(stockNo, history['close'][0]))
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
