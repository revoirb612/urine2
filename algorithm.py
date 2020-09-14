class Algorithm:
    def __init__(self):
        self.present = list()
        self.deal = {1: [], 2: [], 3: []}

        self.call = {1: {'매수호가': [], '매도호가': []}, 2: [], 3: []}
        self.analysis = list()

    def update_deal(self, c20, c10, c27, c28, c15, c228):  # 27 (최우선)매도호가, 28 (최우선)매수호가
        if c10 == c27:  # 상승거래량
            pass
        elif c10 == c28:  # 하락거래량
            c15 *= -1

        self.present.append(c10)
        self.deal[c10].append(c15)

    def update_call(self, c41s, c51s, c61s, c71s, c81s, c91s):
        # 41~50 매도호가, 51~60 매수호가
        # 61~70 매도호가수량, 71~80 매수호가수량
        # 81~90 매도호가직전대비, 91~100 매수호가직전대비
        # 121 매도호가총잔량, 122 매도호가총잔량직전대비, 125 매수호가총잔량, 126 매수호가총잔량직전대비
        # 128 순매수잔량, 129 매수비율, 138 순매도잔량, 139 매도비율

        tmp_sell = dict(zip(c41s, c81s))
        tmp_buy = dict(zip(c51s, c91s))

        for key in tmp_sell.keys():
            if key in self.call.keys():
                self.call[key].append(tmp_sell[key])