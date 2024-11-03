from src.main.AppConst import TradeMode
from src.main.stock_market.helper.CrawlHelper import CrawlHelper
from src.main.stock_market.trader.capital.abstract.AbstractCapitalTrader import AbstractCapitalTrader
from src.main.stock_market.trader.capital.api.CscCore import CscCore
from src.main.stock_market.trader.capital.common.CapitalConst import CscApiEventKind


class CapitalCrawlTrader(AbstractCapitalTrader):

	def __init__(self, broker, api_account, api_pwd):
		super().__init__(broker)
		self.trade_mode = TradeMode.CRAWl
		self.csc_core = CscCore(
			self,
			api_account, api_pwd,
			[CscApiEventKind.QUOTE, CscApiEventKind.REPLY]
		)
		self.csc_api = None
		self.crawlHelper = CrawlHelper()


	def run(self):
		self.csc_core.sync_login()
		self.csc_core.quote_connect_enter_monitor()
