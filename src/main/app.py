# region ====== Debug ======
# endregion

# region ====== Api Config ======
from src.lib.my_lib.module.LoggerModule import Logger
from src.lib.my_lib.utils.DatetimeUtil import DatetimeUtil

Api_Host = "localhost"

Api_ContextPath = "/aiStock/"
Api_Port = 8066

# Api_ContextPath = "/aiStock2/"
# Api_Port = 8067

# Api_Timeout = 30 * 10  # for debug
Api_Timeout = 60 * 60 * 5  # one hour
# endregion -----

# region ====== Api Path ======
Api_BatchSaveOrUpdateStockReportMonthly = "rest/public/1.0.0/batchSaveOrUpdateStockReportMonthly"
Api_BatchSaveOrUpdateStockReportSeasonality = "rest/public/1.0.0/batchSaveOrUpdateStockReportSeasonality"
Api_BatchSaveOrUpdateStockReportDaily = "rest/public/1.0.0/batchSaveOrUpdateStockReportDaily"
Api_BatchSaveOrUpdateFutDataPrice = "rest/public/1.0.0/batchSaveOrUpdateFutDataPrice"
Api_BatchSaveOrUpdateFutContractsDate = "rest/public/1.0.0/batchSaveOrUpdateFutContractsDate"
Api_ListTopRevenueRecently = "rest/public/1.0.0/listTopRevenueRecently"
Api_BatchSaveOrUpdateBrokerLog = "rest/public/1.0.0/batchSaveOrUpdateBrokerLog"
Api_CheckBrokerLogExist = "rest/public/1.0.0/checkBrokerLogExist"
# endregion -----


# region ====== Function Switch ======
# FunctionSwitch_KMA = False
# FunctionSwitch_KMA = True
# endregion -----

