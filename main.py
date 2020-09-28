from PyQt5.QAxContainer import *  # QAxWidget
from PyQt5.QtCore import *  # QEventLoop
from api import *
from fid import *
import pandas as pd
from datetime import date


class Machine(QAxWidget):
    def __init__(self):
        super().__init__()
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

        # 빈 데이터프레임 생성
        self.today = date.today().strftime('%Y%m%d')
        self.df_deal = pd.DataFrame(columns=FID.deal)
        self.df_bid = pd.DataFrame(columns=FID.bid)

        self.login_loop = QEventLoop()
        self.tr_loop = QEventLoop()

        self.account = str()

        # 스크린 번호
        self.tr_screen = "1000"
        self.real_screen = "2000"

        self.connect_events()

        self.login()
        self.set_real_signals()

        # self.count = True
        # self.trade()

    def connect_events(self):
        self.OnEventConnect.connect(self.login_slot)
        self.OnReceiveTrData.connect(self.tr_slot)
        self.OnReceiveRealData.connect(self.real_slot)
        self.OnReceiveMsg.connect(self.msg_slot)
        self.OnReceiveChejanData.connect(self.che_slot)

    def login(self):
        self.login_signal()
        self.tr_signal("예수금상세현황요청")

    def set_real_signals(self):
        code = "065650"  # 메디프론
        self.real_signal()  # 초기화 및 장운영구분
        self.real_signal(code, ";".join(FID.deal), "1")
        self.real_signal(code, ";".join(FID.bid), "1")

    def trade(self):
        if self.count:
            self.order_signal(
                order_type='2',
                stock_code='065650',
                quantity='1',
                price=' ',
                bid_type='81',
            )
            self.count = False

    def login_signal(self):
        self.dynamicCall(API.CommConnect)
        self.login_loop.exec_()

    def login_slot(self, err_code):
        self.get_login_info()
        self.login_loop.exit()

    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        print("%s %s %s %s" % (sScrNo, sRQName, sTrCode, msg))

    def tr_signal(self, tr, stock_code=None):
        if tr == "예수금상세현황요청":
            self.dynamicCall(API.SetInputValue, "계좌번호", self.account)
            self.dynamicCall(API.SetInputValue, "비밀번호", "")
            self.dynamicCall(API.SetInputValue, "비밀번호입력매체구분", "00")
            self.dynamicCall(API.SetInputValue, "조회구분", "2")
            self.dynamicCall(API.CommRqData, tr, "opw00001", "0", self.tr_screen)
            self.tr_loop.exec_()

    def tr_slot(self, scr_no, rq_name, tr_code, record_name, prev_next):
        if rq_name == '예수금상세현황요청':
            result1 = int(self.dynamicCall(API.GetCommData, tr_code, rq_name, 0, "예수금"))
            result2 = int(self.dynamicCall(API.GetCommData, tr_code, rq_name, 0, "출금가능금액"))
            print("예수금 {}원".format(result1))
            print("출금가능 {}원".format(result2))
            self.tr_loop.exit()

    def real_signal(self, code_list=" ", fid_list="215", opt_type="0"):
        result = self.dynamicCall(API.SetRealReg, self.real_screen, code_list, fid_list, opt_type)
        print('실시간 데이터 요청 성공 {}'.format(code_list) if result == 0 else '실시간 데이터 요청 실패')

    def real_slot(self, code, real_type, real_data):  # code: 종목코드, real_type: 실시간 데이터 종류, real_data: 실시간 데이터 전문
        if real_type == '장시작시간':
            result = self.dynamicCall(API.GetCommRealData, code, '215').strip()
            if result == "2":
                self.dynamicCall(API.DisconnectRealData, self.real_screen)
                self.df_deal.to_csv('data/deal.csv', index=False)
                self.df_bid.to_csv('data/bid.csv', index=False)
                print('[매매종료] 결과를 파일로 저장했습니다.')
            else:
                print('[장운영구분] {}'.format(result))

        elif real_type == '주식체결':
            self.df_deal.append(self.to_df(code), ignore_index=True)
            print('[{}]'.format(real_type))

        elif real_type == '주식호가잔량':
            self.df_bid.append(self.to_df(code), ignore_index=True)
            print('[{}]'.format(real_type))

    def to_df(self, code):
        data = {}
        for fid in FID.bid:
            result = self.dynamicCall(API.GetCommRealData, code, fid).strip()
            if fid in FID.float_type:
                data[fid] = float(result)
            elif fid in FID.date_type:
                data[fid] = pd.to_datetime(self.today + result)
            else:
                data[fid] = int(result)
        return pd.DataFrame(data)

    def order_signal(self, order_type, stock_code, quantity, price, bid_type, original_order=" "):
        sRQName = "매매주문"  # 사용자 구분명
        sScreenNo = "6000"  # 화면번호
        sAccNo = self.account  # 계좌번호 10자리
        nOrderType = order_type  # 주문유형, int, 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정
        sCode = stock_code  # 종목코드
        nQty = quantity  # 주문수량, int
        nPrice = price  # 주문가격, int
        sHogaGb = bid_type  # 거래구분, bid, 00: 지정가, 03: 시장가, 81: 장후시간외종가
        sOrgOrderNo = original_order  # 원주문번호, 신규주문에는 공백, 정정(취소) 주문할 원주문번호를 입력합니다.
        result = self.dynamicCall(API.SendOrder,
                                  [sRQName, sScreenNo, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb, sOrgOrderNo])
        print("주문 성공" if result == 0 else "주문실패")

    def che_slot(self, sGubun, nItemCnt, sFIdList):
        print(nItemCnt, sFIdList)
        data = {}
        if sGubun == '0':  # 체결구분 접수와 체결시 '0'값, 국내주식 잔고전달은 '1'값, 파생잔고 전달은 '4'
            print('[접수/체결]', end="\t")
            for nFid in FID.che:
                data[nFid] = self.dynamicCall(API.GetChejanData, nFid).strip()
            print(data)

        elif sGubun == '1':
            print('[국내주식 잔고전달]', end="\t")
            pass

    def get_login_info(self):
        info_list = ['ACCLIST', 'USER_ID', 'USER_NAME']
        for info in info_list:
            result = self.dynamicCall(API.GetLoginInfo, info)
            if info == 'ACCLIST':
                result = result.split(';')[0]
                self.account = result
            print('{} {}'.format(info, result))

    def get_code_list(self, market="10"):
        result = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = result.split(";")
        code_list.pop()
        print("종목코드: %s개" % len(code_list))
