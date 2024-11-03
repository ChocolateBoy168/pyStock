from src.lib.my_lib.module.LoggerModule import Logger
from src.main.AppConst import OpenPositionKind, ClosePositionKind
from src.main.AppConst import TradeMode
from src.main.stock_market import Setting
from src.main.stock_market.Broker import Broker
from src.main.stock_market.strategy.strategy_name.abstract.AbstractStrategy import AbstractStrategy
from src.main.stock_market.trader.capital.CapitalStatisticsTrader import CapitalStatisticsTrader
from src.main.stock_market.trader.capital.abstract.AbstractCapitalTrader import AbstractCapitalTrader
from src.main.util.TickUtil import TickUtil


class StrategyTicks(AbstractStrategy):

    def __init__(self, broker: Broker, id, context):
        # init enable
        self.is_followMasterSumVolume_enable = 'fomSumV' in context
        self.is_avoidSlaveSumVolume_enable = 'aosSumV' in context
        self.is_beverDam_enable = 'bvm' in context
        self.is_indexKma_enable = 'foiKma' in context
        self.is_indexKmaBS_enable = self.is_indexKma_enable and ('rule' in context['foiKma']) and (context['foiKma']['rule'] == 'big_small')
        self.is_indexKmaSlope_enable = self.is_indexKma_enable and ('rule' in context['foiKma']) and (context['foiKma']['rule'] == 'slope')
        self.is_followMasterKma_enable = 'fomKma' in context
        self.is_followMasterKmaSlope_enable = self.is_followMasterKma_enable and ('rule' in context['fomKma']) and (context['fomKma']['rule'] == 'slope')
        self.is_specificRange_enable = 'specRng' in context
        self.is_ignoreFirstTick_enable = ('ignore_first_tick' in context) and (context['ignore_first_tick'] is True)

        super().__init__(broker, id, context)

        self.tick_column = [
            'status', 'stockNo', 'nPtr', 'lDate', 'lTimehms', 'lTimemillismicros',
            'nBid', 'nAsk', 'nClose', 'nQty', 'nSimulate', 'addSubNQty'
        ]

        self.tradeStockTick = self.signal.obtain_stockTick(self.broker.trade_stockNo)


    def rest_variables(self):
        super().rest_variables()

    # 在[是否能新倉]之前 , 若為歷史的訊號, 就排除掉
    def before_could_open_position(self):
        if self.tradeStockTick.currentTick is None:
            return False
        default = True
        trade_mode = self.broker.trader.trade_mode
        if trade_mode == TradeMode.REAL or trade_mode == TradeMode.SIMULATE_REAL or trade_mode == TradeMode.SIMULATE_STATISTICS:
            # 因抓多訊號 tick history 的時間 可能彼此相差太多 , 所以  只要其中之一訊號 還停留在history 就不下單
            for stockNo in self.broker.requestTicks_stockNos:
                stockTick = self.signal.obtain_stockTick(stockNo)
                if stockTick is None:
                    Logger.warning(f'stockNo ${stockNo} can not mapping to stockTick')
                else:
                    try:
                        if (stockTick.currentTick is None) or (stockTick.currentTick['status'] == 'history'):
                            default = False
                            break
                    except Exception as e:
                        Logger.error(e)
                        Logger.warning(f'stockTick.currentTick = {stockTick.currentTick}')
        elif trade_mode == TradeMode.STATISTICS:
            if self.broker.is_morningTradePeriod_and_containNightSignal:
                # 含收夜盤訊號的早盤交易策略 => 只要多訊號其中之一,是夜盤訊號就不開新倉
                for stockNo in self.broker.requestTicks_stockNos:
                    stockTick = self.signal.obtain_stockTick(stockNo)
                    if stockTick is None:
                        Logger.warning(f'stockNo ${stockNo} can not mapping to stockTick')
                    else:
                        try:
                            if stockTick.currentTick is not None:
                                if TickUtil.is_night_period_for_tick(stockTick.currentTick):
                                    default = False
                                    break
                        except Exception as e:
                            Logger.error(e)
                            Logger.warning(f'stockTick.currentTick = {stockTick.currentTick}')
            pass
        return default

    def monitor(self):
        trader: AbstractCapitalTrader = self.trader
        orderHandler = trader.orderHandler

        # 已移至 stockTick's upgrade_signal
        # df = df[(df["nSimulate"] == 0)]
        # if tick['nSimulate'] == 1:
        # 	return False

        # true 表示 trader 尚在處理訂單
        if trader.ordering_status is True:
            return False

        # step 監控是否有單 要平倉 , 若有平倉會觸發 ordering_status 為 True
        open_records = orderHandler.list_opened_records(self.id)
        if len(open_records) > 0:
            # if self.trader.is_real_trade():
            # 	Logger.info(f'策略${self.id}有未平倉的單')
            for open_record in open_records:
                # if self.trader.is_real_trade():
                # 	Logger.info(open_record.to_json_string())
                could, close_position_kind = self.could_close_position(open_record)
                if could is True:
                    # Logger.info(f'平倉kind = {close_position_kind} , from Open 訂單 = {open_record}')
                    self.close_position(close_position_kind, open_record)

        # step 檢查是否 進場的時間之外 (表示不在 start to last  時間以內)
        if self.is_enter_time_not_in_start_to_late() is True:
            return False

        # step 檢查是否expired time , 沒有expired才能建新倉
        if self.is_expired() is True:
            return False

        # step 監控是否要 建立新倉位
        if self.trader.ordering_status is False:
            if len(open_records) < Setting.Max_Num_Open_Order:
                if self.before_could_open_position() is True:
                    could, open_position_kind = self.could_open_position()
                    if could is True:
                        # Logger.info(f'新倉kind = {open_position_kind}')
                        self.open_position(open_position_kind)

    def build(self):
        return super().build()

    # 是否可以建新倉 for buy call or  buy sell
    def could_open_position(self):
        return None, None

    # 是否可以平倉
    def could_close_position(self, open_record):
        return False, None

    # 新倉
    def open_position(self, kind: OpenPositionKind):
        trader: AbstractCapitalTrader = self.trader
        trader.ordering_status = True
        message, code = self.trader.open_position(kind)
        if code == 0:
            keyNo = message # 當 code=0 時, message is keyNo

            if keyNo not in trader.orderHandler.keyNo_mapping_strategy:
                trader.orderHandler.keyNo_mapping_strategy[keyNo] = self.id
            else:
                Logger.error(f'[keyNo_mapping_strategy]  建立新倉時, 委託keyNo {keyNo}, 為何已存在 {trader.orderHandler.keyNo_mapping_strategy}')

            #  2021/07/18 觀察 看是否在這  把 當時 可能進場 交易的tick 給記錄下來 ... 用來之後 judge stop_profit or stop_loss
            if keyNo not in trader.orderHandler.keyNo_mapping_tradeStockTick:
                trader.orderHandler.keyNo_mapping_tradeStockTick[keyNo] = self.tradeStockTick.currentTick.copy() # check有copy => id(self.tradeStockTick.currentTick.copy())
            else:
                Logger.error(f'[keyNo_mapping_tradeStockTick] 建立新倉時, 委託keyNo {keyNo}, 為何已存在  {trader.orderHandler.keyNo_mapping_tradeStockTick}')

            if trader.is_statistics_trade() or trader.is_simulate_statistics_trade():
                # trader.orderHandler.set_use_strategy(keyNo)
                trader: CapitalStatisticsTrader = self.trader
                cache = trader.cache_for_call_replayEvent_onNewData_callback[keyNo]
                trader.csc_api.SKReplyLibEvent_OnNewData_callback(
                    cache['buy_sell'],
                    cache['open_close'],
                    cache['tick'],
                    cache['custom_key_no'],
                    cache['open_order']
                )
                trader.cache_for_call_replayEvent_onNewData_callback.pop(keyNo)

        return message, code

    # 平倉
    def close_position(self, close_position_kind: ClosePositionKind, open_order):
        trader: AbstractCapitalTrader = self.trader
        self.trader.ordering_status = True
        message, code = self.trader.close_position(close_position_kind, open_order)
        if code == 0:
            keyNo = message
            if keyNo not in trader.orderHandler.keyNo_mapping_strategy:
                trader.orderHandler.keyNo_mapping_strategy[keyNo] = self.id
            else:
                Logger.error(f'建立平倉時 ,委託keyNo {keyNo} ,為何已存在 {trader.orderHandler.keyNo_mapping_strategy}')

            # 平倉後 為新倉單 設置 關聯平倉的keyNo
            open_order.close_position_ref_keyNo = keyNo

            if trader.is_statistics_trade() or trader.is_simulate_statistics_trade():
                # trader.orderHandler.set_use_strategy(keyNo)
                trader: CapitalStatisticsTrader = self.trader
                cache = trader.cache_for_call_replayEvent_onNewData_callback[keyNo]
                trader.csc_api.SKReplyLibEvent_OnNewData_callback(
                    cache['buy_sell'],
                    cache['open_close'],
                    cache['tick'],
                    cache['custom_key_no'],
                    cache['open_order']
                )
                trader.cache_for_call_replayEvent_onNewData_callback.pop(keyNo)

        return message, code

    # ==================================

    # region [last enter time]
    def is_enter_time_not_in_start_to_late(self):
        if self.tradeStockTick.currentTick is not None:
            return TickUtil.is_enter_time_not_in_start_to_late(
                self.tradeStockTick.currentTick['lTimehms'],
                self.context['morning_start_enter_time'], self.context['morning_last_enter_time'],
                self.context['night_start_enter_time'], self.context['night_last_enter_time']
            )
        return None

    # endregion

    # region [expired]
    def is_expired(self):
        if self.tradeStockTick.currentTick is not None:
            lTimehms = self.tradeStockTick.currentTick['lTimehms']
            morning_stop_expired_time = self.context['morning_stop_expired_time']
            night_stop_expired_time = self.context['night_stop_expired_time']
            return TickUtil.is_expired(
                lTimehms, morning_stop_expired_time, night_stop_expired_time
            )
        return None

    # endregion

    # ==================================

    # region [followMasterSumVolume]  跟隨主力的量

    def could_open_position_for_followMasterSumVolume(self, could_open_position, open_position_kind):
        info = ''
        rs = []
        stockNos_achieve_of = self.context['fomSumV']['stockNos_achieve_of']['in']
        if open_position_kind == OpenPositionKind.BUY_CALL:
            for stockNo in self.broker.requestTicks_stockNos:
                stockTick = self.signal.obtain_stockTick(stockNo)
                call_sum_volume = +(self.context['fomSumV']['stockNo'][stockNo]['in'])
                if stockTick.master_volume >= call_sum_volume:  # 新倉想做多時,主力的量大過於門檻,考慮進場
                    rs.append(True)
                else:
                    rs.append(False)
                info += f'\n\t{stockNo}主力的量 : {stockTick.master_volume}'
        elif open_position_kind == OpenPositionKind.BUY_PUT:
            for stockNo in self.broker.requestTicks_stockNos:
                stockTick = self.signal.obtain_stockTick(stockNo)
                put_sum_volume = -(self.context['fomSumV']['stockNo'][stockNo]['in'])
                if stockTick.master_volume <= put_sum_volume:  # 新倉想做空時,主力的量小過於門檻,考慮進場
                    rs.append(True)
                else:
                    rs.append(False)
                info += f'\n\t{stockNo}主力的量 : {stockTick.master_volume}'

        if stockNos_achieve_of == 'anyOf':
            could_open_position = any(rs)  # any([]) is False
            info += f'\n\tany({rs}) = {could_open_position}'
        elif stockNos_achieve_of == 'allOf':
            could_open_position = all(rs)  # all([]) is True
            info += f'\n\tall({rs}) = {could_open_position}'

        return could_open_position, info

    def could_close_position_for_followMasterSumVolume(self, could_close_position, open_position_kind):
        info = ''
        rs = []
        stockNos_achieve_of = self.context['fomSumV']['stockNos_achieve_of']['out']
        if open_position_kind == OpenPositionKind.BUY_CALL:
            for stockNo in self.broker.requestTicks_stockNos:
                stockTick = self.signal.obtain_stockTick(stockNo)
                call_sum_volume = +(self.context['fomSumV']['stockNo'][stockNo]['out'])
                if stockTick.master_volume <= call_sum_volume:  # 做多後要平倉時,主力的量小過於門檻,考慮出場
                    rs.append(True)
                else:
                    rs.append(False)
                info += f'\n\t{stockNo}主力的量 : {stockTick.master_volume}'
        elif open_position_kind == OpenPositionKind.BUY_PUT:
            for stockNo in self.broker.requestTicks_stockNos:
                stockTick = self.signal.obtain_stockTick(stockNo)
                put_sum_volume = -(self.context['fomSumV']['stockNo'][stockNo]['out'])
                if stockTick.master_volume >= put_sum_volume:  # 做空後要平倉時,主力的量大過於門檻,考慮出場
                    rs.append(True)
                else:
                    rs.append(False)
                info += f'\n\t{stockNo}主力的量 : {stockTick.master_volume}'

        if stockNos_achieve_of == 'anyOf':
            could_close_position = any(rs)  # any([]) is False
            info += f'\n\tany({rs}) = {could_close_position}'
        elif stockNos_achieve_of == 'allOf':
            could_close_position = all(rs)  # all([]) is True
            info += f'\n\tall({rs}) = {could_close_position}'

        return could_close_position, info

    # endregion

    # region [avoidSlaveSumVolume] 避開散戶的量

    def could_open_position_for_avoidSlaveSumVolume(self, could_open_position, open_position_kind):
        info = ''
        rs = []
        stockNos_achieve_of = self.context['aosSumV']['stockNos_achieve_of']['in']
        if open_position_kind == OpenPositionKind.BUY_CALL:
            for stockNo in self.broker.requestTicks_stockNos:
                stockTick = self.signal.obtain_stockTick(stockNo)
                sum_volume = self.context['aosSumV']['stockNo'][stockNo]['in']
                if sum_volume != None:
                    call_sum_volume = +(sum_volume)
                    if stockTick.slave_volume <= call_sum_volume:  # 新倉做多時, 奴隸的量小於門檻, 表示有避開, 考慮進場
                        rs.append(True)
                    else:
                        rs.append(False)
                    info += f'\n\t{stockNo}奴隸的量 : {stockTick.slave_volume}'
        elif open_position_kind == OpenPositionKind.BUY_PUT:
            for stockNo in self.broker.requestTicks_stockNos:
                stockTick = self.signal.obtain_stockTick(stockNo)
                sum_volume = -(self.context['aosSumV']['stockNo'][stockNo]['in'])
                if sum_volume != None:
                    put_sum_volume = -(sum_volume)
                    if stockTick.slave_volume >= put_sum_volume:  # 新倉做空時, 奴隸的量大於門檻, 表示有避開, 考慮進場
                        rs.append(True)
                    else:
                        rs.append(False)
                    info += f'\n\t{stockNo}奴隸的量 : {stockTick.slave_volume}'

        if stockNos_achieve_of == 'anyOf':
            could_open_position = any(rs)  # any([]) is False
            info += f'\n\tany({rs}) = {could_open_position}'
        elif stockNos_achieve_of == 'allOf':
            could_open_position = all(rs)  # all([]) is True
            info += f'\n\tall({rs}) = {could_open_position}'

        return could_open_position, info

    def could_close_position_for_avoidSlaveSumVolume(self, could_close_position, open_position_kind):
        info = ''
        rs = []
        stockNos_achieve_of = self.context['aosSumV']['stockNos_achieve_of']['out']
        if open_position_kind == OpenPositionKind.BUY_CALL:
            for stockNo in self.broker.requestTicks_stockNos:
                stockTick = self.signal.obtain_stockTick(stockNo)
                sum_volume = self.context['aosSumV']['stockNo'][stockNo]['out']
                if sum_volume != None:  # todo debug null
                    call_sum_volume = +(sum_volume)
                    if stockTick.slave_volume >= call_sum_volume:  # 做多後要平倉時, 奴隸的量大於門檻, 表示沒避開, 考慮出場
                        rs.append(True)
                    else:
                        rs.append(False)
                info += f'\n\t{stockNo}奴隸的量 : {stockTick.slave_volume}'
        elif open_position_kind == OpenPositionKind.BUY_PUT:
            for stockNo in self.broker.requestTicks_stockNos:
                stockTick = self.signal.obtain_stockTick(stockNo)
                sum_volume = self.context['aosSumV']['stockNo'][stockNo]['out']
                if sum_volume != None:  # todo debug null
                    put_sum_volume = -(sum_volume)
                    if stockTick.slave_volume <= put_sum_volume:  # 做空後要平倉時, 奴隸的量小於門檻, 表示沒避開, 考慮出場
                        rs.append(True)
                    else:
                        rs.append(False)
                info += f'\n\t{stockNo}奴隸的量 : {stockTick.slave_volume}'

        if stockNos_achieve_of == 'anyOf':
            could_close_position = any(rs)  # any([]) is False
            info += f'\n\tany({rs}) = {could_close_position}'
        elif stockNos_achieve_of == 'allOf':
            could_close_position = all(rs)  # all([]) is True
            info += f'\n\tall({rs}) = {could_close_position}'

        return could_close_position, info

    # endregion

    # ==================================

    # region [indexKma]

    def obtain_indexKma_rate_of_second(self):
        if self.is_indexKma_enable:
            return self.context['foiKma']['rate_of_second']
        return None

    def has_indexKma_setting_for_stockNo(self, stockNo):
        if self.is_indexKma_enable:
            if 'stockNo' in self.context['foiKma']:
                if stockNo in self.context['foiKma']['stockNo']:
                    return True
        return False

    def list_indexKma_in_mas(self, stockNo):
        return self.context['foiKma']['stockNo'][stockNo]['in']

    def list_indexKma_out_mas(self, stockNo):
        return self.context['foiKma']['stockNo'][stockNo]['out']

    def list_indexKma_mas(self, stockNo):
        kmaBS_in = self.list_indexKma_in_mas(stockNo)
        kmaBS_out = self.list_indexKma_out_mas(stockNo)
        mas = list(set().union(kmaBS_in, kmaBS_out))
        if mas is not None:
            mas.sort()
        return mas

    # endregion

    # region [indexKmaBS]

    def could_open_position_for_indexKmaBS(self, could_open_position, open_position_kind):
        info = ""
        stockNos_achieve_of = self.context['foiKma']['stockNos_achieve_of']['in']
        rs = []
        for stockNo in self.broker.requestTicks_stockNos:
            stockTick = self.signal.obtain_stockTick(stockNo)
            if stockTick.has_indexKma_setting:
                ma = stockTick.indexKma.current_k.ma
                kmaBS_in = self.list_indexKma_in_mas(stockNo)
                if len(kmaBS_in) >= 2:
                    ary = []
                    for index in range(0, len(kmaBS_in) - 1):
                        small_ma = ma[kmaBS_in[index]]
                        big_ma = ma[kmaBS_in[index + 1]]
                        small_ma_val = small_ma['val'] if small_ma is not None and 'val' in small_ma else None
                        big_ma_val = big_ma['val'] if big_ma is not None and 'val' in big_ma else None
                        if (small_ma_val is None) or (big_ma_val is None):  # 一般而言,big_ma_val會先為None,有None不能比較
                            pass
                        else:
                            if open_position_kind == OpenPositionKind.BUY_CALL:
                                ary.append(small_ma_val >= big_ma_val)
                            elif open_position_kind == OpenPositionKind.BUY_PUT:
                                ary.append(small_ma_val <= big_ma_val)
                    if len(ary) > 0:
                        rs.append(all(ary))  # todo all 也要拆出有anyOf allOf的參數
                    else:
                        rs.append(False)
                    info += f'\n\t{stockNo} | {kmaBS_in} | {ma} '

        if stockNos_achieve_of == 'anyOf':
            could_open_position = any(rs)  # any([]) is False
            info += f'\n\tany({rs}) = {could_open_position}'
        elif stockNos_achieve_of == 'allOf':
            could_open_position = all(rs)  # all([]) is True
            info += f'\n\tall({rs}) = {could_open_position}'

        return could_open_position, info

    def could_close_position_for_indexKmaBS(self, could_close_position, open_position_kind):
        info = ""
        stockNos_achieve_of = self.context['foiKma']['stockNos_achieve_of']['out']
        rs = []
        for stockNo in self.broker.requestTicks_stockNos:
            stockTick = self.signal.obtain_stockTick(stockNo)
            if stockTick.has_indexKma_setting:
                ma = stockTick.indexKma.current_k.ma
                kmaBS_out = self.list_indexKma_out_mas(stockNo)
                if len(kmaBS_out) >= 2:
                    ary = []
                    for index in range(0, len(kmaBS_out) - 1):
                        small_ma = ma[kmaBS_out[index]]
                        big_ma = ma[kmaBS_out[index + 1]]
                        small_ma_val = small_ma['val'] if small_ma is not None and 'val' in small_ma else None
                        big_ma_val = big_ma['val'] if big_ma is not None and 'val' in big_ma else None
                        if (small_ma_val is None) or (big_ma_val is None):  # 一般而言,big_ma_val會先為None,有None不能比較
                            pass
                        else:
                            if open_position_kind == OpenPositionKind.BUY_CALL:
                                ary.append(small_ma_val < big_ma_val)
                            elif open_position_kind == OpenPositionKind.BUY_PUT:
                                ary.append(small_ma_val > big_ma_val)
                    if len(ary) > 0:
                        rs.append(all(ary))  # todo all 也要拆出有anyOf allOf的參數
                    else:
                        rs.append(False)
                    info += f'\n\t{stockNo} | {kmaBS_out} | {ma} '

        if stockNos_achieve_of == 'anyOf':
            could_close_position = any(rs)  # any([]) is False
            info += f'\n\tany({rs}) = {could_close_position}'
        elif stockNos_achieve_of == 'allOf':
            could_close_position = all(rs)  # all([]) is True
            info += f'\n\tall({rs}) = {could_close_position}'

        return could_close_position, info

    # endregion

    # region [indexKmaSlope]

    def could_open_position_for_indexKmaSlope(self, could_open_position, open_position_kind):
        info = ""
        stockNos_achieve_of = self.context['foiKma']['stockNos_achieve_of']['in']
        rs = []
        for stockNo in self.broker.requestTicks_stockNos:
            stockTick = self.signal.obtain_stockTick(stockNo)
            if stockTick.has_indexKma_setting:
                ma = stockTick.indexKma.current_k.ma
                kmaSlope_in = self.list_indexKma_in_mas(stockNo)
                if len(kmaSlope_in) >= 1:
                    ary = []
                    for index in range(0, len(kmaSlope_in)):
                        ma_obj = ma[kmaSlope_in[index]]
                        ma_slope = ma_obj['slope'] if ma_obj is not None and 'slope' in ma_obj else None
                        if ma_slope is None:
                            pass
                        else:
                            if open_position_kind == OpenPositionKind.BUY_CALL:
                                ary.append(ma_slope >= 0)  # todo 是否通過for[等於]的的參數
                            elif open_position_kind == OpenPositionKind.BUY_PUT:
                                ary.append(ma_slope <= 0)  # todo 是否通過for[等於]的的參數
                    if len(ary) > 0:
                        rs.append(all(ary))  # todo all 也要拆出有anyOf allOf的參數
                    else:
                        rs.append(False)
                    info += f'\n\t{stockNo} | {kmaSlope_in} | {ma} '

        if stockNos_achieve_of == 'anyOf':
            could_open_position = any(rs)  # any([]) is False
            info += f'\n\tany({rs}) = {could_open_position}'
        elif stockNos_achieve_of == 'allOf':
            could_open_position = all(rs)  # all([]) is True
            info += f'\n\tall({rs}) = {could_open_position}'

        return could_open_position, info

    def could_close_position_for_indexKmaSlope(self, could_close_position, open_position_kind):
        stockNos_achieve_of = self.context['foiKma']['stockNos_achieve_of']['out']
        info = ""
        rs = []
        for stockNo in self.broker.requestTicks_stockNos:
            stockTick = self.signal.obtain_stockTick(stockNo)
            if stockTick.has_indexKma_setting:
                ma = stockTick.indexKma.current_k.ma
                kmaSlope_out = self.list_indexKma_out_mas(stockNo)
                if len(kmaSlope_out) >= 1:
                    ary = []
                    for index in range(0, len(kmaSlope_out)):
                        ma_obj = ma[kmaSlope_out[index]]
                        ma_slope = ma_obj['slope'] if ma_obj is not None and 'slope' in ma_obj else None
                        if ma_slope is None:
                            pass
                        else:
                            if open_position_kind == OpenPositionKind.BUY_CALL:
                                ary.append(ma_slope < 0)
                            elif open_position_kind == OpenPositionKind.BUY_PUT:
                                ary.append(ma_slope > 0)
                    if len(ary) > 0:
                        rs.append(all(ary))  # todo all 也要拆出有anyOf allOf的參數
                    else:
                        rs.append(False)
                    info += f'\n\t{stockNo} | {kmaSlope_out} | {ma} '

        if stockNos_achieve_of == 'anyOf':
            could_close_position = any(rs)  # any([]) is False
            info += f'\n\tany({rs}) = {could_close_position}'
        elif stockNos_achieve_of == 'allOf':
            could_close_position = all(rs)  # all([]) is True
            info += f'\n\tall({rs}) = {could_close_position}'

        return could_close_position, info

    # endregion

    # ==================================

    # region [followMasterKma]

    def obtain_followMasterKma_rate_of_second(self):
        if self.is_followMasterKma_enable:
            return self.context['fomKma']['rate_of_second']
        return None

    def has_followMasterKma_setting_for_stockNo(self, stockNo):
        if self.is_followMasterKma_enable:
            if 'stockNo' in self.context['fomKma']:
                if stockNo in self.context['fomKma']['stockNo']:
                    return True
        return False

    def list_followMasterKma_in_mas(self, stockNo):
        return self.context['fomKma']['stockNo'][stockNo]['in']

    def list_followMasterKma_out_mas(self, stockNo):
        return self.context['fomKma']['stockNo'][stockNo]['out']

    def list_followMasterKma_mas(self, stockNo):
        kmaBS_in = self.list_followMasterKma_in_mas(stockNo)
        kmaBS_out = self.list_followMasterKma_out_mas(stockNo)
        mas = list(set().union(kmaBS_in, kmaBS_out))
        if mas is not None:
            mas.sort()
        return mas

    # endregion

    # region [followMasterKmaSlope]

    def could_open_position_for_followMasterKmaSlope(self, could_open_position, open_position_kind):
        info = ""
        stockNos_achieve_of = self.context['fomKma']['stockNos_achieve_of']['in']
        rs = []
        for stockNo in self.broker.requestTicks_stockNos:
            stockTick = self.signal.obtain_stockTick(stockNo)
            if stockTick.has_followMasterKma_setting:
                ma = stockTick.followMasterKma.current_k.ma
                kmaSlope_in = self.list_followMasterKma_in_mas(stockNo)
                if len(kmaSlope_in) >= 1:
                    ary = []
                    for index in range(0, len(kmaSlope_in)):
                        ma_obj = ma[kmaSlope_in[index]]
                        ma_slope = ma_obj['slope'] if ma_obj is not None and 'slope' in ma_obj else None
                        if ma_slope is None:
                            pass
                        else:
                            if open_position_kind == OpenPositionKind.BUY_CALL:
                                ary.append(ma_slope >= 0)  # todo 是否通過for[等於]的的參數
                            elif open_position_kind == OpenPositionKind.BUY_PUT:
                                ary.append(ma_slope <= 0)  # todo 是否通過for[等於]的的參數
                    if len(ary) > 0:
                        rs.append(all(ary))  # todo all 也要拆出有anyOf allOf的參數
                    else:
                        rs.append(False)
                    info += f'\n\t{stockNo} | {kmaSlope_in} | {ma} '

        if stockNos_achieve_of == 'anyOf':
            could_open_position = any(rs)  # any([]) is False
            info += f'\n\tany({rs}) = {could_open_position}'
        elif stockNos_achieve_of == 'allOf':
            could_open_position = all(rs)  # all([]) is True
            info += f'\n\tall({rs}) = {could_open_position}'

        return could_open_position, info

    def could_close_position_for_followMasterKmaSlope(self, could_close_position, open_position_kind):
        stockNos_achieve_of = self.context['fomKma']['stockNos_achieve_of']['out']
        info = ""
        rs = []
        for stockNo in self.broker.requestTicks_stockNos:
            stockTick = self.signal.obtain_stockTick(stockNo)
            if stockTick.has_followMasterKma_setting:
                ma = stockTick.followMasterKma.current_k.ma
                kmaSlope_out = self.list_followMasterKma_out_mas(stockNo)
                if len(kmaSlope_out) >= 1:
                    ary = []
                    for index in range(0, len(kmaSlope_out)):
                        ma_obj = ma[kmaSlope_out[index]]
                        ma_slope = ma_obj['slope'] if ma_obj is not None and 'slope' in ma_obj else None
                        if ma_slope is None:
                            pass
                        else:
                            if open_position_kind == OpenPositionKind.BUY_CALL:
                                ary.append(ma_slope < 0)
                            elif open_position_kind == OpenPositionKind.BUY_PUT:
                                ary.append(ma_slope > 0)
                    if len(ary) > 0:
                        rs.append(all(ary))  # todo all 也要拆出有anyOf allOf的參數
                    else:
                        rs.append(False)
                    info += f'\n\t{stockNo} | {kmaSlope_out} | {ma} '

        if stockNos_achieve_of == 'anyOf':
            could_close_position = any(rs)  # any([]) is False
            info += f'\n\tany({rs}) = {could_close_position}'
        elif stockNos_achieve_of == 'allOf':
            could_close_position = all(rs)  # all([]) is True
            info += f'\n\tall({rs}) = {could_close_position}'

        return could_close_position, info

    # endregion

    # ==================================

    # region [specificRange]

    def could_open_position_for_specificRange(self, could_open_position, open_position_kind):
        info = ''
        rs = []
        stockNos_achieve_of = self.context['specRng']['stockNos_achieve_of']['in']
        if open_position_kind == OpenPositionKind.BUY_CALL:
            for stockNo in self.broker.requestTicks_stockNos:
                call_price_range = self.context['specRng']['stockNo'][stockNo]['open']['call']
                if (call_price_range != None) and len(call_price_range) == 2:
                    tradePeriodVal = self.broker.periodEnum.value
                    # first_open_price = self.tradeStockTick.first_open_price[tradePeriodVal]
                    stockTick = self.signal.obtain_stockTick(stockNo)
                    first_open_price = stockTick.first_open_price[tradePeriodVal]
                    offset = TickUtil.extract_int_price(stockTick.currentTick) - first_open_price
                    if (call_price_range[0] <= offset) and (offset <= call_price_range[1]):
                        rs.append(True)
                        info += f'\n\t{stockNo} 漲跌[{offset}]點 [有] 介於進場 [做多]的範圍 {call_price_range}'
                    else:
                        rs.append(False)
                        info += f'\n\t{stockNo} 漲跌[{offset}]點 [無] 介於進場 [做多]的範圍 {call_price_range}'

        elif open_position_kind == OpenPositionKind.BUY_PUT:
            for stockNo in self.broker.requestTicks_stockNos:
                put_price_range = self.context['specRng']['stockNo'][stockNo]['open']['put']
                if (put_price_range != None) and len(put_price_range) == 2:
                    tradePeriodVal = self.broker.periodEnum.value
                    # first_open_price = self.tradeStockTick.first_open_price[tradePeriodVal]
                    stockTick = self.signal.obtain_stockTick(stockNo)
                    first_open_price = stockTick.first_open_price[tradePeriodVal]
                    offset = TickUtil.extract_int_price(stockTick.currentTick) - first_open_price
                    if (put_price_range[0] <= offset) and (offset <= put_price_range[1]):
                        rs.append(True)
                        info += f'\n\t{stockNo} 漲跌[{offset}]點 [有] 介於進場 [做空]的範圍 {put_price_range}'
                    else:
                        rs.append(False)
                        info += f'\n\t{stockNo} 漲跌[{offset}]點 [無] 介於進場 [做空]的範圍 {put_price_range}'

        if stockNos_achieve_of == 'anyOf':
            could_open_position = any(rs)  # any([]) is False
            info += f'\n\tany({rs}) = {could_open_position}'
        elif stockNos_achieve_of == 'allOf':
            could_open_position = all(rs)  # all([]) is True
            info += f'\n\tall({rs}) = {could_open_position}'

        return could_open_position, info

    # endregion

    # ==================================
    '''
    '''
