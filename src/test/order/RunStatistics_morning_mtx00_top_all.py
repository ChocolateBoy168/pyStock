from src.lib.my_lib.module.LoggerModule import Logger
from src.main.AppConst import PeriodEnum, TradeMode
from src.main.api.ApiAiStock import ApiAiStock
from src.main.assets.AssetsHelper import AssetsHelper
from src.main.dto.ResponseWrapper import ResponseWrapper
from src.main.stock_market.Broker import Broker
from src.main.stock_market.trader.capital.CapitalStatisticsTrader import CapitalStatisticsTrader
import multiprocessing as mp


def run_statistics(period: PeriodEnum, date, trade_stockNo, strategy_source):
	result: ResponseWrapper = ApiAiStock.checkBrokerLogExist(
		period.value, trade_stockNo, date, TradeMode.STATISTICS.value, strategy_source
	)
	if result.success:
		data = result.data
		exist = data['exist']
		if exist is False:
			broker = Broker(period, date, trade_stockNo, strategy_source, CapitalStatisticsTrader)
			# broker.register_trader(CapitalStatisticsTrader(broker))
			Logger.info(f'\n========start [{broker.broker_log_file}]==========')
			# broker.run(False)
			broker.run(True)
			broker.release_memory()
			Logger.info(f'\n===over [{broker.broker_log_file}]===')
			del broker
		else:
			Logger.info(f'\n已存在: {period.value} {trade_stockNo} {date} {TradeMode.STATISTICS.value} {strategy_source}')
	else:
		Logger.error(f'\nserver error:{result.msg}')


def a_pool(args):
	Logger.info(f'\n{args}')
	# 	run_statistics(args[0], args[1], args[2], args[3])
	# run_statistics(**args)
	run_statistics(*args)


def run():
	# ------
	trade_stockNos = ['MTX00']
	# trade_stockNos = ['TX00']
	# trade_stockNos = ['MTX00', 'TX00']
	# ------
	periodEnums = [PeriodEnum.Morning]
	# periodEnums = [PeriodEnum.Night]
	# periodEnums = [PeriodEnum.Morning, PeriodEnum.Night]
	# ------

	# d = datetime.datetime.now().strftime("%Y%m%d")
	# d = DatetimeUtil.local_today_to_str(ft='%Y%m%d')
	# dates = ['20220124']
	dates = [AssetsHelper.find_last_final_date()]
	# dates = AssetsHelper.list_deal_date(True)

	''' 
		// 想法
		#. 整體停利99 優於 整體停利49
		#. 表示進場次數 越少越好  
		#. 無fomSumV
			- 進場時通常是火車頭, 但也容易遇到假的火車頭 
			- 停利999 優於 有fomSumV停利999 => 所以停利太大有formSumV會表現不好
			- 想走長線 => 停利得變大 => 似乎得拋開 fomSumV (會受限,因為大咖可能報隔日倉,而影響到基準)
			- 波長放越長(走長線,ex:aa_slope_90_60_30_10_5) : 停損停利也要跟著放大 ,
			- 波長放越短(走短線,ex:aa_slope_60) : 停損停利也要跟著縮小 ,    
		#  有fomSum條件後 
			- 進場時通常是火車中端 , 就不易改變方向, 所以無限停利話 反而遇到 很快到站後已偷偷轉方向開 
			- 似乎 a2 > b2 , 無fomSum條件後 似乎 a2 < b2 ,  表示有fomSum後 表示達到乖離率過大 導致 master_unit 下降 , 再想master_unit早夜盤要不同值
			- aa_slope_6030 在 有 fomSumV 下表現會好一些
		# 開盤的 一分鐘可能有大行情 , 但怕追到 人家市價的最極點, 所以需延遲幾秒再進場
		
		// todo
		# 先刪掉瘦身 再通通避開前30秒 重新跑
		# 開盤差一秒的弱差
		  
	'''

	morning_strategy_sources = [
		'StraBvm[root(multi_b1)]        [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_90_60_30_10_5_out_60)][containNight(true)]',
		'StraBvm[root(multi_b8)]        [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_90_60_30_10_5_out_60)][containNight(true)]',
		# ---------
		'StraBvm[root(multi_b2)]        [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',
		'StraBvm[root(multi_b5)]        [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',
		'StraBvm[root(multi_b6)]        [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',
		'StraBvm[root(multi_b6)]        [bvm(aa_noBlock_1)][fomSumV(aa_2)][fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',
		'StraBvm[root(multi_b6)]        [bvm(aa_noBlock_1)][fomSumV(aa_3)][fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',
		'StraBvm[root(multi_b10)]       [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',
		# ============

	]


	night_strategy_sources = []

	# ------
	argsAry = []
	for trade_stockNo in trade_stockNos:
		for periodEnum in periodEnums:
			for date in dates:
				strategy_sources = []
				if periodEnum is PeriodEnum.Morning:
					strategy_sources = morning_strategy_sources
				elif periodEnum is PeriodEnum.Night:
					strategy_sources = night_strategy_sources
				for strategy_source in strategy_sources:
					# run_statistics(
					# 	periodEnum, date, trade_stockNo, strategy_source
					# )
					# ----use fun(**args)----
					# argsAry.append({
					# 	'period': periodEnum,
					# 	'date': date,
					# 	'trade_stockNo': trade_stockNo,
					# 	'strategy_source': strategy_source
					# })
					# ----use fun(*args)----
					argsAry.append(
						(periodEnum, date, trade_stockNo, strategy_source)
					)
	#
	pool = mp.Pool(processes=2)
	pool.map(a_pool, argsAry)
	pool.close()
	exit()


# ==================


# for bever dam strategy
if __name__ == '__main__':
	run()
	exit()


''' fail history
# ---------
'StraBvm[root(multi_b6_ignoreFirstTick)]        [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',
'StraBvm[root(multi_b6_fast1)]  [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',
'StraBvm[root(multi_b6_fast2)]  [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',
'StraBvm[root(multi_b6_fast3)]  [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',
# ---------
'StraBvm[root(multi_a2)]        [bvm(aa_noBlock_1)][fomSumV(aa_1)][fomKma(aa_slope_in_60_20_10_5_out_60)][foiKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',
'StraBvm[root(multi_a2_delay3s)][bvm(aa_noBlock_1)][fomSumV(aa_1)][fomKma(aa_slope_in_60_20_10_5_out_60)][foiKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',
# ---------
'StraBvm[root(multi_a2)]        [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][foiKma(aa_slope_in_10_5_out_10)][containNight(true)]',#new
'StraBvm[root(multi_a2_delay3s)][bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][foiKma(aa_slope_in_10_5_out_10)][containNight(true)]',#new
'StraBvm[root(multi_a2)]        [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][foiKma(aa_slope_in_20_10_5_out_20)][containNight(true)]',#new
'StraBvm[root(multi_a2_delay3s)][bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][foiKma(aa_slope_in_20_10_5_out_20)][containNight(true)]',#new
'StraBvm[root(multi_a5)]        [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][foiKma(aa_slope_in_10_5_out_10)][containNight(true)]',#new
'StraBvm[root(multi_a5_delay3s)][bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][foiKma(aa_slope_in_10_5_out_10)][containNight(true)]',#new
'StraBvm[root(multi_a5)]        [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][foiKma(aa_slope_in_20_10_5_out_20)][containNight(true)]',#new
'StraBvm[root(multi_a5_delay3s)][bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][foiKma(aa_slope_in_20_10_5_out_20)][containNight(true)]',#new
# ---------
'StraBvm[root(multi_a2)]        [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][foiKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',#new
'StraBvm[root(multi_a2_delay3s)][bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][foiKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',#new
# ---------
'StraBvm[root(multi_a5)]        [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][foiKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',#new
'StraBvm[root(multi_a5_delay3s)][bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][foiKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',#new
# ---------5 30 5 10
'StraBvm[root(multi_a5)][bvm(aa_noBlock_1)][fomSumV(aa_1)][fomKma(aa_slope_in_60_30_10_5_out_30)][containNight(true)]',
'StraBvm[root(multi_a5_delay3s)][bvm(aa_noBlock_1)][fomSumV(aa_1)][fomKma(aa_slope_in_60_30_10_5_out_30)][containNight(true)]',
# ---------3 27 4 11
'StraBvm[root(multi_a5)][bvm(aa_noBlock_1)][fomSumV(aa_1)][fomKma(aa_slope_60_30)][containNight(true)]',
'StraBvm[root(multi_a5_delay3s)][bvm(aa_noBlock_1)][fomSumV(aa_1)][fomKma(aa_slope_60_30)][containNight(true)]',
# ---------4 11 6 2
'StraBvm[root(multi_a5)][bvm(aa_noBlock_1)][fomSumV(aa_1)][fomKma(aa_slope_in_90_60_30_10_5_out_60)][containNight(true)]',
'StraBvm[root(multi_a5_delay3s)][bvm(aa_noBlock_1)][fomSumV(aa_1)][fomKma(aa_slope_in_90_60_30_10_5_out_60)][containNight(true)]',
# ---------
'StraBvm[root(multi_b1)][bvm(aa_noBlock_1)]               [fomKma(aa_slope_90)][containNight(true)]', #new
'StraBvm[root(multi_b1_delay3s)][bvm(aa_noBlock_1)]       [fomKma(aa_slope_90)][containNight(true)]', #new
# ---------
'StraBvm[root(multi_a2)]        [bvm(aa_noBlock_1)][fomSumV(aa_1)][fomKma(aa_slope_90_30)][containNight(true)]', # new
'StraBvm[root(multi_a2_delay3s)][bvm(aa_noBlock_1)][fomSumV(aa_1)][fomKma(aa_slope_90_30)][containNight(true)]', # new
# ---------
'StraBvm[root(multi_a5)]        [bvm(aa_noBlock_1)][fomSumV(aa_1)][fomKma(aa_slope_90_30)][containNight(true)]',  # new
'StraBvm[root(multi_a5_delay3s)][bvm(aa_noBlock_1)][fomSumV(aa_1)][fomKma(aa_slope_90_30)][containNight(true)]',  # new
# ---------
'StraBvm[root(multi_a2)]        [bvm(aa_noBlock_1)][fomSumV(aa_1)][fomKma(aa_slope_90_60)][containNight(true)]', # new
'StraBvm[root(multi_a2_delay3s)][bvm(aa_noBlock_1)][fomSumV(aa_1)][fomKma(aa_slope_90_60)][containNight(true)]', # new
# ---------
'StraBvm[root(multi_a5)]        [bvm(aa_noBlock_1)][fomSumV(aa_1)][fomKma(aa_slope_90_60)][containNight(true)]',  # new
'StraBvm[root(multi_a5_delay3s)][bvm(aa_noBlock_1)][fomSumV(aa_1)][fomKma(aa_slope_90_60)][containNight(true)]',  # new
# ---------
'StraBvm[root(multi_b1_1)]      [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_90_60_30_10_5_out_60)][containNight(true)]',# test
'StraBvm[root(multi_b1_1)]      [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',# test
'StraBvm[root(multi_b1_1)]      [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_20)][containNight(true)]',# test
# ---------
'StraBvm[root(multi_b1_2)]      [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_90_60_30_10_5_out_60)][containNight(true)]',# test
'StraBvm[root(multi_b1_2)]      [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',# test
'StraBvm[root(multi_b1_2)]      [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_20)][containNight(true)]',# test
# ---------
'StraBvm[root(multi_b1_3)]      [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_90_60_30_10_5_out_60)][containNight(true)]', # try
'StraBvm[root(multi_b1_4)]      [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_90_60_30_10_5_out_60)][containNight(true)]', # try
'StraBvm[root(multi_b1_3)]      [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',# try
'StraBvm[root(multi_b1_4)]      [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]',# try
# ---------
'StraBvm[root(multi_b1)]        [bvm(aa_noBlock_2)]       [fomKma(aa_slope_in_90_60_30_10_5_out_60)][containNight(true)]', # try
'StraBvm[root(multi_b1_5)]      [bvm(aa_noBlock_2)]       [fomKma(aa_slope_in_90_60_30_10_5_out_60)][containNight(true)]', # try
'StraBvm[root(multi_b2)]        [bvm(aa_noBlock_2)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]', # try
'StraBvm[root(multi_b1_5)]      [bvm(aa_noBlock_2)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]', # try
'StraBvm[root(multi_b5)]        [bvm(aa_noBlock_2)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]', # try
'StraBvm[root(multi_b1_5)]      [bvm(aa_noBlock_2)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]', # try
'''