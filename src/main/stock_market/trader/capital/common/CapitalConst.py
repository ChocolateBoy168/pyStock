from src.lib.my_lib.module.LoggerModule import *
import enum


class CscApiEventKind(enum.Enum):
	QUOTE = 'quote'
	ORDER = 'order'
	REPLY = 'reply'


class BuySell(enum.IntEnum):
	Buy = 0  # 買進
	Sell = 1  # 賣出


class TradeType(enum.IntEnum):
	ROD = 0
	IOC = 1
	FOK = 2


class DayTrade(enum.IntEnum):
	Not_Dang_Chong = 0  # 非當沖
	Dang_Chong = 1  # 當沖


class NewClose(enum.IntEnum):
	Open = 0  # 新倉
	Close = 1  # 平倉
	Auto = 2  # 自動


class Reserved(enum.IntEnum):
	Not_Reserve = 0  # 盤中
	Reserve = 1  # T盤預約


if __name__ == '__main__':
	Logger.info(NewClose.Open)
	Logger.info(NewClose.Open == 0)
	Logger.info(NewClose.Open == TradeType.ROD)
