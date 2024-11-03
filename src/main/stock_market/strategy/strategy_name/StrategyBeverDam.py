import numpy as np

from src.lib.my_lib import MyLib
from src.lib.my_lib.module.LoggerModule import Logger
from src.lib.my_lib.utils import ArrayUtil
from src.main.stock_market.Broker import Broker
from src.main.AppConst import *
from src.main.stock_market.strategy.strategy_name.StrategyTicks import StrategyTicks
from src.main.stock_market.trader.capital.order.ExtendCapitalRecord import ExtendCapitalRecord
from src.main.util.TickUtil import TickUtil

'''
dam 基本觸發條件
trigger_dam 可觸發下注用的  for 新倉
block_dam 阻塞的dam for 平倉

改由訂單中取得
# bet_dam 下注過 表示trigger_dam變成bet_dam for 新倉
# bet_dam not equal betDam  
# betDam : 有下注過的 bet+tick+cancel+block 混合型的資料結構
# runningBetDam

'''


class StrategyBeverDam(StrategyTicks):

	def __init__(self, broker: Broker, id, context):
		super().__init__(broker, id, context)
		self.stock_dams = dict()
		self.stock_trigger_dams = dict()
		self.stock_use_trigger_dam_for_could_open_position = None
		self.keyNo_mapping_stockTriggerDam = dict()

	def rest_variables(self):
		super().rest_variables()
		self.stock_dams = dict()
		self.stock_trigger_dams = dict()
		self.stock_use_trigger_dam_for_could_open_position = None
		self.keyNo_mapping_stockTriggerDam = dict()
		pass

	def build(self):
		result = super().build()
		# 順便init stock_dams and stock_trigger_dams
		for stockNo in self.broker.requestTicks_stockNos:
			self.stock_dams[stockNo] = self.context['bvm']['stockNo'][stockNo]['dams']
			for dam in self.stock_dams[stockNo]:
				if dam['trigger'] is True:
					if stockNo not in self.stock_trigger_dams:
						self.stock_trigger_dams[stockNo] = []
					self.stock_trigger_dams[stockNo].append(dam)
		return result

	def could_open_position_root_for_triggerBeverDam(self, could_open_position):
		if could_open_position is None:
			could_open_position = False
		open_position_kind = None
		stock_trigger_dam = None
		info = ''
		ary = []
		stockNos_achieve_of = self.context['bvm']['stockNos_achieve_of']['in']

		for stockNo in self.stock_trigger_dams:
			trigger_dams = self.stock_trigger_dams[stockNo]
			could = False
			kind = None
			use_trigger_dam = None
			for trigger_dam in trigger_dams:
				could = self.is_trigger_dam_match_ticks(stockNo, trigger_dam)
				if could is True:
					if self.obtain_block_dam_match_ticks(stockNo, trigger_dam) is True:
						could = False
				if could is True:
					kind = self.obtain_open_position_kind(trigger_dam)
					use_trigger_dam = trigger_dam
					info += f'\n\t{stockNo} = {trigger_dam}'
					break  # 跳離 each trigger_dam 這一層
			ary.append({
				'stockNo': stockNo,
				'could': could,
				'kind': kind,
				'use_trigger_dam': use_trigger_dam
			})
		if len(ary) == 0:
			pass
		elif len(ary) == 1:
			item = ary[0]
			could_open_position = item['could']
			open_position_kind = item['kind']
		else:
			def could_fn(item):
				return item['could']

			def compare_kind_fun(before, after):
				return before['kind'] == after['kind']

			if MyLib.all_compare_of(ary, compare_kind_fun):  # 需全部都做同一個方向
				open_position_kind = ary[0]['kind']
				if stockNos_achieve_of == 'anyOf':
					if MyLib.any_of(ary, could_fn):
						could_open_position = True
					info += f'\n\tany({[could_fn(item) for item in ary]}) = {could_open_position}'
				elif stockNos_achieve_of == 'allOf':
					if MyLib.all_of(ary, could_fn):
						could_open_position = True
					info += f'\n\tall({[could_fn(item) for item in ary]}) = {could_open_position}'

		if could_open_position:
			stock_trigger_dam = {}
			for item in ary:
				stock_trigger_dam[item['stockNo']] = item['use_trigger_dam']

		return could_open_position, open_position_kind, stock_trigger_dam, info

	def could_open_position(self):
		could, open_position_kind = super().could_open_position()

		useTriggerDam_info = ""
		followMasterSumVolume_info = ""
		avoidSlaveSumVolume_info = ""
		indexKmaBS_info = ""
		indexKmaSlope_info = ""
		followMasterKmaSlope_info = ""
		specificRange_info = ""

		if self.is_beverDam_enable:
			if could is None:
				could, open_position_kind, self.stock_use_trigger_dam_for_could_open_position, useTriggerDam_info = \
					self.could_open_position_root_for_triggerBeverDam(could)

		if self.is_specificRange_enable:
			if could is True:
				could, specificRange_info = \
					self.could_open_position_for_specificRange(could, open_position_kind)

		if self.is_followMasterSumVolume_enable:
			if could is True:
				could, followMasterSumVolume_info = \
					self.could_open_position_for_followMasterSumVolume(could, open_position_kind)

		if self.is_avoidSlaveSumVolume_enable:
			if could is True:
				could, avoidSlaveSumVolume_info = \
					self.could_open_position_for_avoidSlaveSumVolume(could, open_position_kind)

		if self.is_indexKmaBS_enable:
			if could is True:
				could, indexKmaBS_info = \
					self.could_open_position_for_indexKmaBS(could, open_position_kind)

		if self.is_indexKmaSlope_enable:
			if could is True:
				could, indexKmaSlope_info = \
					self.could_open_position_for_indexKmaSlope(could, open_position_kind)

		if self.is_followMasterKmaSlope_enable:
			if could is True:
				could, followMasterKmaSlope_info = \
					self.could_open_position_for_followMasterKmaSlope(could, open_position_kind)

		if could is True:  # write log
			log = (
				f'----------------------------------------'
				f'\n可能進場,建立新倉[{open_position_kind.value}]'
				f'\n交易的Tick = {self.tradeStockTick.currentTick.values()}'
			)

			if self.is_beverDam_enable:
				log += f'\nuseTriggerDam_info = {useTriggerDam_info}'

			if self.is_followMasterSumVolume_enable:
				log += f'\nfollowMasterSumVolume_info = {followMasterSumVolume_info}'

			if self.is_avoidSlaveSumVolume_enable:
				log += f'\navoidSlaveSumVolume_info = {avoidSlaveSumVolume_info}'

			if self.is_indexKmaBS_enable:
				log += f'\nindexKmaBS_info = {indexKmaBS_info}'

			if self.is_indexKmaSlope_enable:
				log += f'\nindexKmaSlope_info = {indexKmaSlope_info}'

			if self.is_followMasterKmaSlope_enable:
				log += f'\nfollowMasterKmaSlope_info = {followMasterKmaSlope_info}'

			if self.is_specificRange_enable:
				log += f'\nspecificRange_info = {specificRange_info}'

			Logger.info(f'{log}')
			self.broker.write_to_broker_log(log)

		return could, open_position_kind

	def could_close_position_for_blockBeverDam(self, could_close_position):
		info = ''
		rs = []
		stockNos_achieve_of = self.context['bvm']['stockNos_achieve_of']['out']

		for stockNo in self.stock_use_trigger_dam_for_could_open_position:
			use_trigger_dam = self.stock_use_trigger_dam_for_could_open_position[stockNo]
			match_block_dam = self.obtain_block_dam_match_ticks(stockNo, use_trigger_dam)
			info += f'\n\t{stockNo} = {match_block_dam}'
			if match_block_dam is not None:
				rs.append(True)
			else:
				rs.append(False)

		if stockNos_achieve_of == 'anyOf':
			could_close_position = any(rs)  # any([]) is False
			info += f'\n\tany({rs}) = {could_close_position}'
		elif stockNos_achieve_of == 'allOf':
			could_close_position = all(rs)  # all([]) is True
			info += f'\n\tall({rs}) = {could_close_position}'

		return could_close_position, info

	def could_close_position(self, open_record):
		could, close_position_kind = super().could_close_position(open_record)
		key_no = open_record.key_no

		# 2021/07/18  改取 當初進場open_position時 期望的價格.  這樣才能更貼近 統計Statistics的 進出場點.
		begin_price = TickUtil.extract_int_price(self.trader.orderHandler.keyNo_mapping_tradeStockTick[key_no])
		# 當出成交價格 . 因非同步 從委託成到成功的中間忽略多個tick, .
		finish_price = int(float(open_record.price))

		price = begin_price # 2021/07/18 目前採用這個
		# price = finish_price

		open_position_kind = None  # 當初進場是 Call or Put
		# 從trade_trigger_dam得知當初新倉是做多或做空 todo 暫時的,應該改成從交易紀錄 open_record 裡得知
		trade_trigger_dam = self.keyNo_mapping_stockTriggerDam[key_no][self.broker.trade_stockNo]  # 當初進場觸發的dam
		if trade_trigger_dam is not None:
			if self.is_do_call(trade_trigger_dam):
				open_position_kind = OpenPositionKind.BUY_CALL
			if self.is_do_put(trade_trigger_dam):
				open_position_kind = OpenPositionKind.BUY_PUT
		stop_loss_info = ""
		stop_profit_info = ""
		stop_blockDam_info = ""
		stop_followMaster_sumVolume_info = ""
		stop_avoidSlave_sumVolume_info = ""
		stop_indexKmaBS_info = ""
		stop_indexKmaSlope_info = ""
		stop_followMasterKmaSlope_info = ""
		if key_no is None:
			Logger.error('平倉的訂單KeyNo無值')
		else:
			diff = TickUtil.extract_int_price(self.tradeStockTick.currentTick) - price

			# step STOP_LOSS
			if could is False:
				stop_loss = int(self.context['stop_loss'])
				if open_position_kind == OpenPositionKind.BUY_CALL:
					if diff < 0:
						if abs(diff) >= stop_loss:
							could = True
							close_position_kind = ClosePositionKind.STOP_LOSS
							stop_loss_info = f'來自當初 期望價={begin_price} , 成交價={finish_price}'
				elif open_position_kind == OpenPositionKind.BUY_PUT:
					if diff > 0:
						if diff >= stop_loss:
							could = True
							close_position_kind = ClosePositionKind.STOP_LOSS
							stop_loss_info = f'來自當初 期望價={begin_price} , 成交價={finish_price}'

			# step STOP_PROFIT
			if could is False:
				stop_profit = int(self.context['stop_profit'])
				if open_position_kind == OpenPositionKind.BUY_CALL:
					if diff > 0:
						if diff >= stop_profit:
							could = True
							close_position_kind = ClosePositionKind.STOP_PROFIT
							stop_profit_info = f'來自當初 期望價={begin_price} , 成交價={finish_price}'
				elif open_position_kind == OpenPositionKind.BUY_PUT:
					if diff < 0:
						if abs(diff) >= stop_profit:
							could = True
							close_position_kind = ClosePositionKind.STOP_PROFIT
							stop_profit_info = f'來自當初 期望價={begin_price} , 成交價={finish_price}'

			# step STOP_BLOCK_DAM
			if self.is_beverDam_enable:
				if could is False:
					could, stop_blockDam_info = self.could_close_position_for_blockBeverDam(could)
					if could is True:
						close_position_kind = ClosePositionKind.STOP_BLOCK_DAM

			# step follow master
			if self.is_followMasterSumVolume_enable:
				if could is False:
					could, stop_followMaster_sumVolume_info = self.could_close_position_for_followMasterSumVolume(
						could, open_position_kind
					)
					if could is True:
						close_position_kind = ClosePositionKind.STOP_FOLLOW_MASTER_SUM_VOLUME

			# step avoid slave
			if self.is_avoidSlaveSumVolume_enable:
				if could is False:
					could, stop_avoidSlave_sumVolume_info = self.could_close_position_for_avoidSlaveSumVolume(
						could, open_position_kind
					)
					if could is True:
						close_position_kind = ClosePositionKind.STOP_AVOID_SLAVE_SUM_VOLUME

			# step stop for indexKmaBS
			if self.is_indexKmaBS_enable:
				if could is False:
					could, stop_indexKmaBS_info = self.could_close_position_for_indexKmaBS(
						could, open_position_kind
					)
					if could is True:
						close_position_kind = ClosePositionKind.STOP_INDEX_KMA

			# step stop for indexKmaSlope
			if self.is_indexKmaSlope_enable:
				if could is False:
					could, stop_indexKmaSlope_info = self.could_close_position_for_indexKmaSlope(
						could, open_position_kind
					)
					if could is True:
						close_position_kind = ClosePositionKind.STOP_INDEX_KMA

			# step stop for followMasterKmaSlope
			if self.is_followMasterKmaSlope_enable:
				if could is False:
					could, stop_followMasterKmaSlope_info = self.could_close_position_for_followMasterKmaSlope(
						could, open_position_kind
					)
					if could is True:
						close_position_kind = ClosePositionKind.STOP_FOLLOW_MASTER_KMA

			# step STOP_EXPIRED_TIME
			if could is False:
				if self.is_expired() is True:
					could = True
					close_position_kind = ClosePositionKind.STOP_EXPIRED_TIME

		if could is True:
			log = (
				f'\n平倉[{close_position_kind.value}]'
				f'\n交易的Tick = {self.tradeStockTick.currentTick.values()}'
			)

			if stop_loss_info :
				log += f'\nstop_loss_info : {stop_loss_info}'

			if stop_profit_info :
				log += f'\nstop_profit_info : {stop_profit_info}'

			if self.is_beverDam_enable:
				log += f'\nstop_blockDam_info = {stop_blockDam_info}'

			if self.is_followMasterSumVolume_enable:
				log += f'\nstop_followMaster_sumVolume_info = {stop_followMaster_sumVolume_info}'

			if self.is_avoidSlaveSumVolume_enable:
				log += f'\nstop_avoidSlave_sumVolume_info = {stop_avoidSlave_sumVolume_info}'

			if self.is_indexKmaBS_enable:
				log += f'\nstop_indexKmaBS_info = {stop_indexKmaBS_info}'

			if self.is_indexKmaSlope_enable:
				log += f'\nstop_indexKmaSlope_info = {stop_indexKmaSlope_info}'

			if self.is_followMasterKmaSlope_enable:
				log += f'\nstop_followMasterKmaSlope_info = {stop_followMasterKmaSlope_info}'

			Logger.info(f'{log}')
			self.broker.write_to_broker_log(log)

		return could, close_position_kind

	def open_position(self, kind: OpenPositionKind):
		message, code = super().open_position(kind)
		if code == 0:
			keyNo = message
			self.keyNo_mapping_stockTriggerDam[keyNo] = self.stock_use_trigger_dam_for_could_open_position
		# Logger.info(f'暫存{KeyNo} , {self.trigger_dam_for_bind_KeyNo_before_open_position}')
		Logger.info(f'keyNo={message} , code={code}')

	def close_position(self, close_position_kind: ClosePositionKind, open_order: ExtendCapitalRecord):
		message, code = super().close_position(close_position_kind, open_order)
		if code == 0:
			keyNo = message
		Logger.info(f'KeyNo={message} , code={code}')

	# ===============================

	def is_do_call(self, trigger_dam):
		trigger_dam_matches = trigger_dam['matches']
		return bool(np.greater(np.array(trigger_dam_matches), 0).all())

	def is_do_put(self, trigger_dam):
		trigger_dam_matches = trigger_dam['matches']
		return bool(np.less(np.array(trigger_dam_matches), 0).all())

	def find_dam(self, stockNo, dam_name):
		for stock_dam in self.stock_dams[stockNo]:
			if stock_dam['name'] == dam_name:
				return stock_dam
		return None

	def obtain_open_position_kind(self, trigger_dam):
		result = None
		# 目前針對trigger dam(not block_dam), 若matches元素 都>0 , 表示作多buy
		if self.is_do_call(trigger_dam) is True:
			result = OpenPositionKind.BUY_CALL
		elif self.is_do_put(trigger_dam) is True:
			result = OpenPositionKind.BUY_PUT
		return result

	# 符合賭塞的Dam
	def obtain_block_dam_match_ticks(self, stockNo, trigger_dam):
		open_position_kind = self.obtain_open_position_kind(trigger_dam)
		result = None
		for block_dam_name in trigger_dam['blocks']:
			block_dam = self.find_dam(stockNo, block_dam_name)
			match_block = self.is_block_dam_match_ticks(stockNo, block_dam, open_position_kind)
			if match_block is True:
				result = block_dam
				break
		return result

	def is_trigger_dam_match_ticks(self, stockNo, trigger_dam):
		open_position_kind = self.obtain_open_position_kind(trigger_dam)
		return self.is_dam_match_ticks(stockNo, open_position_kind, trigger_dam, DamKind.BET)

	# block_dam的open_position_kind表示當初建立新倉的kind
	def is_block_dam_match_ticks(self, stockNo, block_dam, open_position_kind: OpenPositionKind):
		return self.is_dam_match_ticks(stockNo, open_position_kind, block_dam, DamKind.BLOCK)

	def is_dam_match_ticks(self, stockNo, open_position_kind: OpenPositionKind, dam, dam_kind: DamKind):
		result = False
		ticks = self.signal.obtain_stockTick(stockNo).ticks
		matches = dam["matches"]
		max_frame_size = dam["max_frame_size"]
		reverse = False
		is_buy_call = (open_position_kind == OpenPositionKind.BUY_CALL)
		if is_buy_call:
			if dam_kind == DamKind.BET:
				reverse = True
			elif dam_kind == DamKind.BLOCK:
				reverse = False
		else:
			if dam_kind == DamKind.BET:
				reverse = False
			elif dam_kind == DamKind.BLOCK:
				reverse = True
		matches.sort(reverse=reverse)
		if len(ticks) >= max_frame_size:
			ts = ArrayUtil.tail(ticks, max_frame_size)
			# df = df[(~df["addSubNQty"].str.contains("#"))]
			ts = [t for t in ts if ('#' in str(t['addSubNQty'])) is False]
			addSubNQty_ary = [int(t['addSubNQty']) for t in ts]
			addSubNQty_ary.sort(reverse=reverse)
			if len(addSubNQty_ary) >= len(matches):
				frames = addSubNQty_ary[0:len(matches)]  # tail
				n_A = np.array(frames).astype(int)
				n_B = np.array(matches)
				if dam_kind == DamKind.BET:
					if is_buy_call:
						result = np.greater_equal(n_A, n_B).all()  # np._bool值
					else:
						result = np.less_equal(n_A, n_B).all()  # np._bool值
				elif dam_kind == DamKind.BLOCK:
					if is_buy_call:
						result = np.less_equal(n_A, n_B).all()  # np._bool值
					else:
						result = np.greater_equal(n_A, n_B).all()  # np._bool值
		return bool(result)  # 切記要轉bool(_bool值)  不然 _bool is True 會都是False
