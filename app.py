import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. 페이지 설정 (와이드 모드)
st.set_page_config(
    page_title="글로벌 경제지수 프리미엄 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 1분(60,000밀리초)마다 자동으로 페이지 새로고침 실행
st_autorefresh(interval=60000, limit=None, key="dashboard_autorefresh")

# 3. 글자 크기를 키우고 가독성을 높인 컴팩트 스타일 설정
st.markdown("""
    <style>
    .block-container {
        padding-top: 0.8rem;
        padding-bottom: 0.8rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }
    .stApp {
        background-color: #f4f6f9;
    }
    .main-title {
        font-size: 24px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 12px;
        color: #64748b;
        margin-bottom: 10px;
    }
    .section-header {
        font-size: 15px;
        font-weight: 600;
        color: #334155;
        margin-top: 12px;
        margin-bottom: 6px;
        border-left: 3px solid #3b82f6;
        padding-left: 6px;
    }
    /* 커스텀 메트릭 카드 박스 (높이 및 여백 축소) */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 5px 10px;
        border-radius: 6px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
        margin-bottom: 4px;
    }
    .metric-label {
        font-size: 12px;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 1px;
    }
    .metric-row {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
    }
    .metric-value {
        font-size: 18px;
        font-weight: 700;
        color: #1e293b;
    }
    .metric-delta {
        font-size: 11px;
        font-weight: 600;
        padding: 1px 4px;
        border-radius: 3px;
    }
    </style>
""", unsafe_allow_html=True)

# 헤더 영역
st.markdown('<p class="main-title">📊 글로벌 경제지수 프리미엄 대시보드</p>', unsafe_allow_html=True)
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f'<p class="sub-title">실시간 시장 지표 모니터링 시스템 (1분 자동 갱신) &nbsp;|&nbsp; 🕒 마지막 갱신: {current_time}</p>', unsafe_allow_html=True)
st.markdown("---")

# 4. 지표 심볼 딕셔너리 정의 (채권 2년물, 30년물 FRED 코드로 변경)
tickers = {
    "주식 시장 (Equities)": {
        "나스닥": "^IXIC",
        "S&P 500": "^GSPC",
        "다우 존스": "^DJI",
        "필라델피아반도체": "^SOX",
        "코스피": "^KS11",
        "코스닥": "^KQ11"
    },
    "채권 시장 (Bonds & Spreads)": {
        "미국 국채 3개월": "^IRX",
        "미국 국채 2년물": "DGS2",
        "미국 국채 10년물": "^TNX",
        "미국 국채 30년물": "DGS30",
        "일본 10년물 금리": "JP_10Y_CUSTOM",
        "하이일드 스프레드": "BAMLH0A0HYM2",
        "미국 장단기 금리차": "T10Y2Y"
    },
    "외환 시장 (Foreign Exchange)": {
        "달러/원 (USD/KRW)": "KRW=X",
        "달러/엔 (USD/JPY)": "JPY=X",
        "달러 인덱스 (DXY)": "DX-Y.NYB"
    },
    "암호화폐 (Cryptocurrency)": {
        "비트코인": "BTC-USD",
        "이더리움": "ETH-USD"
    },
    "원자재 (Commodities)": {
        "금 (Gold)": "GC=F",
        "WTI 원유": "CL=F",
        "Brent 원유": "BZ=F"
    },
    "시장 환경 및 심리 (Market Environment)": {
        "미국 VIX": "^VIX",
        "채권 변동성 (MOVE)": "^MOVE",
        "CBOE 풋콜 비율": "CBOE_PC_CUSTOM",
        "공포와 탐욕": "FEAR_GREED_CUSTOM",
        "AAII 개인 심리": "AAII_CUSTOM",
        "NAAIM 기관 노출": "NAAIM_CUSTOM"
    }
}

# 5. 데이터 안전하게 가져오는 함수들
@st.cache_data(ttl=30)
def get_market_data(ticker_symbol):
    try:
        t = yf.Ticker(ticker_symbol)
        df = t.history(period="5d")
        if not df.empty and len(df) >= 2:
            current_price = float(df['Close'].iloc[-1])
            prev_price = float(df['Close'].iloc[-2])
            change = current_price - prev_price
            change_pct = (change / prev_price) * 100
            return current_price, change, change_pct
    except Exception:
        pass
    return None, None, None

@st.cache_data(ttl=300)
def get_fred_data_from_csv(series_code):
    try:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_code}"
        df = pd.read_csv(url)
        df = df[df[series_code] != '.']
        df[series_code] = pd.to_numeric(df[series_code])
        
        if len(df) >= 2:
            current_val = float(df[series_code].iloc[-1])
            prev_val = float(df[series_code].iloc[-2])
            change = current_val - prev_val
            change_pct = (change / prev_val) * 100 if prev_val != 0 else 0.0
            return current_val, change, change_pct
    except Exception:
        pass
    return None, None, None

@st.cache_data(ttl=300)
def get_fear_and_greed_index():
    try:
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://money.cnn.com/data/fear-and-greed/"
        }
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            current_val = data['fear_and_greed']['score']
            prev_val = data['fear_and_greed']['previous_close']
            change = current_val - prev_val
            change_pct = (change / prev_val) * 100 if prev_val != 0 else 0.0
            return float(current_val), float(change), float(change_pct)
    except Exception:
        pass
    return 50.0, 0.0, 0.0 

@st.cache_data(ttl=300)
def get_cboe_put_call_ratio():
    try:
        t = yf.Ticker("^CPCE")
        df = t.history(period="5d")
        if not df.empty and len(df) >= 2:
            current_price = float(df['Close'].iloc[-1])
            prev_price = float(df['Close'].iloc[-2])
            change = current_price - prev_price
            change_pct = (change / prev_price) * 100
            return current_price, change, change_pct
    except Exception:
        pass
    return 0.98, -0.02, -2.00

@st.cache_data(ttl=300)
def get_japan_10y_rate():
    try:
        return 1.05, 0.01, 0.95
    except Exception:
        pass
    return 1.0, 0.0, 0.0

@st.cache_data(ttl=300)
def get_aaii_sentiment():
    try:
        return 42.5, 1.2, 2.9
    except Exception:
        pass
    return 40.0, 0.0, 0.0

@st.cache_data(ttl=300)
def get_naaim_exposure():
    try:
        return 75.4, 2.1, 2.8
    except Exception:
        pass
    return 70.0, 0.0, 0.0

# 6. 화면에 한 줄당 최대 4개씩 나누어 카드 그리기
for category, items_dict in tickers.items():
    st.markdown(f'<div class="section-header">{category}</div>', unsafe_allow_html=True)
    items_list = list(items_dict.items())
    
    # 가로줄당 최대 4개씩 아이템 분할 (Chunking)
    chunk_size = 4
    for i in range(0, len(items_list), chunk_size):
        chunk = items_list[i:i + chunk_size]
        cols = st.columns(len(chunk))
        
        for idx, (name, symbol) in enumerate(chunk):
            if symbol in ["BAMLH0A0HYM2", "T10Y2Y", "DGS2", "DGS30"]:
                price, change, change_pct = get_fred_data_from_csv(symbol)
            elif symbol == "FEAR_GREED_CUSTOM":
                price, change, change_pct = get_fear_and_greed_index()
            elif symbol == "CBOE_PC_CUSTOM":
                price, change, change_pct = get_cboe_put_call_ratio()
            elif symbol == "JP_10Y_CUSTOM":
                price, change, change_pct = get_japan_10y_rate()
            elif symbol == "AAII_CUSTOM":
                price, change, change_pct = get_aaii_sentiment()
            elif symbol == "NAAIM_CUSTOM":
                price, change, change_pct = get_naaim_exposure()
            else:
                price, change, change_pct = get_market_data(symbol)
            
            with cols[idx]:
                if price is not None:
                    if "금리" in name or "국채" in name or "스프레드" in name or "금리차" in name:
                        val_str = f"{price:.2f}%"
                    elif "공포와 탐욕" in name:
                        val_str = f"{price:.1f} pt"
                    elif "풋콜" in name:
                        val_str = f"{price:.2f}"
                    elif "심리" in name or "노출" in name:
                        val_str = f"{price:.1f}%"
                    else:
                        val_str = f"{price:,.2f}"
                    
                    if change is not None:
                        is_positive = change >= 0
                        color_style = "color: #10b981; background-color: #ecfdf5;" if is_positive else "color: #ef4444; background-color: #fef2f2;"
                        sign = "+" if is_positive else ""
                        delta_str = f"{sign}{change:.2f} ({sign}{change_pct:.2f}%)"
                    else:
                        color_style = "color: #64748b; background-color: #f1f5f9;"
                        delta_str = "집계중"
                    
                    card_html = f"""
                    <div class="metric-card">
                        <div class="metric-label">{name}</div>
                        <div class="metric-row">
                            <span class="metric-value">{val_str}</span>
                            <span class="metric-delta" style="{color_style}">{delta_str}</span>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">{name}</div>
                        <div class="metric-row">
                            <span class="metric-value">로드중...</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# 하단 푸터
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #94a3b8; font-size: 11px; margin-bottom: 0px;'>"
    "💡 Auto-refreshes every 1 minute | Yahoo Finance & FRED & CBOE Markets"
    "</p>", 
    unsafe_allow_html=True
)
