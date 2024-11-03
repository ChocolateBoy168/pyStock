from src.main.stock_market.trader.abstract.AbstractRecord import AbstractRecord


class CapitalRecord(AbstractRecord):

	def __init__(self, btrUserID, bstrData):
		super().__init__()

		assert btrUserID is not None, "btrUserID 沒有值"
		assert bstrData is not None, "bstrData 沒有值"

		self.btrUserID = btrUserID
		self.bstrData = bstrData

		# 委託序號  -> todo (成交回報無此欄)??
		self.key_no = None
		# TS:證券 TA:盤後 TL:零股 TF:期貨  TO:選擇權 OF:海期 OO:海選 OS:複委託
		self.market_type = None
		# 委託種類 -> N:委託 C:取消 U:改量 P:改價 (改價含證券逐筆) D:成交 B:改價改量  S:動態退單
		self.type = None
		# 委託狀態 -> Y:失敗 T:逾時 N:正常
		self.order_err = None
		# [TS,TA,TL: 分公司代號 unit no] , [TF,TO: IB 代號 broker id]
		self.broker = None
		# 交易帳號
		self.cust_no = None
		'''
		- 證逐筆[0]   B/S 買/賣，[1,2] 00 現股，01 代資，02 代券，03 融資，04 融券，20 零股，40 拍賣現股 ， [3] I/R/F  IOC / ROD / FOK  [4] 1/2 市價/限價
		- 期[0]      B/買 S/賣，  [1] Y/當沖, N/新倉, O/平倉, 7/代沖銷 ， [2] I/R/F  IOC/ROD/FOK ， [3] 1/2/3/4/5 市價/限價/停損/停損限價/收市
		- 權[0]      B/買 S/賣，  [1] N/新倉 , O/平倉, 7/代沖銷，        [2] I/R/F IOC/ROD/FOK  ， [3] 1/2/3/4/5 市價/限價/停損/停損限價/收市
		- 海期海選[0] B/買 S/賣，  [1] 1/2/3/4/5 市價/限價/停損/停損限價/收市 ，[2] Y當沖/N新倉/O平倉
		- 複委託[0]   B/買 S/賣，  [1] 1/2/3/4/5 市價/限價/停損/停損限價/收市
		'''
		self.buy_sell = None
		# 交易所
		self.exchange_id = None
		# 商品代碼
		self.com_id = None
		# 履約價 七位整數
		self.strike_price = None
		# 委託書號
		self.order_no = None

		# 價格, 已經處理的價格 . 其餘為根據 Type 種類不同，「委託」為委託價；「成交」為成交價;「改價」為修改後價格;「動態退單」為交易所提供之退單基準價
		self.price = None
		# 海外期貨回報用，分子
		self.numerator = None
		# 海外期貨回報用，分母
		self.denominator = None

		# 海外期貨回報用，觸發價格 . 國內期選成交時，第一隻腳成交價
		self.price1 = None
		# 海外期貨回報用，觸發價格分子
		self.numerator1 = None
		# 海外期貨回報用，觸發價格分母
		self.denominator1 = None

		# 國內期選成交時，第二隻腳成交價
		self.price2 = None
		self.numerator2 = None
		self.denominator2 = None

		# TS OS股數/ TF TO OF OO口數 . 根據 Type 種類，「委託」為委託量，「成交」為成交量，「改量」為減量數，「刪單」為原委託剩量
		self.qty = None
		# 參考欄位，異動變更前量，刪單為空值
		self.before_qty = None
		# 參考欄位，異動變更後量，刪單為空值
		self.after_qty = None

		# 交易日期
		self.date = None
		# 交易時間(含冒號EX: 01:02:03)
		self.time = None
		# 成交序號
		self.ok_seq = None
		# 子帳帳號
		self.sub_id = None
		# 營業員編號
		self.sale_no = None

		# 委託介面
		self.agent = None
		# 委託日期(僅提供海外委託，國內尚未提供)
		self.trade_date = None
		# 回報流水號
		self.msg_no = None
		# A:盤中單 B:預約單(僅國內期、選委託)
		self.pre_order = None

		# 第一隻腳商品代碼
		self.com_id1 = None
		# 第一隻腳商品結算年月
		self.year_month1 = None
		# 第一隻腳商品履約價
		self.strike_price1 = None

		# 第二隻腳商品代碼
		self.com_id2 = None
		# 第二隻腳商品結算年月
		self.year_month2 = None
		# 第二隻腳商品履約價
		self.strike_price2 = None

		# 成交序號
		self.execution_no = None
		# 下單期標
		self.price_symbol = None
		# 盤別 A：T盤  B：T+1盤 (僅國內期、選委託)
		self.reserved = None
		# 有效委託日
		self.order_effective = None
		# 選擇權類型C：Call P：Put
		self.call_put = None
		# 交易所單號(依海外交易所實際提供為主)
		self.order_seq = None
		# 第四欄位：OrderErr為Y時，委託單錯誤訊息
		self.error_msg = None

		# 交易所動態退單代碼; E:交易所動態退單
		self.cancel_order_mark_by_exchange = None

		'''
		交易所或後台退單訊息
		[00]:2碼數字,交易所回應代碼及訊息;
		[000]:3碼數字,交易後台代碼及訊息;
		[D]委託成功後,由交易所主動退單及退單原因
		'''
		self.exchange_tandem_msg = None

		self.build_data()

	# 是否成交
	def is_deal_type(self):
		result = False
		if self.type is not None:
			result = (self.type == 'D')
		return result

	def build_data(self):
		cutData = self.bstrData.split(',')
		self.key_no = cutData[0]
		self.market_type = cutData[1]
		self.type = cutData[2]
		self.order_err = cutData[3]
		self.broker = cutData[4]
		self.cust_no = cutData[5]
		self.buy_sell = cutData[6]
		self.exchange_id = cutData[7]
		self.com_id = cutData[8]
		self.strike_price = cutData[9]
		self.order_no = cutData[10]
		self.price = cutData[11]
		self.numerator = cutData[12]
		self.denominator = cutData[13]
		self.price1 = cutData[14]
		self.numerator1 = cutData[15]
		self.denominator1 = cutData[16]
		self.price2 = cutData[17]
		self.numerator2 = cutData[18]
		self.denominator2 = cutData[19]
		self.qty = cutData[20]
		self.before_qty = cutData[21]
		self.after_qty = cutData[22]
		self.date = cutData[23]
		self.time = cutData[24]
		self.ok_seq = cutData[25]
		self.sub_id = cutData[26]
		self.sale_no = cutData[27]
		self.agent = cutData[28]
		self.trade_date = cutData[29]
		self.msg_no = cutData[30]
		self.pre_order = cutData[31]
		self.com_id1 = cutData[32]
		self.year_month1 = cutData[33]
		self.strike_price1 = cutData[34]
		self.com_id2 = cutData[35]
		self.year_month2 = cutData[36]
		self.strike_price2 = cutData[37]
		self.execution_no = cutData[38]
		self.price_symbol = cutData[39]
		self.reserved = cutData[40]
		self.order_effective = cutData[41]
		self.call_put = cutData[42]
		self.order_seq = cutData[43]
		self.error_msg = cutData[44]
		self.cancel_order_mark_by_exchange = cutData[45]
		self.exchange_tandem_msg = cutData[46]

	# 是否期貨
	def is_TF_market_type(self):
		return self.market_type == 'TF'

	# 取消委託單
	def is_cancel_type(self):
		return self.type == 'C'

	# 成交
	def is_deal_type(self):
		return self.type == 'D'
