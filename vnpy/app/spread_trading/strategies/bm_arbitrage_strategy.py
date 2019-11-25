from vnpy.trader.utility import BarGenerator, ArrayManager
from vnpy.app.spread_trading import (
    SpreadStrategyTemplate,
    SpreadAlgoTemplate,
    SpreadData,
    OrderData,
    TradeData,
    TickData,
    BarData
)


class BmArbitrageStrategy(SpreadStrategyTemplate):
    """"""

    author = "wwdd"

    boll_window = 20
    boll_dev = 2
    max_pos = 10
    payup = 10
    interval = 5
    total_pos = 50

    spread_pos = 0.0
    boll_up = 0.0
    boll_down = 0.0
    boll_mid = 0.0

    parameters = [
        "boll_window",
        "boll_dev",
        "max_pos",
        "payup",
        "interval"
    ]
    variables = [
        "spread_pos",
        "boll_up",
        "boll_down",
        "boll_mid"
    ]

    def __init__(
        self,
        strategy_engine,
        strategy_name: str,
        spread: SpreadData,
        setting: dict
    ):
        """"""
        super().__init__(
            strategy_engine, strategy_name, spread, setting
        )

        self.bg = BarGenerator(self.on_spread_bar)
        self.am = ArrayManager()

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")

        self.load_bar(10)

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

        self.put_event()

    def on_spread_data(self):
        """
        Callback when spread price is updated.
        """
        tick = self.get_spread_tick()
        self.on_spread_tick(tick)

    def on_spread_tick(self, tick: TickData):
        """
        Callback when new spread tick data is generated.
        """
        self.bg.update_tick(tick)

    def on_spread_bar(self, bar: BarData):
        """
        Callback when spread bar data is generated.
        """
        self.stop_all_algos()
        print(bar.close_price)

        if not self.spread_pos:
            if bar.close_price > 100:
                self.start_short_algo(
                    bar.close_price - 10,
                    self.max_pos,
                    payup=self.payup,
                    interval=self.interval
                )
            elif bar.close_price < 20:
                self.start_long_algo(
                    bar.close_price - 10,
                    self.max_pos,
                    payup=self.payup,
                    interval=self.interval
                )

        if self.spread_pos == self.total_pos:
            if bar.close_price > 100:
                pass
            elif bar.close_price < 60:
                self.start_long_algo(
                    bar.close_price + 10,
                    abs(self.spread_pos),
                    payup=self.payup,
                    interval=self.interval
                )
        elif self.spread_pos < self.total_pos:
            if bar.close_price > 100:
                self.start_short_algo(
                    bar.close_price - 10,
                    self.max_pos,
                    payup=self.payup,
                    interval=self.interval
                )
            elif bar.close_price < 60:
                self.start_short_algo(
                    bar.close_price - 10,
                    self.max_pos,
                    payup=self.payup,
                    interval=self.interval
                )
        # if not self.spread_pos:
        #     if bar.close_price >= 300:
        #         self.start_short_algo(
        #             bar.close_price - 10,
        #             self.max_pos,
        #             payup=self.payup,
        #             interval=self.interval
        #         )
        #     elif bar.close_price <= 100:
        #         self.start_long_algo(
        #             bar.close_price + 10,
        #             self.max_pos,
        #             payup=self.payup,
        #             interval=self.interval
        #         )
        # elif self.spread_pos < 0:
        #     if bar.close_price <= 300:
        #         self.start_long_algo(
        #             bar.close_price + 10,
        #             abs(self.spread_pos),
        #             payup=self.payup,
        #             interval=self.interval
        #         )
        # else:
        #     if bar.close_price <= 100:
        #         self.start_short_algo(
        #             bar.close_price - 10,
        #             abs(self.spread_pos),
        #             payup=self.payup,
        #             interval=self.interval
        #         )

    def on_spread_pos(self):
        """
        Callback when spread position is updated.
        """
        self.spread_pos = self.get_spread_pos()
        self.put_event()

    def on_spread_algo(self, algo: SpreadAlgoTemplate):
        """
        Callback when algo status is updated.
        """
        pass

    def on_order(self, order: OrderData):
        """
        Callback when order status is updated.
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        Callback when new trade data is received.
        """
        pass

    def stop_open_algos(self):
        """"""
        if self.buy_algoid:
            self.stop_algo(self.buy_algoid)

        if self.short_algoid:
            self.stop_algo(self.short_algoid)

    def stop_close_algos(self):
        """"""
        if self.sell_algoid:
            self.stop_algo(self.sell_algoid)

        if self.cover_algoid:
            self.stop_algo(self.cover_algoid)
