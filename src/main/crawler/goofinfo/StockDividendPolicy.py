import datetime
import os
import platform
import sys
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver


class StockDividend():
	def __init__(self):
		self.template_url = "https://goodinfo.tw/StockInfo/StockDividendPolicy.asp?STOCK_ID={0}"

	def getDividend(self, stockNo):
		url = self.template_url.format(stockNo)
		print(url)
		try:
			root_dir = os.path.dirname(sys.modules['__main__'].__file__)
			webDriver = None
			if platform.system() == 'Windows':
				webDriver = os.path.join(root_dir, 'driverPath/windows/chromedriver.exe')
			elif platform.system() == 'Darwin':
				webDriver = os.path.join(root_dir, 'driverPath/mac/chromedriver')

			web = webdriver.Chrome(webDriver)
			web.get(url)
			time.sleep(1)
			# print(web.page_source)

			soup = BeautifulSoup(web.page_source, 'html.parser')
			table = soup.find_all('table', {'class': 'solid_1_padding_4_0_tbl'})[1]
			tbodys = table.find_all('tbody')
			dfDividend = pd.DataFrame(
				columns=['date', 'year', 'cash_dividend', 'stock_dividend', 'dividend', 'stockNo'])

			for tbody in tbodys:
				trs = tbody.find_all('tr')
				for tr in trs:
					tds = tr.find_all('td')
					values = [ele.text.strip() for ele in tds]
					# print(values)
					if values[0] == '平均' or values[0] == '累計' or values[3] == '-':
						continue

					data = {}
					data['year'] = int(values[0])
					data['cash_dividend'] = float(values[3])
					data['stock_dividend'] = float(values[6])
					data['dividend'] = float(values[7])
					data['stockNo'] = stockNo
					data['date'] = datetime.datetime(int(values[0]), 1, 1).timestamp()
					dfDividend = dfDividend.append(data, ignore_index=True)

			web.close()
			return dfDividend
		except Exception as e:
			print("getDividend " + str(e))
		return None


if __name__ == "__main__":
	dividend = StockDividend()
	dfDividend = dividend.getDividend(2303)
	print(dfDividend)
