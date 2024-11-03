from src.main.AppConst import TradeMode
from src.main.stock_market.trader.capital.abstract.AbstractCapitalTrader import AbstractCapitalTrader
from src.main.stock_market.trader.capital.api.CscSimulateApi import CscSimulateApi
from src.main.stock_market.trader.capital.common.CapitalConst import BuySell, NewClose


class CapitalStatisticsTrader(AbstractCapitalTrader):

	def __init__(self, broker):
		super().__init__(broker)
		self.trade_mode = TradeMode.STATISTICS
		self.csc_core = None
		self.csc_api = CscSimulateApi(self)
		self.cache_for_call_replayEvent_onNewData_callback = {}
		pass

	def obtain_bank_account(self) -> str:
		result = "Simulate_Bank_Account"
		return result


	def send_order(self, buy_sell: BuySell, open_close: NewClose,sTradeType, price, number, open_order=None):
		return self.csc_api.sendFutureOrder(
			self.obtain_bank_account(),
			self.broker.trade_stockNo,
			buy_sell,
			open_close,
			sTradeType,
			price,
			number,
			open_order
		)

	def run(self, ticks):
		for tick in ticks:
			self.broker.strategy.signal.upgrade_tickSignal(tick)
		# Logger.debug(f'upgrade_tickSignal :{tick}')
		# time.sleep(0.00000000000000000000000001) #tick停頓一下下, 刻意讓非同步thread, onNewData replay能早點run到
		pass
