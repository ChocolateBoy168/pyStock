from src.main.stock_market.trader.capital.abstract.AbstractCapitalTrader import AbstractCapitalTrader
from src.main.stock_market.trader.capital.api.CscSimulateApi import CscSimulateApi
from src.main.stock_market.trader.capital.common.CapitalConst import BuySell, NewClose
from src.main.stock_market.trader.capital.api.CscCore import CscCore, CscApiEventKind


class AbstractCapitalSimulateTrader(AbstractCapitalTrader):

	def __init__(self, broker, api_account, api_pwd):
		super().__init__(broker)
		self.csc_core = CscCore(
			self,
			api_account, api_pwd,
			[CscApiEventKind.QUOTE, CscApiEventKind.REPLY]
		)
		self.csc_api = CscSimulateApi(self)

	# todo 模擬
	def obtain_bank_account(self) -> str:
		result = "Simulate_Bank_Account"
		return result

	# todo 模擬
	def send_order(self, buy_sell: BuySell, open_close: NewClose, sTradeType, price, number, order_for_close_position):
		return self.csc_api.sendFutureOrder(
			self.obtain_bank_account(),
			self.broker.trade_stockNo,
			buy_sell,
			open_close,
			sTradeType,
			price,
			number,
			order_for_close_position
		)

	def run(self):
		self.csc_core.sync_login()
		self.csc_core.quote_connect_enter_monitor()
