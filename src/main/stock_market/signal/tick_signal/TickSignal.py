from src.main.stock_market.signal.tick_signal.StockTick import StockTick


class TickSignal:
	def __init__(self, strategy, requestTicks_stockNos):
		self.strategy = strategy
		self.stockTicks = dict()
		for stockNo in requestTicks_stockNos:
			self.stockTicks[stockNo] = StockTick(stockNo, strategy)

	def before_upgrade_signal(self, tick):
		pass

	def upgrade_signal(self, tick):
		if tick['nSimulate'] == 1:
			return False
		self.before_upgrade_signal(tick)
		stockNo = tick['stockNo']
		self.stockTicks[stockNo].upgrade_signal(tick)
		self.after_upgrade_signal()

	def after_upgrade_signal(self):
		# super().after_upgrade_signal()
		self.strategy.monitor()
