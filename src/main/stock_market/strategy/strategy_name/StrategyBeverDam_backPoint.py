from src.lib.my_lib.module.LoggerModule import Logger
from src.main.AppConst import OpenPositionKind
from src.main.stock_market.Broker import Broker
from src.main.stock_market.strategy.strategy_name.StrategyBeverDam import StrategyBeverDam
from src.main.util.TickUtil import TickUtil


class StrategyBeverDam_backPoint(StrategyBeverDam):

	# backPoint = 0  # 有點像static 不可放這

	def __init__(self, broker: Broker, id, context):
		super().__init__(broker, id, context)
		self.backPoint = 0 # 回檔N點
		self.cacheBackEnterPrice = None  # 回檔N點後,等待進場的價格

	# def build(self):
	# 	result = super().build()
	# 	# self.backPoint = self.context['backPoint']
	# 	return result

	# overwrite
	def could_open_position(self):

		if self.cacheBackEnterPrice is None:
			# could, open_position_kind = super(StrategyBeverDam, self).could_open_position()
			could, open_position_kind = super().could_open_position()

			if could is True:
				# 建立回檔N點等待進場
				tradeCurrentTick = self.tradeStockTick.currentTick
				price = TickUtil.extract_int_price(tradeCurrentTick)
				backPrice = None

				if open_position_kind == OpenPositionKind.BUY_CALL:
					backPrice = price - self.backPoint
				elif open_position_kind == OpenPositionKind.BUY_PUT:
					backPrice = price + self.backPoint

				if backPrice is not None:
					self.cacheBackEnterPrice = open_position_kind, backPrice
					log = (
						f'\n先不要進場,建立回檔{self.backPoint}點,等待新進場點[{self.cacheBackEnterPrice}]'
					)
					Logger.info(f'{log}')
					self.broker.write_to_broker_log(log)
					could = False
				else:
					could = False

		else:  # cacheBackEnterPrice is not None
			could = False
			open_position_kind = self.cacheBackEnterPrice[0]
			backPrice = self.cacheBackEnterPrice[1]
			is_block, stop_blockDam_info = self.could_close_position_for_blockBeverDam(True)
			if is_block is True:
				# 等待回檔Ｎ點[cacheBackEnterPrice]進場, 若中途遇到beverDam的反向單,就不等待進場
				self.cacheBackEnterPrice = None
				log = (
					f'\n\t遇到blockDam而[取消回檔進場]'
					f'\n\t交易的Tick = {self.tradeStockTick.currentTick.values()}'
				)
				if self.is_beverDam_enable:
					log += f'\n\tstop_blockDam_info = {stop_blockDam_info}'
				Logger.info(f'{log}')
			else:
				tradeCurrentTick = self.tradeStockTick.currentTick
				tradeCurrentPrice = TickUtil.extract_int_price(tradeCurrentTick)
				if open_position_kind == OpenPositionKind.BUY_CALL:
					if tradeCurrentPrice <= backPrice:
						could = True
				elif open_position_kind == OpenPositionKind.BUY_PUT:
					if tradeCurrentPrice >= backPrice:
						could = True
				if could is True:
					log = (
						f'\n可以進場,回檔達標,建立新倉 [{self.cacheBackEnterPrice}]'
						f'\n\t交易的Tick = {self.tradeStockTick.currentTick.values()}'
					)
					Logger.info(f'{log}')
					self.broker.write_to_broker_log(log)
					self.cacheBackEnterPrice = None  # todo 留意 考量 是否真的委託成功
		return could, open_position_kind
