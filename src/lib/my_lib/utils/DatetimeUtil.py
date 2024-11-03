"""
    https://blog.xuite.net/porpoise/blog/301905371-%5BPython%5D+utc+time+%E8%88%87+local+time+%E4%BA%92%E8%BD%89.
"""

import time
import datetime as dt
from typing import Union


class DatetimeUtil:
	_instance = None

	def __new__(cls, *args, **kw):
		if not cls._instance:
			cls._instance = super(DatetimeUtil, cls).__new__(cls, *args, **kw)
			cls._instance.__initialized = False
		return cls._instance

	def __init__(self):
		if self.__initialized:
			return
		self.__initialized = True

	@staticmethod
	def local_now() -> dt.datetime:
		result = dt.datetime.now()
		return result

	@staticmethod
	def local_now_year() -> dt.datetime:
		me = DatetimeUtil()
		return me.local_now().year

	@staticmethod
	def local_now_month() -> dt.datetime:
		me = DatetimeUtil()
		return me.local_now().month

	@staticmethod
	def local_now_day() -> dt.datetime:
		me = DatetimeUtil()
		return me.local_now().day

	@staticmethod
	def local_now_hour() -> dt.datetime:
		me = DatetimeUtil()
		return me.local_now().hour

	@staticmethod
	def local_now_minute() -> dt.datetime:
		me = DatetimeUtil()
		return me.local_now().minute

	@staticmethod
	def local_now_second() -> dt.datetime:
		me = DatetimeUtil()
		return me.local_now().second

	@staticmethod
	def utc_now() -> dt.datetime:
		# result = dt.datetime.now()
		result = dt.datetime.utcnow()
		# ok  => from now timestamp
		'''
		result = dt.datetime.utcfromtimestamp(
			time.mktime(
				dt.datetime.now().timetuple()
			)
		)
		'''
		return result

	@staticmethod
	def local_today_to_str(ft='%Y-%m-%d') -> str:
		me = DatetimeUtil()
		return me.format_date_to_str(me.local_now(), ft)

	# https://stackoverflow.com/questions/13142347/how-to-remove-leading-and-trailing-zeros-in-a-string-python
	@staticmethod
	def current_time_trip_zero():  # 群益的時間格式
		val = DatetimeUtil.local_today_to_str('%H%M%S').lstrip('0')
		if val == '':  # 剛好晚上12點整
			return 0
		return int(val)

	@staticmethod
	def format_date_to_str(date: dt.datetime, ft='%Y-%m-%dT%H:%M:%S.%fZ') -> str:
		return date.strftime(ft)

	@staticmethod
	def utc_now_format_str() -> str:
		me = DatetimeUtil()
		return me.format_date_to_str(me.utc_now())

	# ex: local => 2019-11-13 00:00:00
	@staticmethod
	def local_today() -> dt.datetime:
		now = dt.datetime.now()
		result: dt.datetime = dt.datetime.strptime(f"{now.year}-{now.month}-{now.day} 00:00:00", "%Y-%m-%d %H:%M:%S")
		return result

	@staticmethod
	def today_to_utc() -> dt.datetime:
		me = DatetimeUtil()
		# dt.datetime.utcfromtimestamp(time.mktime(dt.datetime.strptime("1970-01-01 00:00:00","%Y-%m-%d %H:%M:%S").timetuple()))
		local_today = me.local_today()
		result: dt.datetime = me.local_date_to_utc_date(local_today)
		return result

	@staticmethod
	# dt.datetime or str
	def local_date_to_utc_date(local_date: Union[dt.datetime, str]) -> dt.datetime:
		me = DatetimeUtil()
		result = None
		if isinstance(local_date, str):  # str
			result = me.local_date_to_utc_date(me.date(local_date))
		elif isinstance(local_date, dt.datetime):  # datetime
			result = dt.datetime.utcfromtimestamp(time.mktime(local_date.timetuple()))
		return result

	@staticmethod
	def local_date_to_utc_date_str(local_date: Union[dt.datetime, str]) -> str:
		me = DatetimeUtil()
		return me.format_date_to_str(me.local_date_to_utc_date(local_date))

	@staticmethod
	def date(text: str) -> dt.datetime:
		assert text is not None
		# todo 2222  need regex datetime
		me = DatetimeUtil()
		if ':' in text:  # ex:  DatetimeUtil.date("2019-11-13 13:30:00")
			# result: dt.datetime = dt.datetime.strptime(f"{text}", "%Y-%m-%d %H:%M:%S")
			result = me.tran_to_date(f"{text}", "%Y-%m-%d %H:%M:%S")
		else:  # ex:  DatetimeUtil.date("2019-11-13")
			# result: dt.datetime = dt.datetime.strptime(f"{text} 00:00:00", "%Y-%m-%d %H:%M:%S")
			result = me.tran_to_date(f"{text} 00:00:00", "%Y-%m-%d %H:%M:%S")
		return result

	@staticmethod
	def tran_to_date(text: str, format_str: str) -> dt.datetime:
		assert text is not None
		assert format_str is not None
		result: dt.datetime = dt.datetime.strptime(text, format_str)
		return result

	def demo_spend_time(self):
		start = time.perf_counter()
		for i in range(0, 1000):
			print(i)
		finish = time.perf_counter()
		print(f'{start} to {finish} spend {round(finish - start, 2)} second(s)')


if __name__ == "__main__":
	util = DatetimeUtil()
	print(util.format_date_to_str(dt.datetime.now(), '%Y/%m/%d'))
	print(util.local_today_to_str('%Y/%m/%d'))
# util.demo_spend_time()
