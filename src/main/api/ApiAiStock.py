import json
import urllib
import requests
import src.main.app as app
from src.lib.my_lib import MyLib
from src.lib.my_lib.module.LoggerModule import Logger
from src.main.dto.MonthlyReportDto import MonthlyReportDto
from src.main.dto.ResponseWrapper import ResponseWrapper

'''
# 不適用於data是json的格式 
def _hook_to_response_wrapper(dct):
    resp = ResponseWrapper(dct['success'], dct['msg'], dct['data'])
    return resp
'''


def read_to_response_wrapper(r):
	# print("status:\n{}\nheaders:\n{}\nread:\n{}\n".format(r.status, r.getheaders(), r.read()))
	try:
		bytes = r.read()
		str = bytes.decode("utf-8")
		# dct = json.loads(str)
		# obj = json.loads(str, object_hook=_hook_to_response_wrapper)
		obj = json.loads(str)
		return ResponseWrapper(obj['success'], obj['msg'], obj['data'])
	except Exception as e:
		msg = "Exception 2 => {0}".format(e)
		Logger.error(msg)
		return ResponseWrapper(False, msg, None)
	pass


class ApiAiStock:
	_instance = None

	def __new__(cls, *args, **kw):
		if not cls._instance:
			cls._instance = super(ApiAiStock, cls).__new__(cls, *args, **kw)
			cls._instance.__initialized = False
		return cls._instance

	def __init__(self):
		if self.__initialized:
			return
		self.__initialized = True
		self.mac_addr = MyLib.sys_mac_addr()
		self.host = app.Api_Host
		self.port = app.Api_Port
		self.timeout = app.Api_Timeout

	@staticmethod
	def _path(restPath):
		me = ApiAiStock()
		return urllib.parse.urljoin(app.Api_ContextPath, restPath)

	@staticmethod
	def batchSaveOrUpdateFutDataPrice(batch_uid, data=None, async_fn=None):
		me = ApiAiStock()
		params = {
			'batchUid': batch_uid,
			'dataVersionName': 'SaveOrUpdateFutDataPrice_v1.0.0',
			'data': data
		}
		return MyLib.http_post(me.host, me.port,
							   me._path(app.Api_BatchSaveOrUpdateFutDataPrice),
							   params, read_to_response_wrapper, async_fn, timeout=me.timeout)

	@staticmethod
	def batchSaveOrUpdateFutContractsDate(batch_uid, data=None, async_fn=None):
		me = ApiAiStock()
		params = {
			'batchUid': batch_uid,
			'dataVersionName': 'SaveOrUpdateFutContractsDate_v1.0.0',
			'data': data
		}
		return MyLib.http_post(me.host, me.port,
							   me._path(app.Api_BatchSaveOrUpdateFutContractsDate),
							   params, read_to_response_wrapper, async_fn, timeout=me.timeout)

	@staticmethod
	def batchSaveOrUpdateStockReportSeasonality(batch_uid, data=None, async_fn=None):
		me = ApiAiStock()
		params = {
			'batchUid': batch_uid,
			'dataVersionName': 'v1.0.0',
			'data': data
		}
		return MyLib.http_post(me.host, me.port,
							   me._path(app.Api_BatchSaveOrUpdateStockReportSeasonality),
							   params, read_to_response_wrapper, async_fn, timeout=me.timeout)

	@staticmethod
	def batchSaveOrUpdateStockReportMonthly(batch_uid, data: [MonthlyReportDto] = None, async_fn=None):
		me = ApiAiStock()
		params = {
			'batchUid': batch_uid,
			'dataVersionName': 'v1.0.0',
			'data': data
		}
		return MyLib.http_post(me.host, me.port,
							   me._path(app.Api_BatchSaveOrUpdateStockReportMonthly),
							   params, read_to_response_wrapper, async_fn, timeout=me.timeout)

	@staticmethod
	def batchSaveOrUpdateStockReportDaily(batch_uid, data=None, async_fn=None):
		me = ApiAiStock()
		params = {
			'batchUid': batch_uid,
			'dataVersionName': 'v1.0.0',
			'data': data
		}
		return MyLib.http_post(me.host, me.port,
							   me._path(app.Api_BatchSaveOrUpdateStockReportDaily),
							   params, read_to_response_wrapper, async_fn, timeout=me.timeout)

	@staticmethod
	def listTopRevenueRecently(async_fn=None):
		me = ApiAiStock()
		params = {
			'minMonths': '3',
			'maxMonths': '12',
			'marketCat': '上市',
			'size': '50'
		}

		# 這目前只對json param , 之後須搭配  requests.post 混用 for form params
		'''
		return MyLib.http_post(me.host, me.port,
							  me._path(app.Api_ListTopRevenueRecently),
							  params, read_to_response_wrapper, async_fn, timeout=me.timeout)
		'''

		url = f'http://{me.host}:{me.port}{me._path(app.Api_ListTopRevenueRecently)}'
		r = requests.post(url, data=params)
		# Logger.info(f'\nlistTopRevenueRecently response => {r.text}')
		obj = json.loads(r.text)
		return ResponseWrapper(obj['success'], obj['msg'], obj['data'])

	@staticmethod
	def batchSaveOrUpdateBrokerLog(batch_uid, data=None, async_fn=None):
		me = ApiAiStock()
		params = {
			'batchUid': batch_uid,
			'dataVersionName': 'SaveOrUpdateBrokerLog_v1.0.0',
			'data': data
		}
		return MyLib.http_post(me.host, me.port,
							   me._path(app.Api_BatchSaveOrUpdateBrokerLog),
							   params, read_to_response_wrapper, async_fn, timeout=me.timeout)

	@staticmethod
	def checkBrokerLogExist(period, stock, date, trade, strategy, async_fn=None):
		me = ApiAiStock()
		params = {
			'period': period,
			'stock': stock,
			'date': date,
			'trade': trade,
			'strategy': strategy
		}

		# 這目前只對json param , 之後須搭配  requests.post 混用 for form params
		'''
		return MyLib.http_post(me.host, me.port,
							   me._path(app.Api_CheckBrokerLogExist),
							   params, read_to_response_wrapper, async_fn, timeout=me.timeout)
		'''
		url = f'http://{me.host}:{me.port}{me._path(app.Api_CheckBrokerLogExist)}'
		r = requests.post(url, data=params)
		Logger.info(f'\ncheckBrokerLogExist response => {r.text}')
		obj = json.loads(r.text)
		return ResponseWrapper(obj['success'], obj['msg'], obj['data'])
