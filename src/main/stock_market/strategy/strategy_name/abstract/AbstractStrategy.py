from src.main.stock_market.signal.Signal import Signal


class AbstractStrategy:

	def __init__(self, broker, id, context):
		self.broker = broker
		self.trader = broker.trader
		self.log_path = None
		self.id = id
		self.context = context
		self.signal = Signal(self, broker.requestTicks_stockNos)

	def rest_variables(self):
		pass

	def monitor(self):
		pass

	# region === share method ===

	def build(self):
		return self

	# endregion === share method ===
	pass


'''
	self.acc_df = pd.DataFrame(data={
		'sMarketNo': [],
		'sStockIdx': [],
		'nPtr': [],
		'lDate': [],
		'lTimehms': [],
		'lTimemillismicros': [],
		'nBid': [],
		'nAsk': [],
		'nClose': [],
		'nQty': [],
		'nSimulate': [],
		'addSubNQty': []
	})

def add_record(self, record):
	self.records.append(record)
	self.acc_df = pd.DataFrame(data=self.records, columns=[
		'sMarketNo',
		'sStockIdx',
		'nPtr',
		'lDate',
		'lTimehms',
		'lTimemillismicros',
		'nBid',
		'nAsk',
		'nClose',
		'nQty',
		'nSimulate',
		'addSubNQty'
	], dtype={
		'sMarketNo': int,
		'sStockIdx': int,
		'nPtr': int,
		'lDate': int,
		'lTimehms': int,
		'lTimemillismicros': int,
		'nBid': int,
		'nAsk': int,
		'nClose': int,
		'nQty': int,
		'nSimulate': int,
		'addSubNQty': str
	})
'''
