import enum

class TradeMode(enum.Enum):
	'''
	============ 底下 新倉平倉 因 async , so 從送出委託到成交之間 , 會省略掉 tick收到後 一些策略上的動作 ============
	'''
	# 當下現成資料, 真實下單
	REAL = 'real'

	# 當下現成資料(ticks 來自 currentTick), 模擬真實下單
	SIMULATE_REAL = 'simulate_real'

	'''
	============ 底下 新倉平倉 因 sync , so 從送出委託就立刻假裝成交, 不會省略掉 tick收到後 一些策略上的動作 ============
	'''
	# 當下現成資料(ticks 來自 currentTick), 模擬統計下單
	SIMULATE_STATISTICS = 'simulate_statistics'

	# 歷史資料(ticks來自history), 統計下單
	STATISTICS = 'statistics'

	'''
	============ 底下 爬資料 ============
	'''
	CRAWl = 'crawl'  # todo 暫時for爬資料排程用的 可能要抽出來另外用


class TradeKind(enum.Enum):
	#
	REAL = 'real'  # 真實
	SIMULATE = 'simulate'  # 模擬
	#
	AUTO = 'auto'  # 自動
	MANUAL = 'manual'  # 手動


class PeriodEnum(enum.Enum):
	Morning = 'morning'
	Night = 'night'  # is evening + midnight
	Evening = 'evening'
	Midnight = 'midnight'

class OpenPositionKind(enum.Enum):
	BUY_CALL = 'buy_call'  # 新倉 做多
	BUY_PUT = 'buy_put'  # 新倉 做空


class ClosePositionKind(enum.Enum):
	STOP_LOSS = 'stop_loss'  # 因 停損 而 平倉
	STOP_PROFIT = 'stop_profit'  # 因 停利 而 平倉
	STOP_BLOCK_DAM = 'stop_block_dam'  # 因 達到自訂門檻 而 平倉
	STOP_FOLLOW_MASTER_SUM_VOLUME = 'stop_followMaster_sumVolume'  # 因 沒跟著主力 而 平倉
	STOP_AVOID_SLAVE_SUM_VOLUME = 'stop_avoidSlave_sumVolume'  # 因 沒有避開奴隸 而 明蒼（表示跟到奴隸）
	STOP_INDEX_KMA = 'stop_index_kma'  # 因 指數 KMA (BS/slope/goldenX ...) 而平倉
	STOP_FOLLOW_MASTER_KMA = 'stop_follow_master_kma'  # 因 主力的 量KMA (BS/slope/goldenX ...) 而平倉
	STOP_AVOID_SLAVE_KMA = 'stop_avoid_slave_kma'  # 因 奴隸的 量KMA (BS/slope/goldenX ...) 而平倉
	STOP_EXPIRED_TIME = 'stop_expired_time'  # 因 時間到 而 平倉


class DamKind(enum.Enum):
	BET = 'bet'  # Dam條件 為 下注建新倉
	BLOCK = 'block'  # Dam條件 為 取消下注 or 達到門檻平倉
