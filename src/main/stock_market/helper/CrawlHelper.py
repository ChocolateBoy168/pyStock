import pandas as pd

from src.lib.my_lib import MyLib
from src.lib.my_lib.module.LoggerModule import Logger
from src.main.assets.AssetsHelper import AssetsHelper
from src.lib.my_lib.utils import FileUtil


# import os

class CrawlHelper:

	def __init__(self):
		self.hasHeaderDict = {}  # 是否已產生過header

	@staticmethod
	def add_tick_header_if_empty(file_path):
		# 無內容就加入header
		# if not os.path.exists(file_path):
		if FileUtil.is_file_empty(file_path):
			Logger.info(f'{file_path} 空內容, 加入 header 開始')
			try:
				'''
				# to_csv , 不知為何 另一部電腦跑 會被中斷 Process finished with exit code -1073741819 (0xC0000005)
				pd.DataFrame([{
					'status': 'status',
					# 'sMarketNo': 'sMarketNo',
					# 'sStockIdx': 'sStockIdx',
					'stockNo': 'stockNo',
					'nPtr': 'nPtr',
					'lDate': 'lDate',
					'lTimehms': 'lTimehms',
					'lTimemillismicros': 'lTimemillismicros',
					'nBid': 'nBid',
					'nAsk': 'nAsk',
					'nClose': 'nClose',
					'nQty': 'nQty',
					'nSimulate': 'nSimulate',
					'addSubNQty': 'addSubNQty'
				}]).to_csv(
					file_path,
					mode='a',
					header=False,
					index=False
				)
				'''
				# 回到原始方式
				FileUtil.write(file_path, True, ',', [
					'status', 'stockNo', 'nPtr', 'lDate', 'lTimehms', 'lTimemillismicros', 'nBid', 'nAsk', 'nClose',
					'nQty', 'nSimulate', 'addSubNQty'
				])
			except Exception as e:
				Logger.error(e)

			Logger.info(f'{file_path} 空內容 加入 header 結束')

	# 分開 tick
	def craw_tick_separately(self, tick, change_save_to_history=False):
		file_path = AssetsHelper.gen_temp_craw_tick_file(
			tick['stockNo'],
			tick["lTimehms"],
			change_save_to_history
		)
		if (file_path in self.hasHeaderDict) is False:
			Logger.info(f'{file_path} 重建 開始')
			FileUtil.delete_file_if_exist(file_path)
			FileUtil.create_file_if_not_exist(file_path)
			self.add_tick_header_if_empty(file_path)
			self.hasHeaderDict[file_path] = True
			Logger.info(f'{file_path} 重建 結束')
		'''
		 # to_csv , 不知為何 另一部電腦跑 會被中斷 Process finished with exit code -1073741819 (0xC0000005)
		pd.DataFrame([tick]).to_csv(
			file_path,
			mode='a',
			header=False,
			index=False
		)
		'''
		# 回到原始方式
		FileUtil.write(file_path, True, ',', [
			str(tick['status']), str(tick['stockNo']), str(tick['nPtr']), str(tick['lDate']), str(tick['lTimehms']),
			str(tick['lTimemillismicros']),
			str(tick['nBid']), str(tick['nAsk']), str(tick['nClose']),
			str(tick['nQty']), str(tick['nSimulate']), str(tick['addSubNQty'])
		])

	# 同時 tick
	def craw_tick_simulataneously(self, tick, mix_name):
		file_path = AssetsHelper.gen_temp_craw_tick_file(
			mix_name,
			tick["lTimehms"]
		)
		if (file_path in self.hasHeaderDict) is False:
			MyLib.delete_file_if_exist(file_path)
			MyLib.create_file_if_not_exist(file_path)
			self.add_tick_header_if_empty(file_path)
			self.hasHeaderDict[file_path] = True
		'''
		# to_csv , 不知為何 另一部電腦跑 會被中斷 Process finished with exit code -1073741819 (0xC0000005)
		pd.DataFrame([tick]).to_csv(
			file_path,
			mode='a',
			header=False,
			index=False
		)
		'''
		# 回到原始方式
		FileUtil.write(file_path, True, ',', [
			str(tick['status']), str(tick['stockNo']), str(tick['nPtr']), str(tick['lDate']), str(tick['lTimehms']),
			str(tick['lTimemillismicros']),
			str(tick['nBid']), str(tick['nAsk']), str(tick['nClose']),
			str(tick['nQty']), str(tick['nSimulate']), str(tick['addSubNQty'])
		])

	'''
	@staticmethod
	def add_best5_header_if_empty(file_path):
		# 無內容就加入header
		if FileUtil.is_file_empty(file_path):
			pd.DataFrame([{
				'stockNo': "stockNo",
				#
				'lDate': 'lDate',
				'lTimehms': 'lTimehms',
				#
				'nBestBid1': "nBestBid1",
				'nBestBidQty1': "nBestBidQty1",
				'nBestBid2': "nBestBid2",
				'nBestBidQty2': "nBestBidQty2",
				'nBestBid3': "nBestBid3",
				'nBestBidQty3': "nBestBidQty3",
				'nBestBid4': "nBestBid4",
				'nBestBidQty4': "nBestBidQty4",
				'nBestBid5': "nBestBid5",
				'nBestBidQty5': "nBestBidQty5",
				#
				'nExtendBid': "nExtendBid",
				'nExtendBidQty': "nExtendBidQty",
				#
				'nBestAsk1': "nBestAsk1",
				'nBestAskQty1': "nBestAskQty1",
				'nBestAsk2': "nBestAsk2",
				'nBestAskQty2': "nBestAskQty2",
				'nBestAsk3': "nBestAsk3",
				'nBestAskQty3': "nBestAskQty3",
				'nBestAsk4': "nBestAsk4",
				'nBestAskQty4': "nBestAskQty4",
				'nBestAsk5': "nBestAsk5",
				'nBestAskQty5': "nBestAskQty5",
				#
				'nExtendAsk': "nExtendAsk",
				'nExtendAskQty': "nExtendAskQty",
				#
				'nSimulate': "nSimulate"
			}]).to_csv(
				file_path,
				mode='a',
				header=False,
				index=False
			)
	'''

	'''
	# 分開 best5
	def craw_best5_separately(self, best5):
		file_path = AssetsHelper.gen_temp_craw_best5_file(
			best5['stockNo'],
			best5["lTimehms"]
		)
		if (file_path in self.hasHeaderDict) is False:
			FileUtil.delete_file_if_exist(file_path)
			FileUtil.create_file_if_not_exist(file_path)
			self.add_best5_header_if_empty(file_path)
			self.hasHeaderDict[file_path] = True
		pd.DataFrame([best5]).to_csv(
			file_path,
			mode='a',
			header=False,
			index=False
		)
	'''
