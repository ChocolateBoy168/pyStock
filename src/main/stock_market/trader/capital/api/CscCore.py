from src.lib.my_lib.module.LoggerModule import Logger
from src.main.stock_market.trader.capital.common.CapitalConst import CscApiEventKind


class CscCore:

	def __init__(self, trader, api_account, api_pwd, reg_events: []):
		self.trader = trader
		self.broker = trader.broker
		self.api_account = api_account
		self.api_pwd = api_pwd
		# todo how to set dllPath = 'src/lib/capital_lib/capital_api_X.XX.XX/x64/SKCOM.dll'
		# dllPath = '../../../../../../src/lib/capital_lib/capital_api_2.13.23/x64/SKCOM.dll'
		# dllPath = '../../../../../../src/lib/capital_lib/capital_api_2.13.24/元件/x64/SKCOM.dll'
		# dllPath = '../../../../../../src/lib/capital_lib/capital_api_2.13.28/元件/x64/SKCOM.dll' # 【SK_ERROR_INITIALIZE_FAIL】【【Login Code: 999】】
		dllPath = '../../../../../../src/lib/capital_lib/capital_api_2.13.37/元件/x64/SKCOM.dll'
		import comtypes.client as cc
		cc.GetModule(dllPath)
		import comtypes.gen.SKCOMLib as sk
		self.skC = cc.CreateObject(sk.SKCenterLib, interface=sk.ISKCenterLib)
		self.skOOQ = cc.CreateObject(sk.SKOOQuoteLib, interface=sk.ISKOOQuoteLib)
		self.skO = cc.CreateObject(sk.SKOrderLib, interface=sk.ISKOrderLib)
		self.skOSQ = cc.CreateObject(sk.SKOSQuoteLib, interface=sk.ISKOSQuoteLib)
		self.skQ = cc.CreateObject(sk.SKQuoteLib, interface=sk.ISKQuoteLib)
		self.skR = cc.CreateObject(sk.SKReplyLib, interface=sk.ISKReplyLib)
		self.cc = cc
		self.sk = sk

		for event in reg_events:
			if event == CscApiEventKind.QUOTE:
				self.skQuoteLibEventHandler = cc.GetEvents(self.skQ, self.trader.skQuoteLibEvents)
			elif event == CscApiEventKind.REPLY:
				self.skReplyLibEventHandler = cc.GetEvents(self.skR, self.trader.skReplyLibEvents)
			elif event == CscApiEventKind.ORDER:
				self.skOrderLibEventHandler = cc.GetEvents(self.skO, self.trader.skOrderLibEvents)

		# [for quote events]===========
		self.idx_map = {}
		self.stock_map = {}

		# [for reply events]===========

		# [for order events]===========
		self.account_list = dict(
			stock=[],
			future=[],
			sea_future=[],
			foreign_stock=[],
		)
		self.userID = ""

		pass

	def get_return_code_message(self, nCode, strType, strMessage):
		nCodeMsg = self.skC.SKCenterLib_GetReturnCodeMessage(nCode)
		if (nCode != 0):
			strInfo = "【" + self.skC.SKCenterLib_GetLastLogInfo() + "】"
			result = f'【{strType}】【{strMessage}】【{nCodeMsg}】【{strInfo}】'
		else:
			result = f'【{strType}】【{strMessage}】【{nCodeMsg}】'
		return result

	def sync_login(self, verify_for_order=False):
		account = self.api_account
		pwd = self.api_pwd

		# for 抓ticks
		# 使用群益API不管要幹嘛你都要先登入才行
		m_nCode = self.skC.SKCenterLib_login(account, pwd)
		msg = self.get_return_code_message(m_nCode, "Login", "SKCenterLib_login")
		if (m_nCode != 0):
			Logger.error(msg)
		else:
			Logger.info(msg)

		if verify_for_order is True:  # for 下單
			if m_nCode == 0:
				try:
					nErrorCode = self.skR.SKReplyLib_ConnectByID(account)
					if nErrorCode != 0:
						return "ReplyLib失敗:{}".format(nErrorCode)

					# 下單初始化
					m_nCode = self.skO.SKOrderLib_Initialize()
					Logger.debug("Order {} SKOrderLib_Initialize".format(m_nCode))

					# 讀取憑證ID
					m_nCode = self.skO.ReadCertByID(account)
					Logger.debug("Order {} ReadCertByID".format(m_nCode))

					# 讀取帳戶
					m_nCode = self.skO.GetUserAccount()
					Logger.debug("Order {} GetUserAccount".format(m_nCode))

				except Exception as e:
					Logger.error(e)

	def quote_connect_enter_monitor(self):
		try:
			m_nCode = self.skQ.SKQuoteLib_EnterMonitor()
			msg = self.get_return_code_message(m_nCode, "Quote", "SKQuoteLib_EnterMonitor")
			if (m_nCode != 0):
				Logger.error(msg)
			else:
				Logger.info(msg)
		except Exception as e:
			Logger.error(e)

	def quote_disconnect_leave_monitor(self):
		try:
			m_nCode = self.skQ.SKQuoteLib_LeaveMonitor()
			msg = self.get_return_code_message(m_nCode, "Quote", "SKQuoteLib_LeaveMonitor")
			if (m_nCode != 0):
				Logger.error(msg)
			else:
				Logger.info(msg)
		except Exception as e:
			Logger.error(e)

	def quote_request_ticks(self, stockNo):
		try:
			# pn = 0  # todo 2222222
			pn = self.broker.requestTicks_stockNos.index(stockNo)  # 需再留意 for best5
			m_nCode = self.skQ.SKQuoteLib_RequestTicks(pn, stockNo)
			msg = self.get_return_code_message(m_nCode[1], "Quote", "SKQuoteLib_RequestTicks")
			if (m_nCode[1] != 0):
				Logger.error(msg)
			else:
				Logger.info(msg)
		except Exception as e:
			Logger.error(e)

	def get_stockno_by_stockidx(self, marker_no, stock_idx):
		if stock_idx not in self.idx_map:
			self.trader.skQuoteLibEvents.OnNotifyQuote(marker_no, stock_idx)
		return self.idx_map[stock_idx]['stock_no']

	def get_stockname_by_stockno(self, stock_no):
		if stock_no not in self.stock_map:
			return None
		return self.stock_map[stock_no]['stock_name']
