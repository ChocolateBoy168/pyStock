import time
import pythoncom  # 使用pythoncom 需要 pip install pyiwin32
import schedule as schedule

from src.lib.my_lib import MyLib
from src.lib.my_lib.module.LoggerModule import Logger
from src.main.AppConst import PeriodEnum
from src.main.assets.AssetsHelper import AssetsHelper
from src.main.crawler import CrawStockDaily
from src.main.stock_market.Broker import Broker
from src.main.stock_market.trader.capital import CapitalRealTrader
from src.main.stock_market.trader.capital.CapitalCrawlTrader import CapitalCrawlTrader
from src.main.util import ConfigUtil
import src.test.MergeTicks as MergeTicks


class MySchedule:
	def __init__(self, api_account, api_pwd):
		self.running = False
		self.api_account = api_account
		self.api_pwd = api_pwd
		self.broker = None

	def start(self):
		Logger.info(f'\n========start==========')
		self.broker = Broker(None, None, None, None, CapitalCrawlTrader, self.api_account, self.api_pwd)
		self.broker.run()
		Logger.info(f'\n========start over==========')

	def stop(self):
		Logger.info(f'\n========stop==========')
		if self.broker is not None:
			self.broker.release_memory()
		Logger.info(f'\n========stop over==========')

	def action_before_morning_period(self):
		Logger.info(f'\n======== action_before_morning_period ==========')
		Logger.info(f'\n todo need try_change_temp_night_best5_file_name')

	def after_morning_run_mergeTicks(self):
		Logger.info(f'\n======== after_morning_run_mergeTicks ==========')
		# merge ticks
		MergeTicks.run(AssetsHelper.find_last_final_date())

	def after_morning_run_crawStockDaily(self):
		Logger.info(f'\n======== after_morning_run_crawStockDaily ==========')
		# update stock daily
		CrawStockDaily.run()

	def active(self):
		'''
		# 每天早盤前置作業
		before_morning_time = "08:00"
		schedule.every().monday.at(before_morning_time).do(self.action_before_morning_period)
		schedule.every().tuesday.at(before_morning_time).do(self.action_before_morning_period)
		schedule.every().wednesday.at(before_morning_time).do(self.action_before_morning_period)
		schedule.every().thursday.at(before_morning_time).do(self.action_before_morning_period)
		schedule.every().friday.at(before_morning_time).do(self.action_before_morning_period)
		'''

		# 早盤 集合競價 開始時間 8:30~8:45
		morning_start_time = "08:30"
		schedule.every().monday.at(morning_start_time).do(self.start)
		schedule.every().tuesday.at(morning_start_time).do(self.start)
		schedule.every().wednesday.at(morning_start_time).do(self.start)
		schedule.every().thursday.at(morning_start_time).do(self.start)
		schedule.every().friday.at(morning_start_time).do(self.start)

		#
		morning_end_time = "13:46"
		schedule.every().monday.at(morning_end_time).do(self.stop)
		schedule.every().tuesday.at(morning_end_time).do(self.stop)
		schedule.every().wednesday.at(morning_end_time).do(self.stop)
		schedule.every().thursday.at(morning_end_time).do(self.stop)
		schedule.every().friday.at(morning_end_time).do(self.stop)

		# 每天早盤後 merge tick 排程
		after_morning_time = "14:00"
		schedule.every().monday.at(after_morning_time).do(self.after_morning_run_mergeTicks)
		schedule.every().tuesday.at(after_morning_time).do(self.after_morning_run_mergeTicks)
		schedule.every().wednesday.at(after_morning_time).do(self.after_morning_run_mergeTicks)
		schedule.every().thursday.at(after_morning_time).do(self.after_morning_run_mergeTicks)
		schedule.every().friday.at(after_morning_time).do(self.after_morning_run_mergeTicks)

		# 每天早盤後
		''' 
		after_morning_time = "14:30"
		schedule.every().monday.at(after_morning_time).do(self.after_morning_run_crawStockDaily)
		schedule.every().tuesday.at(after_morning_time).do(self.after_morning_run_crawStockDaily)
		schedule.every().wednesday.at(after_morning_time).do(self.after_morning_run_crawStockDaily)
		schedule.every().thursday.at(after_morning_time).do(self.after_morning_run_crawStockDaily)
		schedule.every().friday.at(after_morning_time).do(self.after_morning_run_crawStockDaily)
		'''

		# 夜盤 暫時不抓資料
		'''
		# 夜盤 集合競價 開始時間 14:50~15:00
		night_start_time = "14:50"
		schedule.every().monday.at(night_start_time).do(self.start)
		schedule.every().tuesday.at(night_start_time).do(self.start)
		schedule.every().wednesday.at(night_start_time).do(self.start)
		schedule.every().thursday.at(night_start_time).do(self.start)
		schedule.every().friday.at(night_start_time).do(self.start)
		#
		night_end_time = "05:01"
		schedule.every().monday.at(night_end_time).do(self.stop)
		schedule.every().tuesday.at(night_end_time).do(self.stop)
		schedule.every().wednesday.at(night_end_time).do(self.stop)
		schedule.every().thursday.at(night_end_time).do(self.stop)
		schedule.every().friday.at(night_end_time).do(self.stop)
		'''


if __name__ == '__main__':
	apiPath = MyLib.parse_arg('--api_path')
	api_account = ConfigUtil.obtain_val(apiPath, 'API', 'account')
	api_pwd = ConfigUtil.obtain_val(apiPath, 'API', 'password')

	# stock = MyLib.parse_arg('--stock')
	# stock = 'TX00'
	mySchedule = MySchedule(api_account, api_pwd)
	# mySchedule.start()
	# MergeTicks.run(AssetsHelper.find_last_final_date())
	mySchedule.active()

	# for csc api quote accept event
	# i = 0
	while True:
		schedule.run_pending()
		time.sleep(1)
		pythoncom.PumpWaitingMessages()
	# print(i)
	# i += 1

	exit()
