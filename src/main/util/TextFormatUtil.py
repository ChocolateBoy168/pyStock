class TextFormatUtil:
	_instance = None

	def __new__(cls, *args, **kw):
		if not cls._instance:
			cls._instance = super(TextFormatUtil, cls).__new__(cls, *args, **kw)
			cls._instance.__initialized = False
		return cls._instance

	def __init__(self):
		if self.__initialized:
			return
		self.__initialized = True

	def close_position_way_ch(self, cmd_id):
		ch = None
		if cmd_id == 'cancel_for_loss':
			ch = '平倉 停損'
		elif cmd_id == 'cancel_for_profit':
			ch = '平倉 停利'
		elif cmd_id == 'cancel_for_expired_time':
			ch = '平倉 逾時'
		return ch

	def tran_int_to_positive_negative_txt(self, num):
		return '' if num is None else '0' if num == 0 else '+{}'.format(num) if num > 0 else '{}'.format(num)
