import pandas as pd


class Lupin:
    def __init__(self):
        self.big_hands = None
        self.data = pd.DataFrame()
        self.

    def update(self, sCode, data)
        if sRealType == "주식체결":
            d_type = 1
            time = c20
            if c10 == c27:  # 상승거래량
                view = 1
            elif c10 == c28:  # 하락거래량
                view = -1
            qty = c15
            price = c10
        elif sRealType == "주식호가잔량":
            d_type = 0
            time = c21

        tmp = {'time': time, 'type': d_type, 'view': view, 'qty': qty, 'price': price}