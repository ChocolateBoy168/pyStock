import math

from src.lib.my_lib.module.LoggerModule import *
from src.lib.my_lib.utils.DatetimeUtil import DatetimeUtil
from src.main.AppConst import PeriodEnum, TradeMode
from src.main.util.TickUtil import TickUtil

try:
	import thread
except ImportError:
	import _thread as thread
import time


class SKQuoteLibEvents:
	def __init__(self, trader):
		from src.main.stock_market.trader.capital.abstract.AbstractCapitalTrader import AbstractCapitalTrader
		self.trader: AbstractCapitalTrader = trader
		self.broker = self.trader.broker

	def OnConnection(self, nKind, nCode):
		Logger.info("OnConnection {}, {}".format(nKind, nCode))
		if (nKind == 3001):
			strMsg = f"[{nCode}] Connected!"

			thread.start_new_thread(self.start_quote, ())
		elif (nKind == 3002):
			strMsg = f"[{nCode}] DisConnected!"
		# exit()
		elif (nKind == 3003):
			strMsg = f"[{nCode}] Stocks ready!"
		# stp1: 3001登入成功後  step2: 3003連線成功後 => 才可進行  step3:request_ticks
		# for stockNo in self.broker.requestTicks_stockNos:
		# 	self.trader.csc_core.quote_request_ticks(stockNo)
		elif (nKind == 3021):
			strMsg = f"[{nCode}] Connect Error!"
		Logger.info(strMsg)

	def start_quote(self):
		Logger.info("start_quote")
		time.sleep(20)
		for stockNo in self.broker.requestTicks_stockNos:
			self.trader.csc_core.quote_request_ticks(stockNo)

	# self.controller.update_conntect_info_ui(strMsg)

	def OnNotifyQuote(self, sMarketNo, sStockidx):
		pStock = self.trader.csc_core.sk.SKSTOCK()
		self.trader.csc_core.skQ.SKQuoteLib_GetStockByIndex(sMarketNo, sStockidx, pStock)
		strMsg = '代碼:', pStock.bstrStockNo, \
				 '名稱:', pStock.bstrStockName, \
				 '開盤價:', pStock.nOpen / math.pow(10, pStock.sDecimal), \
				 '最高:', pStock.nHigh / math.pow(10, pStock.sDecimal), \
				 '最低:', pStock.nLow / math.pow(10, pStock.sDecimal), \
				 '成交價:', pStock.nClose / math.pow(10, pStock.sDecimal), \
				 '總量:', pStock.nTQty
		Logger.info(strMsg)
		self.trader.csc_core.idx_map[sStockidx] = {'stock_no': pStock.bstrStockNo, 'stock_name': pStock.bstrStockName}
		self.trader.csc_core.stock_map[pStock.bstrStockNo] = {'stock_idx': sStockidx,
															  'stock_name': pStock.bstrStockName}

	def process_ticks(self, status, sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid: str,
					  nAsk: str, nClose: str,
					  nQty: str, nSimulate):
		''' 這段要看args , 小心 不能加 會讓程序 在處理IO時, 可能突然中斷 也不會丟出 Error
		frame = inspect.currentframe()
		args, _, _, values = inspect.getargvalues(frame)
		print('function name "%s"' % inspect.getframeinfo(frame)[2])
		for i in args:
			print("    %s = %s" % (i, values[i]))
		'''

		stockNo = self.trader.csc_core.get_stockno_by_stockidx(sMarketNo, sStockIdx)
		if stockNo in self.broker.requestTicks_stockNos:
			add_sub = '#'
			if nClose <= nBid:
				add_sub = '-'
			if nClose >= nAsk:
				add_sub = '+'
			if nClose == nBid and nClose == nAsk:
				add_sub = '#'
			addSubNQty = add_sub + str(nQty)

			tick = {
				# ***  此順序 需跟著  CrawlHelper add_tick_header_if_empty 的順序 一致 才行 ***
				'status': status,  # custom
				'stockNo': stockNo,  # custom
				'nPtr': nPtr,
				'lDate': lDate,
				'lTimehms': lTimehms,
				'lTimemillismicros': lTimemillismicros,
				'nBid': nBid,
				'nAsk': nAsk,
				'nClose': nClose,
				'nQty': nQty,
				'nSimulate': nSimulate,
				'addSubNQty': addSubNQty  # custom
			}

			# debug
			# if status == 'current':
			# 	Logger.info(tick.values())
			# Logger.info(tick.values())

			if self.trader.is_not_crawl():
				# Logger.info(f'收到 tick , {status} {sMarketNo} {nSimulate}')

				# 模擬的不要
				if nSimulate == 1:
					return

				# 目前如果 是跑早盤的話, 需忽略掉夜盤的ticks , todo 考慮看看是否吸收夜盤的ticks
				# if self.broker.periodEnum == PeriodEnum.Morning:
				# 	if TickUtil.is_night_period(lTimehms):
				# 		return

				self.broker.strategy.signal.upgrade_tickSignal(tick)

				'''
				self.trader.tick_queue.put(
					dict(status=status, stockNo=stockNo
						, sMarketNo=sMarketNo, sStockIdx=sStockIdx
						, nPtr=nPtr, lDate=lDate
						, lTimehms=lTimehms, lTimemillismicros=lTimemillismicros
						, nBid=nBid, nAsk=nAsk, nClose=nClose, nQty=nQty, nSimulate=nSimulate)
				)
				'''
			elif self.trader.is_crawl():
				# ticks 只在早盤時段才進行側錄動作(因為會含夜盤資料開始錄起)
				now_lTimehms = DatetimeUtil.current_time_trip_zero()
				if TickUtil.is_morning_period(now_lTimehms):  # 注意 小心 , 要留意跑的時間否則會蓋掉夜盤的資料
					# ===各別====
					self.trader.crawlHelper.craw_tick_separately(tick, True)
					# ===合併====
					'''
					if status == 'current':
						self.trader.crawlHelper.craw_tick_simulataneously(tick, '+'.join(self.broker.requestTicks_stockNos))
					else:
						# todo 須改 介於 lTimehms 之間插入 insert 非 append
						pass
					'''

	def OnNotifyHistoryTicks(self, sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose,
							 nQty, nSimulate):
		'''
		thread.start_new_thread(self.process_ticks,
		                        ("history", sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, str(nBid),
		                         str(nAsk),
		                         str(nClose),
		                         str(nQty), nSimulate))
		Logger.debug(strMsg)
		'''
		self.process_ticks('history', sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk,
						   nClose, nQty, nSimulate)

	def OnNotifyTicks(self, sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty,
					  nSimulate):
		'''
		strMsg = "[OnNotifyTicks]", sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate
		thread.start_new_thread(self.process_ticks, ("current", sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, str(nBid),
		                   str(nAsk),
		                   str(nClose),
		                   str(nQty), nSimulate))
		Logger.debug(strMsg)
		'''
		self.process_ticks('current', sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk,
						   nClose, nQty, nSimulate)

	def OnNotifyBest5(self, sMarketNo, sStockIdx,
					  nBestBid1, nBestBidQty1, nBestBid2, nBestBidQty2, nBestBid3, nBestBidQty3, nBestBid4,
					  nBestBidQty4, nBestBid5, nBestBidQty5,
					  nExtendBid, nExtendBidQty,
					  nBestAsk1, nBestAskQty1, nBestAsk2, nBestAskQty2, nBestAsk3, nBestAskQty3, nBestAsk4,
					  nBestAskQty4, nBestAsk5, nBestAskQty5,
					  nExtendAsk, nExtendAskQty,
					  nSimulate
					  ):
		# 暫時不爬 best5
		return
		if self.trader.is_crawl():
			from src.main.stock_market.trader.capital.CapitalCrawlTrader import CapitalCrawlTrader
			trader: CapitalCrawlTrader = self.trader
			stockNo = trader.csc_core.get_stockno_by_stockidx(sMarketNo, sStockIdx)
			if stockNo in self.broker.requestTicks_stockNos:
				# pStock = self.trader.csc_core.sk.SKBEST5()
				# self.trader.csc_core.skQ.SKQuoteLib_GetBest5(sMarketNo, sStockIdx, pStock)
				best5 = {
					# *** 此順序 需跟著  CrawlHelper add_best5_header_if_empty 的順序 一致 才行 ***
					#
					'stockNo': stockNo,
					#
					'lDate': DatetimeUtil.local_today_to_str(ft='%Y%m%d'),
					'lTimehms': DatetimeUtil.current_time_trip_zero(),
					#
					'nBestBid1': nBestBid1,
					'nBestBidQty1': nBestBidQty1,
					'nBestBid2': nBestBid2,
					'nBestBidQty2': nBestBidQty2,
					'nBestBid3': nBestBid3,
					'nBestBidQty3': nBestBidQty3,
					'nBestBid4': nBestBid4,
					'nBestBidQty4': nBestBidQty4,
					'nBestBid5': nBestBid5,
					'nBestBidQty5': nBestBidQty5,
					#
					'nExtendBid': nExtendBid,
					'nExtendBidQty': nExtendBidQty,
					#
					'nBestAsk1': nBestAsk1,
					'nBestAskQty1': nBestAskQty1,
					'nBestAsk2': nBestAsk2,
					'nBestAskQty2': nBestAskQty2,
					'nBestAsk3': nBestAsk3,
					'nBestAskQty3': nBestAskQty3,
					'nBestAsk4': nBestAsk4,
					'nBestAskQty4': nBestAskQty4,
					'nBestAsk5': nBestAsk5,
					'nBestAskQty5': nBestAskQty5,
					#
					'nExtendAsk': nExtendAsk,
					'nExtendAskQty': nExtendAskQty,
					#
					'nSimulate': nSimulate,
				}
				trader.crawlHelper.craw_best5_separately(best5)

	# Logger.debug(best5.values())

	def OnNotifyKLineData(self, bstrStockNo, bstrData):
		cutData = bstrData.split(',')
		strMsg = bstrStockNo, bstrData
		Logger.debug(strMsg)

	def OnNotifyMarketTot(self, sMarketNo, sPrt, nTime, nTotv, nTots, nTotc):
		strMsg1 = nTotv / 100, "億"
		strMsg2 = nTots, "張"
		strMsg3 = nTotc, "筆"
		Logger.debug("OnNotifyMarketTot {},{},{}".format(strMsg1, strMsg2, strMsg3))

	def OnNotifyMarketHighLow(self, sMarketNo, sPrt, nTime, sUp, sDown, sHigh, sLow, sNoChange):

		strMsg = "成交(上漲/下跌)家數:", sUp, "/", sDown, "成交(漲停/跌停)家數：", sHigh, "/", sLow, "________平盤家數：", sNoChange

		if (sMarketNo == 0):
			Logger.debug(strMsg)
		else:
			Logger.debug(strMsg)

	def OnNotifyStockList(self, sMarketNo, bstrStockData):
		strMsg = "[OnNotifyStockList]", bstrStockData
		Logger.debug(strMsg)

	def OnNotifyMarketBuySell(self, sMarketNo, sPrt, nTime, nBc, nSc, nBs, nSs):
		if (sMarketNo == 0):
			strMsg = "大盤成交買進(張/筆)數：", nBs, "/", nBc, "大盤成交賣出(張/筆)數：", nSs, "/", nSc
			Logger.debug(strMsg)
		else:
			strMsg = "大盤成交買進(張/筆)數：", nBs, "/", nBc, "大盤成交賣出(張/筆)數：", nSs, "/", nSc
			Logger.debug(strMsg)

	def OnNotifyServerTime(self, sHour, sMinute, sSecond, nTotal):
		strMsg = "{:02d}:{:02d}:{:02d}".format(sHour, sMinute, sSecond)

	# Logger.debug(f'serverTime is {strMsg}')

	# self.controller.update_server_time(strMsg)

	def OnNotifyBoolTunel(self, sMarketNo, sStockIdx, bstrAVG, bstrUBT, bstrLBT):
		# Gobal_BoolenAVG_Info["text"] = bstrAVG
		# Gobal_BoolenUBT_Info["text"] = bstrUBT
		# Gobal_BoolenLBT_Info["text"] = bstrLBT
		Logger.debug("OnNotifyBoolTunel")

	def OnNotifyMACD(self, sMarketNo, sStockidx, bstrMACD, bstrDIF, bstrOSC):
		# Gobal_MACD_Inf["text"] = bstrMACD
		# Gobal_DIF_Inf["text"] = bstrDIF
		# Gobal_OSC_Inf["text"] = bstrOSC
		Logger.debug("OnNotifyMACD")

	def OnNotifyFutureTradeInfo(self, bstrStockNo, sMarketNo, sStockIdx, nBuyTotalCount, nSellTotalCount, nBuyTotalQty,
								nSellTotalQty, nBuyDealTotalCount, nSellDealTotalCount):
		# Gobal_MarketNo_Inf["text"] = str(sMarketNo)
		# Gobal_TotalBuy_Inf["text"] = str(nBuyTotalCount)
		# Gobal_TotalBuyP_Inf["text"] = str(nBuyTotalQty)
		# Gobal_TotalSucessB_Inf["text"] = str(nBuyDealTotalCount)
		# Gobal_StockIdx_Inf["text"] = str(sStockIdx)
		# Gobal_TotalSell_Inf["text"] = str(nSellTotalCount)
		# Gobal_TotalSellP_Inf["text"] = str(nSellTotalQty)
		# Gobal_TotalSucessS_Inf["text"] = str(nSellDealTotalCount)
		Logger.debug("OnNotifyFutureTradeInfo")

	def OnNotifyStrikePrices(self, bstrOptionData):
		sum = " "
		m_nCount = 0
		strData = ""
		strData = "[OnNotifyStrikePrices]" + bstrOptionData
		Logger.debug(strData)
