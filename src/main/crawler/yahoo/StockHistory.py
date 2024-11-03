import datetime
import json

import pandas as pd
import requests
from bs4 import BeautifulSoup


class Class():
	def __init__(self):
		self.template_url = "https://finance.yahoo.com/quote/{0}/history?period1={1}&period2={2}&interval=1d&filter=history&frequency=1d"

	"""
		return: pandas dataframe format:  
			date: DateTime,
			open: float, 
			high: float, 
			low: float, 
			close: float, 
			volume: float, 
			adjclose: float, 
			stockNo: string  
	"""

	def crawHistory(self, stockNo, startTime, endTime, ext='.TW'):
		url = self.template_url.format(stockNo + ext, int(startTime.timestamp()), int(endTime.timestamp()))
		# print(url)
		print(url)
		try:
			result = requests.get(url)
			# print(result)
			if result.status_code == 200:
				# print(result.text)
				context = None
				soup = BeautifulSoup(result.text, 'html.parser')
				# print(soup.prettify())
				tags = soup.find_all('script')
				for i in range(len(tags) - 1, 0, -1):
					tag = tags[i]
					if tag.string is not None and tag.string.find('root.App.main') >= 0:
						s = tag.string.find('root.App.main = ') + len('root.App.main = ')
						e = tag.string.find('}}}};') + 4
						context = tag.string[s:e]
						break

				if context is not None:
					data = json.loads(context)
					prices = data['context']['dispatcher']['stores']['HistoricalPriceStore']['prices']
					dfHistory = pd.DataFrame(
						columns=['date', 'open', 'high', 'low', 'close', 'volume', 'adjclose', 'stockNo'])
					for price in prices:
						if 'open' in price.keys() and price['open'] is not None:
							price['stockNo'] = stockNo
							# 時間轉成以天為單位，避免取到盤中的價格
							date = datetime.datetime.fromtimestamp(price['date'])
							# 注意時間有+8
							date = datetime.datetime(date.year, date.month, date.day, 8).timestamp()
							price['date'] = date
							dfHistory = dfHistory.append(price, ignore_index=True)
					# print(price)

					# 統一數值成float
					dfHistory['open'] = dfHistory['open'].astype(float)
					dfHistory['high'] = dfHistory['high'].astype(float)
					dfHistory['low'] = dfHistory['low'].astype(float)
					dfHistory['close'] = dfHistory['close'].astype(float)
					dfHistory['volume'] = dfHistory['volume'].astype(float)
					dfHistory['adjclose'] = dfHistory['adjclose'].astype(float)
					# print(dfHistory.head())
					# print('download success')
					return dfHistory
		except Exception as e:
			# Log.Error("getHistory " + str(e))
			print("getHistory " + str(e))
		return None
