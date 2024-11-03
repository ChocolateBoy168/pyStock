from random import randrange

import numpy as np
import pandas as pd

from src.lib.my_lib import MyLib
from src.lib.my_lib.MyLib import MyCustomError
from src.lib.my_lib.module.LoggerModule import Logger
from src.lib.my_lib.utils.JsonUtil import JsonUtil
from src.lib.my_lib.utils.PandaUtil import PandaUtil
from src.main.AppConst import PeriodEnum
from src.main.api.ApiAiStock import ApiAiStock
from src.main.assets.AssetsHelper import AssetsHelper
from src.main.stock_market.helper.StrategyHelper import StrategyHelper
from src.main.stock_market.trader.abstract.AbstractTrader import AbstractTrader
from src.main.stock_market.trader.capital.CapitalCrawlTrader import CapitalCrawlTrader
from src.main.stock_market.trader.capital.CapitalStatisticsTrader import CapitalStatisticsTrader


class Broker:

	def __init__(self,
				 periodEnum: PeriodEnum, date, trade_stockNo, strategy_source,
				 traderClass, traderAccount=None, traderPwd=None
				 ):
		self.periodEnum = periodEnum
		self.date = date
		self.trade_stockNo = trade_stockNo
		self.strategy = None
		self.is_morningTradePeriod_and_containNightSignal = False

		# step: create trader
		self.trader: AbstractTrader = None
		if traderClass == CapitalCrawlTrader:
			self.requestTicks_stockNos = ['TX00', 'MTX00']
			self.trader = traderClass(self, traderAccount, traderPwd)
		else:
			# step: parse strategy context

			strategyId, stra_ctxt, strategyClass = StrategyHelper.parse_strategy_source(
				periodEnum, strategy_source
			)

			if (self.periodEnum == PeriodEnum.Morning) and StrategyHelper.contain_night(stra_ctxt):
				self.is_morningTradePeriod_and_containNightSignal = True

			self.requestTicks_stockNos = StrategyHelper.try_expand_request_ticks_stockNos(
				trade_stockNo, stra_ctxt
			)
			if traderClass == CapitalStatisticsTrader:
				self.trader = traderClass(self)
			else:
				self.trader = traderClass(self, traderAccount, traderPwd)

			# step: create strategy
			'''
			 建立strategy放在trader之後的原因
			 1. 建立 strategy 時要有 trader 
			 2. strategy.build 要有 requestTicks_stockNos
			 '''

			self.strategy = strategyClass(self, strategyId, stra_ctxt)
			self.strategy.build()

			# step: broker log
			self.broker_log_file = AssetsHelper.gen_temp_tick_statistics_file(
				self.periodEnum.value, self.trade_stockNo, self.date, self.trader.trade_mode.value, self.strategy.id,
				"md"
			)

	def release_memory(self):
		if self.trader is not None:
			self.trader.release_memory()
			del self.trader
		if self.strategy is not None:
			if self.strategy.signal is not None:
				del self.strategy.signal
			del self.strategy
		del self.requestTicks_stockNos
		del self

	def register_trader(self, trader: AbstractTrader):
		self.trader = trader
		if self.trader.is_not_crawl():
			assert self.trade_stockNo in self.requestTicks_stockNos, 'trade_stockNo 在 requestTicks_stockNos 裡需指定'

	# [log]
	def write_to_broker_log(self, txt):
		if self.broker_log_file is None:
			raise MyCustomError("broker_log_file need to be defined")
		# Logger.info(txt)
		with open(self.broker_log_file, "a+", encoding='utf8') as f:
			f.seek(0)
			data = f.read(100)
			if len(data) > 0:
				f.write("\n")
			f.write(txt)
			f.close()

	def read_broker_log(self):
		txt = ''
		with open(self.broker_log_file, "r", encoding='utf8') as f:
			txt = f.read()
			f.close()
		return txt

	def clear_broker_log(self):
		MyLib.delete_file_if_exist(self.broker_log_file)

	def save_to_server(self):
		# save to server data
		brokerLog = self.read_broker_log()
		data = [{
			# 組合起來成為key
			'period': self.periodEnum.value,
			'stock': self.trade_stockNo,
			'date': self.date,
			'trade': self.trader.trade_mode.value,
			'strategy': self.strategy.id,

			# info
			'brokerLog': brokerLog,
			'lot': self.trader.profitHandler.lot,
			'cost': int(self.trader.profitHandler.cost),
			'profit': int(self.trader.profitHandler.profit),
		}]
		batch_uid = randrange(1000, 9999)
		result = ApiAiStock.batchSaveOrUpdateBrokerLog(batch_uid, data)
		Logger.info(f'batchSaveOrUpdateBrokerLog response => {JsonUtil.to_json_str(result.data)}')

	def run(self, save_to_server=False):
		if self.trader.is_statistics_trade():
			stock_path_dir = 'None'
			if len(self.requestTicks_stockNos) == 1:  # 單一訊號
				stock_path_dir = self.requestTicks_stockNos[0]
			elif len(self.requestTicks_stockNos) >= 2:  # 多訊號
				# stock_path_dir = '+'.join(self.requestTicks_stockNos)
				stock_path_dir = 'TX00+MTX00'  # todo 配合路徑 需再思考更好的組合方式
			if stock_path_dir is not None:
				history_path = AssetsHelper.gen_tick_history_path(self.periodEnum.value, stock_path_dir, self.date)
				if history_path is not None:
					Logger.info(f'讀取{history_path}')
					df = pd.read_csv(history_path)
					Logger.info(f'讀取結束')
					# use index dict (fast)
					'''
					跑到一半會出現 -1073741819 (0xC0000005) [猜有可能]是底下這行造成的,因為多個process同時使用了PathUtil的to_dict
					'''
					ticks = PandaUtil.to_records_dict(df)
					Logger.info(f'df轉成ticks over')
					# 早盤前面加入夜盤的ticks
					if self.is_morningTradePeriod_and_containNightSignal:
						night_path = AssetsHelper.gen_tick_history_path(
							PeriodEnum.Night.value, stock_path_dir, self.date
						)
						Logger.info(f'加入夜盤的ticks')
						if night_path is not None:
							Logger.info(f'讀取夜盤{night_path}')
							night_df = pd.read_csv(night_path)
							Logger.info(f'讀取夜盤結束')
							night_ticks = PandaUtil.to_records_dict(night_df)
							Logger.info(f'df轉成夜盤ticks over')
							ticks = night_ticks + ticks
						else:
							Logger.warning(f"{night_path}夜盤tick不存在")
					self.trader.run(ticks)
				else:
					Logger.warning(
						'Warn=> file {}/{}/{}.csv can not find'.format(self.periodEnum.value, stock_path_dir,
																	   self.date))
		else:
			self.trader.run()

		if save_to_server:
			self.save_to_server()

	# [method]
	def obtain_trade_stockTick(self):
		return self.strategy.signal.obtain_stockTick(self.trade_stockNo)

	def obtain_trade_stockTick_currentTick(self):
		return self.obtain_trade_stockTick().currentTick


if __name__ == '__main__':
	print(np.array([2, 2, 6, 1, 7, 8]))
	print(np.array([2, 2, 6, 1, 7, 8]) >= 6)
	print(np.array([2, 2, 6, 1, 7, 8]) >= np.array([5, 6]))
	exit()
