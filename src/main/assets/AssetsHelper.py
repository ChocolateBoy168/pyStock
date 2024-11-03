import os
import pathlib

import pandas as pd

from src.lib.my_lib.module.LoggerModule import Logger
from src.lib.my_lib.utils.DatetimeUtil import DatetimeUtil
from src.main.util.TickUtil import TickUtil
from src.lib.my_lib.utils import FileUtil


class AssetsHelper:
	_instance = None

	def __new__(cls, *args, **kw):
		if not cls._instance:
			cls._instance = super(AssetsHelper, cls).__new__(cls, *args, **kw)
			cls._instance.__initialized = False
		return cls._instance

	def __init__(self):
		if self.__initialized:
			return
		self.__initialized = True
		# temp
		self.temp_craw_tick_dir_path = str(pathlib.Path(__file__).parent / 'temp/craw/ticks')
		self.temp_craw_best5_dir_path = str(pathlib.Path(__file__).parent / 'temp/craw/best5')
		self.temp_tick_trade_dir_path = str(pathlib.Path(__file__).parent / 'temp/tick_trade')
		self.temp_tick_statistics_dir_path = str(pathlib.Path(__file__).parent / 'temp/tick_statistics')
		# history
		# RunScheduleDaily
		self.history_ticks_dir_path = str(pathlib.Path(__file__).parent / 'history/ticks')
		# RunScheduleDaily 2
		# self.history_ticks_dir_path = str(pathlib.Path(__file__).parent / 'history/ticks2')
		self.history_best5_dir_path = str(pathlib.Path(__file__).parent / 'history/best5')  # todo 2222

	@staticmethod
	def gen_tick_history_path(period, stock_path_dir, lDate):
		me = AssetsHelper()
		# file_path_txt = me.history_ticks_dir_path + "/{}/{}/{}.{}".format(
		# 	period, stock_path_dir, lDate, "csv"
		# )
		path_file = os.path.join(me.history_ticks_dir_path, period, stock_path_dir, f'{lDate}.csv')
		if FileUtil.is_file_exist(path_file):
			return path_file
		else:
			return None

	@staticmethod
	def gen_mix_tick_history_path(period, mixStockNo, date):
		me = AssetsHelper()
		path_file = os.path.join(me.history_ticks_dir_path, period, mixStockNo, f'{date}.csv')
		return path_file

	@staticmethod
	def gen_temp_craw_tick_file(stockNo, history_or_current_lTimehms, change_save_to_history):
		me = AssetsHelper()
		period = TickUtil.extract_period_txt(history_or_current_lTimehms)
		# 若用lDate,夜盤會12點前後日期不一致, 改用現在日期 適用於早盤跑 可以吃 夜盤history資料
		fileName = DatetimeUtil.local_today_to_str(ft='%Y%m%d')

		if change_save_to_history:
			path_file = os.path.join(me.history_ticks_dir_path, period, stockNo, f'{fileName}.csv')
		else:
			# path_file = me.temp_craw_tick_dir_path + "/{}/{}/{}.{}".format(period, stockNo, today, "csv")
			path_file = os.path.join(me.temp_craw_tick_dir_path, period, stockNo, f'{fileName}.csv')

		return path_file

	@staticmethod
	def gen_temp_craw_best5_file(stockNo, current_lTimehms):
		me = AssetsHelper()
		period = TickUtil.extract_period_txt(current_lTimehms)
		fileName = DatetimeUtil.local_today_to_str(ft='%Y%m%d')
		if TickUtil.is_night_period(current_lTimehms):
			fileName = 'temp_night_best5_file'
		path_file = os.path.join(me.temp_craw_best5_dir_path, period, stockNo, f'{fileName}.csv')
		return path_file

	@staticmethod
	def gen_temp_tick_statistics_file(period, stockNo, date, tradeMode, broker_id, suffix):
		me = AssetsHelper()
		# path_file = me.temp_tick_statistics_dir_path + "/{}/{}/{}/{}.{}".format(
		# 	period, stockNo, date, strategy_name, suffix
		# )
		# todo path過長 導致 FileNotFoundError
		path_file = os.path.join(
			me.temp_tick_statistics_dir_path,
			# period,
			# stockNo,
			date,
			# tradeMode,
			f'{broker_id}.{suffix}'
		)
		FileUtil.create_file_if_not_exist(path_file, True)
		return path_file

	@staticmethod
	def gen_temp_tick_trade_file(who, id, suffix):
		me = AssetsHelper()
		# path_file = me.temp_tick_trade_dir_path + "/{}/{}.{}".format(
		# 	who, id, suffix
		# )
		path_file = os.path.join(me.temp_tick_trade_dir_path, who, f'{id}.{suffix}')
		FileUtil.create_file_if_not_exist(path_file, True)
		return path_file

	@staticmethod
	def find_last_file_for_morning_TX00():
		me = AssetsHelper()
		return me.list_history_file_for_morning_TX00(True, True)[0]

	@staticmethod
	def find_last_final_date():
		me = AssetsHelper()
		# 暫時從大台 找出最後一次資料的日期
		path_file = me.find_last_file_for_morning_TX00()
		return path_file[-12:-4]

	@staticmethod
	def find_last_file_for_morning_MTX00():
		me = AssetsHelper()
		return me.list_history_file_for_morning_MTX00(True, True)[0]

	@staticmethod
	def list_history_file_for_morning_TX00(include_settlement_date, reverse=False):
		me = AssetsHelper()
		return me.list_history_file('morning', 'TX00', include_settlement_date, reverse)

	@staticmethod
	def list_history_file_for_morning_MTX00(include_settlement_date, reverse=False):
		me = AssetsHelper()
		return me.list_history_file('morning', 'MTX00', include_settlement_date, reverse)

	@staticmethod
	def list_history_file_for_night_TX00(include_settlement_date, reverse=False):
		me = AssetsHelper()
		return me.list_history_file('night', 'TX00', include_settlement_date, reverse)

	@staticmethod
	def list_history_file_for_night_MTX00(include_settlement_date, reverse=False):
		me = AssetsHelper()
		return me.list_history_file('night', 'MTX00', include_settlement_date, reverse)

	'''
		include_settlement_date: false 表示排開 台指結算日 與 摩台結算日
	'''

	@staticmethod
	def list_history_file_for_day(day, stockNo='TX00', period='morning'):
		me = AssetsHelper()
		result = []
		# path_dir = f"{me.history_ticks_dir_path}/{period}/{stockNo}"
		path_dir = os.path.join(me.history_ticks_dir_path, period, stockNo)
		list = os.listdir(path_dir)
		list.sort()
		for f in list:
			if day in f:
				return os.path.join(path_dir, f)
		return None

	@staticmethod
	def list_history_file_for_month(month, stockNo='TX00', period='morning'):
		me = AssetsHelper()
		result = []
		# path_dir = f"{me.history_ticks_dir_path}/{period}/{stockNo}"
		path_dir = os.path.join(me.history_ticks_dir_path, period, stockNo)
		list = os.listdir(path_dir)
		list.sort()
		for f in list:
			if month in f:
				result.append(os.path.join(path_dir, f))
		return result

	@staticmethod
	def list_history_file(period, stockNo, include_settlement_date=True, reverse=False):
		me = AssetsHelper()
		result = []
		# path_dir = f"{me.history_ticks_dir_path}/{period}/{stockNo}"
		path_dir = os.path.join(me.history_ticks_dir_path, period, stockNo)
		list = os.listdir(path_dir)
		list.sort()
		for f in list:
			if len(f.split('.')[0]) == 8:  # 八位.csv
				f_name = f[0:8]
				if 'null' not in f and f_name.isdigit():
					date = DatetimeUtil.tran_to_date(f_name, "%Y%m%d")
					weekday = date.weekday() + 1
					can_append = True
					if weekday == 3:  # 星期三
						# print(f'{f} is Wednesday')
						if include_settlement_date is False:
							can_append = False
					# 看摩台指結算 要不要一起考慮進來 可能需 統計 才知道 , 日期如下 https://yaci0221.pixnet.net/blog/post/42993287
					if can_append is True:
						result.append(os.path.join(path_dir, f))
		result.sort(reverse=reverse)
		return result

	@staticmethod
	def _tran_new_format_tick_history():
		me = AssetsHelper()
		tick_old_history_dir_path = str(pathlib.Path(__file__).parent / 'tick_history_old')
		period = 'night'
		stockNo = 'TX00'
		path_dir = os.path.join(tick_old_history_dir_path, period, stockNo)
		for f in os.listdir(path_dir):
			if 'null' not in f and f[0:8].isdigit():
				file_path = os.path.join(path_dir, f)
				df = pd.read_csv(file_path)
				df = df.rename(columns={
					'sMarketNo': 'status',
					'sStockIdx': 'stockNo'
				})
				df['status'] = 'history'
				df['stockNo'] = stockNo
				out_file = os.path.join(me.history_ticks_dir_path, period, stockNo, f)
				df.to_csv(out_file, index=False)

	@staticmethod
	def list_deal_date(reverse=False, interrupt_date=None):
		me = AssetsHelper()
		list1 = list(map(lambda txt: txt[-12:-4], me.list_history_file_for_morning_TX00(True, True)))
		list2 = list(map(lambda txt: txt[-12:-4], me.list_history_file_for_morning_MTX00(True, True)))
		# result = list(set(list1).union(list2))
		result = list(set(list1).intersection(list2))  # 應該要用交集才對, 大小台都有ticks 才能計算雙訊號
		result.sort(reverse=reverse)
		if interrupt_date is not None:
			if reverse is True:  # 反向 : 從 最進 到 以前
				result = [x for x in result if x <= interrupt_date]
				pass
			else:  # 正向 : 從 以前 到 最近
				result = [x for x in result if x >= interrupt_date]
				pass
		return result


if __name__ == '__main__':
	# Logger.info(AssetsHelper.list_deal_date())
	# Logger.info(AssetsHelper.list_history_file_for_morning_MTX00(True, False))
	# Logger.info(AssetsHelper.list_history_file_for_morning_MTX00(False))
	# Logger.info(AssetsHelper.find_last_file_for_morning_MTX00())
	# Logger.info(AssetsHelper.find_last_file_for_morning_TX00())
	Logger.info(AssetsHelper.list_deal_date(True, '20200721'))
	exit()

'''  依照當下日期來產生檔名 bad way

def list_deal_fix_date():
	dates = [
		# ===now===
		'20200612',

		'20200611', '20200610', '20200609', '20200608', '20200605', '20200604', '20200603', '20200602', '20200601',
		#
		'20200529', '20200528', '20200527', '20200526', '20200525', '20200521', '20200520', '20200519', '20200518',
		'20200515', '20200514', '20200513',
		'20200512', '20200511', '20200508', '20200507', '20200506', '20200505', '20200504',
		#
		'20200430', '20200429', '20200428', '20200427', '20200424', '20200423', '20200422', '20200421', '20200420',
		'20200417', '20200416', '20200415', '20200414', '20200410', '20200409', '20200408', '20200407', '20200406',
		'20200401',
		#
		'20200331', '20200320', '20200319', '20200318', '20200313', '20200312', '20200311',
		'20200309', '20200306',  '20200304', '20200303', '20200302'
	]
	return dates
		
def gen_tick_cache_name(self):
	name = DatetimeUtil.local_today_to_str('%Y%mXX')
	period = "undefined"

	now_hour = dt.datetime.now().hour
	if now_hour in range(9, 14):
		name = DatetimeUtil.local_today_to_str('%Y%m%d')
		period = "morning"
	elif now_hour in range(15, 24):
		name = DatetimeUtil.local_today_to_str('%Y%m%d')
		period = "night"
	elif now_hour in range(0, 5):
		#todo 應該不是昨天,  需抓早盤最後一次成交日才對
		yesterday = dt.datetime.today() - dt.timedelta(days=1)
		name = yesterday.strftime('%Y%m%d')
		period = "night"

	return "tick_{}_{}.{}".format(name, period, "csv")
'''
