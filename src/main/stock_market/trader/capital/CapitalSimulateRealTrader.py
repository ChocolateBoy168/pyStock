from src.main.AppConst import TradeMode
from src.main.stock_market.trader.capital.abstract.AbstractCapitalSimulateTrader import AbstractCapitalSimulateTrader


class CapitalSimulateRealTrader(AbstractCapitalSimulateTrader):

	def __init__(self, broker, api_account, api_pwd):
		super().__init__(broker, api_account, api_pwd)
		self.trade_mode = TradeMode.SIMULATE_REAL
