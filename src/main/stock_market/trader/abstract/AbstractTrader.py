from src.main.AppConst import TradeMode


# 避開循環參考
# from src.main.stock_market.strategy.strategy_name.abstract.AbstractStrategy import AbstractStrategy


class AbstractTrader:

	def __init__(self, broker):
		from src.main.stock_market.Broker import Broker #避開循環參考
		self.broker: Broker = broker
		self.trade_mode = None
		self.ordering_status = False  # todo 之後可能各個策略上有自己的訂單狀態, [目前是共用一個訂單狀態 可能有問題]
		pass

	def release_memory(self):
		pass

	def open_position(self):
		pass

	def close_position(self):
		pass

	def on_order_reply(self):
		pass

	def change_trade_mode(mode: TradeMode):
		# todo if real to simulate : 考慮有單是否要平倉?
		# if simulate to real
		pass

	#  region ======== share method ========
	def is_real_trade(self):
		return self.trade_mode == TradeMode.REAL

	def is_simulate_real_trade(self):
		return self.trade_mode == TradeMode.SIMULATE_REAL

	def is_simulate_statistics_trade(self):
		return self.trade_mode == TradeMode.SIMULATE_STATISTICS

	def is_statistics_trade(self):
		return self.trade_mode == TradeMode.STATISTICS

	def is_crawl(self):
		return self.trade_mode == TradeMode.CRAWl

	def is_not_crawl(self):
		return self.trade_mode != TradeMode.CRAWl

	#  endregion ======== share method ========

	# def set_verify_output_path(self, path):
	# 	self.verify_output_path = path

	# def verify_output(self, data):
	# 	if self.verify_output_path is None:
	# 		raise MyLib.MyCustomError("verify_output_path is None")
	# 	print(data)
	# 	with open(self.verify_output_path, "w", encoding='utf8') as f:
	# 		f.write(data)
	# 		f.close()

	# def read_verify(self):
	# 	txt = ''
	# 	with open(self.verify_output_path, "r", encoding='utf8') as f:
	# 		txt = f.read()
	# 		f.close()
	# 	return txt
	pass
