from PyQt5.QAxContainer import *  # QAxWidget
from PyQt5.QtCore import *  # QEventLoop
import numpy as np
import pandas as pd
import functions


class Machine(QAxWidget):
    def __init__(self):
        super().__init__()
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.func = functions.Functions()

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
        self.tr_signal("주식기본정보요청")
        self.tr_signal("주식외국인요청")

    def trade(self):
        self.real_signal()  # 초기화
        self.real_signal(sTrCodeList="005930", sTrFidList="214")

    def login_signal(self):
        self.dynamicCall(self.func.CommConnect)
        print("로그인 시도 중...")
        self.login_loop.exec_()

    def login_slot(self, err_code):
        self.get_login_info()
        self.login_loop.exit()

    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        print("-" * 90)
        print("%s %s %s %s" % (sScrNo, sRQName, sTrCode, msg))
        print("-" * 90)

    def tr_signal(self, tr_name):
        if tr_name == "예수금상세현황요청":
            self.dynamicCall(self.func.SetInputValue, "계좌번호", self.account)
            self.dynamicCall(self.func.SetInputValue, "비밀번호", "")
            self.dynamicCall(self.func.SetInputValue, "비밀번호입력매체구분", "00")
            self.dynamicCall(self.func.SetInputValue, "조회구분", "2")
            self.dynamicCall(self.func.CommRqData, tr_name, "opw00001", "0", self.tr_screen)
            self.tr_loop.exec_()

        elif tr_name == "주식기본정보요청":
            self.dynamicCall(self.func.SetInputValue, "종목코드", "005930")
            self.dynamicCall(self.func.CommRqData, tr_name, "opt10001", "0", "3000")
            self.tr_loop.exec_()

        elif tr_name == "주식일봉차트조회":
            self.dynamicCall(self.func.SetInputValue, "종목코드", "005930")
            # self.dynamicCall(self.func.SetInputValue, "기준일자", "20200901")
            self.dynamicCall(self.func.SetInputValue, "수정주가구분", "1")
            self.dynamicCall(self.func.CommRqData, tr_name, "opt10081", "0", "4000")
            self.tr_loop.exec_()

        elif tr_name == "주식외국인요청":
            self.dynamicCall(self.func.SetInputValue, "종목코드", "005930")
            self.dynamicCall(self.func.CommRqData, tr_name, "opt10008", "0", "5000")

    def tr_slot(self, sScrNo, sRqName, sTrCode, sRecordName, sPrevNext):
        if sRqName == "예수금상세현황요청":
            result_1 = self.dynamicCall(self.func.GetCommData, sTrCode, sRqName, 0, "예수금")
            result_2 = self.dynamicCall(self.func.GetCommData, sTrCode, sRqName, 0, "출금가능금액")
            print("예수금: %s원" % int(result_1))
            print("출금가능: %s원" % int(result_2))
            print("-" * 90)
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
            # 일자, 종가, 전일대비, 거래량, 변동수량, 보유주식수, 비중, 취득가능주식수, 외국인한도, 외국인한도증감, 한도소진률
            df = pd.DataFrame(result)
            df.set_index(0, inplace=True)
            pd.set_option('display.max_row', 200)
            pd.set_option('display.max_columns', 15)
            print(df)

    def real_signal(self, sTrCodeList=" ", sTrFidList="215", strOptType="0"):
        result = self.dynamicCall(self.func.SetRealReg, self.real_screen, sTrCodeList, sTrFidList, strOptType)

        if result == 0:
            print("실시간 종목 정상 처리 %s" % sTrCodeList)

    def real_slot(self, sCode, sRealType, sRealData):
        result_1 = self.dynamicCall(self.func.GetCommRealData, sCode, "215")
        print(result_1)

    def get_login_info(self):
        acc_list = self.dynamicCall(self.func.GetLoginInfo, "ACCLIST")
        user_name = self.dynamicCall(self.func.GetLoginInfo, "USER_NAME")
        user_id = self.dynamicCall(self.func.GetLoginInfo, "USER_ID")
        self.account = acc_list.split(";")[0]
        print("계좌번호: %s" % self.account)
        print("유저이름: %s" % user_name)
        print("아이디: %s" % user_id)

    def get_code_list(self, market="10"):
        result = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = result.split(";")
        code_list.pop()
        print("종목코드: %s개" % len(code_list))
