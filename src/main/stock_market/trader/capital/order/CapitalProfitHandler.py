from src.lib.my_lib.module.LoggerModule import LoggerWithRotate, Logger
from src.main.stock_market.trader.abstract.ProfitHandleAbstract import ProfitHandleAbstract


class CapitalProfitHandler(ProfitHandleAbstract):
	# 一口(25元手續費 + 約10元稅) => 一點: 25/50 + 10/50
	# FEE = 0.5 + 0.2

	# 一口(25元手續費 + 12元稅 + 2點滑價) => 一點: 25/50 + 12/50  + 2/2
	FEE = 0.5 + 0.24 + 1

	def __init__(self, trader):
		self.trader = trader
		self.broker = trader.broker
		#
		self.lot = 0
		self.cost = 0
		self.profit = 0
		self.earn = 0  # profit - last_profit

	def on_open(self):
		self.lot += 1
		self.cost += self.FEE
		self.profit -= self.FEE
		self.show()

	def on_close(self, profit):
		self.lot += 1
		self.cost += self.FEE
		last_profit = self.profit
		self.profit -= self.FEE
		self.profit += profit
		self.earn = self.profit - last_profit
		self.show(True)

	def clear(self):
		self.lot = 0
		self.cost = 0
		self.profit = 0
		self.earn = 0
		self.show()

	def show(self, show_earn=False):
		log = f"lot:{self.lot} cost:{int(self.cost)} profit:{int(self.profit)}"
		if show_earn is True:
			log = f"lot:{self.lot} cost:{int(self.cost)} profit:{int(self.profit)} 【earn:{int(self.earn)}】"
		Logger.info(log)
		self.broker.write_to_broker_log(log)
