import datetime
import multiprocessing as mp
import sys
from random import randrange

from pandas import DataFrame

from src.lib.my_lib.module.LoggerModule import Logger
from src.lib.my_lib.utils.DatetimeUtil import DatetimeUtil
from src.main.api.ApiAiStock import ApiAiStock
from src.main.crawler.yahoo import StockHistory


def a_pool(args):
    csd = Class.instance()
    # records = csd.start_request(argDict['stockNo'], argDict['numDay'])
    records = csd.start_request(*args)  # *set
    return records


def craw_stock_ohlc(stockNos, numDay):
    cs = Class.instance()
    pool = mp.Pool(processes=cs.process_num)
    result = pool.map(a_pool, [(stockNo, numDay) for stockNo in stockNos])
    pool.close()
    # return [i for i in result if i]  # remove none item
    return [item for sublist in result for item in sublist]  # flat list out of list of lists


class Class:
    _instance = None

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(Class, cls).__new__(cls, *args, **kw)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.process_num = 1
        self.__initialized = True

    @staticmethod
    def instance():
        csd = Class()
        Logger.info(csd)
        return csd

    # lastDays 近幾天
    def start_request(self, stockNo, lastDays=7):
        print(stockNo)
        stockNo = str(stockNo)
        stockHistory = StockHistory.Class()
        now_time = datetime.datetime.now()
        # todo  https://stackoverflow.com/questions/4130922/how-to-increment-datetime-by-custom-months-in-python-without-using-library
        start_time = now_time - datetime.timedelta(lastDays)
        df = stockHistory.crawHistory(stockNo, start_time, now_time)
        if df is None:
            df = stockHistory.crawHistory(stockNo, start_time, now_time, '.TWO')
            if df is None:
                raise RuntimeError(f'查無{stockNo}資料')
        return self.parse(df)

    def parse(self, df: DataFrame):
        df = df.rename(columns={
            'adjclose': 'adjClose'
        })
        for index, row in df.iterrows():
            d = datetime.datetime.fromtimestamp(row['date'])
            # val = f'{d.year}{d.month}{d.day}'
            val = DatetimeUtil.format_date_to_str(d, '%Y%m%d')
            df.at[index, 'date'] = val
        records = df.to_dict('row')
        for record in records:
            record['date'] = str(int(record['date']))
            record['open'] = round(record['open'], 2)
            record['high'] = round(record['high'], 2)
            record['low'] = round(record['low'], 2)
            record['close'] = round(record['close'], 2)
            record['adjClose'] = round(record['adjClose'], 2)
            record['volume'] = int(record['volume'])
        return records


def run():
    '''
    # todo 查詢網址 http://localhost:8066/aiStock/rest/public/latest/docs.html
    -- 2021/08 上櫃
    http://localhost:8066/aiStock/rest/public/1.0.0/showStockStatistics?tranTo=html&stockNos=5483,8299,6488,5371,8044,5347,3260,5609,1785,6147,8415,3105,6274,4966,5536,2035,5014,5457,6227,5820,6180,1795,5425,6548,6220,3264,5289,3293,6469,8240,3558,6182,6118,8436,3227,3388,8358,5009,4736,8916,5013,8924,6290,6190,5306,6163,3707,3483,3484,3548
    http://localhost:8066/aiStock/rest/public/1.0.0/showStockStatistics?tranTo=html&orderCondition=cat_per&stockNos=5483,8299,6488,5371,8044,5347,3260,5609,1785,6147,8415,3105,6274,4966,5536,2035,5014,5457,6227,5820,6180,1795,5425,6548,6220,3264,5289,3293,6469,8240,3558,6182,6118,8436,3227,3388,8358,5009,4736,8916,5013,8924,6290,6190,5306,6163,3707,3483,3484,3548
    http://localhost:8066/aiStock/rest/public/1.0.0/showStockStatistics?tranTo=html&sdMonth=12&sdPercent=50%25&orderCondition=cat_per&stockNos=5483,8299,6488,5371,8044,5347,3260,5609,1785,6147,8415,3105,6274,4966,5536,2035,5014,5457,6227,5820,6180,1795,5425,6548,6220,3264,5289,3293,6469,8240,3558,6182,6118,8436,3227,3388,8358,5009,4736,8916,5013,8924,6290,6190,5306,6163,3707,3483,3484,3548
    http://localhost:8066/aiStock/rest/public/1.0.0/showStockStatistics?tranTo=html&stockNos=
    -- 2023/03 上市
    http://localhost:8066/aiStock/rest/public/1.0.0/showStockStatistics?tranTo=html&stockNos=1216,2912,2207,2409,1605,3481,2618,2377,2610,2867,2027,2376,3034,2105,2885,5871,1313,2886,2887,2404,2206,2006,2884,5880,2880,6196,2890,2633,2371,2014,2634,9941,2801,2015,2903,1718,2542,2204,1503,3704,3023,1447,1590,4906,2227,6189,3661,2362,1319
    http://localhost:8066/aiStock/rest/public/1.0.0/showStockStatistics?tranTo=html&orderCondition=cat_per&stockNos=1216,2912,2207,2409,1605,3481,2618,2377,2610,2867,2027,2376,3034,2105,2885,5871,1313,2886,2887,2404,2206,2006,2884,5880,2880,6196,2890,2633,2371,2014,2634,9941,2801,2015,2903,1718,2542,2204,1503,3704,3023,1447,1590,4906,2227,6189,3661,2362,1319
    http://localhost:8066/aiStock/rest/public/1.0.0/showStockStatistics?tranTo=html&sdMonth=12&sdPercent=50%25&orderCondition=cat_per&stockNos=1216,2912,2207,2409,1605,3481,2618,2377,2610,2867,2027,2376,3034,2105,2885,5871,1313,2886,2887,2404,2206,2006,2884,5880,2880,6196,2890,2633,2371,2014,2634,9941,2801,2015,2903,1718,2542,2204,1503,3704,3023,1447,1590,4906,2227,6189,3661,2362,1319
    -- 2023/05
    http://localhost:8066/aiStock/rest/public/1.0.0/showStockStatistics?tranTo=html&stockNos=2308,2912,2207,2882,2409,3481,1605,2618,2377,2610,8112,3034,2867,2027,2376,2105,2891,2379,9933,5871,2885,2023,3033,2886,1313,2404,2395,2206,2884,2006,1504,5880,3017,2880,2890,1909,2633,2371,5876,1717,2634,1904,2014,2542,9941,2015,2801,1718,2204
    -- 2023/06
    http://localhost:8066/aiStock/rest/public/1.0.0/showStockStatistics?tranTo=html&stockNos=1216,2882,2912,2207,1402,2409,2881,3481,2905,2618,1605,2610,2377,8112,2891,2867,3034,1101,1210,2885,2379,2105,5871,9921,1102,2886,2201,3033,2883,2023,2404,1313,2206,1504,2006,5880,2884,2880,3017,2890,5876,2371,2633,1802,2542,9941,2204,9907,4919
    '''
    result = craw_stock_ohlc([
        # 上市 : 暫時沒用
        # 上櫃 : 暫時沒用
    ], 3)
    print(result)
    if len(result) > 0:
        batch_uid = randrange(1000, 9999)
        api = ApiAiStock()
        result = api.batchSaveOrUpdateStockReportDaily(batch_uid, result)
        Logger.info(result)


def main():
    run()


if __name__ == "__main__":
    main()
    exit()
    sys.exit(1)
