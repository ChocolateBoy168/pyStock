from src.main.stock_market.signal.tick_signal.KMA import KMA, KmaPrototypeEnum
from src.main.util.TickUtil import TickUtil


class StockTick:
	def __init__(self, stockNo, strategy):
		self.stockNo = stockNo
		from src.main.stock_market.strategy.strategy_name.StrategyTicks import StrategyTicks
		self.strategy: StrategyTicks = strategy
		self.currentTick = None
		self.ticks = []  # 紀錄tick,可以拿來驗證kma
		self.first_open_price = {
			"morning": None,
			"night": None
		}
		self.ignore_first_tick = { # 均線量價運算,忽略開盤第一個tick
			"morning": None,
			"night": None
		}
		# indexKma
		self.has_indexKma_setting = self.strategy.has_indexKma_setting_for_stockNo(stockNo)
		if self.has_indexKma_setting:
			self.indexKma = KMA(
				self,
				KmaPrototypeEnum.INDEX,
				# rateOfSecond : if 60s is mean 1 min k
				rate_of_second=self.strategy.obtain_indexKma_rate_of_second(),
				mas=self.strategy.list_indexKma_mas(stockNo)
			)
		# followMasterKma
		self.has_followMasterKma_setting = self.strategy.has_followMasterKma_setting_for_stockNo(stockNo)
		if self.has_followMasterKma_setting:
			self.followMasterKma = KMA(
				self,
				KmaPrototypeEnum.FOLLOW_MASTER,
				# rateOfSecond : if 60s is mean 1 min k
				rate_of_second=self.strategy.obtain_followMasterKma_rate_of_second(),
				mas=self.strategy.list_followMasterKma_mas(stockNo)
			)

		# ===[master]===
		from src.main.stock_market.helper.StrategyHelper import StrategyHelper
		self.master_unit = StrategyHelper.obtain_master_unit(self.strategy.context, self.stockNo)
		self.master_cost = 0
		self.master_volume = 0
		self.master_avg_close = 0
		# self.master_price_volume_records = []
		# master call
		self.master_call_cost = 0
		self.master_call_volume = 0
		self.master_call_avg_cost = 0
		# master put
		self.master_put_cost = 0
		self.master_put_volume = 0
		self.master_put_avg_cost = 0

		# ===[slave]===
		self.slave_unit = StrategyHelper.obtain_slave_unit(self.strategy.context, self.stockNo)
		self.slave_cost = 0
		self.slave_volume = 0
		self.slave_avg_close = 0
		# self.slave_price_volume_records = []
		# slave call
		self.slave_call_cost = 0
		self.slave_call_volume = 0
		self.slave_call_avg_cost = 0
		# slave put
		self.slave_put_cost = 0
		self.slave_put_volume = 0
		self.slave_put_avg_cost = 0

	def upgrade_signal(self, tick):
		self.currentTick = tick

		# step 記錄開盤價
		if self.first_open_price['morning'] is None:
			if TickUtil.is_morning_period_for_tick(tick):
				self.first_open_price['morning'] = TickUtil.extract_int_price(tick)
		if self.first_open_price['night'] is None:
			if TickUtil.is_night_period_for_tick(tick):
				self.first_open_price['night'] = TickUtil.extract_int_price(tick)

		# step 是否忽略, 存開盤第一個tick, 後續的均線運算就會忽略此tick
		if self.strategy.is_ignoreFirstTick_enable:
			if self.ignore_first_tick['morning'] is None:
				if TickUtil.is_morning_period_for_tick(tick):
					self.ignore_first_tick['morning'] = TickUtil.extract_int_nQty(tick)
					return
			if self.ignore_first_tick['night'] is None:
				if TickUtil.is_night_period_for_tick(tick):
					self.ignore_first_tick['night'] = TickUtil.extract_int_nQty(tick)
					return

		# step 存下tick 才能進行 後續的均線運算
		# df_ticks = df_ticks.append([tick], sort=True)
		self.ticks.append(tick)

		# step  先更新 主力 散戶的 量價值
		if TickUtil.is_addSubNQty_not_ambiguous(tick):
			# price = tick['nClose'] / 100
			'''
			OverflowError: integer division result too large for a float
			https://stackoverflow.com/questions/27946595/how-to-manage-division-of-huge-numbers-in-python
			'''
			# price = tick['nClose'] // 100
			price = TickUtil.extract_int_price(tick)

			addSubNQty = int(tick['addSubNQty'])
			if addSubNQty != 0:
				if abs(addSubNQty) >= self.master_unit:  # 主力
					# 是否 排除掉一早開盤的撮合大單
					# lTimehms = tick["lTimehms"]
					# if lTimehms == 84500:
					# 	if addSubNQty > 100:
					# 		return

					# master call
					if addSubNQty > 0:
						self.master_call_cost += addSubNQty * price
						self.master_call_volume += addSubNQty
						self.master_call_avg_cost = int(self.master_call_cost / self.master_call_volume)

					# master put
					elif addSubNQty < 0:
						self.master_put_cost += addSubNQty * price
						self.master_put_volume += addSubNQty
						self.master_put_avg_cost = int(self.master_put_cost / self.master_put_volume)

					# master
					self.master_cost += addSubNQty * price
					self.master_volume += addSubNQty
					self.master_avg_close = int(
						(self.master_call_cost + abs(self.master_put_cost))
						/ (self.master_call_volume + abs(self.master_put_volume))
					)
				# self.master_price_volume_records.append({
				# 	"price": price,
				# 	"volume": self.master_volume
				# })
				elif abs(addSubNQty) <= self.slave_unit:  # 散戶
					# slave call
					if addSubNQty > 0:
						self.slave_call_cost += addSubNQty * price
						self.slave_call_volume += addSubNQty
						self.slave_call_avg_cost = int(self.slave_call_cost / self.slave_call_volume)

					# slave put
					elif addSubNQty < 0:
						self.slave_put_cost += addSubNQty * price
						self.slave_put_volume += addSubNQty
						self.slave_put_avg_cost = int(self.slave_put_cost / self.slave_put_volume)

					# slave
					self.slave_cost += addSubNQty * price
					self.slave_volume += addSubNQty
					self.slave_avg_close = int(
						(self.slave_call_cost + abs(self.slave_put_cost))
						/ (self.slave_call_volume + abs(self.slave_put_volume))
					)
					# self.slave_price_volume_records.append({
					# 	"price": price,
					# 	"volume": self.slave_volume
					# })
					pass

		# step 再進行kma 的運算
		if self.has_indexKma_setting:
			self.indexKma.add_tick(tick)

		if self.has_followMasterKma_setting:
			self.followMasterKma.add_tick(tick)

	def obtain_ticks_size(self):
		return len(self.ticks)

	def obtain_ticks_for_last_limit(self, last_limit):
		# main_index = self.obtain_ticks_size()
		# min_index = 0
		# if main_index > last_limit:
		# 	min_index = main_index - last_limit
		# return self.df_ticks.iloc[min_index:main_index]

		# return self.df_ticks.tail(last_limit)
		# df = pd.DataFrame(
		# 	self.signal.ticks[-last_limit:],
		# 	columns=[
		# 		'stockNo', 'nPtr', 'lDate', 'lTimehms', 'lTimemillismicros', 'nBid', 'nAsk', 'nClose',
		# 		'nQty', 'nSimulate', 'addSubNQty'
		# 	]
		# )
		return self.ticks[-last_limit:]

	def info(self):
		title = f'{self.stockNo} ' if self.stockNo == 'TX00' else f'{self.stockNo}'
		info = f'{title} : ' \
			   f'[M({self.master_volume} {self.master_avg_close}) S({self.slave_volume} {self.slave_avg_close})] ' \
			   f'call[M({self.master_call_volume} {self.master_call_avg_cost}) S({self.slave_call_volume} {self.slave_call_avg_cost})] ' \
			   f'put[M({self.master_put_volume} {self.master_put_avg_cost}) S({self.slave_put_volume} {self.slave_put_avg_cost})] '
		return info
