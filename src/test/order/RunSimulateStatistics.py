import datetime
import time

import pythoncom  # 使用pythoncom 需要 pip install pyiwin32

from src.lib.my_lib import MyLib
from src.lib.my_lib.module.LoggerModule import Logger
from src.main.AppConst import PeriodEnum
from src.main.stock_market.Broker import Broker
from src.main.stock_market.trader.capital.CapitalSimulateStatisticsTrader import CapitalSimulateStatisticsTrader
from src.main.util import ConfigUtil

if __name__ == '__main__':
	apiPath = MyLib.parse_arg('--api_path')
	api_account = ConfigUtil.obtain_val(apiPath, 'API', 'account')
	api_pwd = ConfigUtil.obtain_val(apiPath, 'API', 'password')

	date = datetime.datetime.now().strftime("%Y%m%d")

	periodEnum = PeriodEnum.Morning
	strategy_source = 'StraBvm[root(multi_b6)]        [bvm(aa_noBlock_1)]       [fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]'

	# periodEnum = PeriodEnum.Night
	# strategy_source = 'StraBvm[root(multi_1)][bvm(an_1)][fomSumV(aa_1)]'

	broker = Broker(periodEnum, date, "MTX00", strategy_source, CapitalSimulateStatisticsTrader, api_account, api_pwd)

	Logger.info(f'\n========start [{broker.broker_log_file}]==========')
	broker.run()

	# for csc api quote accept event todo why ?
	while True:
		time.sleep(1)
		pythoncom.PumpWaitingMessages()

	broker.release_memory()
	Logger.info(f'\n========over [{broker.broker_log_file}]==========')

	exit()
