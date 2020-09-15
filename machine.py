from PyQt5.QAxContainer import *  # QAxWidget
from PyQt5.QtCore import *  # QEventLoop
from functions import Functions
from bid import Bid
from lupin import Lupin
import numpy as np
import pandas as pd


class Machine(QAxWidget):
    def __init__(self):
        super().__init__()
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.func = Functions()
        self.order = Bid()
        self.lupin = dict()

        self.login_loop = QEventLoop()
        self.tr_loop = QEventLoop()
        self.code_roop = QEventLoop()

        self.account = str()

        self.tr_screen = "1000"
        self.real_screen = "2000"

        self.connect_events()

        self.login()
        self.analyze()
        self.trade()

    def connect_events(self):
        self.OnEventConnect.connect(self.login_slot)
        self.OnReceiveTrData.connect(self.tr_slot)
        self.OnReceiveRealData.connect(self.real_slot)
        self.OnReceiveMsg.connect(self.msg_slot)

    def login(self):
        self.login_signal()
        self.tr_signal("예수금상세현황요청")

    def analyze(self):
        # self.tr_signal("주식기본정보요청")
        # self.tr_signal("주식외국인요청", stock_code="065650")
        # self.tr_signal("외인연속순매매상위요청")
        self.real_signal(" ", "215", "0")  # 초기화 및 장운영구분
        self.real_signal()

    def trade(self):
        pass

    def login_signal(self):
        self.dynamicCall(self.func.CommConnect)
        self.login_loop.exec_()

    def login_slot(self, err_code):
        self.get_login_info()
        self.login_loop.exit()

    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        print("%s %s %s %s" % (sScrNo, sRQName, sTrCode, msg))

    def tr_signal(self, tr, stock_code=None):
        if tr == "예수금상세현황요청":
            self.dynamicCall(self.func.SetInputValue, "계좌번호", self.account)
            self.dynamicCall(self.func.SetInputValue, "비밀번호", "")
            self.dynamicCall(self.func.SetInputValue, "비밀번호입력매체구분", "00")
            self.dynamicCall(self.func.SetInputValue, "조회구분", "2")
            self.dynamicCall(self.func.CommRqData, tr, "opw00001", "0", self.tr_screen)
            self.tr_loop.exec_()

        elif tr == "주식기본정보요청":
            self.dynamicCall(self.func.SetInputValue, "종목코드", "005930")
            self.dynamicCall(self.func.CommRqData, tr, "opt10001", "0", "3000")
            self.tr_loop.exec_()

        elif tr == "주식일봉차트조회":
            self.dynamicCall(self.func.SetInputValue, "종목코드", "005930")
            self.dynamicCall(self.func.SetInputValue, "수정주가구분", "1")
            self.dynamicCall(self.func.CommRqData, tr, "opt10081", "0", "4000")
            self.tr_loop.exec_()

        elif tr == "주식외국인요청":
            self.dynamicCall(self.func.SetInputValue, "종목코드", stock_code)
            self.dynamicCall(self.func.CommRqData, tr, "opt10008", "0", "5000")

        elif tr == "외인연속순매매상위요청":
            self.dynamicCall(self.func.SetInputValue, "시장구분", "000")
            self.dynamicCall(self.func.SetInputValue, "매매구분", "1")  # 1: 연속순매도 2: 연속순매수
            self.dynamicCall(self.func.SetInputValue, "기준일구분", "1")  # 0: 당일기준 1: 전일기준
            self.dynamicCall(self.func.CommRqData, tr, "OPT10035", "0", "6000")

    def tr_slot(self, sScrNo, sRqName, sTrCode, sRecordName, sPrevNext):
        if sRqName == "예수금상세현황요청":
            result_1 = self.dynamicCall(self.func.GetCommData, sTrCode, sRqName, 0, "예수금")
            result_2 = self.dynamicCall(self.func.GetCommData, sTrCode, sRqName, 0, "출금가능금액")
            print("예수금: %s원" % int(result_1))
            print("출금가능: %s원" % int(result_2))
            self.tr_loop.exit()

        elif sRqName == "주식기본정보요청":
            item_list = ["종목코드", "종목명", "자본금", "상장주식", "PER", "EPS", "ROE", "PBR"]
            for item in item_list:
                result = self.dynamicCall(self.func.GetCommData, sTrCode, sRqName, 0, item)
                print("%s: %s" % (item, result.strip()), end=" ")
            print()
            self.tr_loop.exit()

        elif sRqName == "주식일봉차트조회":
            result = self.dynamicCall(self.func.GetCommDataEx, sTrCode, sRqName)
            # 0: 없음, 1: 현재가(종가), 2: 거래량, 3: 거래대금, 4: 일자, 5: 시가, 6: 고가, 7: 저가

            def get_sum(ma, days):
                sum_list = []
                tmp = 0
                for day in result[:ma]:
                    tmp += int(day[1])
                sum_list.append(tmp)
                for i in range(days-1):
                    sum_list.append(sum_list[i] - int(result[i][1]) + int(result[i+ma][1]))
                return np.array(sum_list)

            arr = get_sum(5, 50)
            print(arr)
            self.tr_loop.exit()

        elif sRqName == "주식외국인요청":
            result = self.dynamicCall(self.func.GetCommDataEx, sTrCode, sRqName)
            # 0 일자, 1 종가, 2 전일대비, 3 거래량, 4 변동수량, 5 보유주식수, 6 비중, 취득가능주식수, 외국인한도, 외국인한도증감, 한도소진률
            df = pd.DataFrame(result)
            df.set_index(0, inplace=True)
            pd.set_option('display.max_row', 200)
            pd.set_option('display.max_columns', 15)
            print(df)

        elif sRqName == "외인연속순매매상위요청":
            result = self.dynamicCall(self.func.GetCommDataEx, sTrCode, sRqName)
            # 0: 종목코드 1: 종목명 2: 현재가 3: 전일대비기호 4: 전일대비 5: D-1 6: D-2 7: D-3 8: 합계 한도소진율 전일대비1 전일대비2 전일대비3
            df = pd.DataFrame(result)
            pd.set_option('display.max_columns', 15)
            print(df)

    def real_signal(self, sTrCodeList, sTrFidList, strOptType):
        result = self.dynamicCall(self.func.SetRealReg, self.real_screen, sTrCodeList, sTrFidList, strOptType)
        if result == 0:
            if sTrCodeList == " ":
                print("실시간 종목 등록(장운영구분)")
            else:
                self.lupin.update({sTrCodeList: Lupin()})  # 주의, 인스턴스 생성 시각과 데이터 수신 시각
                print("실시간 종목 등록(%s, %s)" % (sTrCodeList, strOptType))

    def real_slot(self, sCode, sRealType, sRealData):
        s20 = s10 = s15 = view = power = fact = None

        if sRealType == '장시작시간':
            result = self.dynamicCall(self.func.GetCommRealData, sCode, "215")
            if result.strip() != "":
                print(result)
            return 0

        elif sRealType == '주식체결':
            # data = {'time': time, 'price': price, 'qty': qty, 'view': view, 'power': power, 'fact': fact}

            data = {}
            for i in fid.keys():
                result = self.dynamicCall(self.func.GetCommRealData, sCode, str(i))
                data[i] = result.strip()

            # Lupin 에서 가중치 계산
            # view = 'neg'
            # if data[10] == data[27]:
            #     view = 'pos'

        elif sRealType == '주식호가잔량':
            # data = {'time': time, 'price': price, 'qty': qty, 'view': view, 'power': power, 'fact': fact}


            total_hope_sell = self.dynamicCall(self.func.GetCommRealData, sCode, "121")  # 매도호가총잔량
            total_hope_buy = self.dynamicCall(self.func.GetCommRealData, sCode, "125")  # 매수호가총잔량

            fact = "hope"  # real 체결, hope 호가
            s20 = self.dynamicCall(self.func.GetCommRealData, sCode, "21")  # 호가시간

            for i in range(81, 91):
                s15 = self.dynamicCall(self.func.GetCommRealData, sCode, str(i))  # 매도호가직전대비 1~10
                if s15 == 0:
                    pass
                else:
                    s10 = self.dynamicCall(self.func.GetCommRealData, sCode, str(i-40))  # 매도호가 1~10
                    power = abs(11-(i-80))  # 가중치 매도호가1 = 10, 매도호가10 = 1
                    if s15 > 0:  # 매도호가잔량 증가
                        view = 'pos'
                    elif s15 < 0:  # 매도호가잔량 감소
                        view = 'neg'

            for i in range(91, 101):
                s15 = self.dynamicCall(self.func.GetCommRealData, sCode, str(i))  # 매수호가직전대비 1~10
                if s15 == 0:
                    pass
                else:
                    s10 = self.dynamicCall(self.func.GetCommRealData, sCode, str(i-40))  # 매수호가 1~10
                    power = abs(11-(i-90))  # 가중치 매수호가1 = 10, 매수호가10 = 1
                    if s15 > 0:  # 매수호가잔량 증가
                        view = 'neg'
                    elif s15 < 0:  # 매수호가잔량 감소
                        view = 'pos'


        data = {'time': s20, 'price': s10, 'qty': s15, 'view': view, 'power': power, 'fact': fact}
        self.lupin.update(sCode, data)

    def order_signal(self, order_type, stock_code, quantity, price, bid_type, original_order=" "):
        sRQName = "매매주문"  # 사용자 구분명
        sScreenNo = "6000"  # 화면번호
        sAccNo = self.account  # 계좌번호 10자리
        nOrderType = order_type  # 주문유형, int, 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정
        sCode = stock_code  # 종목코드
        nQty = quantity  # 주문수량, int
        nPrice = price  # 주문가격, int
        sHogaGb = bid_type  # 거래구분, bid
        sOrgOrderNo = original_order  # 원주문번호, 신규주문에는 공백, 정정(취소) 주문할 원주문번호를 입력합니다.

        result = self.dynamicCall(self.func.SendOrder, sRQName, sScreenNo, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb, sOrgOrderNo)
        if result == 0:
            print("주문 성공")
        else:
            print("주문 실패")

    def get_login_info(self):
        info_list = ["ACCLIST", "USER_ID", "USER_NAME", "GetServerGubun"]
        for info in info_list:
            result = self.dynamicCall(self.func.GetLoginInfo, info)
            if info == "ACCLIST":
                result = result.split(";")[0]
                self.account = result
            print("%s: %s" % (info, result))

    def get_code_list(self, market="10"):
        result = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = result.split(";")
        code_list.pop()
        print("종목코드: %s개" % len(code_list))
