'''
    #Build Configuration
        Module name: scrapy
        Parameter: runspider CrawStockMonthly.py -s FEED_EXPORT_ENCODING='utf-8' -t json -o "scrapy_out_to_json.json"
        Working directory: pyCapitalStock\src\main\crawler
    #直覺方式requests爬 , 參考 tools/reports.py
'''

# from src._mylib.utils.log_util import LogUtil
# -*- coding: utf-8 -*-
import os
from datetime import datetime, timedelta
from random import randrange

import pandas as pd
import scrapy
from htmltable_df.extractor import Extractor

from src.lib.my_lib.module.LoggerModule import Logger
from src.lib.my_lib.utils.PandaUtil import PandaUtil
from src.main.api.ApiAiStock import ApiAiStock

stock_type = {
    '國內上市': 'https://mops.twse.com.tw/nas/t21/sii/t21sc03_{}_{}_0.html',
    # '國外上市': 'https://mops.twse.com.tw/nas/t21/sii/t21sc03_{}_{}_1.html',

    # '國內上櫃': 'https://mops.twse.com.tw/nas/t21/otc/t21sc03_{}_{}_0.html',
    # '國外上櫃': 'https://mops.twse.com.tw/nas/t21/otc/t21sc03_{}_{}_1.html',
    # '國內興櫃': 'https://mops.twse.com.tw/nas/t21/rotc/t21sc03_{}_{}_0.html',
    # '國外興櫃': 'https://mops.twse.com.tw/nas/t21/rotc/t21sc03_{}_{}_1.html',

    # '國內公發公司': 'https://mops.twse.com.tw/nas/t21/pub/t21sc03_{}_{}_0.html',
    # '國外公發公司': 'https://mops.twse.com.tw/nas/t21/pub/t21sc03_{}_{}_1.html'
}


class TemplateSpider(scrapy.Spider):
    name = "stock_rev_mm"

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 1,
        'MONGODB_COLLECTION': name,
        'MONGODB_ITEM_CACHE': 1000,
        'MONGODB_UNIQ_KEY': [("YY", -1), ("MM", 1), ("公司代號", 1)],
    }

    def __init__(self, beginDate=None, endDate=None, *args, **kwargs):
        super(TemplateSpider, self).__init__(beginDate=beginDate, endDate=endDate, *args, **kwargs)
        self.api = ApiAiStock()
        self.out_file_name = "scrapy_out_to_json.json"
        # step : remove out file
        if self.out_file_name in os.listdir():
            os.remove(self.out_file_name)

    def start_requests(self):
        if not self.beginDate and not self.endDate:
            if True:  # custom year date
                # todo 查詢網址 http://homewin.sytes.net:8066/aiStock/rest/public/latest/docs.html
                for key, val in stock_type.items():
                    YY = 112
                    MM = 7  # todo 似乎3號開始陸陸續續公布營收,不要太早改月份,來執行,至少等到出表日期為每個月10號起後再來爬. 不然太早爬,會因top50會抓未公佈的新月營收
                    url = val.format(YY, MM)
                    yield scrapy.Request(url, meta={'STOCK_TYPE': key, 'YY': YY, 'MM': MM})
            else:  # 最近20天
                date = datetime.today()
                self.beginDate = (date - timedelta(days=20)).strftime("%Y-%m-%d")
                self.endDate = date.strftime("%Y-%m-%d")
                for date in pd.date_range(self.beginDate, self.endDate, freq='M'):
                    for key, val in stock_type.items():
                        YY = date.year - 1911
                        MM = date.month
                        url = val.format(YY, MM)
                        yield scrapy.Request(url, meta={'STOCK_TYPE': key, 'YY': YY, 'MM': MM})

    def parse(self, response):
        meta = response.meta

        df_combine = pd.DataFrame([])
        for table in response.css('table[bgcolor="#FFFFFF"]'):
            # treq0 = table.parent().parent().parent()('tr:eq(0)')
            # INDUSTRY_TYPE = re.search('產業別：(\w+)', treq0("th:contains('產業別')").text()).group(1)

            extractor = Extractor(table.extract())
            if extractor.df().shape[0] > 0:  # 表示有資料
                data = extractor.df()[:-1]  # debug extractor.df()[:-1].to_dict('row')
                data = data.applymap(lambda x: x.strip().replace(',', ''))
                # debbug data.to_dict('row')
                data.insert(0, 'MM', meta.get('MM'))
                data.insert(0, 'YY', meta.get('YY'))
                # data.insert(0, 'INDUSTRY_TYPE', INDUSTRY_TYPE)
                data.insert(0, 'STOCK_TYPE', meta.get('STOCK_TYPE'))

                # df_new = data.loc[:, ['公司代號', '公司名稱', 'YY', 'MM', '營業收入_當月營收']]
                df_new = data.loc[:, ['公司代號', 'YY', 'MM', '營業收入_當月營收']]
                for r in PandaUtil.to_records_dict(df_new):
                    yield r
                df_combine = pd.concat([df_combine, df_new])

        # change head name
        df_combine = df_combine.rename(columns={
            '公司代號': 'stockNo',
            # '公司名稱': 'companyName',
            'YY': 'year',
            'MM': 'month',
            '營業收入_當月營收': 'revenue'
        })
        # data: [MonthlyReportDto] = []
        # for r in df_combine.to_dict('row'):
        #     data.append({})
        if df_combine.size > 0:
            batch_uid = randrange(1000, 9999)
            result = self.api.batchSaveOrUpdateStockReportMonthly(batch_uid, df_combine.to_dict('row'))
            Logger.info(result)

    def start(self):
        self.start_requests()
        pass


class Revenue:
    _instance = None

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(Revenue, cls).__new__(cls, *args, **kw)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True

    def run(self):
        # LogUtil.Info('test')
        s = TemplateSpider()
        s.start_requests()
        s.start()


def main():
    revenue = Revenue()
    revenue.run()

    pass


if __name__ == "__main__":
    main()
