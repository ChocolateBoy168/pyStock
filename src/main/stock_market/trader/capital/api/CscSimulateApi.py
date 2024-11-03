import threading
import time

from src.lib.my_lib import MyLib
from src.main.stock_market.trader.capital.common.CapitalConst import BuySell, NewClose, Reserved, TradeType, DayTrade, \
	Logger
from src.main.stock_market.trader.capital.api.AbstractCscApi import AbstractCscApi


class CscSimulateApi(AbstractCscApi):

	def __init__(self, trader):
		from src.main.stock_market.trader.capital.abstract.AbstractCapitalTrader import AbstractCapitalTrader
		self.trader: AbstractCapitalTrader = trader
		self.broker = trader.broker

	def sendFutureOrder(
			self,
			bankAccount,
			stockNo,
			buy_sell: BuySell,
			open_close: NewClose,
			sTradeType,
			price,
			number,
			open_order=None
	):
		tick = self.broker.obtain_trade_stockTick_currentTick()
		custom_key_no = MyLib.random_str(12)  # 12碼
		message, m_nCode = custom_key_no, 0
		# Logger.info(f"After SendFutureOrder , KeyNo = {message} , m_nCode = {m_nCode}")  # 留意平倉的KeyNo如何對應到新倉的KeyNo

		trader = self.trader
		# 適合模擬無交易時段 history (ticks是爆大量的收到,須採用sync)
		if trader.is_statistics_trade() or trader.is_simulate_statistics_trade():
			'''
			# 跑統計時 試著模擬 async for invoke SKReplyLibEvent's OnNewData Event
			# 但比起main thread for回圈,很快就把ticks跑完 才回傳replay已晚,所以只好不用async
			self.SKReplyLibEvent_OnNewData_callback(
				buy_sell, open_close, tick, custom_key_no, open_order
			)
			'''
			# 需盡量模仿跟時實際狀況跑的一樣, 不然會有其他問題
			# ex:算獲利找不到 close_position_ref_keyNo
			# ex:ExtendCapitalRecord 使用哪個策略
			# 只好先快取起來, 改在 StrategyTicks 得到 message, code 後再呼叫 SKReplyLibEvent_OnNewData_callback
			from src.main.stock_market.trader.capital.CapitalStatisticsTrader import CapitalStatisticsTrader
			trader: CapitalStatisticsTrader = self.trader
			trader.cache_for_call_replayEvent_onNewData_callback[custom_key_no] = {
				'buy_sell': buy_sell,
				'open_close': open_close,
				'tick': tick,
				'custom_key_no': custom_key_no,
				'open_order': open_order
			}
		elif trader.is_simulate_real_trade():  # 適合模擬當下交易時段 current (ticks是delay的收到,符合async )
			# Logger.debug(f'[tick 1] = {tick}')
			t = threading.Thread(
				target=self.SKReplyLibEvent_OnNewData_callback,
				args=[buy_sell, open_close, tick, custom_key_no, open_order]
			)
			t.start()
		return message, m_nCode

	def decreaseOrderBySeqNo(self):
		return None, -1

	def cancelOrderByStockNo(self):
		return None, -1

	def cancelOrderBySeqNo(self):
		return None, -1

	def SKReplyLibEvent_OnNewData_callback(
			self, buySell: BuySell, open_close: NewClose, tick, custom_key_no, open_order
	):
		if self.trader.is_simulate_real_trade():
			Logger.debug(f'current thread {threading.current_thread()} ')
			time.sleep(0.5)

		close = float(tick['nClose']) / 100
		stockNo = tick['stockNo']
		# slip = random.randint(-2, 2)  # 模擬滑價
		slip = 0
		if open_close == NewClose.Open:
			if buySell == BuySell.Buy:
				# 模擬新倉 做多委託
				data_str = "{},TF,N,N,9135,193524,BNI10,TW,{},,,{},,,,,,,,,1,0,1,20200312,09:11:53,,0,97,o,20200312,1010000083911,A,2834,,,,,,,,,,,,,," \
					.format(custom_key_no, stockNo, close)
				self.trader.skReplyLibEvents.OnNewData("Lxxxxxxxxx", data_str)
				# 模擬 市價成交
				data_str = "{},TF,D,N,9135,193524,BNI10,TW,{},,,{},,,,,,,,,1,0,1,20200312,09:11:53,,0,97,o,20200312,1010000083911,A,2834,,,,,,,,,,,,,," \
					.format(custom_key_no, stockNo, close + slip)
				self.trader.skReplyLibEvents.OnNewData("Lxxxxxxxxx", data_str)
			elif buySell == BuySell.Sell:
				# 模擬新倉 做空委託
				data_str = "{},TF,N,N,9135,193524,SNI10,TW,{},,,{},,,,,,,,,1,0,1,20200312,09:11:53,,0,97,o,20200312,1010000083911,A,2834,,,,,,,,,,,,,," \
					.format(custom_key_no, stockNo, close)
				self.trader.skReplyLibEvents.OnNewData("Lxxxxxxxxx", data_str)
				# 模擬 市價成交
				data_str = "{},TF,D,N,9135,193524,SNI10,TW,{},,,{},,,,,,,,,1,0,1,20200312,09:11:53,,0,97,o,20200312,1010000083911,A,2834,,,,,,,,,,,,,," \
					.format(custom_key_no, stockNo, close + slip)
				self.trader.skReplyLibEvents.OnNewData("Lxxxxxxxxx", data_str)
		elif open_close == NewClose.Close:
			# profit = random.randint(-20, 20)
			if open_order.buy_sell == 'BNI10':
				# 模擬 委託
				data_str = "{},TF,N,N,9135,193524,SOI10,TW,{},,,{},,,,,,,,,1,0,1,20200312,09:11:53,,0,97,o,20200312,1010000083911,A,2834,,,,,,,,,,,,,," \
					.format(custom_key_no, stockNo, close)
				self.trader.skReplyLibEvents.OnNewData("Lxxxxxxxxx", data_str)
				# 模擬 市價成交
				data_str = "{},TF,D,N,9135,193524,SOI10,TW,{},,,{},,,,,,,,,1,0,1,20200312,09:11:53,,0,97,o,20200312,1010000083911,A,2834,,,,,,,,,,,,,," \
					.format(custom_key_no, stockNo, close - slip)
				self.trader.skReplyLibEvents.OnNewData("Lxxxxxxxxx", data_str)
			elif open_order.buy_sell == 'SNI10':
				# 模擬 委託
				data_str = "{},TF,N,N,9135,193524,BOI10,TW,{},,,{},,,,,,,,,1,0,1,20200312,09:11:53,,0,97,o,20200312,1010000083911,A,2834,,,,,,,,,,,,,," \
					.format(custom_key_no, stockNo, close)
				self.trader.skReplyLibEvents.OnNewData("Lxxxxxxxxx", data_str)
				# 模擬 市價成交
				data_str = "{},TF,D,N,9135,193524,BOI10,TW,{},,,{},,,,,,,,,1,0,1,20200312,09:11:53,,0,97,o,20200312,1010000083911,A,2834,,,,,,,,,,,,,," \
					.format(custom_key_no, stockNo, close - slip)
				self.trader.skReplyLibEvents.OnNewData("Lxxxxxxxxx", data_str)

		if self.trader.is_simulate_real_trade():
			Logger.debug(
				f'[此時 會交易stockNo 的tick ]{self.broker.obtain_trade_stockTick_currentTick().values()}')
		pass


if __name__ == '__main__':
	# 期貨 新倉
	buy_sell = 'BNI10'  # 新倉做多
	buy_sell = 'SNI10'  # 新倉做空
	buy_sell = 'SOI10'  # 平倉多單
	buy_sell = 'BOI10'  # 平倉空單

	# 選擇權
	buy_sell = 'BAR20'  # 新倉做多
	buy_sell = 'SOR20'  # 平倉多單

	# buy_sell.startswith('BN', 0, 2)
	pass
