class SignalHelper:
	_instance = None


	def __new__(cls, *args, **kw):
		if not cls._instance:
			cls._instance = super(SignalHelper, cls).__new__(cls, *args, **kw)
			cls._instance.__initialized = False
		return cls._instance

	def __init__(self):
		if self.__initialized:
			return
		self.__initialized = True
