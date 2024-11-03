import pandas as pd

from src.lib.my_lib.module.LoggerModule import Logger
from src.lib.my_lib.utils.PandaUtil import PandaUtil
from src.main.AppConst import PeriodEnum
from src.main.assets.AssetsHelper import AssetsHelper
from src.main.stock_market.helper.CrawlHelper import CrawlHelper
from src.main.util.TickUtil import TickUtil
from src.lib.my_lib.utils import FileUtil


def get_sort_field(tick):
	return tick['lTimehms'], tick['lTimemillismicros']


# def run_now():
# 	# date = AssetsHelper.list_deal_date()[0]
# 	# date = datetime.datetime.now().strftime("%Y%m%d")
# 	# date = DatetimeUtil.local_today_to_str(ft='%Y%m%d')
# 	date = AssetsHelper.find_last_final_date()
# 	run(date)

def run(date):
	# ------
	periodEnums = [PeriodEnum.Morning, PeriodEnum.Night]
	# ------
	for periodEnum in periodEnums:
		tx_data_path = AssetsHelper.gen_tick_history_path(periodEnum.value, "TX00", date)
		mtx_data_path = AssetsHelper.gen_tick_history_path(periodEnum.value, "MTX00", date)
		if tx_data_path is None or mtx_data_path is None:
			Logger.warning(f'file {tx_data_path}  not find!')
		else:
			tx_df = pd.read_csv(tx_data_path)
			mtx_df = pd.read_csv(mtx_data_path)
			tx_ticks = PandaUtil.to_records_dict(tx_df)
			mtx_ticks = PandaUtil.to_records_dict(mtx_df)
			mix_ticks = tx_ticks + mtx_ticks
			correct_ticks = None
			if periodEnum == PeriodEnum.Morning:
				# mix_ticks.sort(key=get_sort_field)
				mix_ticks.sort(key=lambda t: (t['lTimehms'], t['lTimemillismicros']))  # 適合早盤
				correct_ticks = mix_ticks
			elif periodEnum == PeriodEnum.Night:
				mix_ticks.sort(key=lambda t: (t['lTimehms'], t['lTimemillismicros']))
				# 需再 將 資料上(midnight)下(evening)兩部分對調 成 evening first midnight second
				switch_index = \
					[i for i, tick in enumerate(mix_ticks) if TickUtil.is_evening_period(tick['lTimehms']) is True][
						0]
				correct_ticks = mix_ticks[switch_index:] + mix_ticks[:switch_index]

			Logger.info(len(correct_ticks))
			if correct_ticks is not None and len(correct_ticks) > 0:
				file_path = AssetsHelper.gen_mix_tick_history_path(
					periodEnum.value,
					"TX00+MTX00",
					date
				)
				FileUtil.delete_file_if_exist(file_path)
				FileUtil.create_file_if_not_exist(file_path)
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
	run(AssetsHelper.find_last_final_date())
	exit()
