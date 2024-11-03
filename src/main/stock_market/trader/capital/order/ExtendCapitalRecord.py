from src.main.stock_market.trader.capital.order.CapitalRecord import CapitalRecord


class ExtendCapitalRecord(CapitalRecord):

	def __init__(self, capitalOrderHandler, btrUserID, bstrData):
		super().__init__(btrUserID, bstrData)
		self.capitalOrderHandler = capitalOrderHandler

		# trader = self.capitalOrderHandler.trader

		# 當初下單使用哪個策略
		# self.use_strategy = None
		# if trader.is_not_statistics_trade() is True:
		# 	self.use_strategy = capitalOrderHandler.keyNo_mapping_strategy[self.key_no]
		if self.key_no in capitalOrderHandler.keyNo_mapping_strategy:
			self.use_strategy = capitalOrderHandler.keyNo_mapping_strategy[self.key_no]
		else: # 表示過往的單
			self.use_strategy = None
			# todo 之後 若 app 異常終止後 重新啟動 所需處理未平倉的單 但該如何綁策略?
			pass

		# 平倉時關連到哪個委託序號 , 有值不代表真正的平倉 , 還得 藉由handler 中的 scan_closed_record 查出 此平倉單 是否 委託成功
		# 目前用在 新倉的record[record.buy_sell.startswith('BN', 0, 2) or record.buy_sell.startswith('SN', 0, 2)]
		self.close_position_ref_keyNo = None

	def to_json_string(self):
		json_str = f'{{"btrUserID":"{self.btrUserID}" , "bstrData":"{self.bstrData}"}}'
		return json_str