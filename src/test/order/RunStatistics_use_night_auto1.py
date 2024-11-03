from src.lib.my_lib.module.LoggerModule import Logger
from src.main.AppConst import PeriodEnum, TradeMode
from src.main.api.ApiAiStock import ApiAiStock
from src.main.assets.AssetsHelper import AssetsHelper
from src.main.dto.ResponseWrapper import ResponseWrapper
from src.main.stock_market.Broker import Broker
from src.main.stock_market.trader.capital.CapitalStatisticsTrader import CapitalStatisticsTrader
import multiprocessing as mp


def run_statistics(period: PeriodEnum, date, trade_stockNo, strategy_source):
    result: ResponseWrapper = ApiAiStock.checkBrokerLogExist(
        period.value, trade_stockNo, date, TradeMode.STATISTICS.value, strategy_source
    )
    if result.success:
        data = result.data
        exist = data['exist']
        if exist is False:
            broker = Broker(period, date, trade_stockNo, strategy_source, CapitalStatisticsTrader)
            # broker.register_trader(CapitalStatisticsTrader(broker))
            Logger.info(f'\n========start [{broker.broker_log_file}]==========')
            # broker.run(False)
            broker.run(True)
            broker.release_memory()
            Logger.info(f'\n===over [{broker.broker_log_file}]===')
            del broker
        else:
            Logger.info(f'\n已存在: {period.value} {trade_stockNo} {date} {TradeMode.STATISTICS.value} {strategy_source}')
    else:
        Logger.error(f'\nserver error:{result.msg}')


def a_pool(args):
    Logger.info(f'\n{args}')
    run_statistics(*args)


def run():
    # ------
    trade_stockNos = ['MTX00']
    # trade_stockNos = ['TX00']
    # trade_stockNos = ['MTX00', 'TX00']
    # ------
    periodEnums = [PeriodEnum.Morning]
    # periodEnums = [PeriodEnum.Night]
    # periodEnums = [PeriodEnum.Morning, PeriodEnum.Night]
    # ------

    # d = datetime.datetime.now().strftime("%Y%m%d")
    # d = DatetimeUtil.local_today_to_str(ft='%Y%m%d')
    # dates = [AssetsHelper.find_last_final_date()]
    dates = AssetsHelper.list_deal_date(True)

    # 之後可參數化 ex: StraBvm[Bvm(1,2,3...)][fomSumV(3,2,1...)]
    morning_strategy_sources = [
        'StraBvm[root(multi_e2)][bvm(aa_noBlock_1)]               [fomKma(aa_slope_60)][containNight(true)]',
        'StraBvm[root(multi_e2)][bvm(aa_noBlock_1)][fomSumV(aa_1)][fomKma(aa_slope_60)][containNight(true)]',
        'StraBvm[root(multi_e2)][bvm(aa_noBlock_1)][fomSumV(aa_1)][fomKma(aa_slope_60)][foiKma(aa_slope_60)][containNight(true)]',
    ]
    night_strategy_sources = []

    # ------
    argsAry = []
    for trade_stockNo in trade_stockNos:
        for periodEnum in periodEnums:
            for date in dates:
                strategy_sources = []
                if periodEnum is PeriodEnum.Morning:
                    strategy_sources = morning_strategy_sources
                elif periodEnum is PeriodEnum.Night:
                    strategy_sources = night_strategy_sources
                for strategy_source in strategy_sources:
                    argsAry.append(
                        (periodEnum, date, trade_stockNo, strategy_source)
                    )
    #
    pool = mp.Pool(processes=8)
    Logger.info(f"共{len(argsAry)}筆")
    pool.map(a_pool, argsAry)
    pool.close()
    exit()


# ==================


# for bever dam strategy
if __name__ == '__main__':
    run()
    exit()
