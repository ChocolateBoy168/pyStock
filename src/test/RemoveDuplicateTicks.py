import numpy as np
import pandas as pd

from src.lib.my_lib import MyLib
from src.lib.my_lib.module.LoggerModule import Logger
from src.lib.my_lib.utils.PandaUtil import PandaUtil
from src.main.AppConst import PeriodEnum
from src.main.assets.AssetsHelper import AssetsHelper
from src.main.stock_market.helper.CrawlHelper import CrawlHelper


def get_sort_field(tick):
	return tick['lTimehms'], tick['lTimemillismicros']


# def run_now():
# 	# date = AssetsHelper.list_deal_date()[0]
# 	# date = datetime.datetime.now().strftime("%Y%m%d")
# 	# date = DatetimeUtil.local_today_to_str(ft='%Y%m%d')
# 	date = AssetsHelper.find_last_final_date()
# 	run(date)

def run(stockNo, date, period, start, end):
	# ------
	data_pth = AssetsHelper.gen_tick_history_path(period.value, stockNo, date)
	if data_pth is None or data_pth is None:
		Logger.warning(f'file {data_pth}  not find!')
	else:
		df = pd.read_csv(data_pth)
		ticks = PandaUtil.to_records_dict(df)
		correct_ticks = []

		# for tick in ticks:
		# 	exist = False
		# 	for tick2 in correct_ticks:
		# 		if tick['nPtr'] == tick2['nPtr']:
		# 			exist = True
		# 			break
		# 	if exist is False:
		# 		correct_ticks.append(tick)
		# for ptr in np.range(35748, 127933):

		def build_dict(ary, key):
			# return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(ary))
			return dict((d[key], d) for (index, d) in enumerate(ary))

		tick_dict = build_dict(ticks, 'nPtr')
		for nPtr in np.arange(start, end):
			# for tick in ticks:
			# 	if tick['nPtr'] == nPtr:
			# 		correct_ticks.append(tick)
			# 		break
			t = tick_dict.get(nPtr)
			if t is not None:
				correct_ticks.append(t)
			else:
				Logger.warning(f'tick is none when nPtr is {nPtr}')

		Logger.info(len(correct_ticks))
		if correct_ticks is not None and len(correct_ticks) > 0:
			file_path = AssetsHelper.gen_mix_tick_history_path(
				period.value,
				stockNo,
				date
			)
			MyLib.delete_file_if_exist(file_path)
			MyLib.create_file_if_not_exist(file_path)
			CrawlHelper.add_tick_header_if_empty(file_path)
			pd.DataFrame(correct_ticks).to_csv(
				file_path,
				mode='a',
				header=False,
				index=False
			)


# ==================


# for bever dam strategy
if __name__ == '__main__':
	# run('MTX00', '20200716', PeriodEnum.Morning, 35748, 127933 + 1)
	run('TX00', '20200716', PeriodEnum.Morning, 20243, 78501 + 1)
	exit()
