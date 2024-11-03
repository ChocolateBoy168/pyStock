import json
import logging

import numpy as np


# https://blog.csdn.net/ztf312/article/details/88866335
class NpSupportEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, np.integer):
			return int(o)
		elif isinstance(o, np.floating):
			return float(o)
		elif isinstance(o, np.ndarray):
			return o.tolist()
		else:
			return super(NpSupportEncoder, self).default(o)


class JsonUtil:
	_instance = None

	def __new__(cls, *args, **kw):
		if not cls._instance:
			cls._instance = super(JsonUtil, cls).__new__(cls, *args, **kw)
			cls._instance.__initialized = False
		return cls._instance

	def __init__(self):
		if self.__initialized:
			return
		self.__initialized = True
		self.logger = logging.getLogger("JsonUtil")


	@staticmethod
	def to_json_str(any, ensure_ascii=False):
		return json.dumps(any, cls=NpSupportEncoder, ensure_ascii=ensure_ascii)
