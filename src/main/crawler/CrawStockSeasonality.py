import multiprocessing as mp
import sys
import time
from random import randrange

from bs4 import BeautifulSoup
from selenium import webdriver

from src.lib.my_lib.module.LoggerModule import Logger
from src.lib.web_driver.Path import WebDriverPath
from src.main.api.ApiAiStock import ApiAiStock
from src.main.crawler.CrawStockSeasonalityPool import a_pool


def craw_stock_eps_roe_roa(stockNos):
	css = CrawStockSeasonality.instance()
	pool = mp.Pool(processes=css.process_num)
	stockNos.append('quit_browser')
	stockNos = [str(stockNo) for stockNo in stockNos]
	result = pool.map(a_pool, stockNos)
	pool.close()
	# return [i for i in result if i]  # remove none item
	return [item for sublist in result for item in sublist]  # flat list out of list of lists


class CrawStockSeasonality:
	_instance = None

	def __new__(cls, *args, **kw):
		if not cls._instance:
			cls._instance = super(CrawStockSeasonality, cls).__new__(cls, *args, **kw)
			cls._instance.__initialized = False
		return cls._instance

	def __init__(self):
		if self.__initialized:
			return
		self.req_url = 'https://goodinfo.tw/StockInfo/StockBzPerformance.asp?STOCK_ID={0}&YEAR_PERIOD=1&RPT_CAT=QUAR'
		self.process_num = 1  # todo num by cpu core , 開四個 process 被 goodinfo 盯上 鎖 ip
		self.browser = None
		self.__initialized = True

	@staticmethod
	def instance():
		css = CrawStockSeasonality()
		Logger.info(css)
		return css

	def init_browser_if_empty(self):
		if self.browser is None:
			path = WebDriverPath.get()
			options = webdriver.ChromeOptions()
			'''
			selenium.common.exceptions.WebDriverException: Message: unknown Error: cannot find Chrome binary
			https://programmersought.com/article/47711748581/
			'''
			options.binary_location = 'C:/Program Files/Google/Chrome/Application/chrome.exe'  # for my company's x64 chrome
			# https://stackoverflow.com/questions/16180428/can-selenium-webdriver-open-browser-windows-silently-in-background
			options.add_argument("--headless")
			self.browser = webdriver.Chrome(path, options=options)

	def start_request(self, stockNo):
		url = self.req_url.format(stockNo)
		# r = requests.get(url)
		# Logger.info(r.status_code == requests.codes.ok)
		self.browser.get(url)
		time.sleep(1)  # 須加上時間 延後1s爬, 不然沒間隔秒數 ,會爬很快 被鎖ip
		return self.parse(stockNo, self.browser.page_source)

	def parse(self, stockNo, pageSource):
		print(stockNo)
		# 找出最近一筆有資料的 : 季度/單季ROE/單季ROA/EPS/eps年增
		soup = BeautifulSoup(pageSource, 'html.parser')
		# table = soup.find_all('table', {'class': 'solid_1_padding_4_2_tbl'})[1]
		# trs = soup.select('.solid_1_padding_4_0_tbl tbody tr')
		trs = soup.select('#divDetail table tbody tr')  # todo 222222 有變了 要重爬
		records = []
		for tr in trs:
			tds = tr.select('td')
			if len(tds) >= 22:
				yearSeason = tds[0].text
				roe = tds[16].text
				roa = tds[18].text
				eps = tds[20].text
				bps = tds[22].text
				# eps_minus_last_year = tds[21].text
				if eps != '-' and roe != '-' and roa != '-' and bps != '-':
					result = {
						'stockNo': stockNo,
						'year': int(yearSeason.split('Q')[0]),
						'season': int(yearSeason.split('Q')[1]),
						'roe': float(roe),
						'roa': float(roa),
						'eps': float(eps),
						'bps': float(bps),
						# 'eps_minus_last_year': eps_minus_last_year
					}
					records.append(result)
		# break
		# Logger.info(records)
		return records


def main():
	'''
	https://json-csv.com/
	'''
	# CrawStockSeasonality.instance()
	# result =  craw_stock_eps_roe_roa(['2317'])
	# result =  craw_stock_eps_roe_roa(['2317', '2330'])
	# result =  craw_stock_eps_roe_roa(['2330', '00642U', '2330'])  # how about has no data ,ex: 00642U 石油
	result = craw_stock_eps_roe_roa([
		# 上市:
		1216,2882,2912,2207,1402,2409,2881,3481,2905,2618,1605,2610,2377,8112,2891,2867,3034,1101,1210,2885,2379,2105,5871,9921,1102,2886,2201,3033,2883,2023,2404,1313,2206,1504,2006,5880,2884,2880,3017,2890,5876,2371,2633,1802,2542,9941,2204,9907,4919
		# 上櫃 : 暫時沒用
	])
	print(result)
	if len(result) > 0:
		batch_uid = randrange(1000, 9999)
		api = ApiAiStock()
		result = api.batchSaveOrUpdateStockReportSeasonality(batch_uid, result)
		Logger.info(result)


if __name__ == "__main__":
	main()
	exit()
	sys.exit(1)
