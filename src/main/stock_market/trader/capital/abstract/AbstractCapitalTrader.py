from src.lib.my_lib.module.LoggerModule import Logger
from src.main.AppConst import OpenPositionKind, ClosePositionKind, TradeMode
from src.main.stock_market.trader.abstract.AbstractTrader import AbstractTrader
from src.main.stock_market.trader.capital.common.CapitalConst import NewClose, BuySell, TradeType
from src.main.stock_market.trader.capital.api.CscCore import CscCore
from src.main.stock_market.trader.capital.api.AbstractCscApi import AbstractCscApi
from src.main.stock_market.trader.capital.event.SKOrderLibEvents import SKOrderLibEvents
from src.main.stock_market.trader.capital.event.SKQuoteLibEvents import SKQuoteLibEvents
from src.main.stock_market.trader.capital.event.SKReplyLibEvents import SKReplyLibEvents
from src.main.stock_market.trader.capital.order.CapitalOrderHandler import CapitalOrderHandler
from src.main.stock_market.trader.capital.order.CapitalProfitHandler import CapitalProfitHandler
from src.main.stock_market.trader.capital.order.ExtendCapitalRecord import ExtendCapitalRecord
from src.main.util.TickUtil import TickUtil


class AbstractCapitalTrader(AbstractTrader):

	def __init__(self, broker):
		super().__init__(broker)

		# 為了跑統計也可以用到,就沒放進csc_core裡頭
		self.skQuoteLibEvents = SKQuoteLibEvents(self)
		self.skReplyLibEvents = SKReplyLibEvents(self)
		self.skOrderLibEvents = SKOrderLibEvents(self)

		self.csc_api: AbstractCscApi = None
		self.csc_core: CscCore = None
		self.orderHandler = CapitalOrderHandler(self)
		self.profitHandler = CapitalProfitHandler(self)

	def release_memory(self):
		del self.skQuoteLibEvents
		del self.skReplyLibEvents
		del self.skOrderLibEvents
		del self.csc_api
		del self.csc_core
		del self.orderHandler
		del self.profitHandler

	def obtain_bank_account(self) -> str:
		return None

	def open_position(self, kind: OpenPositionKind):
		if self.trade_mode == TradeMode.REAL:
			# 新倉 用 限價
			# sTradeType = TradeType.ROD
			# 新倉 後來也改用 市價  不然會跟不到大單 但相對的 滑價 會偏多 https://www.capital.com.tw/simulation/
			sTradeType = TradeType.IOC # 用IOC, price 要記得設 'M'
		else:
			sTradeType = TradeType.ROD # 回測只能用ROD

		tradeTick = self.broker.obtain_trade_stockTick_currentTick()
		price = TickUtil.extract_int_price(tradeTick)
		buy_sell = BuySell.Buy if kind == OpenPositionKind.BUY_CALL else BuySell.Sell
		Logger.info(f'\n 進場點 = {price}')
		if sTradeType == TradeType.IOC:
			slidePrice = 'M'
			Logger.info(f'\n 市價進場')
		else:
			slide = 5
			slidePrice = (price + slide) if kind == OpenPositionKind.BUY_CALL else (price - slide)
			Logger.info(f'\n 滑價{slide}點, 進場價 = {slidePrice}')
			if slidePrice < 0:
				raise RuntimeError(f'進場滑價後是負的 {slidePrice}')
		if price > 0:
			if self.trade_mode == TradeMode.REAL:
				return self.send_order(buy_sell, NewClose.Auto, sTradeType, slidePrice, 1, None)  # 自動 進場
			else:
				return self.send_order(buy_sell, NewClose.Open, sTradeType, slidePrice, 1, None)  # 新倉 進場
		else:
			error = f'kind={kind}, 價格是負的{price}'
			Logger.error(error)
			raise RuntimeError(error)

	def close_position(self, close_position_kind: ClosePositionKind, open_order):
		# 平倉 用 市價
		sTradeType = TradeType.IOC
		if open_order.buy_sell.startswith('BN', 0, 2):  # 當初買進建立新倉
			if self.trade_mode == TradeMode.REAL:
				return self.send_order(BuySell.Sell, NewClose.Auto, sTradeType, 'M', 1,
									   open_order)  # 自動賣出 出場 , todo 觀察 看是否能修正此偶爾發生此問題=> 勾選平倉而留倉部位不足,退單! code=999
			else:
				return self.send_order(BuySell.Sell, NewClose.Close, sTradeType, 'M', 1, open_order)  # 平倉賣出 出場

		elif open_order.buy_sell.startswith('SN', 0, 2):  # 當建賣出立初新倉
			if self.trade_mode == TradeMode.REAL:
				return self.send_order(BuySell.Buy, NewClose.Auto, sTradeType, 'M', 1,
									   open_order)  # 自動買進 出場, 看是否能修正此偶爾發生此問題=> 勾選平倉而留倉部位不足,退單! code=999
			else:
				return self.send_order(BuySell.Buy, NewClose.Close, sTradeType, 'M', 1, open_order)  # 平倉買進 出場

	def send_order(self):
		pass

	def on_order_reply(self, record: ExtendCapitalRecord):
		# 目前只針對期貨
		if record.is_TF_market_type():  # 因為可能接受來其他軟體的下單
			if record.is_cancel_type():
				self.ordering_status = False
			elif record.is_deal_type():
				if record.buy_sell.startswith('BN', 0, 2):  # 做多的新倉
					self.profitHandler.on_open()
					self.ordering_status = False
				elif record.buy_sell.startswith('SN', 0, 2):  # 做空的新倉
					self.profitHandler.on_open()
					self.ordering_status = False
				elif record.buy_sell.startswith('SO', 0, 2):  # 做多的平倉
					'''
					# 先找出被平倉的單
					order_no = list(order_handle.open_orders.keys())[0]
					open_order = order_handle.open_orders[order_no]
					if 'B' not in open_order['BuySell']:
						raise RuntimeError('cant close order')
					assert data['Qty'] == open_order['Qty'], "平倉數量必須相等"
					# 算出獲利
					profit = (float(data['Price']) - float(open_order['Price'])) * int(data['Qty'])
					self.profit_handle.on_close(profit)
					order_handle.close_order(data, open_order)
					'''
					# 先找出被平倉的單(也是當初建立新倉的單)
					opened_record = self.orderHandler.find_deal_record_for_close_position_ref_keyNo(record.key_no)
					if opened_record == None:
						error = f'找不到當初新倉的單,平倉的單key_no={record.key_no}'
						Logger.error(error)
						raise RuntimeError(error)
					assert record.qty == opened_record.qty, "平倉數量必須相等"
					# 算出獲利
					profit = (float(record.price) - float(opened_record.price)) * int(record.qty)  # 先買後賣
					self.profitHandler.on_close(profit)
					self.ordering_status = False
				elif record.buy_sell.startswith('BO', 0, 2):  # 做空的平倉
					'''
					# 先找出被平倉的單
					order_no = list(order_handle.open_orders.keys())[0]
					open_order = order_handle.open_orders[order_no]
					if 'S' not in open_order['BuySell']:
						raise RuntimeError('cant close order')
					assert data['Qty'] == open_order['Qty'], "平倉數量必須相等"
					# 算出獲利
					profit = (float(open_order['Price']) - float(data['Price'])) * int(data['Qty'])
					self.profit_handle.on_close(profit)
					self.ordering_status = False
					order_handle.close_order(data, open_order)
					'''
					opened_record = self.orderHandler.find_deal_record_for_close_position_ref_keyNo(record.key_no)
					if opened_record == None:
						error = f'找不到當初新倉的單,平倉的單key_no={record.key_no}'
						Logger.error(error)
						raise RuntimeError(error)
					assert record.qty == opened_record.qty, "平倉數量必須相等"
					# 算出獲利
					profit = (float(opened_record.price) - float(record.price)) * int(record.qty)  # 先賣後買
					self.profitHandler.on_close(profit)
					self.ordering_status = False
