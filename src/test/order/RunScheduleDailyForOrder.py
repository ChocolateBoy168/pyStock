import datetime
import time

import pythoncom  # 使用pythoncom 需要 pip install pyiwin32
import schedule as schedule

from src.lib.my_lib import MyLib
from src.lib.my_lib.module.LoggerModule import Logger
from src.main.AppConst import PeriodEnum
from src.main.stock_market.Broker import Broker
from src.main.stock_market.trader.capital.CapitalRealTrader import CapitalRealTrader
from src.main.stock_market.trader.capital.CapitalSimulateRealTrader import CapitalSimulateRealTrader
from src.main.util import ConfigUtil


class MySchedule:
	def __init__(self, api_account, api_pwd):
		self.running = False
		self.api_account = api_account
		self.api_pwd = api_pwd
		self.broker = None

	def start(self):
		Logger.info(f'\n========start==========')
		date = datetime.datetime.now().strftime("%Y%m%d")

		# periodEnum = PeriodEnum.Night
		# strategy_source = 'StraBvm[root(multi_1)][bvm(an_1)][fomSumV(aa_1)]'

		periodEnum = PeriodEnum.Morning
		strategy_source = 'StraBvm[root(multi_b6)]        [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]'

		# self.broker = Broker(periodEnum, date, "MTX00", strategy_source, CapitalSimulateRealTrader, api_account, api_pwd) #模擬
		self.broker = Broker(periodEnum, date, "MTX00", strategy_source, CapitalRealTrader, api_account, api_pwd) # real
		Logger.info(f'\n broker log file [{self.broker.broker_log_file}]')
		self.broker.run()
		Logger.info(f'\n========start over==========')

	def stop(self):
		Logger.info(f'\n========stop==========')
		if self.broker is not None:
			self.broker.release_memory()
		Logger.info(f'\nexit~')
		exit()
		# sys.exit()
		Logger.info(f'\n========stop over==========')

	def active(self):
		morning_start_time = "08:40"
		schedule.every().monday.at(morning_start_time).do(self.start)
		schedule.every().tuesday.at(morning_start_time).do(self.start)
		schedule.every().wednesday.at(morning_start_time).do(self.start)
		schedule.every().thursday.at(morning_start_time).do(self.start)
		schedule.every().friday.at(morning_start_time).do(self.start)
		# =========
		morning_end_time = "13:50"
		schedule.every().monday.at(morning_end_time).do(self.stop)
		schedule.every().tuesday.at(morning_end_time).do(self.stop)
		schedule.every().wednesday.at(morning_end_time).do(self.stop)
		schedule.every().thursday.at(morning_end_time).do(self.stop)
		schedule.every().friday.at(morning_end_time).do(self.stop)


if __name__ == '__main__':
	apiPath = MyLib.parse_arg('--api_path')
	api_account = ConfigUtil.obtain_val(apiPath, 'API', 'account')
	api_pwd = ConfigUtil.obtain_val(apiPath, 'API', 'password')
	mySchedule = MySchedule(api_account, api_pwd)
	# mySchedule.start()
	mySchedule.active()

	# for csc api quote accept event
	while True:
		schedule.run_pending()
		time.sleep(1)
		pythoncom.PumpWaitingMessages()

	exit()
