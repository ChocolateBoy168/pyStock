from src.main.AppConst import TradeMode
from src.main.stock_market.trader.capital.abstract.AbstractCapitalTrader import AbstractCapitalTrader
from src.main.stock_market.trader.capital.api.CscRealApi import CscRealApi
from src.main.stock_market.trader.capital.common.CapitalConst import BuySell, NewClose
from src.main.stock_market.trader.capital.api.CscCore import CscCore, CscApiEventKind


class CapitalRealTrader(AbstractCapitalTrader):

	def __init__(self, broker, api_account, api_pwd):
		super().__init__(broker)
		self.trade_mode = TradeMode.REAL
		self.csc_core = CscCore(
			self,
			api_account, api_pwd,
			[CscApiEventKind.QUOTE, CscApiEventKind.ORDER, CscApiEventKind.REPLY]
		)
		self.csc_api = CscRealApi(self)

	def obtain_bank_account(self) -> str:
		result = self.csc_core.account_list['future'][0]
		return result

	def send_order(self, buy_sell: BuySell, open_close: NewClose, sTradeType, price, number, not_used=None):
		return self.csc_api.sendFutureOrder(
			self.obtain_bank_account(),
			self.broker.trade_stockNo,
			buy_sell,
			open_close,
			sTradeType,
			price,
			number
		)

	def run(self):
		self.csc_core.sync_login(True)
		self.csc_core.quote_connect_enter_monitor()
		# todo
		pass
