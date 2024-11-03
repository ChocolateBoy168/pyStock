import importlib
import json
import os
import pathlib
import re

from src.lib.my_lib.module.LoggerModule import Logger
from src.main.AppConst import PeriodEnum
from src.main.stock_market.strategy.strategy_name.abstract.AbstractStrategy import AbstractStrategy

'''
	strategyId = strategyName(strategyParamConfigName)
	strategyFileName = strategyId.json
'''


class StrategyHelper:
	_instance = None

	def __new__(cls, *args, **kw):
		if not cls._instance:
			cls._instance = super(StrategyHelper, cls).__new__(cls, *args, **kw)
			cls._instance.__initialized = False
		return cls._instance

	def __init__(self):
		if self.__initialized:
			return
		self.__initialized = True

	@staticmethod
	def try_expand_request_ticks_stockNos(tradeStockNo, stra_ctxt):
		stockNos = [tradeStockNo]
		# extend extra signals
		if 'request_signal' in stra_ctxt:
			keys = list(stra_ctxt['request_signal']['stockNo'].keys())
			if tradeStockNo not in keys:
				raise RuntimeError(f'策略 {stra_ctxt} 沒有 trade stockNo {tradeStockNo} 的訊號設定')
			if stra_ctxt['request_multi_stockNo_ticks'] is True:
				for stockNo_signal in keys:
					if stockNo_signal not in stockNos:
						stockNos.append(stockNo_signal)
		return stockNos

	@staticmethod
	def tran_to_strategyClass(strategy_class_name: str):
		# m = sys.modules[__name__]
		# m = pathlib.Path(__file__).parent
		m = importlib.import_module(f'src.main.stock_market.strategy.strategy_name.{strategy_class_name}')
		c = getattr(m, strategy_class_name)
		return c

	@staticmethod
	def parse_strategy_source(period: PeriodEnum, strategy_source) -> AbstractStrategy:
		if strategy_source == None:
			return None
		me = StrategyHelper()
		strategyId = strategy_source
		# tokens = re.findall(r'([\w]+)', strategy_source)  #good way for start learn regx
		strategy_name_abbrev = re.findall(r'^([\w]+)', strategy_source)[0]
		if 'StraBvm' in strategy_name_abbrev:  # 目前用在 StrategyBeverDam and StrategyBeverDam_backPoint
			strategy_class_name = strategy_name_abbrev.replace('StraBvm', 'StrategyBeverDam')
			strategyClass = me.tran_to_strategyClass(strategy_class_name)
		else:
			raise RuntimeError(f'尚縮寫策略{strategy_name_abbrev}未定義')
		stra_seed_sources = strategy_source.split(strategy_name_abbrev)[1]
		# strategy_seeds = re.findall(r'[(.*\([\w]+\)\)]', strategy_seeds_source)
		stra_seed_ctxt_names = re.findall(r'\[(\w+\(\w+\))\]', stra_seed_sources)
		stra_ctxt = dict()
		for stra_seed_ctxt_name in stra_seed_ctxt_names:
			Logger.info(f'stra_seed_ctxt_name = {stra_seed_ctxt_name}')
			stra_seed_name = re.findall(r'(\w+)\(\w+\)', stra_seed_ctxt_name)[0]  # 取第一個()的值
			# 還原seed全名
			stra_seed_full_name = stra_seed_name \
				.replace('bvm', 'BeverDam') \
				.replace('aosSumV', 'AvoidSlaveSumVolume') \
				.replace('aosKma', 'AvoidSlaveKma') \
				.replace('fomSumV', 'FollowMasterSumVolume') \
				.replace('fomKma', 'FollowMasterKma') \
				.replace('foiKma', 'FollowIndexKma') \
				.replace('specRng', 'SpecificRange')

			stra_seed_path = os.path.join(pathlib.Path(__file__).parent.parent,
										  'strategy', 'strategy_seeds', period.value, stra_seed_ctxt_name + '.json')
			with open(stra_seed_path, 'r', encoding='utf-8') as reader:
				stra_seed_ctxt = json.loads(reader.read())
				if stra_seed_name == 'root':
					if True:  # verify
						if period == PeriodEnum.Morning:
							last_enter_time = stra_seed_ctxt['morning_last_enter_time']
							stop_expired_time = stra_seed_ctxt['morning_stop_expired_time']
						elif period == PeriodEnum.Night:
							last_enter_time = stra_seed_ctxt['night_last_enter_time']
							stop_expired_time = stra_seed_ctxt['night_stop_expired_time']
						if last_enter_time > stop_expired_time:
							raise RuntimeError(f'[最後進場時間]{last_enter_time}不能超過[逾時出場時間]{stop_expired_time}')
					stra_ctxt.update(stra_seed_ctxt)
				else:
					stra_ctxt[stra_seed_name] = stra_seed_ctxt

		return strategyId, stra_ctxt, strategyClass

	@staticmethod
	def obtain_master_unit(context, stockNo):
		return context['request_signal']['stockNo'][stockNo]['master_unit']

	@staticmethod
	def obtain_slave_unit(context, stockNo):
		return context['request_signal']['stockNo'][stockNo]['slave_unit']

	# todo 需換掉  改成用 strategy.context.contain_night , 避免每次tick進來都要再判斷 浪費時間
	@staticmethod
	def contain_night(context):
		if 'containNight' in context:
			return context['containNight']['active']
		return False

if __name__ == '__main__':
	helper = StrategyHelper()
	helper.parse_strategy_source(
		PeriodEnum.Morning,
		'StraBvm[root(multi_1)][bvm(aa_noBlock_1)][fomSumV(aa_1)][foiKma(aa_slope_1)][fomKma(aa_slope_1)]'
	)
	exit()
