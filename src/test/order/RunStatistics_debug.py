
from src.lib.my_lib.module.LoggerModule import Logger
from src.main.AppConst import PeriodEnum
from src.main.assets.AssetsHelper import AssetsHelper
from src.main.stock_market.Broker import Broker
from src.main.stock_market.trader.capital.CapitalStatisticsTrader import CapitalStatisticsTrader


def run_statistics(period: PeriodEnum, date, trade_stockNo, strategy_source):
	broker = Broker(period, date, trade_stockNo, strategy_source, CapitalStatisticsTrader)
	# broker.register_trader(CapitalStatisticsTrader(broker))
	Logger.info(f'\n========start [{broker.broker_log_file}]==========')
	broker.run(False)
	# broker.run(True)
	broker.release_memory()
	Logger.info(f'\n===over [{broker.broker_log_file}]===')

def run():
	# ------
	trade_stockNos = ['MTX00']
	# trade_stockNos = ['TX00']
	# ------
	periodEnums = [PeriodEnum.Morning]
	# periodEnums = [PeriodEnum.Night]
	# ------

	# d = datetime.datetime.now().strftime("%Y%m%d")
	# d = DatetimeUtil.local_today_to_str(ft='%Y%m%d')
	# dates = ['20210625']
	dates = [AssetsHelper.find_last_final_date()]
	# dates = AssetsHelper.list_deal_date(True)

	# 之後可參數化 ex: StraBvm[Bvm(1,2,3...)][fomSumV(3,2,1...)]
	morning_strategy_sources = [
		#'StraBvm[root(multi_b6)]        [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]'
		'StraBvm[root(multi_a6_ignoreFirstTick)]        [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]'
	]

	night_strategy_sources = []

	# ------
	for trade_stockNo in trade_stockNos:
		for periodEnum in periodEnums:
			for date in dates:
				strategy_sources = []
				if periodEnum is PeriodEnum.Morning:
					strategy_sources = morning_strategy_sources
				elif periodEnum is PeriodEnum.Night:
					strategy_sources = night_strategy_sources
				for strategy_source in strategy_sources:
					run_statistics(
						periodEnum, date, trade_stockNo, strategy_source
					)
	exit()


# ==================


# for bever dam strategy
if __name__ == '__main__':
	run()
	exit()
