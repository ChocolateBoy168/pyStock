import configparser

from src.lib.my_lib.module.LoggerModule import Logger


def obtain_val(config_path, level1, level2):
	try:
		cp = configparser.ConfigParser()
		cp.read(config_path)
		return cp[level1][level2] if level2 in cp[level1] else None
	except Exception as e:
		Logger.error(e)
