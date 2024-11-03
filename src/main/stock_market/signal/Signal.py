from src.main.stock_market.signal.tick_signal.StockTick import StockTick
from src.main.stock_market.signal.tick_signal.TickSignal import TickSignal

'''
	目前訊號來源只有 ticks signal
	todo 之後 訊號來源 可擴增 大盤價量 , 三大法人價量 關係 , 美股盤勢 .....等  
'''


class Signal:
	def __init__(self, strategy, requestTicks_stockNos):
		self.strategy = strategy
		self.tickSignal = TickSignal(self.strategy, requestTicks_stockNos)
		self.longTermChipsSignal = None  # todo 訊號來自長期法人的籌碼與成本

	def obtain_stockTick(self, stockNo) -> StockTick:
		return self.tickSignal.stockTicks[stockNo]

	def upgrade_tickSignal(self, tick):
		self.tickSignal.upgrade_signal(tick)
