from src.lib.my_lib.module.LoggerModule import Logger
from src.main.stock_market.trader.capital.common.CapitalConst import BuySell, NewClose, Reserved, TradeType, DayTrade
from src.main.stock_market.trader.capital.api.AbstractCscApi import AbstractCscApi


class CscRealApi(AbstractCscApi):

	def __init__(self, trader):
		self.trader = trader
		self.broker = trader.broker
		self.sk = self.trader.csc_core.sk
		self.skO = self.trader.csc_core.skO
		self.api_account = self.trader.csc_core.api_account
		self.api_async = False

	def sendFutureOrder(
			self,
			bankAccount,
			stockNo,
			buy_sell: BuySell,
			open_close: NewClose,
			sTradeType: TradeType,
			price,
			number
	):
		sReserved = Reserved.Not_Reserve
		sDayTrade = DayTrade.Not_Dang_Chong
		try:
			# 建立下單用的參數(FUTUREORDER)物件(下單時要填商品代號,買賣別,委託價,數量等等的一個物件)
			oOrder = self.sk.FUTUREORDER()

			# 填入完整帳號
			oOrder.bstrFullAccount = bankAccount
			# 填入期權代號
			oOrder.bstrStockNo = stockNo
			# 買賣別
			oOrder.sBuySell = buy_sell
			# 新倉 0 、平倉 1、自動 2
			oOrder.sNewClose = open_close
			# 盤中 0、T盤預約 1
			oOrder.sReserved = sReserved

			# ROD 0、IOC 1、FOK 2
			oOrder.sTradeType = sTradeType
			# 非當沖 0、當沖 1
			oOrder.sDayTrade = sDayTrade
			# 委託價，「M」表示市價，{移動停損、MIT皆無須價格}
			oOrder.bstrPrice = str(price)
			# 委託數量
			oOrder.nQty = int(number)

			log = (
				f"\n[Before SendFurtureOrder]:\n"
				f"bankAccount={oOrder.bstrFullAccount} "
				f"stockNo={oOrder.bstrStockNo} "
				f"bidAsk={oOrder.sBuySell} "
				f"sNewClose={oOrder.sNewClose} "
				f"sReserved={oOrder.sReserved} "
				f"sTradeType={oOrder.sTradeType} "
				f"sDayTrade={oOrder.sDayTrade} "
				f"bstrPrice={oOrder.bstrPrice} "
				f"nQty={oOrder.nQty}\n"
			)
			Logger.info(f'{log}')
			self.broker.write_to_broker_log(log)
			message, m_nCode = self.skO.SendFutureOrder(self.api_account, self.api_async, oOrder)
			log = (
				f"\n[After SendFurtureOrder]\n"
				f"message={message}\n"
				f"m_nCode={m_nCode}"
			)
			Logger.info(f'{log}')
			self.broker.write_to_broker_log(log)
			return message, m_nCode
		except Exception as e:
			Logger.error("SendFutureOrder : " + str(e))
			return None, -1

	def decreaseOrderBySeqNo(self, bankAccount, orderSeqNo, decreaseQty):
		try:
			message, m_nCode = self.skO.DecreaseOrderBySeqNo(
				self.api_account, self.api_async, bankAccount, orderSeqNo, int(decreaseQty)
			)
			Logger.info(f"After DecreaseOrderBySeqNo , message = {message} , m_nCode = {m_nCode}")
			return message, m_nCode
		except Exception as e:
			Logger.error("DecreaseOrderBySeqNo : " + str(e))
			return None, -1

	def cancelOrderByStockNo(self, bankAccount, stockNo):
		"""欲刪除的委託商品代號，空白則刪除所該帳號所屬登入ID之所有委託，請注意。"""
		try:
			if stockNo is None or stockNo == "":
				print("cancelOrderByStockNo stockNo is empty!!!!")
				return "fail", -1
			message, m_nCode = self.skO.CancelOrderByStockNo(
				self.api_account, self.api_async, bankAccount, stockNo
			)
			Logger.info(f"After CancelOrderByStockNo , message = {message} , m_nCode = {m_nCode}")
			return message, m_nCode
		except Exception as e:
			Logger.error("CancelOrderByStockNo : " + str(e))
		return None, -1

	def cancelOrderBySeqNo(self, bankAccount, orderSeqNo):
		try:
			if orderSeqNo is None or orderSeqNo == "":
				print("cancelOrderBySeqNo orderSeqNo is empty!!!!")
				return "fail", -1
			message, m_nCode = self.skO.CancelOrderBySeqNo(
				self.api_account, self.api_async, bankAccount, orderSeqNo
			)
			Logger.info(f"After CancelOrderBySeqNo , message = {message} , m_nCode = {m_nCode}")
			return message, m_nCode
		except Exception as e:
			Logger.error("CancelOrderBySeqNo : " + str(e))
		return None, -1

	def cancelAllOrder(self, bankAccount):
		"""欲刪除的委託商品代號，空白則刪除所該帳號所屬登入ID之所有委託，請注意。"""
		try:
			message, m_nCode = self.skO.CancelOrderByStockNo(self.api_account, self.api_async, bankAccount, "")
			Logger.info("cancelAllOrder message = " + message)
			return message, m_nCode
		except Exception as e:
			Logger.info("cancelAllOrder : " + str(e))
		return "fail", -1
