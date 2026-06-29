import streamlit as st
import pandas as pd
import yfinance as yf

MACRO_TITLE_MAP = {
    '[미국10년국채금리]': '[미국10년국채금리]',
    '미국10년국채금리': '[미국10년국채금리]',
    '[장단기 금리차]': '[장단기 금리차]',
    '장단기 금리차': '[장단기 금리차]',
    '[USD/KRW 환율]': '[USD/KRW 환율]',
    'USD/KRW 환율': '[USD/KRW 환율]',
    '[USD/JPY 환율]': '[USD/JPY 환율]',
    'USD/JPY 환율': '[USD/JPY 환율]',
    '[vix지수]': '[vix지수]',
    'vix지수': '[vix지수]',
    '[하이일드 스프레드]': '[하이일드 스프레드]',
    '하이일드 스프레드': '[하이일드 스프레드]',
    '[XLF-QQQ괴리율]': '[XLF-QQQ괴리율]',
    'XLF-QQQ괴리율': '[XLF-QQQ괴리율]',
    '[ADX 추세강도]': '[ADX 추세강도]',
    'ADX 추세강도': '[ADX 추세강도]',
    '[ADX(QQQ추세강도)]': '[ADX 추세강도]',
    '[달러인덱스]': '[DXY]',
    '[DXY]': '[DXY]',
    'DXY': '[DXY]',
    '[일본10년국채금리]': '[일본10년국채금리]',
    '일본10년국채금리': '[일본10년국채금리]',
    '[일본금리]': '[일본10년국채금리]',
    '일본금리': '[일본10년국채금리]'
}

@st.cache_data(ttl=3600)
def get_macro_changes():
    changes = {}
    try:
        import yfinance as yf
        data = yf.download('KRW=X JPY=X ^VIX ^TNX XLF QQQ DX-Y.NYB', period='5d', progress=False)
        closes = data['Close']
        if len(closes) >= 2:
            
            usd_c = closes['KRW=X'].dropna()
            jpy_c = closes['JPY=X'].dropna()
            vix_c = closes['^VIX'].dropna()
            tnx_c = closes['^TNX'].dropna()
            xlf_c = closes['XLF'].dropna()
            qqq_c = closes['QQQ'].dropna()
            
            if len(usd_c) >= 2: changes['[USD/KRW 환율]'] = usd_c.iloc[-1] - usd_c.iloc[-2]
            if len(jpy_c) >= 2: changes['[USD/JPY 환율]'] = jpy_c.iloc[-1] - jpy_c.iloc[-2]
            if len(vix_c) >= 2: changes['[vix지수]'] = vix_c.iloc[-1] - vix_c.iloc[-2]
            if len(tnx_c) >= 2: changes['[미국10년국채금리]'] = tnx_c.iloc[-1] - tnx_c.iloc[-2]
            
            dxy_c = closes['DX-Y.NYB'].dropna()
            if len(dxy_c) >= 2: changes['[DXY]'] = dxy_c.iloc[-1] - dxy_c.iloc[-2]
            
            # XLF-QQQ
            if len(xlf_c) >= 2 and len(qqq_c) >= 2:
                xlf_today = xlf_c.iloc[-1]
                qqq_today = qqq_c.iloc[-1]
                xlf_yest = xlf_c.iloc[-2]
                qqq_yest = qqq_c.iloc[-2]
            
            if not __import__('pandas').isna(xlf_today) and not __import__('pandas').isna(qqq_today):
                today_ratio = xlf_today / qqq_today
                yest_ratio = xlf_yest / qqq_yest
                changes['XLF'] = today_ratio - yest_ratio
    except:
        pass
    return changes

import yfinance as yf
import numpy as np
import datetime
import calendar
import holidays
import urllib.request
import io
import requests
import json
import os
from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.graph_objects as go
CONFIG_FILE = "config.json"


def load_config():
    default_config = {
        "goal_amount": "10000000000", 
        "target_date": "2027-08-31",
        "up_rates": [4.0, 6.0, 8.0, 10.0, 12.0, 20.0],
        "down_rates": [-1.0, -1.5, -2.0, -3.0, -5.0, -10.0]
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                default_config.update(data)
                return default_config
        except:
            pass
    return default_config

def save_config(config_dict):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_dict, f)

if 'gs_val' not in st.session_state:
    st.session_state.gs_val = 100
if 'ty_val' not in st.session_state:
    import datetime
    st.session_state.ty_val = datetime.date.today().year + 5

st.set_page_config(page_title="금융 자산 대시보드", layout="wide", initial_sidebar_state="collapsed")

# === [보안 PIN 잠금 화면 로직] ===
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('''
    <style>
    /* 배경: 완전한 블랙에서 아주 깊은 남색 그라데이션 */
    .stApp {
        background: radial-gradient(circle at center, #0a0a1a 0%, #000000 100%);
    }
    
    /* 화면 중앙 컨테이너 */
    .pin-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 15vh;
        color: white;
    }
    
    /* 야광 점멸 애니메이션 정의 (연보라 & 주황 믹스) */
    @keyframes neonBreathe {
        0% {
            text-shadow: 0 0 10px rgba(184, 154, 255, 0.4), 0 0 20px rgba(184, 154, 255, 0.2);
        }
        50% {
            text-shadow: 0 0 20px rgba(255, 153, 0, 0.8), 0 0 40px rgba(255, 107, 0, 0.5), 0 0 60px rgba(255, 107, 0, 0.3);
            color: #ffffff;
        }
        100% {
            text-shadow: 0 0 10px rgba(184, 154, 255, 0.4), 0 0 20px rgba(184, 154, 255, 0.2);
        }
    }

    /* 타이틀 텍스트 (흰색 기본 + 야광 애니메이션) */
    .oracle-title {
        font-size: 3.5rem;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: 8px;
        margin-bottom: 5px;
        text-align: center;
        font-family: 'Inter', 'Arial Black', sans-serif;
        animation: neonBreathe 3s infinite ease-in-out;
    }
    
    .pin-subtitle {
        color: #888888;
        font-size: 1.1rem;
        margin-bottom: 40px;
        text-align: center;
        letter-spacing: 2px;
    }

    /* 입력창 폭 좁게 중앙 정렬 */
    div[data-testid="stTextInput"] {
        width: 300px !important;
        margin: 0 auto !important;
    }
    
    /* 텍스트 인풋 디자인 */
    div[data-baseweb="input"] {
        background-color: rgba(20, 20, 30, 0.8) !important;
        border: 1px solid rgba(184, 154, 255, 0.3) !important;
        border-radius: 20px !important;
        transition: all 0.3s ease;
    }
    
    /* 텍스트 인풋 포커스 시 주황색 네온 띠 */
    div[data-baseweb="input"]:focus-within {
        border-color: #FF9900 !important;
        box-shadow: 0 0 20px rgba(255, 153, 0, 0.4) !important;
        background-color: rgba(0, 0, 0, 0.9) !important;
    }

    div[data-baseweb="input"] input {
        color: white !important;
        font-size: 3rem !important;
        text-align: center !important;
        letter-spacing: 25px !important;
        caret-color: #FF9900 !important;
        padding: 20px !important;
    }
    </style>
    
    <div class="pin-container">
        <div class="oracle-title">ASSET 333</div>
        <div class="pin-subtitle">4자리 보안 PIN을 입력하세요</div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.write("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pin = st.text_input("PIN", type="password", label_visibility="collapsed", key="pin_input")
        if pin:
            app_pin = ""
            try:
                # secrets에서 PIN을 가져옴. 없으면 "1234"
                app_pin = str(st.secrets.get("APP_PIN", "1234"))
            except:
                app_pin = "1234"
                
            if pin == app_pin:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ 비밀번호가 틀렸습니다.")
    st.stop()
# =================================


# 사이버펑크 & Glassmorphism 글로벌 CSS 주입
st.markdown("""
<style>
    /* Glassmorphism 카드 컨테이너 */
    .glass-card {
        background: rgba(26, 17, 42, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 153, 0, 0.15);
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        margin-top: 20px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border: 1px solid rgba(255, 153, 0, 0.4);
        box-shadow: 0 8px 32px 0 rgba(255, 153, 0, 0.1);
    }

    /* 핵심 결과값 텍스트 (네온 글로우 효과) */
    .neon-result {
        font-size: 4.5rem;
        font-weight: 900;
        color: #FF9900;
        text-align: center;
        text-shadow: 0 0 10px rgba(255, 153, 0, 0.6), 
                     0 0 20px rgba(255, 153, 0, 0.4), 
                     0 0 40px rgba(255, 107, 0, 0.2);
        margin: 10px 0;
        line-height: 1.2;
    }

    /* 서브 타이틀 및 라벨 */
    .sub-label {
        font-size: 1.2rem;
        color: #A0A0A0;
        text-align: center;
        margin-bottom: 5px;
    }

    /* Streamlit 슬라이더 테마 커스텀 (CSS override) */

    /* 탭 디자인 커스텀 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        color: #A0A0A0;
        font-size: 1.1rem;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #FF9900 !important;
        border-bottom-color: #FF9900 !important;
    }

        /* V5 CSS */
        .marquee-wrapper { width: 100%; overflow: hidden; background: rgba(255, 107, 0, 0.1); padding: 8px 0; border-top: 1px solid rgba(255,107,0,0.3); border-bottom: 1px solid rgba(255,107,0,0.3); margin-bottom: 25px; }
        .marquee-content { display: inline-block; white-space: nowrap; animation: marquee 20s linear infinite; color: #FF6B00; font-weight: bold; font-size: 14px; letter-spacing: 2px; }
        @keyframes marquee { 0% { transform: translateX(100vw); } 100% { transform: translateX(-100%); } }
        .glass-card { background: rgba(26, 17, 42, 0.8); backdrop-filter: blur(16px); border: 1px solid rgba(255, 107, 0, 0.2); border-radius: 18px; padding: 20px; margin-bottom: 20px; }
        .swipe-container { display: flex; overflow-x: auto; gap: 15px; padding-bottom: 15px; scroll-snap-type: x mandatory; scrollbar-width: none; scrollbar-color: rgba(255, 107, 0, 0.5) rgba(255, 255, 255, 0.05); padding-top:10px; }
        .swipe-container::-webkit-scrollbar { display: none !important; }



        .macro-card { flex: 0 0 auto; width: 40vw; max-width: 140px; scroll-snap-align: start; text-align: center; padding: 15px 10px; margin-bottom: 0; }
        .asset-card { flex: 0 0 auto; width: 85vw; max-width: 320px; scroll-snap-align: start; margin-bottom: 0; position: relative; }
        .neon-text { font-size: 38px; font-weight: 900; color: #FF6B00; text-shadow: 0 0 10px rgba(255, 107, 0, 0.6); margin: 5px 0; }
        .profit-positive { color: #00E676; font-weight: bold; }
        .profit-negative { color: #00BFFF; font-weight: bold; }
        .progress-bar-container { background-color: rgba(255,255,255,0.1); height: 10px; border-radius: 5px; width: 100%; margin-top: 20px; overflow: hidden; }
        .progress-bar-fill { background-color: #FF6B00; height: 10px; border-radius: 5px; }
        /* Hover Effects */
        .hover-macro:hover { transform: translateY(-5px) scale(1.02); box-shadow: 0 10px 25px rgba(255, 255, 255, 0.2); border-color: white; }
        .hover-stock:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(30, 55, 153, 0.8); border-color: #1e3799; }
        .hover-gold:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(241, 196, 15, 0.8); border-color: #f1c40f; }
        .hover-bond:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(0, 216, 214, 0.8); border-color: #00d8d6; }
        .hover-coin:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(255, 107, 0, 0.8); border-color: #FF6B00; }
        .hover-cash:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(108, 92, 231, 0.8); border-color: #6c5ce7; }

    </style>
""", unsafe_allow_html=True)

if "google_sheets" in st.secrets:
    URL_DASHBOARD = st.secrets["google_sheets"]["URL_DASHBOARD"]
    URL_ACCOUNT = st.secrets["google_sheets"]["URL_ACCOUNT"]
    URL_CALENDAR = st.secrets["google_sheets"]["URL_CALENDAR"]
    URL_RECORDS = st.secrets["google_sheets"]["URL_RECORDS"]
    URL_PNL_DAILY = st.secrets["google_sheets"]["URL_PNL_DAILY"]
    URL_PNL_MONTHLY = st.secrets["google_sheets"]["URL_PNL_MONTHLY"]
else:
    st.error("Google Sheets URL 설정이 필요합니다. `.streamlit/secrets.toml` 파일을 확인해주세요.")
    st.stop()

def get_upbit_btc_price():
    try:
        response = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-BTC", timeout=3)
        btc_price = response.json()[0]['trade_price']
        btc_price_str = f"{btc_price:,.0f}"
    except Exception:
        btc_price_str = "95,965,000"
    return btc_price_str

@st.cache_data(ttl=86400)
def get_all_krx_tickers():
    ticker_dict = {}
    try:
        import FinanceDataReader as fdr
        krx = fdr.StockListing('KRX')
        for idx, row in krx.iterrows():
            name = str(row['Name']).replace(" ", "").upper()
            code = str(row['Code'])
            market = str(row['Market']).upper()
            if market == 'KOSPI':
                ticker_dict[name] = code + ".KS"
            elif market == 'KOSDAQ':
                ticker_dict[name] = code + ".KQ"
            else:
                ticker_dict[name] = code + ".KS"
    except Exception as e:
        print("FDR Load Error:", e)
    return ticker_dict

@st.cache_data(ttl=86400)
def get_ticker_from_name(stock_name):
    if not stock_name:
        return ""
        
    clean_name = stock_name.replace(" ", "").upper()
    
    # 1. Foreign Stock Korean Name Mapping
    foreign_dict = {
        "애플": "AAPL", "테슬라": "TSLA", "엔비디아": "NVDA", 
        "마이크로소프트": "MSFT", "마소": "MSFT", "알파벳": "GOOGL", "구글": "GOOGL",
        "아마존": "AMZN", "메타": "META", "페이스북": "META", "넷플릭스": "NFLX",
        "팔란티어": "PLTR", "에이엠디": "AMD", "인텔": "INTC",
        "퀄컴": "QCOM", "브로드컴": "AVGO", "ASML": "ASML",
        "일라이릴리": "LLY", "노보노디스크": "NVO",
        "테슬라모터스": "TSLA", "스타벅스": "SBUX", "코카콜라": "KO",
        "비트코인": "BTC-USD", "이더리움": "ETH-USD",
        "스페이스X": "SPCX"
    }
    if clean_name in foreign_dict:
        return foreign_dict[clean_name]
    
    # 2. Check KRX dictionary (Korean Stocks)
    krx_dict = get_all_krx_tickers()
    if clean_name in krx_dict:
        return krx_dict[clean_name]
        
    for k, v in krx_dict.items():
        if k in clean_name or clean_name in k:
            return v
            
    # 2. Check Yahoo Finance Search (US Stocks / Tickers)
    try:
        import urllib.parse, urllib.request, json
        q = urllib.parse.quote(stock_name)
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={q}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode('utf-8'))
            quotes = data.get('quotes', [])
            if quotes:
                for q in quotes:
                    if q.get('quoteType') == 'EQUITY':
                        return q['symbol']
                return quotes[0]['symbol']
    except Exception:
        pass
        
    return stock_name

@st.cache_data(ttl=60)
def load_all_data(urls_dict):
    results = {}
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        future_to_name = {executor.submit(load_and_clean_data_no_cache, url, name == "ACCOUNT"): name for name, url in urls_dict.items()}
        for future in concurrent.futures.as_completed(future_to_name):
            name = future_to_name[future]
            try:
                results[name] = future.result()
            except Exception as e:
                results[name] = pd.DataFrame()
    return results

def load_and_clean_data_no_cache(url, is_multi_header=False):
    if not url or url.startswith("여기에"):
        return pd.DataFrame()
    try:
        if is_multi_header:
            df = pd.read_csv(url, header=None)
            def clean_header(val):
                s = str(val).strip()
                if s.startswith('Unnamed:') or s in ['', 'nan', 'NaN', 'None']:
                    return np.nan
                return s
            
            level0 = df.iloc[1].apply(clean_header).ffill().fillna('')
            level1 = df.iloc[2].apply(clean_header).fillna('')
            
            seen = {}
            new_level1 = []
            for l0, l1 in zip(level0, level1):
                col_tuple = (l0, l1)
                if col_tuple in seen:
                    seen[col_tuple] += 1
                    new_level1.append(f"{l1}{' ' * seen[col_tuple]}")
                else:
                    seen[col_tuple] = 0
                    new_level1.append(l1)
            
            df.columns = pd.MultiIndex.from_arrays([level0, new_level1])
            df = df.iloc[3:].reset_index(drop=True)
        else:
            df = pd.read_csv(url, header=1)
            seen = {}
            new_cols = []
            for c in df.columns:
                if c in seen:
                    seen[c] += 1
                    new_cols.append(f"{c}_{seen[c]}")
                else:
                    seen[c] = 0
                    new_cols.append(c)
            df.columns = new_cols
            
        df = df.dropna(how='all')
        
        cols_to_drop = []
        for c in df.columns:
            c_str = str(c)
            if '0' == c_str.strip() or 'Unnamed: 0' in c_str or '차트' in c_str or '(억)' in c_str:
                cols_to_drop.append(c)
            elif isinstance(c, tuple):
                if any(str(x).strip() == '0' or 'Unnamed: 0' in str(x) or '차트' in str(x) or '(억)' in str(x) for x in c):
                    cols_to_drop.append(c)
                    
        df = df.drop(columns=cols_to_drop, errors='ignore')
        def clean_val(x):
            x_str = str(x).strip()
            if x_str in ['#VALUE!', '#DIV/0!', '#N/A', '#REF!', '#NAME?', '#NUM!', '#NULL!', '', '-', 'nan', 'NaN']:
                return 0.0
            try:
                return float(x_str.replace(',', ''))
            except ValueError:
                return x
        for col in df.columns:
            df[col] = df[col].apply(clean_val)
                    
        df = df.fillna(0.0)
        
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str)
                
        return df
    except Exception as e:
        st.error(f"데이터 로드 에러: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_and_clean_data(url, is_multi_header=False):
    return load_and_clean_data_no_cache(url, is_multi_header)

def find_metric(df, label, col_offset=1):
    label_clean = label.replace(" ", "")
    for r in range(min(20, len(df))): # top metrics are in the first 20 rows
        for c in range(min(20, len(df.columns))):
            val = str(df.iloc[r, c]).replace(" ", "")
            if label_clean in val and val != "":
                try:
                    return str(df.iloc[r, c + col_offset]).strip()
                except:
                    return "-"
    return "-"

@st.cache_data(ttl=300)
def get_market_data():
    data = {"USD_KRW": "1,380.0", "VIX": "16.25", "US_10Y": "4.491%", "T10Y2Y": "-", "HY_SPREAD": "-", "ADX_QQQ": "-", "XLF_QQQ_DIFF": "-"}
    try:
        hist = yf.download("KRW=X ^VIX ^TNX QQQ XLF", period="40d", progress=False)
        if not hist.empty and 'Close' in hist:
            if 'KRW=X' in hist['Close']: data["USD_KRW"] = f"{hist['Close']['KRW=X'].dropna().iloc[-1]:,.1f}"
            if '^VIX' in hist['Close']: data["VIX"] = f"{hist['Close']['^VIX'].dropna().iloc[-1]:.2f}"
            if '^TNX' in hist['Close']: data["US_10Y"] = f"{hist['Close']['^TNX'].dropna().iloc[-1]:.3f}%"
            
            if 'QQQ' in hist['Close'] and 'XLF' in hist['Close']:
                qqq_close = hist['Close']['QQQ'].dropna()
                xlf_close = hist['Close']['XLF'].dropna()
                if len(qqq_close) >= 21 and len(xlf_close) >= 21:
                    qqq_diff = (qqq_close.iloc[-1] - qqq_close.iloc[-21]) / qqq_close.iloc[-21]
                    xlf_diff = (xlf_close.iloc[-1] - xlf_close.iloc[-21]) / xlf_close.iloc[-21]
                    diff_pct = (xlf_diff - qqq_diff) * 100
                    data["XLF_QQQ_DIFF"] = f"{diff_pct:+.2f}%"

        # Calculate ADX for QQQ
        if not hist.empty and 'High' in hist and 'QQQ' in hist['High']:
            high = hist['High']['QQQ'].dropna()
            low = hist['Low']['QQQ'].dropna()
            close = hist['Close']['QQQ'].dropna()
            if len(close) > 28:
                up_move = high.diff()
                down_move = -low.diff()
                import numpy as np
                import pandas as pd
                plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0), index=high.index)
                minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0), index=high.index)
                tr1 = high - low
                tr2 = (high - close.shift(1)).abs()
                tr3 = (low - close.shift(1)).abs()
                tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
                
                window = 14
                atr = tr.ewm(alpha=1/window, adjust=False).mean()
                plus_di = 100 * (plus_dm.ewm(alpha=1/window, adjust=False).mean() / atr)
                minus_di = 100 * (minus_dm.ewm(alpha=1/window, adjust=False).mean() / atr)
                dx = (abs(plus_di - minus_di) / (plus_di + minus_di)).replace([np.inf, -np.inf], 0).fillna(0) * 100
                adx = dx.ewm(alpha=1/window, adjust=False).mean()
                data["ADX_QQQ"] = f"{adx.iloc[-1]:.1f}"
    except Exception:
        pass
        
        # Removed FRED API calls as they timeout and cause page load delays.
        # T10Y2Y is sourced from Google Sheets, and HY_SPREAD is manually input.
        
    return data
def format_styler(styler):
    def custom_formatter(x):
        if pd.isna(x) or str(x).strip() in ['', 'nan', 'NaN', 'None']:
            return ''
        x_str = str(x).strip()
        if '%' in x_str:
            return x_str
        try:
            val = float(x_str.replace(',', ''))
            return f"{val:,.0f}"
        except ValueError:
            return x_str
            
    return styler.format(formatter=custom_formatter)

# --- Right Sidebar Manual ---
st.markdown('''
    <style>
        /* Move sidebar to the right */
        [data-testid="stSidebar"] {
            left: auto !important;
            right: 0 !important;
            border-left: 1px solid #333;
            border-right: none;
        }
        /* Move sidebar toggle button to the top right, near Deploy */
        [data-testid="collapsedControl"] {
            left: auto !important;
            right: 80px !important;
            top: 10px !important;
            z-index: 999999 !important;
            background-color: #0A0A0C;
            border-radius: 5px;
        }
        /* Adjust main area padding when right sidebar is expanded */
        [data-testid="stSidebarExpanded"] + section {
            margin-left: 0 !important;
            margin-right: 21rem !important;
        }
    
        /* V5 CSS */
        .marquee-wrapper { width: 100%; overflow: hidden; background: rgba(255, 107, 0, 0.1); padding: 8px 0; border-top: 1px solid rgba(255,107,0,0.3); border-bottom: 1px solid rgba(255,107,0,0.3); margin-bottom: 25px; }
        .marquee-content { display: inline-block; white-space: nowrap; animation: marquee 20s linear infinite; color: #FF6B00; font-weight: bold; font-size: 14px; letter-spacing: 2px; }
        @keyframes marquee { 0% { transform: translateX(100vw); } 100% { transform: translateX(-100%); } }
        .glass-card { background: rgba(26, 17, 42, 0.8); backdrop-filter: blur(16px); border: 1px solid rgba(255, 107, 0, 0.2); border-radius: 18px; padding: 20px; margin-bottom: 20px; }
        .swipe-container { display: flex; overflow-x: auto; gap: 15px; padding-bottom: 15px; scroll-snap-type: x mandatory; scrollbar-width: none; scrollbar-color: rgba(255, 107, 0, 0.5) rgba(255, 255, 255, 0.05); padding-top:10px; }
        .swipe-container::-webkit-scrollbar { display: none !important; }
        
        
        
        .macro-card { flex: 0 0 auto; width: 40vw; max-width: 140px; scroll-snap-align: start; text-align: center; padding: 15px 10px; margin-bottom: 0; }
        .asset-card { flex: 0 0 auto; width: 85vw; max-width: 320px; scroll-snap-align: start; margin-bottom: 0; position: relative; }
        .neon-text { font-size: 38px; font-weight: 900; color: #FF6B00; text-shadow: 0 0 10px rgba(255, 107, 0, 0.6); margin: 5px 0; }
        .profit-positive { color: #00E676; font-weight: bold; }
        .profit-negative { color: #00BFFF; font-weight: bold; }
        .progress-bar-container { background-color: rgba(255,255,255,0.1); height: 10px; border-radius: 5px; width: 100%; margin-top: 20px; overflow: hidden; }
        .progress-bar-fill { background-color: #FF6B00; height: 10px; border-radius: 5px; }
        /* Hover Effects */
        .hover-macro:hover { transform: translateY(-5px) scale(1.02); box-shadow: 0 10px 25px rgba(255, 255, 255, 0.2); border-color: white; }
        .hover-stock:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(30, 55, 153, 0.8); border-color: #1e3799; }
        .hover-gold:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(241, 196, 15, 0.8); border-color: #f1c40f; }
        .hover-bond:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(0, 216, 214, 0.8); border-color: #00d8d6; }
        .hover-coin:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(255, 107, 0, 0.8); border-color: #FF6B00; }
        .hover-cash:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(108, 92, 231, 0.8); border-color: #6c5ce7; }

    </style>
''', unsafe_allow_html=True)

with st.sidebar:
    st.title("💡 이용 매뉴얼")
    st.markdown('''
    <div style="background-color: #1A112A; padding: 15px; border-radius: 10px; border: 1px solid #333; margin-bottom: 20px;">
        <h5 style="color: #FF9900; margin-top: 0;">⬇️ 노션(Notion)에 저장하는 방법</h5>
        <ol style="color: #d0d0d0; line-height: 1.6; font-size: 13px; padding-left: 15px;">
            <li>아래 <b>다운로드</b> 버튼으로 <code>.md</code> 파일을 받습니다.</li>
            <li>노션 빈 페이지에 <b>드래그 앤 드롭</b> 하면 완료!</li>
        </ol>
    </div>
    ''', unsafe_allow_html=True)
    
    manual_md = '''
# 📈 개인 주식 및 자산 관리 대시보드 이용 매뉴얼

본 대시보드는 구글 스프레드시트와 연동하여 나의 모든 자산 흐름과 시장 지표를 파악하고, 체계적인 매매 기록 및 모의 투자를 지원하는 툴입니다.

---

## 0. 시작하기 전에: 구글 시트 연동 🔑
개인 자산 데이터가 저장된 구글 스프레드시트를 가장 먼저 연결해야 합니다.
1. 앱 좌측의 사이드바 메뉴 하단에서 `Google Sheets URL 입력` 칸을 찾습니다.
2. **<span style="color: #4ade80; font-weight: bold;">본인의 구글 시트 주소(URL)를 복사하여 붙여넣기</span>** 합니다.
3. 입력 즉시 모든 정보가 대시보드에 실시간으로 연동됩니다!

---

## 1. 대시보드 (Dashboard) 📊
현재 자산 총합과 목표 달성률, 그리고 시장 흐름을 한눈에 보는 화면입니다.

* **목표 설정**: 최상단에서 **<span style="color: #4ade80; font-weight: bold;">목표 금액</span>**과 **<span style="color: #4ade80; font-weight: bold;">목표일</span>**을 입력하면 달성률(%)과 D-Day가 자동 계산됩니다.
* **자산 요약**: 자산 총액 및 투자 비중이 도넛 차트로 제공됩니다.
* **거시 경제 & 공포탐욕지수**: 코스피, 나스닥, 환율 등 핵심 지표와 시장 심리를 제공합니다.

## 2. 증권계좌현황 (Account Status) 💼
구글 시트에 기록된 각 계좌별 보유 종목의 실시간 평가금액과 수익률을 제공합니다.

## 3. 매매 기록 (Trade Records) ✍️
* **매매 캘린더**: 이번 달 달력에 일별 실현 손익을 표시합니다. (수익은 적색, 손실은 청색)
* **매매 기록**: 상세 매매 내역을 표로 확인합니다.
* **모의계산**: 가상의 **<span style="color: #4ade80; font-weight: bold;">매수 수량 및 단가</span>**를 표에 직접 입력해 보세요. 예상 금액과 수익률이 즉시 자동 계산됩니다!
* **익절/손절 계산기**: 표에 원하는 **<span style="color: #4ade80; font-weight: bold;">목표 수익률(%)과 하락률(%)</span>**을 입력하면 정확한 매도 단가를 산출해 줍니다.

## 4. 손익 현황 (PnL Status) 💰
* **일별 손익**: 매일매일의 수익/손실 및 입출금 내역을 파악합니다.
* **월별 손익**: 월 단위 누적 손익 표와 막대형 차트를 제공합니다.
'''
    st.download_button(
        label="📥 매뉴얼 다운로드 (.md)",
        data=manual_md,
        file_name="stock_dashboard_manual.md",
        mime="text/markdown",
        use_container_width=True
    )
    st.markdown("---")
    st.markdown(manual_md)
# ----------------------------

menu_options = ["대시보드", "매매 기록"]

if "menu_selection" not in st.session_state:
    page_from_url = st.query_params.get("page", "대시보드")
    st.session_state.menu_selection = page_from_url if page_from_url in menu_options else "대시보드"
if "record_tab" not in st.session_state:
    st.session_state.record_tab = "매매 캘린더"
if "pnl_tab" not in st.session_state:
    st.session_state.pnl_tab = "일별 손익"

default_index = menu_options.index(st.session_state.menu_selection)

st.markdown("""
    <style>
        div[data-testid="stElementContainer"]:has(iframe[title="streamlit_option_menu.option_menu"]) {
            position: sticky;
            top: 60px;
            z-index: 999;
            background-color: #0A0A0C;
            padding-top: 10px;
            padding-bottom: 5px;
        }
    
        /* V5 CSS */
        .marquee-wrapper { width: 100%; overflow: hidden; background: rgba(255, 107, 0, 0.1); padding: 8px 0; border-top: 1px solid rgba(255,107,0,0.3); border-bottom: 1px solid rgba(255,107,0,0.3); margin-bottom: 25px; }
        .marquee-content { display: inline-block; white-space: nowrap; animation: marquee 20s linear infinite; color: #FF6B00; font-weight: bold; font-size: 14px; letter-spacing: 2px; }
        @keyframes marquee { 0% { transform: translateX(100vw); } 100% { transform: translateX(-100%); } }
        .glass-card { background: rgba(26, 17, 42, 0.8); backdrop-filter: blur(16px); border: 1px solid rgba(255, 107, 0, 0.2); border-radius: 18px; padding: 20px; margin-bottom: 20px; }
        .swipe-container { display: flex; overflow-x: auto; gap: 15px; padding-bottom: 15px; scroll-snap-type: x mandatory; scrollbar-width: none; scrollbar-color: rgba(255, 107, 0, 0.5) rgba(255, 255, 255, 0.05); padding-top:10px; }
        .swipe-container::-webkit-scrollbar { display: none !important; }
        
        
        
        .macro-card { flex: 0 0 auto; width: 40vw; max-width: 140px; scroll-snap-align: start; text-align: center; padding: 15px 10px; margin-bottom: 0; }
        .asset-card { flex: 0 0 auto; width: 85vw; max-width: 320px; scroll-snap-align: start; margin-bottom: 0; position: relative; }
        .neon-text { font-size: 38px; font-weight: 900; color: #FF6B00; text-shadow: 0 0 10px rgba(255, 107, 0, 0.6); margin: 5px 0; }
        .profit-positive { color: #00E676; font-weight: bold; }
        .profit-negative { color: #00BFFF; font-weight: bold; }
        .progress-bar-container { background-color: rgba(255,255,255,0.1); height: 10px; border-radius: 5px; width: 100%; margin-top: 20px; overflow: hidden; }
        .progress-bar-fill { background-color: #FF6B00; height: 10px; border-radius: 5px; }
        /* Hover Effects */
        .hover-macro:hover { transform: translateY(-5px) scale(1.02); box-shadow: 0 10px 25px rgba(255, 255, 255, 0.2); border-color: white; }
        .hover-stock:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(30, 55, 153, 0.8); border-color: #1e3799; }
        .hover-gold:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(241, 196, 15, 0.8); border-color: #f1c40f; }
        .hover-bond:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(0, 216, 214, 0.8); border-color: #00d8d6; }
        .hover-coin:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(255, 107, 0, 0.8); border-color: #FF6B00; }
        .hover-cash:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(108, 92, 231, 0.8); border-color: #6c5ce7; }

    </style>
""", unsafe_allow_html=True)

menu = option_menu(
    menu_title=None, 
    options=menu_options, 
    icons=['', '', ''], 
    menu_icon="cast", 
    default_index=default_index, 
    orientation="horizontal",
    styles={
        "container": {"padding": "5px", "background-color": "#1A112A", "border": "1px solid #333333", "border-radius": "12px", "margin-bottom": "25px", "max-width": "100%"},
        "icon": {"display": "none"}, 
        "nav-link": {"font-size": "15px", "font-weight": "500", "text-align": "center", "margin":"0px 5px", "padding": "10px", "--hover-color": "#222222", "color": "#d0d0d0", "border-radius": "8px"},
        "nav-link-selected": {"background-color": "#FF9900", "color": "#000000", "font-weight": "bold"},
    }
)

if menu != st.session_state.menu_selection:
    st.session_state.menu_selection = menu
    st.query_params["page"] = menu

st.query_params["page"] = menu
# ===== Imported Functions from app_8507.py =====
import logging
logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def format_num(val) -> str:
    """숫자/문자열 값을 천단위 콤마 포맷으로 변환."""
    if val == "-":
        return "-"
    val_str = str(val).strip()
    prefix = ""
    for sym in ["+", "-", "▲", "▼"]:
        if val_str.startswith(sym):
            prefix = sym
            break
    try:
        fval = float(
            val_str.replace(",", "").replace("%", "")
            .replace("+", "").replace("-", "")
            .replace("▲", "").replace("▼", "")
        )
        if "%" in val_str:
            return f"{prefix}{fval:,.2f}%"
        elif fval == int(fval):
            return f"{prefix}{int(fval):,}"
        else:
            return f"{prefix}{fval:,.1f}"
    except ValueError:
        return val_str

def format_styler(styler):
    """DataFrame Styler에 천단위 콤마 포맷 적용."""
    def custom_formatter(x):
        if pd.isna(x) or str(x).strip() in {"", "nan", "NaN", "None"}:
            return ""
        x_str = str(x).strip()
        if "%" in x_str:
            return x_str
        try:
            val = float(x_str.replace(",", ""))
            return f"{val:,.0f}"
        except ValueError:
            return x_str
    return styler.format(formatter=custom_formatter)

def format_kr_amount(val: float) -> str:
    """금액을 억/만 단위 한국어 포맷으로 변환."""
    if abs(val) >= 100_000_000:
        return f"{val/100_000_000:,.1f}억" if val % 100_000_000 != 0 else f"{val/100_000_000:,.0f}억"
    elif abs(val) >= 10_000:
        return f"{val/10_000:,.0f}만"
    return f"{val:,.0f}"

def safe_int_float(val, default=0) -> float:
    """안전한 숫자 변환. 실패 시 default 반환."""
    try:
        return float(str(val).replace(",", "").strip())
    except (ValueError, TypeError):
        return default

def get_color_by_value(val) -> str:
    """양수=적색, 음수=청색, 0=흰색 반환."""
    try:
        v = float(str(val).replace(",", "").replace("%", "").strip())
        if v > 0:
            return "#ff4757"
        elif v < 0:
            return "#1e90ff"
        else:
            return "white"
    except:
        return "white"

@st.cache_data(ttl=300)
def load_records_data(url: str) -> pd.DataFrame:
    """매매 기록 데이터 로드 (캐시 적용)."""
    return load_and_clean_data(url)

def render_trade_records(urls: dict):
    df_dash = load_and_clean_data(urls['dashboard'])
    
    stock_eval = find_metric(df_dash, "주식 평가금액", col_offset=1)
    stock_profit = find_metric(df_dash, "주식 평가손익", col_offset=1)
    stock_principal = stock_eval - stock_profit
    
    total_realized_ytd = find_metric(df_dash, "올해 누적 실현손익", col_offset=1)
    avg_monthly = find_metric(df_dash, "올해 월평균 실현손익", col_offset=1)
    
    if stock_principal <= 0:
        ytd_roi_str = "원금 회수 완료 🚀"
        est_roi_str = "원금 회수 완료 🚀"
        total_roi_str = "원금 회수 완료 🚀"
        chart_ytd_roi = 0.0
        chart_est_roi = 0.0
        chart_total_roi = 0.0
    else:
        ytd_roi = (total_realized_ytd / stock_principal) * 100
        est_roi = ((avg_monthly * 12) / stock_principal) * 100
        total_roi = ((total_realized_ytd + stock_profit) / stock_principal) * 100
        
        ytd_roi_str = f"{ytd_roi:.2f}%"
        est_roi_str = f"{est_roi:.2f}%"
        total_roi_str = f"{total_roi:.2f}%"
        
        chart_ytd_roi = ytd_roi
        chart_est_roi = est_roi
        chart_total_roi = total_roi

    st.markdown("### 📈 월별 실현 수익 및 수익률 추이")
    col_chart1, col_chart2 = st.columns(2)
    
    months = [f"{i}월" for i in range(1, 13)]
    monthly_vals = []
    for m in months:
        monthly_vals.append(find_metric(df_dash, f"{m} 실현손익", col_offset=1))
        
    df_monthly = pd.DataFrame({'월': months, '실현수익': monthly_vals, '수익률': [chart_ytd_roi/12 * i for i in range(1, 13)]})
    
    with col_chart1:
        fig1 = px.bar(df_monthly, x='월', y='실현수익', title='올해 실현수익 금액 그래프', color_discrete_sequence=['#FF5A5F'])
        fig1.update_layout(paper_bgcolor="#0E1117", plot_bgcolor="#0E1117", font={'color':'white'})
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_chart2:
        fig2 = px.bar(df_monthly, x='월', y='수익률', title='실현수익률 막대그래프', color_discrete_sequence=['#32CD32'])
        fig2.update_layout(paper_bgcolor="#0E1117", plot_bgcolor="#0E1117", font={'color':'white'})
        st.plotly_chart(fig2, use_container_width=True)
        
    st.markdown("### 🎯 달성 목표 및 실현 수익 요약")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1: st.metric("올해 실현 수익률", ytd_roi_str)
    with col_s2: st.metric("연말 예상 수익률", est_roi_str)
    with col_s3: st.metric("올해 총 수익률", total_roi_str)
        
    st.markdown("---")
    df_rec = load_records_data(urls['trade_records'])
    if df_rec.empty:
        st.info("매매 기록이 없습니다.")
    else:
        _render_trade_calendar(df_rec)
        _render_trade_table(df_rec)

def get_cached_previous_close(ticker: str) -> float:
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        hist = t.history(period='5d')
        if not hist.empty and len(hist) > 1:
            return float(hist['Close'].iloc[-2])
        elif len(hist) == 1:
            return float(hist['Close'].iloc[0])
    except:
        pass
    return 0.0

def _render_profit_loss_calculator():
    """익절/손절 계산기 렌더링."""
    st.subheader("🚀 익절/손절 계산기")
    col_input, col_up, col_down = st.columns([1, 1.5, 1.5])

    with col_input:
        stock_name  = st.text_input("종목명 (입력 후 Enter)", value="SK하이닉스")
        auto_ticker = get_ticker_from_name(stock_name)
        # 특정 종목 폴백 처리
        FALLBACK_TICKERS = {"SK하이닉스": "000660", "삼성전자": "005930"}
        if auto_ticker == stock_name and stock_name in FALLBACK_TICKERS:
            auto_ticker = FALLBACK_TICKERS[stock_name]

        ticker_symbol = st.text_input("야후 파이낸스 티커", value=auto_ticker)

        is_foreign = bool(ticker_symbol) and not (
            ticker_symbol.endswith(".KS") or ticker_symbol.endswith(".KQ") or
            (ticker_symbol.isdigit() and len(ticker_symbol) == 6)
        )

        prev_close = None
        if ticker_symbol:
            prev_close = get_cached_previous_close(ticker_symbol)
            if prev_close is None:
                st.warning(f"⚠️ 전일 종가 조회 실패 ({ticker_symbol}). 수동으로 입력하거나 티커를 확인해 주세요.")

        if prev_close is None:
            prev_close = 150.0 if is_foreign else 215_000.0

        if is_foreign:
            st.markdown(f"<div style='font-size:14px;font-weight:600;color:#FF9900;margin-top:25px;'>전일 종가: ${prev_close:,.2f}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='font-size:14px;font-weight:600;color:#FF9900;margin-top:25px;'>전일 종가: {prev_close:,.0f} 원</div>", unsafe_allow_html=True)

    # 수익률 테이블 초기화
    
    up_rates_list = st.session_state.get('config', {}).get("up_rates", [4.0, 6.0, 8.0, 10.0, 12.0, 20.0])
    down_rates_list = st.session_state.get('config', {}).get("down_rates", [-3.0, -5.0, -7.0, -10.0, -15.0, -20.0])

    if "up_rates_df" not in st.session_state:
        st.session_state.up_rates_df = pd.DataFrame({
            "수익률(%)": up_rates_list,
            "목표 가격": [0.0] * len(up_rates_list),
            "목표 손익": [0.0] * len(up_rates_list)
        })
    if "down_rates_df" not in st.session_state:
        st.session_state.down_rates_df = pd.DataFrame({
            "하락률(%)": down_rates_list,
            "손절 가격": [0.0] * len(down_rates_list),
            "예상 손익": [0.0] * len(down_rates_list)
        })

    price_format = "{:,.2f}" if is_foreign else "{:,.0f}"
    up_prices   = prev_close * (1 + st.session_state.up_rates_df["수익률(%)"] / 100.0)
    down_prices = prev_close * (1 + st.session_state.down_rates_df["하락률(%)"] / 100.0)

    st.session_state.up_rates_df["목표 가격"]  = up_prices.round(2) if is_foreign else up_prices.astype(int)
    st.session_state.down_rates_df["손절 가격"] = down_prices.round(2) if is_foreign else down_prices.astype(int)

    with col_up:
        edited_up = st.data_editor(
            st.session_state.up_rates_df.style.format(formatter={"목표 가격": price_format}),
            use_container_width=True, hide_index=True, num_rows="dynamic",
            column_config={"수익률(%)": st.column_config.NumberColumn(format="%.1f%%")},
            disabled=["목표 가격"], key="up_rates_editor",
        )
    with col_down:
        edited_down = st.data_editor(
            st.session_state.down_rates_df.style.format(formatter={"손절 가격": price_format}),
            use_container_width=True, hide_index=True, num_rows="dynamic",
            column_config={"하락률(%)": st.column_config.NumberColumn(format="%.1f%%")},
            disabled=["손절 가격"], key="down_rates_editor",
        )

    # 변경 감지 후 저장 (rerun 조건 명확화)
    changed_rates = False
    if not edited_up.equals(st.session_state.up_rates_df):
        st.session_state.up_rates_df = edited_up
        st.session_state.config["up_rates"] = edited_up["수익률(%)"].tolist()
        changed_rates = True
    if not edited_down.equals(st.session_state.down_rates_df):
        st.session_state.down_rates_df = edited_down
        st.session_state.config["down_rates"] = edited_down["하락률(%)"].tolist()
        changed_rates = True

    if changed_rates:
        save_config(st.session_state.config)
        st.rerun()  # 변경 시에만 rerun (무한 루프 방지)

# =============================================================================
# ── 탭 4: 손익 현황 ──
# =============================================================================
def _clean_withdrawals_memos(df: pd.DataFrame) -> pd.DataFrame:
    """출금/메모 컬럼 정제."""
    if df.empty:
        return df
    df = df.copy()  # 원본 불변 (in-place 수정 방지)
    first_col = df.columns[0]
    df = df[~df[first_col].astype(str).str.strip().isin(["0.0", "0"])]
    for col in df.columns:
        if "Unnamed" in str(col):
            df = df.rename(columns={col: "비고"})
    if "비고" in df.columns:
        df["비고"] = df["비고"].apply(lambda x: "" if str(x).strip() in {"0.0", "0", "nan", "NaN"} else x)
    for col in df.columns:
        if "출금" in str(col):
            df[col] = df[col].apply(lambda x: "" if x in {0, 0.0} else x)
    return df

def _style_pnl_dataframe(df: pd.DataFrame):
    """손익 DataFrame 스타일링."""
    first_col = df.columns[0]

    def style_logic(styler):
        def row_style(row):
            if str(row[first_col]).strip() == "총계":
                return ["background-color: #2b2e35; font-weight: bold;"] * len(row)
            return [""] * len(row)
        styler = styler.apply(row_style, axis=1)

        def color_profit_loss(val):
            if isinstance(val, (int, float)):
                if val > 0: return "color: #ff4757;"
                if val < 0: return "color: #1e90ff;"
            return ""

        for col in df.columns:
            if "손익" in str(col) or "수익" in str(col):
                styler = styler.map(color_profit_loss, subset=[col])
            elif "출금" in str(col):
                styler = styler.map(
                    lambda v: "color: #feca57; font-weight: bold;" if v not in {"", 0} else "",
                    subset=[col],
                )
        styler.set_table_styles([
            {"selector": "table", "props": [("background-color", "#1A112A"), ("border-collapse", "collapse"), ("color", "white")]},
            {"selector": "th, td", "props": [("border", "1px solid #2b2e35"), ("padding", "10px"), ("text-align", "right")]},
            {"selector": "th", "props": [("background-color", "#0A0A0C"), ("color", "#FF9900"), ("text-align", "center"), ("font-weight", "bold")]},
            {"selector": "th.row_heading", "props": [("background-color", "#0A0A0C"), ("color", "#FF9900"), ("text-align", "left")]},
        ])
        return styler

    return df.style.pipe(format_styler).pipe(style_logic)

def _render_pnl_bar_chart(df: pd.DataFrame, title: str):
    """손익 막대 차트 렌더링."""
    if df.empty:
        st.info("차트 데이터가 없습니다.")
        return
    try:
        date_col   = df.columns[0]
        profit_col = next((c for c in df.columns if "실현손익" in str(c).replace(" ", "")), None)
        if not profit_col:
            profit_col = next((c for c in df.columns if "손익" in str(c)), None)
        if not profit_col:
            st.warning("손익 컬럼을 찾을 수 없습니다.")
            return

        df_chart = df[df[date_col].astype(str).str.strip() != "총계"].copy()
        df_chart = df_chart.iloc[::-1]
        if len(df_chart) > 30:
            df_chart = df_chart.tail(30)

        df_chart[profit_col] = pd.to_numeric(df_chart[profit_col], errors="coerce").fillna(0)
        text_labels = [format_kr_amount(v) for v in df_chart[profit_col]]

        fig = px.bar(df_chart, x=date_col, y=profit_col, text=text_labels)
        fig.update_traces(
            marker_color=["#ff4757" if v > 0 else "#1e90ff" for v in df_chart[profit_col]],
            textfont_size=11, textangle=0, textposition="outside", cliponaxis=False,
        )
        fig.update_layout(
            title=title,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#d2d2d2"),
            xaxis_title="", yaxis_title="",
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False, height=350, yaxis_tickformat=",.0f",
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.1)")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        logger.error("손익 차트 렌더링 실패: %s", e)
        st.error(f"❌ 차트 렌더링 실패: {e}")

def render_pnl(urls: dict):
    """손익 현황 탭 렌더링."""
    pnl_tab = option_menu(
        None, ["일별 손익", "월별 손익"],
        icons=['', '', ''],
        default_index=0 if st.session_state.pnl_tab == "일별 손익" else 1,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#111111", "border": "1px solid #333333", "border-radius": "8px", "margin-bottom": "15px", "max-width": "300px"},
            "nav-link": {"font-size": "14px", "text-align": "center", "margin": "0px", "padding": "8px", "--hover-color": "#222222", "color": "#d0d0d0"},
            "nav-link-selected": {"background-color": "#FF9900", "color": "#000000", "font-weight": "bold"},
        },
    )
    if pnl_tab != st.session_state.pnl_tab:
        st.session_state.pnl_tab = pnl_tab
        st.rerun()

    if pnl_tab == "일별 손익":
        df_daily = load_and_clean_data(urls.get("DAILY", ""))
        if not df_daily.empty:
            df_daily = _clean_withdrawals_memos(df_daily)
            st.markdown("<br><h4 style='color:#FF9900;'>📊 일별 실현손익 추이</h4>", unsafe_allow_html=True)
            _render_pnl_bar_chart(df_daily, "일별 실현손익")
            with st.expander("📋 일별 손익 상세 표", expanded=False):
                st.dataframe(_style_pnl_dataframe(df_daily), use_container_width=True, hide_index=True)
        else:
            st.info("일별 손익 데이터를 불러오지 못했습니다.")

    elif pnl_tab == "월별 손익":
        df_monthly = load_and_clean_data(urls.get("MONTHLY", ""))
        if not df_monthly.empty:
            df_monthly = _clean_withdrawals_memos(df_monthly)
            st.markdown("<br><h4 style='color:#FF9900;'>📊 월별 실현손익 추이</h4>", unsafe_allow_html=True)
            _render_pnl_bar_chart(df_monthly, "월별 실현손익")
            with st.expander("📋 월별 손익 상세 표", expanded=False):
                st.dataframe(_style_pnl_dataframe(df_monthly), use_container_width=True, hide_index=True)
        else:
            st.info("월별 손익 데이터를 불러오지 못했습니다.")

# =============================================================================
# ── 탭 5: 시뮬레이터 ──
# =============================================================================

if menu == "대시보드":
    df_dash = load_and_clean_data(urls_dict['DASHBOARD'])
    if df_dash.empty:
        st.warning("대시보드 데이터를 불러올 수 없습니다.")
    else:
        stock_eval = find_metric(df_dash, "주식 평가금액", col_offset=1)
        stock_profit = find_metric(df_dash, "주식 평가손익", col_offset=1)
        total_assets = find_metric(df_dash, "총 자산", col_offset=1)
        stock_principal = stock_eval - stock_profit
        
        total_realized_ytd = find_metric(df_dash, "올해 누적 실현손익", col_offset=1)
        avg_monthly_realized = find_metric(df_dash, "올해 월평균 실현손익", col_offset=1)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'''
                <div style="background-color: #1E1E2D; padding: 30px; border-radius: 15px; text-align: center; border: 1px solid #333;">
                    <p style="color: #A0A0B0; font-size: 1.2rem; margin:0;">주식 운용 원금 (순수 매입금)</p>
                    <h1 style="color: #FFF; font-size: 2.5rem; margin:10px 0;">₩{format_num(stock_principal)}</h1>
                </div>
            ''', unsafe_allow_html=True)
        with col2:
            st.markdown(f'''
                <div style="background-color: #1E1E2D; padding: 30px; border-radius: 15px; text-align: center; border: 1px solid #333;">
                    <p style="color: #A0A0B0; font-size: 1.2rem; margin:0;">주식 발생 총수익</p>
                    <h1 style="color: #FF5A5F; font-size: 2.5rem; margin:10px 0;">₩{format_num(total_realized_ytd + stock_profit)}</h1>
                </div>
            ''', unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)

        target_value = 10000000000
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=total_assets,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "100억 달성 속도계", 'font': {'size': 24, 'color': 'white'}},
            number={'valueformat': ',.0f', 'prefix': "₩", 'font': {'size': 40, 'color': '#FF5A5F'}},
            gauge={
                'axis': {'range': [None, target_value], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "#FF5A5F"},
                'bgcolor': "#1E1E2D",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, target_value * 0.5], 'color': '#111116'},
                    {'range': [target_value * 0.5, target_value * 0.8], 'color': '#2a2a35'},
                    {'range': [target_value * 0.8, target_value], 'color': '#424254'}],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': total_assets}
            }
        ))
        fig_gauge.update_layout(paper_bgcolor="#0E1117", font={'color': "white", 'family': "Arial"}, margin=dict(t=50, b=20, l=20, r=20), height=400)
        st.plotly_chart(fig_gauge, use_container_width=True)

        st.markdown("<br><br>", unsafe_allow_html=True)

        col_donut, col_summary = st.columns([1, 1])
        asset_types = ["주식", "금", "미국채", "현금", "연금저축/IRP", "비트코인"]
        asset_vals = []
        for atype in asset_types:
            val = find_metric(df_dash, f"{atype} 평가금액", col_offset=1)
            if val == 0 and atype == "주식": val = stock_eval
            asset_vals.append(val)
        
        df_assets = pd.DataFrame({'자산군': asset_types, '금액': asset_vals})
        df_assets = df_assets[df_assets['금액'] > 0]
        
        with col_donut:
            fig_donut = px.pie(df_assets, values='금액', names='자산군', hole=0.6, title="전체 자산 배분")
            fig_donut.update_traces(textinfo='percent+label', textfont_size=14, marker=dict(colors=px.colors.qualitative.Pastel))
            fig_donut.update_layout(paper_bgcolor="#0E1117", plot_bgcolor="#0E1117", font={'color': 'white'}, showlegend=False, height=400)
            st.plotly_chart(fig_donut, use_container_width=True)
        
        with col_summary:
            st.markdown("### 개인 / 법인 자산 요약")
            personal = find_metric(df_dash, "개인 자산", col_offset=1)
            corp = find_metric(df_dash, "법인 자산", col_offset=1)
            if personal == 0 and corp == 0:
                personal = total_assets * 0.7
                corp = total_assets * 0.3
            
            st.markdown(f'''
                <div style="background-color: #1E1E2D; padding: 20px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #FF5A5F;">
                    <h4 style="margin:0; color:#A0A0B0;">개인 자산</h4>
                    <h2 style="margin:5px 0 0 0; color:#FFF;">₩{format_num(personal)}</h2>
                </div>
                <div style="background-color: #1E1E2D; padding: 20px; border-radius: 10px; border-left: 5px solid #32CD32;">
                    <h4 style="margin:0; color:#A0A0B0;">법인 자산</h4>
                    <h2 style="margin:5px 0 0 0; color:#FFF;">₩{format_num(corp)}</h2>
                </div>
            ''', unsafe_allow_html=True)


elif menu == "매매 기록":
    urls_dict = {
        "DASHBOARD": URL_DASHBOARD,
        "ACCOUNT": URL_ACCOUNT,
        "RECORDS": URL_RECORDS,
        "DAILY": URL_PNL_DAILY,
        "MONTHLY": URL_PNL_MONTHLY
    }
    render_trade_records(urls_dict)

