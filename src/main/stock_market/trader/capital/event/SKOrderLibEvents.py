import datetime

import pandas as pd

from src.lib.my_lib.module.LoggerModule import *


class SKOrderLibEvents:
	def __init__(self, trader):
		from src.main.stock_market.trader.capital.abstract.AbstractCapitalTrader import AbstractCapitalTrader
		self.trader: AbstractCapitalTrader = trader

	'''
	bstrLogInID [登入ID]
	bstrAccountData [市場,分公司,分公司代號,帳號,身份證字號,姓名,?]
	市場 [TS:證券 TA:盤後 TL:零股 TF:期貨 TO:選擇權 OF:海期 OO:海選 OS:複委託]
	'''
	def OnAccount(self, bstrLogInID, bstrAccountData):
		Logger.info("id = {}, data = {}".format(bstrLogInID, bstrAccountData))
		self.trader.csc_core.userID = bstrLogInID
		strValues = bstrAccountData.split(',')
		strAccount = strValues[1] + strValues[3]
		if strValues[0] == 'TS':
			self.trader.csc_core.account_list['stock'].append(strAccount)
		elif strValues[0] == 'TF':
			self.trader.csc_core.account_list['future'].append(strAccount)
		elif strValues[0] == 'OF':
			self.trader.csc_core.account_list['sea_future'].append(strAccount)
		elif strValues[0] == 'OS':
			self.trader.csc_core.account_list['foreign_stock'].append(strAccount)

	def onRequestProfitReport(self, data):
		columns = ['broker', 'account', 'stockNo', 'tradingType', 'number', 'close', 'marketPrice'
			, 'netAsset', 'profit', 'avgCost', 'realCost', 'cost', 'commission', 'estimatedCommission'
			, 'tax', 'unknown', 'margin', 'financing', 'interest', 'roi', 'otherNumber', 'date']

		values = data.split(',')
		values[-1] = str(datetime.datetime.now().timestamp())
		df = pd.DataFrame([values], columns=columns)
		df['close'] = df['close'].astype(float)
		df['marketPrice'] = df['marketPrice'].astype(float)
		df['netAsset'] = df['netAsset'].astype(float)
		df['profit'] = df['profit'].astype(float)
		df['agvCost'] = df['agvCost'].astype(float)
		df['cost'] = df['cost'].astype(float)
		df['realCost'] = df['realCost'].astype(float)
		df['roi'] = df['roi'].astype(float)
		# self.WM.accountDb.updateStockProfit(df)
		Logger.info(df)
