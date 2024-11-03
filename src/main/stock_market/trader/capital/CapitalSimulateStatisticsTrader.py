from src.main.AppConst import TradeMode
from src.main.stock_market.trader.capital.abstract.AbstractCapitalSimulateTrader import AbstractCapitalSimulateTrader


class CapitalSimulateStatisticsTrader(AbstractCapitalSimulateTrader):

	def __init__(self, broker, api_account, api_pwd):
		super().__init__(broker, api_account, api_pwd)
		self.trade_mode = TradeMode.SIMULATE_STATISTICS
		self.cache_for_call_replayEvent_onNewData_callback = {}
