import multiprocessing as mp
import sys
import time

from bs4 import BeautifulSoup
from selenium import webdriver

from src.lib.my_lib.module.LoggerModule import Logger
from src.lib.web_driver.Path import WebDriverPath


def a_pool(args):
    # Logger.info(f'\n{args}')
    # record = self.start_request(*args)
    cs = CrawStock.instance()
    print(cs)
    cs.init_browsers_if_empty()
    record = cs.start_request(*args)
    return record


class CrawStock:
    _instance = None

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(CrawStock, cls).__new__(cls, *args, **kw)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.req_url = 'https://goodinfo.tw/StockInfo/StockBzPerformance.asp?STOCK_ID={0}&YEAR_PERIOD=1&RPT_CAT=QUAR'
        self.browser_num = 2 # todo num by cpu core , 開四個 process 被 goodinfo 盯上 鎖 ip
        self.browsers = []
        self.__initialized = True

    @staticmethod
    def instance():
        return CrawStock()

    def init_browsers_if_empty(self):
        if (len(self.browsers) == 0):
            for i in range(self.browser_num):
                path = WebDriverPath.get()
                options = webdriver.ChromeOptions()
                '''
                selenium.common.exceptions.WebDriverException: Message: unknown Error: cannot find Chrome binary
                https://programmersought.com/article/47711748581/
                '''
                # options.binary_location = 'C:/Program Files/Google/Chrome/Application/chrome.exe'  # for my company's x64 chrome
                # https://stackoverflow.com/questions/16180428/can-selenium-webdriver-open-browser-windows-silently-in-background
                #options.add_argument("--headless")
                browser = webdriver.Chrome(path, options=options)
                self.browsers.append(browser)

    @staticmethod
    def start_requests(stockNos):
        me = CrawStock.instance()
        argsAry = []

        # dispatch stockNo to browserIndex
        size = len(stockNos)
        for i in range(size):
            argsAry.append(
                # (me.browsers[i % me.browser_num], stockNos[i])
                # (me, i % browser_num, stockNos[i])
                # 以上 error => AttributeError: Can't pickle local object
                (i % me.browser_num, stockNos[i])
            )

        # run pool , 留意, 似乎會把遠本的thread 切斷 分流到各process上 ,
        # pool導致後來的a_pool裡的CrawStock.instance與現在的Craw.instance是不一致的,
        # 這樣會導致後來取道的browsers為空,改用init_browsers_if_empty來解決
        pool = mp.Pool(processes=me.browser_num)
        result = pool.map(a_pool, argsAry)
        pool.close()

        # release browser
        for i in range(len(me.browsers)):
            browser = me.browsers[i]
            # browser.close()
            browser.quit()
        me.browsers.clear()

        Logger.info(result)
        return result

    def start_request(self, browserIndex, stockNo):
        # Logger.info(f'{browserIndex},{stockNo}')
        browser = self.browsers[browserIndex]
        url = self.req_url.format(stockNo)
        # r = requests.get(url)
        # Logger.info(r.status_code == requests.codes.ok)
        browser.get(url)
        time.sleep(1)  # 須加上時間 延後1s爬, 不然沒間隔秒數 ,會爬很快 被鎖ip
        return self.parse(stockNo, browser.page_source)

    def parse(self, stockNo, pageSource):
        # 找出最近一筆有資料的 : 季度/單季ROE/單季ROA/EPS/eps年增
        soup = BeautifulSoup(pageSource, 'html.parser')
        # table = soup.find_all('table', {'class': 'solid_1_padding_4_2_tbl'})[1]
        trs = soup.select('.solid_1_padding_4_0_tbl tbody tr')
        result = None
        for tr in trs:
            tds = tr.select('td')
            season = tds[0].text
            roe = tds[16].text
            roa = tds[18].text
            eps = tds[20].text
            eps_minus_last_year = tds[21].text
            if eps != '-':
                result = {
                    'stockNo': stockNo,
                    'season': season,
                    'roe': roe,
                    'roa': roa,
                    'eps': eps,
                    'eps_minus_last_year': eps_minus_last_year
                }
                break
        Logger.info(result)
        return result


def main():
    CrawStock.instance()
    # CrawStock.start_requests(['2317'])
    # CrawStock.start_requests(['2317', '2330'])
    # CrawStock.start_requests(['2330', '00642U', '2330'])  # how about has no data ,ex: 00642U 石油
    CrawStock.start_requests(['2002', '2017', '2317', '2330', '2618', '2882', '9904', '9907'])


if __name__ == "__main__":
    main()
    exit()
    sys.exit(1)
