import logging
import os
from logging.handlers import TimedRotatingFileHandler

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

COLORS = {
	'DEBUG': CYAN,
	'INFO': GREEN,
	'WARNING': YELLOW,
	'ERROR': RED,
	'CRITICAL': MAGENTA,
}


def formatter_message(fmt, use_color=True):
	if use_color:
		fmt = fmt.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
	else:
		fmt = fmt.replace("$RESET", "").replace("$BOLD", "")
	return fmt


class MyColoredFormatter(logging.Formatter):
	def __init__(self, fmt, use_color=True):
		logging.Formatter.__init__(self, fmt=fmt)
		self.use_color = use_color

	def color_txt(self, color, obj):
		txt = str(obj)
		return COLOR_SEQ % (30 + color) + txt + RESET_SEQ

	def format(self, record):
		if self.use_color:
			levelname = record.levelname
			if levelname in COLORS:
				c = COLORS[levelname]
				# record.levelname = self.color_txt(c, record.levelname)
				record.levelname = self.color_txt(c, record.levelname[0])
				record.msg = self.color_txt(c, record.msg)
				record.filename = self.color_txt(c, record.filename)
				record.funcName = self.color_txt(c, record.funcName)
			if True:
				# record.asctime = self.color_txt(WHITE, record.asctime)
				record.threadName = self.color_txt(WHITE, record.threadName)
				# record.lineno = self.color_txt(WHITE, record.lineno)
				pass
		return logging.Formatter.format(self, record)


'''
class MyColoredLogger(logging.Logger):
	# FORMAT_STR = "[$BOLD%(name)-20s$RESET][%(levelname)-18s]  %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
	# FORMAT_STR = '%(asctime)s[%(levelname)-20s][%(threadName)s,%(filename)s:%(funcName)s:%(lineno)d] => $BOLD%(message)s$RESET'
	FORMAT_STR = '%(asctime)s[%(levelname)s][%(threadName)s][%(filename)s:%(funcName)s:%(lineno)d] => $BOLD%(message)s$RESET'

	def __init__(self, name):
		logging.Logger.__init__(self, name, logging.DEBUG)
		fmt = formatter_message(self.FORMAT_STR, True)
		color_formatter = MyColoredFormatter(fmt)
		console_handle = logging.StreamHandler()
		console_handle.setFormatter(color_formatter)
		self.addHandler(console_handle)
		return
'''


class MyLogger(logging.Logger):
	# _instance = None

	# FORMAT_STR = "[$BOLD%(name)-20s$RESET][%(levelname)-18s]  %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
	# FORMAT_STR = '%(asctime)s[%(levelname)-20s][%(threadName)s,%(filename)s:%(funcName)s:%(lineno)d] => $BOLD%(message)s$RESET'
	FORMAT_STR = '%(asctime)s[%(levelname)s][%(process)s %(processName)s %(threadName)s][%(filename)s:%(funcName)s:%(lineno)d] => $BOLD%(message)s$RESET'

	# ROTATING_FORMAT_STR ='%(asctime)s - %(levelname)s : %(message)s'
	# ROTATING_FORMAT_STR = '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S'
	# ROTATING_FORMAT_STR = '%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
	# ROTATING_FORMAT_STR = '%(asctime)s[%(levelname)s][%(threadName)s,%(filename)s:%(funcName)s:%(lineno)d] => %(message)s'
	ROTATING_FORMAT_STR = '%(asctime)s[%(levelname)s][%(process)s %(processName)s %(threadName)s][%(filename)s:%(funcName)s:%(lineno)d] => %(message)s'

	# logger_with_rotating = None
	# logger_without_rotating = None

	# def __new__(cls, *args, **kw):
	# 	if not cls._instance:
	# 		cls._instance = super(Logger, cls).__new__(cls, *args, **kw)
	# 		cls._instance.__initialized = False
	# 	return cls._instance

	def __init__(self, name, level, rotating):
		super().__init__(name, level)

		# logging.setLoggerClass(MyColoredLogger)
		# logger = logging.getLogger(name)
		# logger.setLevel(level)

		# step 先 [rotating log]
		if rotating is True:
			formatter = logging.Formatter(self.ROTATING_FORMAT_STR)
			# log_path = os.path.join(Path.home(), 'logs')
			# todo 暫時的 , how to find "src的上一層/log" path
			log_path = os.path.join(
				os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
				'rotating_log')
			os.makedirs(log_path, exist_ok=True)
			rotating_handler = TimedRotatingFileHandler(
				os.path.join(log_path, 'roulette.log'),
				when='d',
				backupCount=10,
				encoding='utf-8'
			)
			rotating_handler.setFormatter(formatter)
			self.addHandler(rotating_handler)

		# step 後 [console log]
		'''
		 #user coloredlogs fail for color
		# Initialize coloredlogs.
		# coloredlogs.install()
		coloredlogs.install(level='DEBUG')
		# coloredlogs.install(level='INFO')
		# coloredlogs.install(logger=self.logger)
		
		# logger.addHandler(logging.StreamHandler(sys.stdout))
		console_handler = logging.StreamHandler()
		format_str = '%(asctime)s[%(levelname)s,%(threadName)s,%(filename)s:%(lineno)d]=>%(message)s'
		# formatter = logging.Formatter(format_str)
		formatter = coloredlogs.ColoredFormatter(format_str)
		console_handler.setFormatter(formatter)
		logger.addHandler(console_handler)
		'''
		fmt = formatter_message(self.FORMAT_STR, True)
		color_formatter = MyColoredFormatter(fmt)
		console_handle = logging.StreamHandler()
		console_handle.setFormatter(color_formatter)
		self.addHandler(console_handle)

	'''
	@staticmethod
	def debug(message, rotating=True):
		me = Logger()
		if rotating is True:
			me.logger_with_rotating.debug(message)
		else:
			me.logger_without_rotating.debug(message)

	
	@staticmethod
	def info(message, rotating=True):
		me = Logger()
		if rotating is True:
			me.logger_with_rotating.info(message)
		else:
			me.logger_without_rotating.info(message)

	@staticmethod
	def warning(message, rotating=True):
		me = Logger()
		if rotating is True:
			me.logger_with_rotating.warning(message)
		else:
			me.logger_without_rotating.warning(message)

	@staticmethod
	def error(message, rotating=True):
		me = Logger()
		if rotating is True:
			me.logger_with_rotating.error(message)
		else:
			me.logger_without_rotating.error(message)

	@staticmethod
	def critical(message, rotating=True):
		me = Logger()
		if rotating is True:
			me.logger_with_rotating.critical(message)
		else:
			me.logger_without_rotating.critical(message)
	'''


level = logging.DEBUG
# level = logging.INFO
# level = logging.WARNING

LoggerWithRotate: logging.Logger = MyLogger(f'{__name__}.with.rotating', level, True)
Logger: logging.Logger = MyLogger(f'{__name__}.without.rotating', level, False)

if __name__ == "__main__":
	LoggerWithRotate.debug("debug")
	LoggerWithRotate.info("info")
	LoggerWithRotate.warning("warning")
	Logger.warning("warning without rotating")
	LoggerWithRotate.error("error")
	LoggerWithRotate.critical("critical")
	exit()
