from src.lib.my_lib.module.LoggerModule import Logger


class SKReplyLibEvents:
	def __init__(self, trader):
		from src.main.stock_market.trader.capital.abstract.AbstractCapitalTrader import AbstractCapitalTrader
		self.trader: AbstractCapitalTrader = trader

	def OnConnect(self, btrUserID, nErrorCode):
		if nErrorCode == 0:
			strMsg = f"{nErrorCode}", btrUserID, "Connected!"
		else:
			strMsg = f"{nErrorCode}", btrUserID, "Connect Error!"
		Logger.debug(strMsg)

	def OnDisconnect(self, btrUserID, nErrorCode):
		if nErrorCode == 3002:
			strMsg = f"OnDisconnect , {btrUserID} 您已經斷線囉~~~"
		# exit()
		else:
			strMsg = f"{nErrorCode}", btrUserID
		Logger.debug(strMsg)

	def OnComplete(self, btrUserID):
		Logger.debug(btrUserID)

	def OnData(self, btrUserID, bstrData):
		cutData = bstrData.split(',')
		# print(cutData[0])
		# print(cutData[10])
		pass

	def OnNewData(self, btrUserID, bstrData):
		# 目前bstrData 規格是由47個欄位組成
		# if self.trader.is_real_trade():
		# 	Logger.info(f'{btrUserID},{bstrData}')
		size = len(bstrData.split(','))
		if size == 47:
			# if self.trader.is_real_trade():
			# 	Logger.info(f'正常由47個欄位組成')
			verifyRecord = self.trader.orderHandler.tranTo_verify_record(btrUserID, bstrData)
			if verifyRecord is not None:
				self.trader.on_order_reply(verifyRecord)
		else:
			Logger.warning(f'由{size}個欄位組成 => {bstrData}')

	# https://easontseng.blogspot.com/2019/07/api-21317-login-skwarningregisterreplyl.html
	def OnReplyMessage(self, bstrUserID, bstrMessage, sConfirmCode=0xFFFF):  # or sConfirmCode = -1
		# 根據API 手冊，login 前會先檢查這個 callback,
		# 要返回 VARIANT_TRUE 給 server,  表示看過公告了，我預設返回值是 0xFFFF
		Logger.info(f'OnReplyMessage: {bstrUserID},{bstrMessage}')
		return sConfirmCode

	def OnReplyClearMessage(self, bstrUserID):
		Logger.debug(bstrUserID)

	def OnSolaceReplyDisconnect(self, btrUserID, nErrorCode):
		if nErrorCode == 3002:
			strMsg = "OnSolaceReplyDisconnect SK_SUBJECT_CONNECTION_DISCONNECT"
		else:
			strMsg = nErrorCode

	def OnSmartData(self, btrUserID, bstrData):
		cutData = bstrData.split(',')

	def OnReplyClear(self, bstrMarket):
		strMsg = "Clear Market: " + bstrMarket
