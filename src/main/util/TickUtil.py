from datetime import datetime

from src.lib.my_lib.module.LoggerModule import Logger
from src.main.AppConst import PeriodEnum


class TickUtil:
	_instance = None

	def __new__(cls, *args, **kw):
		if not cls._instance:
			cls._instance = super(TickUtil, cls).__new__(cls, *args, **kw)
			cls._instance.__initialized = False
		return cls._instance

	def __init__(self):
		if self.__initialized:
			return
		self.__initialized = True

	@staticmethod
	def extract_int_price(tick):
		return int(int(tick['nClose']) // 100)

	@staticmethod
	def extract_int_nQty(tick):
		return int(tick['nQty'])

	@staticmethod
	def extract_dateTime(tick):
		lDate = tick['lDate']
		lTimehms = tick['lTimehms']
		# todo sometime MemoryError  why?
		dt = datetime.strptime("{} {:06d}".format(lDate, int(lTimehms)), "%Y%m%d %H%M%S")
		return dt

	@staticmethod
	def is_addSubNQty_not_ambiguous(tick):
		return '#' not in str(tick['addSubNQty'])

	@staticmethod
	def is_enter_time_not_in_start_to_late(
			lTimehms,
			morning_start_enter_time=84500, morning_last_enter_time=133000,
			night_start_enter_time=133000, night_last_enter_time=45939,
	):
		me = TickUtil()
		notIn = False
		if me.is_morning_period(lTimehms):
			if lTimehms < morning_start_enter_time:
				notIn = True
			if lTimehms > morning_last_enter_time:
				notIn = True
		elif me.is_night_period(lTimehms):
			if lTimehms < night_start_enter_time:
				notIn = True
			# 小心需相同evening or midnight時段
			if me.is_evening_period(lTimehms) and me.is_evening_period(night_last_enter_time):
				if lTimehms > night_last_enter_time:
					notIn = True
			elif me.is_midnight_period(lTimehms) and me.is_midnight_period(night_last_enter_time):
				if lTimehms > night_last_enter_time:
					notIn = True
		else:
			Logger.error('不可能發生,交易時段不明確', lTimehms)
		return notIn

	@staticmethod
	def is_expired(lTimehms, morning_expired_time=134430, night_expired_time=45939):
		me = TickUtil()
		expired = False
		if me.is_morning_period(lTimehms):
			if lTimehms >= morning_expired_time:
				expired = True
		elif me.is_night_period(lTimehms):  # 小心需相同evening or midnight時段
			if me.is_evening_period(lTimehms) and me.is_evening_period(night_expired_time):
				if lTimehms >= night_expired_time:
					expired = True
			elif me.is_midnight_period(lTimehms) and me.is_midnight_period(night_expired_time):
				if lTimehms >= night_expired_time:
					expired = True
		else:
			Logger.error('不可能發生,交易時段不明確', lTimehms)
		return expired

	@staticmethod
	def extract_period(tick):
		me = TickUtil()
		period = None
		if me.is_morning_period_for_tick(tick):
			period = PeriodEnum.Morning
		elif me.is_night_period_for_tick(tick):
			period = PeriodEnum.Night
		return period

	@staticmethod
	def extract_period_txt(lTimehms):
		me = TickUtil()
		period = None
		if me.is_night_period(lTimehms):
			period = 'night'
		elif me.is_morning_period(lTimehms):
			period = 'morning'
		return period

	@staticmethod
	def is_morning_period(lTimehms):
		me = TickUtil()
		return me.obtain_period_txt(lTimehms) == "morning"

	@staticmethod
	def is_night_period(lTimehms):
		me = TickUtil()
		return me.is_evening_period(lTimehms) or me.is_midnight_period(lTimehms)

	@staticmethod
	def is_evening_period(lTimehms):
		me = TickUtil()
		return me.obtain_period_txt(lTimehms) == "evening"

	@staticmethod
	def is_midnight_period(lTimehms):
		me = TickUtil()
		return me.obtain_period_txt(lTimehms) == "midnight"

	# ----

	@staticmethod
	def is_morning_period_for_tick(tick):
		me = TickUtil()
		return me.is_morning_period(tick['lTimehms'])

	@staticmethod
	def is_night_period_for_tick(tick):
		me = TickUtil()
		return me.is_night_period(tick['lTimehms'])

	# ----

	@staticmethod
	def obtain_period_txt(lTimehms):
		period = None
		# if lTimehms in range(83000, 134500 + 1):
		if lTimehms in range(80000, 140000):
			period = "morning"
		# elif lTimehms in range(145000, 240000 + 1):
		elif lTimehms in range(143000, 240000 + 1):
			period = "evening"  # night first
		# elif lTimehms in range(0, 50000 + 1):
		elif lTimehms in range(0, 53000):
			period = "midnight"  # night second
		return period
