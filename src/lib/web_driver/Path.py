import os
import pathlib
import platform


class WebDriverPath:
	'''
	_instance = None
	def __new__(cls, *args, **kw):
		if not cls._instance:
			cls._instance = super(WebDriverPath, cls).__new__(cls, *args, **kw)
			cls._instance.__initialized = False
		return cls._instance

	def __init__(self):
		if self.__initialized:
			return
		self.__initialized = True
	'''

	@staticmethod
	def get():
		webDriverPath = None
		if platform.system() == 'Windows':
			webDriverPath = os.path.join(pathlib.Path(__file__).parent, 'windows/chromedriver.exe')
		elif platform.system() == 'Darwin':
			webDriverPath = os.path.join(pathlib.Path(__file__).parent, 'mac/chromedriver')
		return webDriverPath
