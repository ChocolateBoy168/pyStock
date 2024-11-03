# import json
from src.lib.my_lib.module.LoggerModule import Logger
from src.main.stock_market.trader.abstract.AbstractOrderHandler import AbstractOrderHandler
from src.main.stock_market.trader.capital.order.ExtendCapitalRecord import ExtendCapitalRecord


class CapitalOrderHandler(AbstractOrderHandler):
	# 一口(25元手續費 + 約10元稅) => 一點: 25/50 + 10/50
	FEE = 0.5 + 0.2

	'''
	# keyNo_mapping_records			=> {keyNo : [委託record ,成交record]}
	# keyNo_mapping_strategy		=> {keyNo : which策略}
	# keyNo_mapping_tradeStockTick	=> {keyNo : 當初tick} // 紀錄當初Judge進場時的價格(tick裡), 之後為了 stop_profit or stop_loss 用的,
															盡可能與模擬的(Statistics) 數據一致 , 否則模擬的已停利,真實的未停利.
	'''
	def __init__(self, trader):
		super().__init__(trader)
		self.use_market_type = 'TF'
		self.keyNo_mapping_records = {}  # 收到的期貨單(委託,成交之類的records)
		self.keyNo_mapping_strategy = {}
		self.keyNo_mapping_tradeStockTick = {}

	# ====[create]====

	def tranTo_verify_record(self, btrUserID, bstrData):
		record = ExtendCapitalRecord(self, btrUserID, bstrData)
		if record.use_strategy is None:  # 如果此record未綁定策略表示過時的單
			if self.trader.is_real_trade():
				# 20210601 第二次 用市價委託 ,卻傳回 委託失敗 , bstrData無key_no值, 這樣難以知道當初的委託序號, 可能是群益的bug 需觀察
				log = (f'策略過往單 或 非策略手動單 或 委託失敗(需觀察): {record.to_json_string()}')
				Logger.info(f'{log}')
				self.trader.broker.write_to_broker_log(log)
			return None
		else:
			if self.trader.is_real_trade():
				log = (f'新的 record : {record.to_json_string()}')
				Logger.info(f'{log}')
				self.trader.broker.write_to_broker_log(log)

			self.records_log.append(record)
			# upgrade keyNo_mapping_records
			if record.key_no not in self.keyNo_mapping_records:
				self.keyNo_mapping_records[record.key_no] = []
			if (record.market_type == self.use_market_type) and (record.order_err == 'N'):  # N is 正常
				self.keyNo_mapping_records[record.key_no].append(record)  # 委託正常 或 成交正常 都會放進來
			if self.trader.is_real_trade():
				log = (f'目前 keyNo [{record.key_no}] 有 {len(self.keyNo_mapping_records[record.key_no])} 筆 record')
				Logger.info(f'{log}')
				self.trader.broker.write_to_broker_log(log)
			return record

	# ====[query by condition]====

	# 期貨key_no清單
	def list_all_keyNos(self):
		return self.keyNo_mapping_records.keys()

	# 某keyNo 的 期貨records
	def list_records_for_keyNo(self, key_no):
		return self.keyNo_mapping_records[key_no]

	# 期貨 all records
	def list_all_records(self):
		result = []
		keynNos = self.list_all_keyNos()
		for keynNo in keynNos:
			records = self.keyNo_mapping_records[keynNo]
			for record in records:
				result.append(record)
		return result

	def list_deal_records(self):
		result = []
		records = self.list_all_records()
		for record in records:
			r: ExtendCapitalRecord = record
			if r.type == 'D':
				result.append(record)
		return result

	# 某策略 的 期貨records
	def list_records_for_strategy(self, strategy_id):
		result = []
		records = self.list_all_records()
		for record in records:
			r: ExtendCapitalRecord = record
			if r.use_strategy is not None:
				if r.use_strategy == strategy_id:
					result.append(r)
		return result

	# 某策略 的 期貨key_no清單
	def list_keyNos_for_strategy(self, strategy_id):
		result = []
		records = self.list_records_for_strategy(strategy_id)
		for record in records:
			r: ExtendCapitalRecord = record
			if r.key_no not in result:
				result.append(r.key_no)
		return result

	# 某策略 的 [委託有成功]且[未平倉]期貨record
	def list_opened_records(self, strategy_id):
		result = []
		keyNos = self.list_keyNos_for_strategy(strategy_id)
		for keyNo in keyNos:
			is_opened, opened_record_if_opened = self.find_deal_record_for_opened(keyNo)
			if is_opened is True:
				result.append(opened_record_if_opened)
		return result

	# [委託有成交]且[新倉]且[未平倉] todo (需實測才知道)  委託種類尚有 C:取消 U:改量 P:改價 (改價含證券逐筆) B:改價改量  S:動態退單
	def find_deal_record_for_opened(self, key_no):
		records = self.list_records_for_keyNo(key_no)
		is_opened = False
		opened_record_if_opened = None
		# 因非同步,事件有時成交會比委託先到
		for record in records:
			if record.type == 'N':  # 委託種類:委託
				pass
			if record.type == 'D':  # 委託種類:成交
				# 新倉買 or 新倉賣 todo [策略A的新倉買(order1) + 策略B的新倉賣(order2)] : 這樣 order2 收到的buy_sell 會是平倉嗎? => 目前只suppert一個策略跑
				if record.buy_sell.startswith('BN', 0, 2) or record.buy_sell.startswith('SN', 0, 2):
					if record.close_position_ref_keyNo is None:  # 表示未平倉
						is_opened = True
						opened_record_if_opened = record
					else:
						close_position_ref_keyNo = record.close_position_ref_keyNo
						# close_position_ref_keyNo 有值不代表真正的平倉 , 還得 藉由find_deal_record_for_closed 查出 此平倉單 委託是否 真的成交
						is_closed, closed_record_if_closed = self.find_deal_record_for_closed(
							close_position_ref_keyNo
						)
						if is_closed is False:
							is_opened = True
							opened_record_if_opened = record
		return is_opened, opened_record_if_opened

	#  [委託有成交]且[平倉] todo ,小心 需要實測才知道 [策略A的新倉買(order1) + 策略B的新倉賣(order2)] : 這樣 order2 收到的buy_sell 會是平倉嗎?
	def find_deal_record_for_closed(self, key_no):
		records = self.list_records_for_keyNo(key_no)
		is_closed = False
		closed_record_if_closed = None
		# 因非同步,事件有時成交會比委託先到
		for record in records:
			if record.type == 'N':  # 委託種類:委託
				pass
			if record.type == 'D':  # 委託種類:成交
				# 平倉買 or 平倉賣 todo [策略A的新倉買(order1) + 策略B的新倉賣(order2)] : 這樣 order2 收到的 buy_sell 會是平倉嗎?  => 目前只support一個策略跑
				if record.buy_sell.startswith('BO', 0, 2) or record.buy_sell.startswith('SO', 0, 2):
					is_closed = True
					closed_record_if_closed = record
		return is_closed, closed_record_if_closed

	def find_deal_record_for_close_position_ref_keyNo(self, close_position_ref_keyNo):
		records = self.list_deal_records()
		for record in records:
			r: ExtendCapitalRecord = record
			if r.close_position_ref_keyNo == close_position_ref_keyNo:
				return r
		return None


if __name__ == '__main__':
	l = ['a', 'b']
	if 'c' not in l:
		l.append('c')
	print(l)

'''
class CapitalOrderHandle(OrderHandleAbstract):
	def __init__(self, broker):
		super().__init__(broker)

	def clear_all(self):
		self.__init__()

	def append(self, order):
		self.orders[order['KeyNo']] = order

	def delete(self, order_no, orders=None):
		if orders is None:
			orders = self.orders
		orders.pop(order_no, None)
		return orders

	def close_order(self, order, open_order):
		self.close_orders[order['KeyNo']] = order
		self.open_orders = self.delete(open_order['KeyNo'], self.open_orders)
		self.finish_orders[open_order['KeyNo']] = {'open': open_order, 'close': order}

	def open_order(self, order):
		self.open_orders[order['KeyNo']] = order
		self.orders = self.delete(order['KeyNo'], self.orders)
'''
