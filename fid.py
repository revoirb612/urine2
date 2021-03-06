class FID:
    float_type = ['12', '30', '31', '228', '129', '139']
    date_type = ['20', '21']

    deal = [
        '20',  # 체결시간(HHMMSS): 시간 타입으로 변경 필요
        '10',  # 현재가, 체결가, 실시간종가 -(전일종가대비)
        '11',  # 전일대비 -(전일종가대비)
        '12',  # 등락율 -(전일종가대비)
        '27',  # (최우선)매도호가, -(전일종가대비)
        '28',  # (최우선)매수호가 -(전일종가대비)
        '15',  # 거래량, 체결량 -(매도량)
        '13',  # 누적거래량 누적체결량
        '16',  # 시가 -(전일종가대비)
        '17',  # 고가 -(전일종가대비)
        '18',  # 저가 -(전일종가대비)
        '26',  # 전일거래량 대비(주) -(전일총거래량대비)
        '30',  # 전일거래량 대비(비율) -(전일총거래량대비)
        '31',  # 거래회전율
        '228',  # 체결강도
    ]

    bid = [
        '21',  # 호가시간(HHMMSS): 시간 타입으로 변경 필요
        '61',  # 매도호가수량1
        '62',  # 매도호가수량2
        '63',  # 매도호가수량3
        '64',  # 매도호가수량4
        '65',  # 매도호가수량5
        '66',  # 매도호가수량6
        '67',  # 매도호가수량7
        '68',  # 매도호가수량8
        '69',  # 매도호가수량9
        '70',  # 매도호가수량10
        '71',  # 매수호가수량1
        '72',  # 매수호가수량2
        '73',  # 매수호가수량3
        '74',  # 매수호가수량4
        '75',  # 매수호가수량5
        '76',  # 매수호가수량6
        '77',  # 매수호가수량7
        '78',  # 매수호가수량8
        '79',  # 매수호가수량9
        '80',  # 매수호가수량10
        '121',  # 매도호가 총잔량
        '122',  # 매도호가 총잔량 직전대비 -(직전대비)
        '125',  # 매수호가 총잔량
        '126',  # 매수호가 총잔량 직전대비 -(직전대비)
        '128',  # 순매수잔량(총매수잔량-총매도잔량) -(가능)
        '129',  # 매수비율
        '138',  # 순매도잔량(총매도잔량-총매수잔량) -(가능)
        '139',  # 매도비율
    ]

    che = [
        '9201',  # 계좌번호
        '9203',  # 주문번호
        '9001',  # 종목코드, 업종코드
        '912',  # 주문업무분류
        '913',  # 주문상태
        '302',  # 종목명
        '900',  # 주문수량
        '901',  # 주문가격
        '902',  # 미체결수량
        '903',  # 주문구분
        '906',  # 매매구분
        '907',  # 매도수구분
        '908',  # 주문/체결시간
        '910',  # 체결가
        '911',  # 체결량
    ]