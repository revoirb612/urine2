class Price:
    def __init__(self):
        self.last_modified = None
        self.sell_price_ratio = float()  # 매도세
        self.buy_price_ratio = float()  # 매수세

        self.main_buy_price = dict()
        self.main_sell_price = dict()


    def update_sell_price_ratio(self):
        pass

    def update_buy_price_ratio(self):
        pass

    def set_price(self, data):
        sell_price = set(data[0:10])  # 매도호가 1~10
        sell_quantity = data[20:30]  # 매도호가 1~10 수량
        buy_price = set(data[10:20])  # 매수호가 1~10
        buy_quantity = data[30:40]  # 매수호가 1~10 수량

        tmp_sell_dict = dict(zip(sell_price, sell_quantity))
        tmp_buy_dict = dict(zip(buy_price, buy_quantity))

        set(self.main_sell_price)
        set(self.main_buy_price)

        sell_price_first = 1
        buy_price_first = 2

        
