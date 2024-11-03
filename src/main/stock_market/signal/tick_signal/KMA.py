import enum

from src.lib.my_lib.module.LoggerModule import Logger
from src.lib.my_lib.utils.PandaUtil import PandaUtil
from src.main.AppConst import PeriodEnum
from src.main.assets.AssetsHelper import AssetsHelper
from src.main.util.TickUtil import TickUtil
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


class KmaPrototypeEnum(enum.Enum):
	#
	INDEX = 'index'  # 指數
	FOLLOW_MASTER = 'follow_master'  # 跟隨主力
	AVOID_SLAVE = 'avoid_slave'  # 避開散戶


class K:
	def __init__(self, stockTick, prototype, stockNo, dt_key, mas=[]):
		self.stockTick = stockTick
		self.prototype = prototype
		# base
		self.dt_key = dt_key  # datetime key
		# ohlc
		self.open = None
		self.high = None
		self.low = None
		self.close = None
		# mas
		self.ma = dict()
		for id in mas:
			self.ma[id] = dict(val=None, slope=None)
		# k vol
		self.k_nQty = None  # 無正負的量
		self.k_addSubNQty = None  # 有正負的量
		# k sum vol
		self.sum_nQty = None  # 無正負 加總
		self.sum_addSubNQty = None  # 有正負 加總
		# other #todo 量能分布
		self.detail = None
		self.stockNo = stockNo
		self.ticks_per_k = []  # 針對這一根k裡累積的tick

	def add_tick(self, tick):
		# Logger.info(f'{self.dt_key} add tick {tick}')
		source = None
		if self.prototype == KmaPrototypeEnum.INDEX:
			source = TickUtil.extract_int_price(tick)
		elif self.prototype == KmaPrototypeEnum.FOLLOW_MASTER:
			source = self.stockTick.master_volume
		elif self.prototype == KmaPrototypeEnum.AVOID_SLAVE:
			source = self.stockTick.slave_volume
		if source is None:
			raise RuntimeError('source 不應該 None')
		nQty = TickUtil.extract_int_nQty(tick)
		if self.is_empty():  # 第一根k的第一個tick
			if (len(self.ticks_per_k) != 0):
				raise RuntimeError('第一根的第一個tick,length應該是0才對')
			self.open = source
			self.close = source
			self.high = source
			self.low = source
			self.k_nQty = nQty
			self.sum_nQty = nQty
			if TickUtil.is_addSubNQty_not_ambiguous(tick):
				int_addSubNQty = int(tick['addSubNQty'])
				self.k_addSubNQty = int_addSubNQty
				self.sum_addSubNQty = int_addSubNQty
			else:
				self.sum_addSubNQty = 0
				self.k_addSubNQty = 0
		else:  # 第一根k的第二個tick(含之後) or 第二根k(含之後)
			if len(self.ticks_per_k) == 0:  # 表示第 N 跟K的第一個tick
				self.open = source
			self.close = source
			if source > self.high:
				self.high = source
			if source < self.low:
				self.low = source
			self.k_nQty += nQty
			self.sum_nQty += nQty
			if TickUtil.is_addSubNQty_not_ambiguous(tick):
				int_addSubNQty = int(tick['addSubNQty'])
				self.k_addSubNQty += int_addSubNQty
				self.sum_addSubNQty += int_addSubNQty
		# self.stockNo = tick['stockNo']
		self.ticks_per_k.append(tick)

	def is_empty(self):
		return self.open == None

	def info(self):
		title = f'{self.stockNo} ' if self.stockNo == 'TX00' else f'{self.stockNo}'
		info = f'{title} {self.dt_key} : ' \
			   f'ohlc[{self.open} {self.high} {self.low} {self.close} {self.close - self.open}] ' \
			   f'ma[{self.ma}] ' \
			   f'kVol[{self.k_nQty} {self.k_addSubNQty}] ' \
			   f'sumVol[{self.sum_nQty} {self.sum_addSubNQty}] ' \
			   f'detail[{self.detail}]'
		return info


class KMA:
	# ma: 計算各ma的值
	def __init__(self, stockTick, prototype, rate_of_second=1, mas=[]):
		self.stockTick = stockTick
		self.prototype = prototype
		self.period = self.stockTick.strategy.broker.periodEnum
		self.trade_date_str = self.stockTick.strategy.broker.date
		self.rate_of_second = rate_of_second
		self.mas = mas
		self.ks = dict()
		self.prev_k: K = None
		self.current_k: K = None
		self.regular_dt_format = '%Y-%m-%d %H:%M:%S'  # 也就是datetime64.astype(datetime)後的預設格式

	def add_tick(self, tick):
		dt = TickUtil.extract_dateTime(tick)
		dt_key_str = dt.strftime(self.regular_dt_format)
		if len(self.ks) == 0:
			self.ks = self.gen_ks(tick['stockNo'], dt.year, dt.month, dt.day, self.mas)
		self.k_recursive_fill_empty(dt)
		near_key_str, near_key_index = self.find_near_key(dt_key_str)
		if near_key_str is not None:
			if near_key_index >= 1:  # 第二根K,[0,1,.....]之後,才有前一個k
				prev_key = list(self.ks.keys())[near_key_index - 1]
				self.prev_k = self.ks[prev_key]
			self.current_k = self.ks[near_key_str]
			self.current_k.add_tick(tick)
			# set k's ma's value
			near_key_index_left = list(self.ks.keys()).index(near_key_str)
			near_key_index_right = near_key_index_left + 1
			for ma_id in self.current_k.ma:
				if (near_key_index_right >= ma_id):  # k棒數量 要大於等於 [幾ma is ma_id]
					near_keys = list(self.ks.keys())[(near_key_index_right - ma_id): near_key_index_right]
					# Logger.debug(f'{near_keys}')
					try:
						# 最後幾根Ｋ棒的平均值
						# if False:
						# 	#可能因沒錄到的tick 導致k's close is none, 這樣平均值含none 會出錯
						# 	avg = np.mean([
						# 		self.ks[key].close for key in near_keys
						# 	])
						sum = 0
						count = 0
						for key in near_keys:
							if self.ks[key].close is not None:
								sum += self.ks[key].close
								count += 1
						# if sum == 0:
						# 	Logger.info('總和剛好為0')
						avg = sum / count
						self.current_k.ma[ma_id]['val'] = avg
						if self.prev_k is None:
							self.current_k.ma[ma_id]['slope'] = None
						else:
							pre_k_ma_val = self.prev_k.ma[ma_id]['val']
							if pre_k_ma_val is None:
								self.current_k.ma[ma_id]['slope'] = None
							else:
								self.current_k.ma[ma_id]['slope'] = avg - pre_k_ma_val  # todo 斜率暫時用與前一個kma相減
					# Logger.debug(f'{self.current_k.ma}')
					except Exception as e:
						Logger.error(e)

	# Logger.info(self.ks[near_key_str].info())

	# 往前找到有值的K棒,並填補[中間連續]或[最後一個]空洞的K棒
	def k_recursive_fill_empty(self, dt) -> K:
		dt_key_str = dt.strftime(self.regular_dt_format)
		near_key_str, near_key_index = self.find_near_key(dt_key_str)
		if near_key_str is None:
			return None
		k = self.ks[near_key_str]
		if k.is_empty():
			prev_dt = datetime.strptime(near_key_str, self.regular_dt_format) - timedelta(seconds=self.rate_of_second)
			head_dt = datetime.strptime(list(self.ks.keys())[0], self.regular_dt_format)
			if (prev_dt < head_dt) is True:  # 碰壁 over head
				return None
			'''
				[註A]如果含夜盤訊號的早盤交易, if rate_of_scond=60, dt = 08:45 那 prev_dt = 08:44 , 
				find_near_key(prev_dt) 會剛好是夜盤的最後一個key (04:59) , 
				這樣就不必擔心訊號 從夜盤最後一根k copy到 早盤第一根K 的失敗
				
				[註B]只copy第一層reference的name-value, 
				但ma的第二層reference[val/slope]不會真正的copy到,
				所以會用同一個參考(這樣會導致k的val/slope若變化,則prev_k的val/slope也會隨著變化,)
				
				[註C]當 每 [新K中,收到第一個tick] 初始化完後, 就列印 [前一根k中,收到最後一個tick] 的資訊
			'''
			prev_k = self.k_recursive_fill_empty(prev_dt)  # [註A]
			if prev_k is not None:
				k.open = prev_k.close
				k.close = k.open
				k.high = k.open
				k.low = k.open
				k.ma = prev_k.ma.copy()  # [註B]
				# 需再copy第二層 ***重要***
				for ma_id in prev_k.ma.keys():
					k.ma[ma_id] = dict(
						val=prev_k.ma[ma_id]['val'],
						slope=prev_k.ma[ma_id]['slope']
					)
				k.k_nQty = 0
				k.k_addSubNQty = 0
				k.sum_nQty = prev_k.sum_nQty
				k.sum_addSubNQty = prev_k.sum_addSubNQty
				k.detail = prev_k.detail
				k.stockNo = prev_k.stockNo

				# [註C]
				if False:
					if prev_k.stockNo == 'TX00':
						Logger.debug(prev_k.info())
						Logger.debug(self.stockTick.info())
					else:
						Logger.info(prev_k.info())
						Logger.info(self.stockTick.info())
				return k
			else:
				return None
		else:
			return k

	def find_near_key(self, dt_key):
		result = None
		keys = list(self.ks.keys())
		keys_size = len(keys)
		index = -1
		for index in range(keys_size):
			left = keys[index]
			if index >= (keys_size - 1):  # 最後一個
				if (dt_key >= left):
					result = left
					break
			else:
				right = keys[index + 1]
				if (dt_key >= left) and dt_key < right:
					result = left
					break
		if result is None:
			# 發生紀錄: 可能群益bug,剛好過了晚上12點,丟來的日期卻不是過了晚上12點 ex: 20210510.csv => history,MTX00,25678,20210507,0,20000,1736900,1737000,1737000,3,0,+3
			# 解法 需校正時間 , 暫時忽略此tick不處理
			Logger.error(f'不該發生的dt_key={dt_key}')
		return result, index

	#配置ks空間
	def gen_ks(self, stockNo, y: int, m: int, d: int, mas=[]):
		ks = dict()

		if self.stockTick.strategy.broker.is_morningTradePeriod_and_containNightSignal:
			# 配置夜盤
			start_night = datetime(y, m, d, 15, 0, 0)
			end_night = start_night + timedelta(hours=14)
			keys = np.arange(
				start_night, end_night, timedelta(seconds=self.rate_of_second)
			).astype(datetime).astype(str)
			for key in keys:
				ks[key] = K(self.stockTick, self.prototype, stockNo, key, mas)

			# 配置早盤
			# start_morning = datetime(end_night.year, end_night.month, end_night.day, 8, 45, 0) # 要小心 這個有問題 星期五過清晨00點後的夜盤 銜接到 下禮拜一的早盤 ,日期是不一樣的
			trade_date = datetime.strptime(self.trade_date_str, '%Y%m%d')
			start_morning = datetime(trade_date.year, trade_date.month, trade_date.day, 8, 45, 0)

			end_morning = start_morning + timedelta(hours=5)
			keys = np.arange(
				start_morning, end_morning, timedelta(seconds=self.rate_of_second)
			).astype(datetime).astype(str)
			for key in keys:
				ks[key] = K(self.stockTick, self.prototype, stockNo, key, mas)
		else:
			if self.period == PeriodEnum.Morning:
				start = datetime(y, m, d, 8, 45, 0)
				end = start + timedelta(hours=5)
			elif self.period == PeriodEnum.Night:
				start = datetime(y, m, d, 15, 0, 0)
				end = start + timedelta(hours=14)
			else:
				raise RuntimeError(f' cant not identify period {self.period}')
			keys = np.arange(
				start, end, timedelta(seconds=self.rate_of_second)
			).astype(datetime).astype(str)
			for key in keys:
				ks[key] = K(self.stockTick, self.prototype, stockNo, key, mas)

		return ks

	def log_ks(self):
		ks = self.ks
		for key in ks.keys():
			k = ks[key]
			if k.is_empty() is False:
				Logger.info(k.info())


# ====
if __name__ == '__main__':
	period = PeriodEnum.Morning.value
	# period = PeriodEnum.Night.value
	# stock_path_dir = 'TX00+MTX00'
	# stock_path_dir = 'MTX00'
	stock_path_dir = 'debug'
	date = '20200708_debug'
	history_path = AssetsHelper.gen_tick_history_path(period, stock_path_dir, date)
	ticks = []
	if history_path is not None:
		df = pd.read_csv(history_path)
		# a = list(set(df[df['stockNo'] == 'MTX00']['lTimehms']))
		# np.sort(a)
		# use index dict (fast)
		ticks = PandaUtil.to_records_dict(df)
	#
	kma = KMA(1, [5, 10])
	for t in ticks:
		if t['nSimulate'] == 1:
			continue
		kma.add_tick(t)
	kma.log_ks()

# ====

if __name__ == '__main__demo1':
	tick_time = datetime.strptime(
		"{} {:06d}".format('20200707', int('84500'))
		, "%Y%m%d %H%M%S"
	)
	np.arange(datetime(1985, 7, 1), datetime(2015, 7, 1), timedelta(days=1)).astype(datetime)

	# morning
	morning_start = datetime(2020, 7, 7, 8, 45, 0)
	morning_end = morning_start + timedelta(hours=5)
	np.arange(morning_start, morning_end, timedelta(minutes=1))
	np.arange(morning_start, morning_end, timedelta(seconds=1))

	# night
	night_start = datetime(2020, 7, 7, 15, 0, 0)
	night_end = night_start + timedelta(hours=14)
	np.arange(night_start, night_end, timedelta(minutes=1))
	np.arange(night_start, night_end, timedelta(seconds=1))
	keys = (np.arange(night_start, night_end, timedelta(seconds=1))).astype(datetime).astype(str)
