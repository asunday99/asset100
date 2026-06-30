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
    icons=['', ''], 
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
    """매매 기록 탭 - 미래에셋 스타일 UI"""
    import datetime
    
    # ── 세션 상태 초기화 ──────────────────────────────────────────
    if "trade_view_mode" not in st.session_state:
        st.session_state.trade_view_mode = "월별"
    if "trade_nav_year" not in st.session_state:
        st.session_state.trade_nav_year = datetime.date.today().year
    if "trade_nav_month" not in st.session_state:
        st.session_state.trade_nav_month = datetime.date.today().month
    if "show_perf_chart" not in st.session_state:
        st.session_state.show_perf_chart = False
    if "record_tab" not in st.session_state:
        st.session_state.record_tab = "매매 캘린더"

    # ── 최대 폭 제한 ───────────────────────────────────────────────
    st.markdown("""
    <style>
    /* 매매기록 탭 화면폭을 860px로 제한 */
    @media screen and (min-width: 860px) {
        .block-container {
            max-width: 860px !important;
        }
    }
    </style>
    <div style="max-width: 860px; margin: 0 auto;">
    """, unsafe_allow_html=True)

    # ── 이번 달 수익 계산 (일별 데이터 합산) ─────────────────────────────────
    import datetime as _dt
    _month_profit = 0
    _today = _dt.date.today()
    try:
        _df_daily = load_and_clean_data(urls.get("DAILY", ""))
        if not _df_daily.empty:
            # 날짜 컴럼 파싱 (26.6.30. 형식)
            _date_col = _df_daily.columns[0]
            _pnl_col = next((c for c in _df_daily.columns if "실현손익" in str(c).replace(" ", "")), None)
            if _pnl_col:
                _df_daily["_date"] = pd.to_datetime(
                    _df_daily[_date_col].astype(str).str.replace(" ", ""), format="%y.%m.%d.", errors="coerce"
                ).dt.date
                _df_daily[_pnl_col] = pd.to_numeric(
                    _df_daily[_pnl_col].astype(str).str.replace(",", ""), errors="coerce"
                ).fillna(0)
                _this_month = _df_daily[
                    _df_daily["_date"].apply(lambda d: d is not None and not pd.isna(d) and d.year == _today.year and d.month == _today.month)
                ]
                _month_profit = int(_this_month[_pnl_col].sum())
    except Exception:
        _month_profit = 0

    if _month_profit > 0:
        _profit_text = f"+{_month_profit:,}원"
        _profit_color = "#FF4B4B"
        _msg = "벌고 있어요! 🚀"
        _expander_title = f"📅 이번 달 +{_month_profit:,}원 벌고 있어요!"
    elif _month_profit < 0:
        _profit_text = f"{_month_profit:,}원"
        _profit_color = "#4B9FFF"
        _msg = "빠졌어요 💧"
        _expander_title = f"📅 이번 달 {_month_profit:,}원 빠졌어요"
    else:
        _profit_text = "0원"
        _profit_color = "#A0A0A0"
        _msg = "아직 0원이에요"
        _expander_title = f"📅 이번 달 아직 0원이에요"

    # ── 임팩트 있는 이번 달 수익 헤더 ──────────────────────────────────────
    st.markdown(f"""
<div style='
    background: linear-gradient(135deg, #1a0a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid {_profit_color}44;
    border-left: 4px solid {_profit_color};
    border-radius: 16px;
    padding: 28px 28px 22px 28px;
    margin-bottom: 20px;
    text-align: center;
'>
  <div style='color:#A0A0B0; font-size:14px; letter-spacing:2px; margin-bottom:10px;'>이번 달 수익</div>
  <div style='color:{_profit_color}; font-size:44px; font-weight:900; letter-spacing:-1px; margin-bottom:8px;'>{_profit_text}</div>
  <div style='color:#d0d0d0; font-size:18px; font-weight:500;'>{_msg}</div>
</div>
""", unsafe_allow_html=True)

    # ── 매매 캘린더 ─────────────────────────────────────────────────
    with st.expander(_expander_title, expanded=True):
        df_rec = load_records_data(urls.get("RECORDS", ""))
        _render_trade_calendar(df_rec)

    # ── 익절/손절 계산기 ────────────────────────────────────────
    # ── 연간 실현수익 막대 차트 (일별 데이터 직접 집계) ────────────────────────────────────────────
    try:
        import datetime as _dt2
        _df_daily_chart = load_and_clean_data(urls.get("DAILY", ""))
        _df_dash_chart = load_and_clean_data(urls.get("DASHBOARD", ""))
        if not _df_daily_chart.empty:
            _dc2 = _df_daily_chart.columns[0]
            _pc2 = next((c for c in _df_daily_chart.columns if "실현손익" in str(c).replace(" ", "")), None)
            _year_profit_c = 0
            _monthly_profits_c = {i: 0 for i in range(1, 13)}
            if _pc2:
                _tmp2 = _df_daily_chart.copy()
                _tmp2['_date2'] = pd.to_datetime(
                    _tmp2[_dc2].astype(str).str.replace(' ', ''), format='%y.%m.%d.', errors='coerce'
                )
                _tmp2[_pc2] = pd.to_numeric(_tmp2[_pc2].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
                _tmp2 = _tmp2.dropna(subset=['_date2'])
                _cur_year = _dt2.date.today().year
                _year_rows = _tmp2[_tmp2['_date2'].dt.year == _cur_year]
                for _, _row in _year_rows.iterrows():
                    _m = _row['_date2'].month
                    _val = int(_row[_pc2])
                    _monthly_profits_c[_m] = _monthly_profits_c.get(_m, 0) + _val
                    _year_profit_c += _val
            _max_profit_c = max(max(_monthly_profits_c.values()), 1)
            _bars_html_c = ""
            for _m in range(1, 13):
                _p = _monthly_profits_c[_m]
                _h = max(min(int((_p / _max_profit_c) * 100), 100), 5) if _p > 0 else 2
                _clr = "#FF6B00" if _p > 0 else "#333"
                _lbl = f"<div style=\'color:#FF6B00;font-size:10px;font-weight:bold;margin-bottom:2px;white-space:nowrap;\'>{int(_p/10000):,}</div>" if _p > 0 else ""
                _bars_html_c += f"<div style=\'display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:120px;width:7%;margin:0 1%;\'>{_lbl}<div style=\'background-color:{_clr};width:100%;height:{_h}%;border-radius:4px 4px 0 0;\'></div><div style=\'color:#a0a0a0;font-size:10px;margin-top:5px;\'>{_m}</div></div>"
            _chart1 = f"<div style=\'background-color:#111;border-radius:12px;padding:20px;margin-bottom:15px;\'><div style=\'display:flex;align-items:center;margin-bottom:20px;\'><div style=\'width:30px;height:30px;border-radius:50%;background:conic-gradient(#FF6B00 0% 15%,#333 15% 100%);margin-right:15px;\'></div><div style=\'color:white;font-size:16px;font-weight:bold;line-height:1.4;\'>올해 달성한 실현수익은<br><span style=\'font-size:20px;\'>{_year_profit_c:,}원 이에요</span></div></div><div style=\'display:flex;align-items:flex-end;justify-content:space-between;height:130px;border-bottom:1px solid #333;padding-bottom:5px;\'>{_bars_html_c}</div></div>"
            st.markdown(_chart1, unsafe_allow_html=True)
            # ── 올해 실현수익률 & 연말 예상: 매매기록에서 직접 계산 ──
            try:
                _df_rec_chart = load_records_data(urls.get("RECORDS", ""))
                _monthly_rates_c2 = {i: [] for i in range(1, 13)}
                if not _df_rec_chart.empty and "날짜" in _df_rec_chart.columns and "수익률" in _df_rec_chart.columns:
                    _df_rec_chart["_rc_date"] = pd.to_datetime(
                        _df_rec_chart["날짜"].astype(str).str.replace(" ", ""), format="%y.%m.%d.", errors="coerce"
                    )
                    _df_rec_chart["_rc_rate"] = pd.to_numeric(
                        _df_rec_chart["수익률"].astype(str).str.replace(",", ""), errors="coerce"
                    )
                    _rc_year = _dt2.date.today().year
                    _rc_rows = _df_rec_chart.dropna(subset=["_rc_date", "_rc_rate"])
                    _rc_rows = _rc_rows[_rc_rows["_rc_date"].dt.year == _rc_year]
                    if "계좌" in _rc_rows.columns:
                        _rc_rows = _rc_rows[_rc_rows["계좌"].astype(str).str.strip() != "모의계산"]
                    for _, _rr in _rc_rows.iterrows():
                        _rm = _rr["_rc_date"].month
                        _rv = float(_rr["_rc_rate"])
                        if _rv != 0:
                            _monthly_rates_c2[_rm].append(_rv)
                _monthly_avg_rates2 = {}
                for _mi in range(1, 13):
                    if _monthly_rates_c2[_mi]:
                        _monthly_avg_rates2[_mi] = sum(_monthly_rates_c2[_mi]) / len(_monthly_rates_c2[_mi])
                    else:
                        _monthly_avg_rates2[_mi] = 0.0
                _all_rates2 = [r for rates in _monthly_rates_c2.values() for r in rates]
                _ytd_val = sum(_all_rates2) / len(_all_rates2) if _all_rates2 else 0.0
                _ytd = f"{_ytd_val:.2f}%"
                _today_m2 = _dt2.date.today().month
                _today_d2 = _dt2.date.today().day
                # 완료된 개월수: 당월 1일~4일이면 전월까지, 그 외 당월 포함
                _completed_months2 = _today_m2 - 1 if _today_d2 <= 4 else _today_m2
                _completed_months2 = max(_completed_months2, 1)
                # 연말 예상 = 올해 전체 수익률 평균 × (12 / 완료 개월수)
                if _all_rates2 and _completed_months2 > 0:
                    _exp_val = _ytd_val * (12 / _completed_months2)
                    _exp = f"{_exp_val:.2f}%"
                else:
                    _exp = "0%"
            except Exception:
                _ytd = "0%"
                _exp = "0%"
                _monthly_avg_rates2 = {i: 0.0 for i in range(1, 13)}
            # ── 두 번째 차트: 월별 수익률(%) 막대 (보라색) ──
            _max_rate_c2 = max(max(_monthly_avg_rates2.values()), 0.1)
            _bars_html_rate2 = ""
            for _m in range(1, 13):
                _r = _monthly_avg_rates2.get(_m, 0.0)
                _h2 = max(min(int((_r / _max_rate_c2) * 100), 100), 5) if _r > 0 else 2
                _clr2 = "#8A2BE2" if _r > 0 else "#333"
                _lbl2 = (f"<div style='color:#8A2BE2;font-size:10px;font-weight:bold;margin-bottom:2px;white-space:nowrap;'>{_r:.1f}%</div>" if _r > 0 else "")
                _bars_html_rate2 += (
                    f"<div style='display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:120px;width:7%;margin:0 1%;'>"
                    f"{_lbl2}<div style='background-color:{_clr2};width:100%;height:{_h2}%;border-radius:4px 4px 0 0;'></div>"
                    f"<div style='color:#a0a0a0;font-size:10px;margin-top:5px;'>{_m}</div></div>"
                )
            _chart2 = (
                f"<div style='background-color:#111;border-radius:12px;padding:20px;margin-bottom:15px;'>"
                f"<div style='display:flex;align-items:center;margin-bottom:20px;'>"
                f"<div style='width:30px;height:30px;border-radius:50%;background:conic-gradient(#8A2BE2 0% 15%,#333 15% 100%);margin-right:15px;'></div>"
                f"<div style='color:white;font-size:16px;font-weight:bold;line-height:1.4;'>올해 실현수익률은 "
                f"<span style='font-size:20px;color:#8A2BE2;'>{_ytd}</span> 이에요<br>"
                f"<span style='font-size:13px;color:#A0A0A0;font-weight:normal;'>이 추세라면 연말까지 {_exp} 예상돼요</span>"
                f"</div></div>"
                f"<div style='display:flex;align-items:flex-end;justify-content:space-between;height:130px;border-bottom:1px solid #333;padding-bottom:5px;'>{_bars_html_rate2}</div></div>"
            )
            st.markdown(_chart2, unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown("---")
    _render_profit_loss_calculator()

    st.markdown('</div>', unsafe_allow_html=True)
\

def _render_trade_calendar(df_rec: pd.DataFrame):
    """매매 캘린더 렌더링."""
    today = datetime.date.today()
    year, month = today.year, today.month
    st.subheader(f"📅 {year}년 {month}월")

    kr_holidays = holidays.KR()
    daily_pnl_dict: dict = {}

    if not df_rec.empty:
        try:
            df_rec["계좌"]    = df_rec["계좌"].astype(str).str.strip()
            df_rec["날짜_str"] = df_rec["날짜"].astype(str).str.strip()
            is_mock  = (df_rec["계좌"] == "모의계산") | (df_rec["날짜_str"] == "모의계산")
            df_real  = df_rec[~is_mock].copy()

            if "날짜" in df_real.columns and "차익실현금액" in df_real.columns:
                df_real["date"] = pd.to_datetime(
                    df_real["날짜_str"].str.replace(" ", ""), format="%y.%m.%d.", errors="coerce"
                ).dt.date
                df_real["차익실현금액"] = pd.to_numeric(
                    df_real["차익실현금액"].astype(str).str.replace(",", ""), errors="coerce"
                ).fillna(0)
                daily_pnl_dict = df_real.groupby("date")["차익실현금액"].sum().to_dict()
        except Exception as e:
            logger.warning("캘린더 데이터 파싱 실패: %s", e)
            st.warning(f"⚠️ 캘린더 데이터 파싱 실패: {e}")

    monthly_total = sum(v for k, v in daily_pnl_dict.items() if k.year == year and k.month == month)

    cal   = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdatescalendar(year, month)

    html_str = '<table style="width:100%;table-layout:fixed;border-collapse:collapse;border:1px solid #333;">'
    html_str += "<tr>"
    for day_name in ["일", "월", "화", "수", "목", "금", "토"]:
        html_str += f'<th style="background-color:#0A0A0C;color:#FF9900;padding:10px;border:1px solid #2b2e35;width:14.28%;text-align:center;">{day_name}</th>'
    html_str += "</tr>"

    for week in weeks:
        html_str += "<tr>"
        for d in week:
            day_text   = str(d.day) if d.month == month else " "
            style_date = "height:30px;background-color:#111111;color:#FF9900;font-weight:bold;text-align:left;padding:5px;border:1px solid #2b2e35;width:14.28%;"
            html_str  += f'<td style="{style_date}">{day_text}</td>'
        html_str += "</tr><tr>"
        for d in week:
            if d.month == month and d in daily_pnl_dict:
                val = daily_pnl_dict[d]
                bg_style      = "background-color:#000000;"
                val_color     = get_color_by_value(val)
                formatted_val = f"{val:,.0f}" if val != 0 else "&nbsp;"
            elif d.month == month and d.weekday() < 5 and d in kr_holidays:
                bg_style      = "background-color:#000000;"
                val_color     = "#888888"
                formatted_val = "휴장"
            else:
                bg_style      = "background-color:#000000;"
                val_color     = "white"
                formatted_val = "&nbsp;"
            style_data = f"height:80px;{bg_style}color:{val_color};border:1px solid #2b2e35;text-align:center;vertical-align:middle;padding:5px;font-size:15px;font-weight:bold;"
            html_str  += f'<td style="{style_data}">{formatted_val}</td>'
        html_str += "</tr>"
    html_str += "</table>"
    st.markdown(html_str, unsafe_allow_html=True)

def _render_trade_table(df_rec: pd.DataFrame):
    """매매 기록 표 및 모의계산 렌더링."""
    if df_rec.empty:
        st.info("매매 기록 데이터가 없습니다.")
        return

    df_rec = df_rec.drop(columns=[c for c in df_rec.columns if "기타" in str(c)], errors="ignore")
    df_rec["계좌"] = df_rec["계좌"].astype(str).str.strip()
    df_rec["날짜"] = df_rec["날짜"].astype(str).str.strip()
    is_mock = (df_rec["계좌"] == "모의계산") | (df_rec["날짜"] == "모의계산")
    df_real = df_rec[~is_mock]
    df_mock = df_rec[is_mock]

    numeric_cols = df_rec.select_dtypes(include=["float", "int"]).columns.tolist()

    def apply_style(df_to_style: pd.DataFrame):
        styler         = df_to_style.style
        num_cols_here  = [c for c in numeric_cols if c in df_to_style.columns]
        if "수익률" in num_cols_here:
            styler = styler.format("{:,.2f}", subset=["수익률"], na_rep="")
            others = [c for c in num_cols_here if c != "수익률"]
            if others:
                styler = styler.format("{:,.0f}", subset=others, na_rep="")
        elif num_cols_here:
            styler = styler.format("{:,.0f}", subset=num_cols_here, na_rep="")

        if "차익실현금액" in df_to_style.columns:
            def color_profit(val):
                if isinstance(val, (int, float)):
                    if val > 0: return "background-color: #990000;"
                    if val < 0: return "background-color: #1155cc;"
                return ""
            styler = styler.map(color_profit, subset=["차익실현금액"])

        if "날짜" in df_to_style.columns and len(df_to_style) > 0:
            try:
                dates = pd.to_datetime(
                    df_to_style["날짜"].astype(str).str.replace(" ", ""), format="%y.%m.%d.", errors="coerce"
                )
                max_date_str = (
                    df_to_style.loc[dates.idxmax(), "날짜"] if dates.notna().any()
                    else df_to_style["날짜"].max()
                )

                def highlight_recent(row):
                    return ["background-color: #38761d;" if str(row.get("날짜", "")) == str(max_date_str) else ""] * len(row)
                styler = styler.apply(highlight_recent, axis=1)
            except Exception as e:
                logger.warning("최신 날짜 하이라이트 실패: %s", e)
        return styler

    st.subheader("📋 매매 기록")
    if not df_real.empty:
        st.dataframe(apply_style(df_real), use_container_width=True, hide_index=True)
    else:
        st.info("실제 매매 기록이 없습니다.")

    st.markdown("---")
    st.subheader("💡 모의계산")
    mock_cols = ["종목명", "매수_수량", "매수_단가", "매수_금액", "매도_수량", "매도_단가", "매도_금액", "매매비용", "차익실현금액", "수익률"]

    if "mock_data" not in st.session_state:
        st.session_state.mock_data = df_mock[[c for c in mock_cols if c in df_mock.columns]].copy()

    edited_mock = st.data_editor(
        apply_style(st.session_state.mock_data),
        num_rows="dynamic", hide_index=True, use_container_width=True,
        disabled=["매수_금액", "매도_금액", "차익실현금액", "수익률"],
        key="mock_data_editor",
    )

    changed = False
    for i, row in edited_mock.iterrows():
        try:
            b_qty = safe_int_float(row.get("매수_수량", 0))
            old_b = safe_int_float(st.session_state.mock_data.at[i, "매수_수량"]) if i in st.session_state.mock_data.index else 0
            s_qty = b_qty if b_qty != old_b else safe_int_float(row.get("매도_수량", 0))
            if b_qty != old_b:
                edited_mock.at[i, "매도_수량"] = s_qty
                changed = True

            b_prc = safe_int_float(row.get("매수_단가", 0))
            s_prc = safe_int_float(row.get("매도_단가", 0))
            cost  = safe_int_float(row.get("매매비용", 0))
            n_buy  = b_qty * b_prc
            n_sell = s_qty * s_prc
            n_prof = n_sell - n_buy - cost
            n_rate = (n_prof / n_buy * 100) if n_buy > 0 else 0.0

            if (abs(safe_int_float(row.get("매수_금액", 0)) - n_buy) > 0.01 or
                abs(safe_int_float(row.get("매도_금액", 0)) - n_sell) > 0.01 or
                abs(safe_int_float(row.get("차익실현금액", 0)) - n_prof) > 0.01 or
                abs(safe_int_float(row.get("수익률", 0)) - n_rate) > 0.01):
                edited_mock.at[i, "매수_금액"]    = n_buy
                edited_mock.at[i, "매도_금액"]    = n_sell
                edited_mock.at[i, "차익실현금액"] = n_prof
                edited_mock.at[i, "수익률"]       = n_rate
                changed = True
        except Exception as e:
            logger.warning("모의계산 행 %d 계산 실패: %s", i, e)

    if edited_mock.isnull().values.any():
        edited_mock = edited_mock.fillna(0)
        if "종목명" in edited_mock.columns:
            edited_mock["종목명"] = edited_mock["종목명"].replace(0, "")
        changed = True

    if changed:
        st.session_state.mock_data = edited_mock
        st.rerun()


@st.cache_data(ttl=3600)
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
    
    if "config" not in st.session_state:
        st.session_state.config = load_config()
        st.session_state.goal_amount_str = f"{int(st.session_state.config['goal_amount']):,}"
        st.session_state.target_date_val = datetime.datetime.strptime(st.session_state.config['target_date'], "%Y-%m-%d").date()

    def format_goal_amount():
        val = st.session_state.goal_amount_input.replace(",", "")
        try:
            st.session_state.goal_amount_str = f"{int(val):,}"
            st.session_state.config['goal_amount'] = str(int(val))
            save_config(st.session_state.config)
        except ValueError:
            pass

    def update_target_date():
        st.session_state.target_date_val = st.session_state.target_date_input
        st.session_state.config['target_date'] = st.session_state.target_date_input.strftime("%Y-%m-%d")
        save_config(st.session_state.config)

    try:
        GOAL_AMOUNT = int(st.session_state.goal_amount_str.replace(",", ""))
    except ValueError:
        GOAL_AMOUNT = 10_000_000_000
        
    target_date = st.session_state.target_date_val
    
    d_days = (target_date - datetime.date.today()).days
    
    urls_dict = {
        "DASHBOARD": URL_DASHBOARD,
        "ACCOUNT": URL_ACCOUNT,
        "RECORDS": URL_RECORDS,
        "DAILY": URL_PNL_DAILY,
        "MONTHLY": URL_PNL_MONTHLY
    }
    all_data = load_all_data(urls_dict)
    
    df_account = all_data.get("ACCOUNT", pd.DataFrame())
    df_dash = all_data.get("DASHBOARD", pd.DataFrame())
    df_daily = all_data.get("DAILY", pd.DataFrame())
    df_monthly = all_data.get("MONTHLY", pd.DataFrame())
    today_profit = 0
    month_profit = 0
    year_profit = 0
    today_profit_pct = 0.0
    
    # ── 일별 데이터에서 직접 월별 집계 (손익현황_월별 시트 CSV export 불가 대체) ──
    df_monthly_computed = pd.DataFrame()
    if not df_daily.empty:
        try:
            _dc = df_daily.columns[0]
            _pc = next((c for c in df_daily.columns if '실현손익' in str(c).replace(' ', '')), None)
            _ac = next((c for c in df_daily.columns if '자산총액' in str(c).replace(' ', '') or '당일자산' in str(c).replace(' ', '')), None)
            _cc = next((c for c in df_daily.columns if '매매비용' in str(c).replace(' ', '') or '당일매매' in str(c).replace(' ', '')), None)
            if _pc:
                _tmp = df_daily.copy()
                _tmp['_date'] = pd.to_datetime(
                    _tmp[_dc].astype(str).str.replace(' ', ''), format='%y.%m.%d.', errors='coerce'
                )
                _tmp[_pc] = pd.to_numeric(_tmp[_pc].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
                if _ac:
                    _tmp[_ac] = pd.to_numeric(_tmp[_ac].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
                if _cc:
                    _tmp[_cc] = pd.to_numeric(_tmp[_cc].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
                _tmp = _tmp.dropna(subset=['_date'])
                _tmp['_ym'] = _tmp['_date'].dt.to_period('M')
                rows = []
                for ym, grp in _tmp.groupby('_ym'):
                    last_row = grp.sort_values('_date').iloc[-1]
                    last_asset = int(last_row[_ac]) if _ac else 0
                    sum_cost = int(grp[_cc].sum()) if _cc else 0
                    sum_pnl = int(grp[_pc].sum())
                    rows.append({'년-월': str(ym), '자산총액': last_asset, '매매비용': sum_cost, '실현손익': sum_pnl})
                if rows:
                    df_monthly_computed = pd.DataFrame(rows[::-1])  # 최신월 먼저
        except:
            pass
    
    # df_monthly_computed가 있으면 우선 사용, 없으면 기존 df_monthly 사용
    if not df_monthly_computed.empty:
        df_monthly = df_monthly_computed
    
    if not df_daily.empty:
        try:
            profit_col = next((c for c in df_daily.columns if '실현손익' in str(c).replace(' ', '')), df_daily.columns[2])
            val_str = str(df_daily.iloc[0][profit_col]).replace(',', '')
            today_profit = int(float(val_str))
        except:
            pass
            
    if not df_monthly.empty:
        try:
            profit_col = next((c for c in df_monthly.columns if '실현손익' in str(c).replace(' ', '')), df_monthly.columns[2])
            val_str = str(df_monthly.iloc[0][profit_col]).replace(',', '')
            month_profit = int(float(val_str))
            
            date_col = df_monthly.columns[0]
            year_data = df_monthly[df_monthly[date_col].astype(str).str.contains(str(datetime.date.today().year), na=False)]
            year_sum = 0
            for v in year_data[profit_col]:
                try:
                    year_sum += int(float(str(v).replace(',', '')))
                except: pass
            year_profit = year_sum
        except:
            pass
        
    
    # 동적 파싱으로 현황 요약 테이블 찾기
    summary_start_row = 7
    if not df_dash.empty:
        for r in range(len(df_dash)):
            if '현황요약' in str(df_dash.iloc[r, 0]).replace(' ', ''):
                summary_start_row = r + 1
                break
                
    total_assets = 0
    if not df_dash.empty and len(df_dash) >= summary_start_row + 2:
        val_str = str(df_dash.iloc[summary_start_row + 1, 1]).replace(',', '').strip()
        try:
            total_assets = int(float(val_str))
        except ValueError:
            total_assets = 0
            
    achievement_rate = (total_assets / GOAL_AMOUNT) * 100 if GOAL_AMOUNT > 0 else 0
    progress_val = min(max(achievement_rate / 100, 0.0), 1.0)

    # --- 스샷 2 UI 시작 ---
    

    if total_assets > 0:
        base_asset = total_assets - today_profit
        if base_asset > 0:
            today_profit_pct = (today_profit / base_asset) * 100
            
    sign = "+" if today_profit > 0 else ""
    color = "#FF1493" if today_profit < 0 else "#FF4B4B"
    
    month_profit_pct = 0.0
    if total_assets > 0:
        month_base_asset = total_assets - month_profit
        if month_base_asset > 0:
            month_profit_pct = (month_profit / month_base_asset) * 100
            
    month_sign = "+" if month_profit > 0 else ""
    month_color = "#FF1493" if month_profit < 0 else "#FF4B4B"
    
    col_left, col_right = st.columns([1.3, 1.0], gap="large")
    with col_left:
        gs_val = st.session_state.gs_val
        if 'target_date_dynamic' not in st.session_state:
            _ucfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_config.json')
            try:
                with open(_ucfg_path, 'r') as _f:
                    _ucfg = json.load(_f)
                st.session_state.target_date_dynamic = datetime.datetime.strptime(_ucfg.get('goal_date', ''), '%Y-%m-%d').date()
                st.session_state.gs_val = float(_ucfg.get('goal_amount_eok', st.session_state.gs_val))
            except:
                st.session_state.target_date_dynamic = datetime.date.today()
        
        target_date_dynamic = st.session_state.target_date_dynamic
        if target_date_dynamic is None:
            target_date_dynamic = datetime.date.today()
            st.session_state.target_date_dynamic = target_date_dynamic
        ach = min((total_assets / (gs_val*100000000)) * 100, 100.0) if gs_val > 0 else 0
        d_days_dynamic = (target_date_dynamic - datetime.date.today()).days
        formatted_gs_val = f"{gs_val:.1f}".rstrip('0').rstrip('.')

        st.markdown(f'''<div class='glass-card' style='padding: 20px; padding-bottom:5px; border-radius: 15px 15px 0 0; border-bottom: none; margin-bottom: 0;'>
<div style="text-align:center; padding-top:10px;">
<div class="neon-text" style="font-size:42px;">₩{int(total_assets):,}</div>
<div style="font-size:16px; color:#A0A0A0; margin-top:5px; margin-bottom: 25px;">당월 실현수익 <span style="color:{month_color};">{month_sign}{month_profit:,}원</span></div>
        
<div style="width:100%; background-color:rgba(255,255,255,0.05); border-radius:10px; height:8px; margin-top:20px; margin-bottom:10px; overflow:hidden;">
<div style="width:{ach}%; background:linear-gradient(90deg, #FF6B00, #FF9900); height:100%; border-radius:10px;"></div>
</div>
<div style="font-size:15px; color:#E0E0E0; font-weight:bold; display:flex; flex-wrap:nowrap; justify-content:space-between; align-items:center; letter-spacing:0.5px; gap: 4px;">
<span style="color:#FF9900; font-weight:900; font-size:14px; white-space:nowrap;">{ach:.2f}% 달성</span>
<div style="display:flex; align-items:center; flex-wrap:nowrap; gap:6px;">
<span style="font-size:12px;">목표 {formatted_gs_val}억</span>
<span style="font-size:11px; color:#FFFFFF; background-color:rgba(255,255,255,0.15); padding:2px 6px; border-radius:10px; white-space:nowrap;">D-{d_days_dynamic}</span>
</div>
</div>
    </div>''', unsafe_allow_html=True)
        
        with st.expander("⚙️ 목표 재설정", expanded=False):
            st.components.v1.html('''<script>
const elements = parent.document.querySelectorAll('div[data-testid="stExpander"] details summary p');
elements.forEach(el => {
    if (el.innerText.includes("목표 재설정")) {
        el.style.fontSize = "70%";
        el.style.opacity = "0.7";
    }
});
</script>''', height=0)
            sc1, sc2 = st.columns(2)
            with sc1:
                new_amt = st.number_input("목표 금액 (원)", value=int(st.session_state.gs_val * 100000000), step=100000000)
                if new_amt != int(st.session_state.gs_val * 100000000):
                    st.session_state.gs_val = new_amt / 100000000.0
                    _ucfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_config.json')
                    try:
                        _ucfg = {}
                        if os.path.exists(_ucfg_path):
                            with open(_ucfg_path, 'r') as _f:
                                _ucfg = json.load(_f)
                        _ucfg['goal_amount_eok'] = st.session_state.gs_val
                        _ucfg['goal_date'] = st.session_state.get('target_date_dynamic', datetime.date.today()).strftime('%Y-%m-%d')
                        with open(_ucfg_path, 'w') as _f:
                            json.dump(_ucfg, _f)
                    except:
                        pass
                    st.rerun()

            with sc2:
                new_date = st.date_input(
                    "📅 목표일 달력 (선택)",
                    value=st.session_state.get('target_date_dynamic', datetime.date.today()),
                    format="YYYY/MM/DD"
                )
                if new_date is None:
                    new_date = datetime.date.today()
                if new_date != st.session_state.get('target_date_dynamic', datetime.date.today()):
                    st.session_state.target_date_dynamic = new_date
                    _ucfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_config.json')
                    try:
                        _ucfg = {}
                        if os.path.exists(_ucfg_path):
                            with open(_ucfg_path, 'r') as _f:
                                _ucfg = json.load(_f)
                        _ucfg['goal_date'] = new_date.strftime('%Y-%m-%d')
                        _ucfg['goal_amount_eok'] = st.session_state.gs_val
                        with open(_ucfg_path, 'w') as _f:
                            json.dump(_ucfg, _f)
                    except:
                        pass
                    st.rerun()

        # -- 매크로 지표 expander --
        with st.expander("📊 매크로 지표", expanded=False):
            try:
                macro_changes = get_macro_changes()
                pairs = []
                
                # 강건한 데이터행 추출 (헤더 무시)
                for lc, vc in [(13, 14), (15, 16)]:
                    for row_i in range(min(15, len(df_dash))):
                        try:
                            raw_lbl = str(df_dash.iloc[row_i, lc]).replace('[','').replace(']','').strip()
                            val = str(df_dash.iloc[row_i, vc]).strip()
                            if raw_lbl and raw_lbl != 'nan' and 'Unnamed' not in raw_lbl and val and val != 'nan' and val != '0.0':
                                pairs.append((raw_lbl, val))
                        except: pass
                
                # 순서 보장을 위해 중복 제거 및 8개만 선택
                TARGET_ORDER = [
                    '[미국10년국채금리]', '[장단기 금리차]', '[USD/KRW 환율]', '[USD/JPY 환율]',
                    '[일본10년국채금리]', '[DXY]', '[XLF-QQQ괴리율]', '[ADX 추세강도]',
                    '[하이일드 스프레드]', '[vix지수]'
                ]
                
                # Map available pairs to a dictionary by target title
                mapped_vals = {}
                for raw_lbl, val in pairs:
                    lbl = MACRO_TITLE_MAP.get(raw_lbl, raw_lbl)
                    if lbl not in mapped_vals:
                        mapped_vals[lbl] = val
                
                # Add default loading values for missing items
                for t in TARGET_ORDER:
                    if t not in mapped_vals:
                        mapped_vals[t] = "로드 중..."
                        
                cards_html_list = []
                for lbl in TARGET_ORDER:
                    val = mapped_vals[lbl]
                    
                    change_str = ""
                    if lbl in macro_changes:
                        chg = macro_changes[lbl]
                        if chg is not None and not __import__('pandas').isna(chg):
                            sign = "+" if chg > 0 else ""
                            change_color = "#FF4B4B" if chg > 0 else "#1e90ff"
                            change_str = f' <span style="font-size:12px; font-weight:700; color:{change_color};">({sign}{chg:.2f})</span>'
                    
                    diff_color = 'color:white;'
                    # Padding reduced to make boxes thinner as requested
                    cards_html_list.append(f'<div style="background:#1a1a2e;border-radius:12px;padding:8px 10px;text-align:center;"><div style="color:#a0a0a0;font-size:11px;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{lbl}</div><div style="{diff_color}font-size:15px;font-weight:bold;">{val}{change_str}</div></div>')
                
                # 순서에 맞춰 3줄로 나눔
                row1 = "".join(cards_html_list[0:4])
                row2 = "".join(cards_html_list[4:8])
                row3 = "".join(cards_html_list[8:10])
                
                # Mobile shows 2 per line, desktop 4 per line
                macro_grid_html = f'''
                <style>
                .macro-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin-bottom:8px; }}
                .macro-grid-row3 {{ display:grid; grid-template-columns:repeat(2,1fr); gap:8px; margin-bottom:8px; width:50%; margin: 0 auto; }}
                @media(max-width:768px){{
                    .macro-grid {{ grid-template-columns:repeat(2,1fr); }}
                    .macro-grid-row3 {{ width:100%; }}
                }}
                </style>
                <div class="macro-grid">{row1}</div>
                <div class="macro-grid">{row2}</div>
                <div class="macro-grid-row3">{row3}</div>
                '''
                st.markdown(macro_grid_html, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"매크로 지표 로딩 실패: {e}")

        # -- Toss Style Bar Chart --
        try:
            import pandas as pd
            import datetime
            if df_monthly.empty or len(df_monthly.columns) < 3:
                st.info("월별 손익 데이터를 불러오는 중입니다. 잠시 후 새로고침해 주세요.")
                raise ValueError("df_monthly empty")
            date_col = df_monthly.columns[0]
            profit_col = next((c for c in df_monthly.columns if '실현손익' in str(c).replace(' ', '')), df_monthly.columns[2])
            
            # Extract 2026 data
            year_data = df_monthly[df_monthly[date_col].astype(str).str.contains(str(datetime.date.today().year), na=False)].copy()
            
            monthly_profits = {i: 0 for i in range(1, 13)}
            for r in range(len(year_data)):
                d_str = str(year_data.iloc[r][date_col])
                val_str = str(year_data.iloc[r][profit_col]).replace(',', '')
                try:
                    m = int(d_str.split('-')[1].replace('월','').strip())
                    monthly_profits[m] = int(float(val_str))
                except: pass
                
            max_profit = max(max(monthly_profits.values()), 1)
            
            bars_html = ""
            for m in range(1, 13):
                p = monthly_profits[m]
                height_pct = max(min(int((p / max_profit) * 100), 100), 5) if p > 0 else 2
                color = "#FF6B00" if p > 0 else "#333"
                
                # Add text label for p (in 10,000s: 만원)
                if p > 0:
                    val_manwon = f"{int(p / 10000):,}"
                    label_html = f"<div style='color:#FF6B00; font-size:10px; font-weight:bold; margin-bottom:2px; white-space:nowrap;'>{val_manwon}</div>"
                else:
                    label_html = ""

                bars_html += f"""
                <div style='display:flex; flex-direction:column; align-items:center; justify-content:flex-end; height:120px; width:7%; margin:0 1%;'>
                    {label_html}
                    <div style='background-color:{color}; width:100%; height:{height_pct}%; border-radius:4px 4px 0 0;'></div>
                    <div style='color:#a0a0a0; font-size:10px; margin-top:5px;'>{m}</div>
                </div>
                """
                
            chart_html = f"""
            <div style='background-color:#111; border-radius:12px; padding:20px; margin-bottom:15px;'>
                <div style='display:flex; align-items:center; margin-bottom:20px;'>
                    <div style='width:30px; height:30px; border-radius:50%; background:conic-gradient(#FF6B00 0% 15%, #333 15% 100%); margin-right:15px;'></div>
                    <div style='color:white; font-size:16px; font-weight:bold; line-height:1.4;'>
                        올해 달성한 실현수익은<br>
                        <span style='font-size:20px;'>{year_profit:,}원 이에요</span>
                    </div>
                </div>
                <div style='display:flex; align-items:flex-end; justify-content:space-between; height:130px; border-bottom:1px solid #333; padding-bottom:5px;'>
                    {bars_html}
                </div>
            </div>
            """
            import re; st.markdown(re.sub(r'\n\s+', ' ', chart_html), unsafe_allow_html=True)

            try:
                ytd_return = str(df_dash.iloc[4, 12]).strip()
                expected_return = str(df_dash.iloc[5, 12]).strip()
                if ytd_return == 'nan': ytd_return = '0%'
                if expected_return == 'nan': expected_return = '0%'
            except:
                ytd_return = '0%'
                expected_return = '0%'


            chart_html2 = f"""
            <div style='background-color:#111; border-radius:12px; padding:20px; margin-bottom:15px;'>
                <div style='display:flex; align-items:center; margin-bottom:20px;'>
                    <div style='width:30px; height:30px; border-radius:50%; background:conic-gradient(#8A2BE2 0% 15%, #333 15% 100%); margin-right:15px;'></div>
                    <div style='color:white; font-size:16px; font-weight:bold; line-height:1.4;'>
                        올해 실현수익률은 <span style='font-size:20px; color:#8A2BE2;'>{ytd_return}</span> 이에요<br>
                        <span style='font-size:13px; color:#A0A0A0; font-weight:normal;'>이 추세라면 연말까지 {expected_return} 예상돼요</span>
                    </div>
                </div>
                <div style='display:flex; align-items:flex-end; justify-content:space-between; height:130px; border-bottom:1px solid #333; padding-bottom:5px;'>
                    {bars_html}
                </div>
            </div>
            """
            import re; st.markdown(re.sub(r'\n\s+', ' ', chart_html2), unsafe_allow_html=True)

            
            # -- Side-by-Side UI (Target vs Realized) --
            current_month = datetime.datetime.now().month
            prev_month = current_month - 1 if current_month > 1 else 12
            
            curr_profit = monthly_profits.get(current_month, 0)
            prev_profit = monthly_profits.get(prev_month, 0)
            
            # Extract target and actual values from df_dash
            try:
                monthly_target_pct_str = str(df_dash.columns[10])
                daily_target_pct_str = str(df_dash.iloc[0, 10])
                daily_target_amt_str = str(df_dash.iloc[1, 10])
                
                prev_profit_pct_str = str(df_dash.columns[12])
                prev_profit_amt_str = str(df_dash.iloc[0, 12])
                curr_profit_pct_str = str(df_dash.iloc[1, 12])
            except Exception as e:
                monthly_target_pct_str = "-"
                daily_target_pct_str = "-"
                daily_target_amt_str = "-"
                prev_profit_pct_str = "-"
                prev_profit_amt_str = "-"
                curr_profit_pct_str = "-"
                
            summary_html = f"""
            <div style='display:flex; gap:15px; margin-bottom:15px;'>
                <!-- Left Box: Target -->
                <div style='flex:1; background-color:#1e1410; border:1px solid #4a2b12; border-radius:12px; padding:20px;'>
                    <h4 style='color:#FF9900; margin-top:0; margin-bottom:20px; font-size:16px;'>달성 목표</h4>
                    <div style='display:flex; justify-content:space-between; margin-bottom:12px;'>
                        <div style='color:#a0a0a0; font-size:13px;'>매월 달성할 수익률</div>
                        <div style='color:white; font-size:14px; font-weight:bold;'>{monthly_target_pct_str}</div>
                    </div>
                    <div style='display:flex; justify-content:space-between; margin-bottom:12px;'>
                        <div style='color:#a0a0a0; font-size:13px;'>매일 달성할 수익률</div>
                        <div style='color:white; font-size:14px; font-weight:bold;'>{daily_target_pct_str}</div>
                    </div>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <div style='color:#a0a0a0; font-size:13px;'>매일 달성할 실현금액</div>
                        <div style='color:#FF9900; font-size:15px; font-weight:bold;'>{daily_target_amt_str}원</div>
                    </div>
                </div>
                
                <!-- Right Box: Actual -->
                <div style='flex:1; background-color:#16102b; border:1px solid #2a1b42; border-radius:12px; padding:20px;'>
                    <h4 style='color:#b89aff; margin-top:0; margin-bottom:20px; font-size:16px;'>실현 수익</h4>
                    <div style='display:flex; justify-content:space-between; margin-bottom:12px;'>
                        <div style='color:#a0a0a0; font-size:13px;'>전월 실현 수익률</div>
                        <div style='color:white; font-size:14px; font-weight:bold;'>{prev_profit_pct_str}</div>
                    </div>
                    <div style='display:flex; justify-content:space-between; margin-bottom:12px;'>
                        <div style='color:#a0a0a0; font-size:13px;'>전월 실현 수익금</div>
                        <div style='color:white; font-size:14px; font-weight:bold;'>{prev_profit_amt_str}</div>
                    </div>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <div style='color:#a0a0a0; font-size:13px;'>당월 실현 수익률</div>
                        <div style='background-color:#10b981; color:white; padding:4px 8px; border-radius:6px; font-size:14px; font-weight:bold;'>{curr_profit_pct_str}</div>
                    </div>
                </div>
            </div>
            """
            import re; st.markdown(re.sub(r'\n\s+', ' ', summary_html), unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error rendering toss chart: {e}")
                
    
        
    trading_days = max(1, int(np.busday_count(datetime.date.today(), target_date + datetime.timedelta(days=1))))
    if total_assets > 0 and GOAL_AMOUNT > total_assets:
        daily_req_amt = (GOAL_AMOUNT - total_assets) / trading_days
        daily_req_rate = daily_req_amt / total_assets
        monthly_req_rate = daily_req_rate * 21
    else:
        daily_req_rate = 0
        monthly_req_rate = 0
        daily_req_amt = 0
    daily_req_rate_str = f"{daily_req_rate * 100:,.2f}%"
    monthly_req_rate_str = f"{monthly_req_rate * 100:,.2f}%"
    daily_req_amt_str = f"{int(daily_req_amt):,}"
    
    cur_month_profit_amt = "-"
    cur_month_profit_rate = "-"
    prev_month_profit_rate = "-"
    prev_month_profit_amt = "-"
    
    def find_metric_multi(df, labels, col_offset=1):
        for label in labels:
            label_clean = label.replace(" ", "")
            # Search in rows
            for r in range(min(20, len(df))):
                for c in range(min(20, len(df.columns))):
                    val = str(df.iloc[r, c]).replace(" ", "")
                    if label_clean in val and val != "":
                        try:
                            return str(df.iloc[r, c + col_offset]).strip()
                        except:
                            pass
            # Search in headers
            for c in range(min(20, len(df.columns))):
                val = str(df.columns[c]).replace(" ", "")
                if label_clean in val and val != "":
                    try:
                        return str(df.columns[c + col_offset]).strip()
                    except:
                        pass
        return "-"

    

    def format_num(val):
        if val == "-": return "-"
        val_str = str(val).strip()
        
        prefix = ""
        if val_str.startswith('+'): prefix = "+"
        elif val_str.startswith('-'): prefix = "-"
        elif val_str.startswith('▲'): prefix = "▲"
        elif val_str.startswith('▼'): prefix = "▼"
        
        try:
            fval = float(val_str.replace(',', '').replace('%', '').replace('+', '').replace('-', '').replace('▲', '').replace('▼', ''))
            
            if "%" in val_str:
                formatted = f"{fval:,.2f}%"
            elif fval.is_integer():
                formatted = f"{int(fval):,}"
            else:
                formatted = f"{fval:,.1f}"
                
            return f"{prefix}{formatted}"
        except:
            return val_str

    def extract_card_data(df, label_col_idx, val_col_idx, max_items=4):
        extracted = []
        if not df.empty and len(df.columns) > max(label_col_idx, val_col_idx):
            # Check header
            l = str(df.columns[label_col_idx]).strip()
            v = str(df.columns[val_col_idx]).strip()
            if "Unnamed" not in l and l != "" and str(l) != "nan" and str(l) != "0.0":
                extracted.append((l, format_num(v)))
            # Check rows
            for i in range(min(5, len(df))):
                l = str(df.iloc[i, label_col_idx]).strip()
                v = str(df.iloc[i, val_col_idx]).strip()
                if "Unnamed" not in l and l != "" and str(l) != "nan" and str(l) != "0.0":
                    if str(v) != "nan" and v != "":
                        extracted.append((l, format_num(v)))
        return extracted[:max_items]
    
    goal_metrics = extract_card_data(df_dash, 8, 10)
    profit_metrics = extract_card_data(df_dash, 11, 12)
    market_metrics_1 = extract_card_data(df_dash, 13, 14, 4)
    market_metrics_2 = extract_card_data(df_dash, 15, 16, 4)

    def get_color(val_str):
        val_str = str(val_str)
        if '-' in val_str or '▼' in val_str: return '#1e90ff'
        if '+' in val_str or '▲' in val_str: return '#ff4757'
        return 'white'

    def get_adx_color(val_str):
        try:
            val = float(str(val_str).replace('%', '').strip())
            if val >= 40: return '#ff4757'
            elif val >= 25: return '#feca57'
            else: return '#2ed573'
        except:
            return 'white'

    def render_metric_card(title, rows_list):
        rows_html = ""
        for label, val_text, val_color, val_bg, change_val in rows_list:
            bg_style = f"background-color: {val_bg}; padding: 0 4px; border-radius: 3px;" if val_bg else ""
            
            # Format the change value UI if it exists
            change_html = ""
            if change_val and change_val != "-":
                c_color = "#ff4757" if "+" in str(change_val) else ("#1e90ff" if "-" in str(change_val) else "#a0a0a0")
                change_html = f"<span style='color: {c_color}; font-size: 12px; margin-left: 8px;'>{change_val}</span>"

            rows_html += f"""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
    <span style="color: #A0A0A0; font-size: 13px;">{label}</span>
    <div style="text-align: right;">
        <span style="color: {val_color}; {bg_style} font-size: 16px; font-weight: bold;">{val_text}</span>
        {change_html}
    </div>
</div>
"""
        return f"""
<div class="glass-card" style="padding: 20px; margin-bottom: 10px; min-height: 200px;">
    <div style="color: #FF9900; font-size: 17px; font-weight: bold; margin-bottom: 15px;">{title}</div>
    {rows_html}
</div>
"""

    with col_right:
        # 구글 시트 대시보드 탭에서 자산 카드 데이터 동적 파싱
        # 구조: summary_start_row 기준 헤더행=row+0, 평가금액=row+1, 평가손익=row+2, 수익률=row+3
        # 컬럼: col0=항목명, col1=총합계, col2=주식, col3=금, col4=채권, col5=코인, col6=현금성
        _cat_meta = [
            ("주식",  2, "hover-stock", "#1e90ff"),
            ("금",    3, "hover-gold",  "#f1c40f"),
            ("채권",  4, "hover-bond",  "#00d8d6"),
            ("코인",  5, "hover-coin",  "#FF6B00"),
            ("현금성",6, "hover-cash",  "#6c5ce7"),
        ]
        def _parse_num(val):
            try:
                return float(str(val).replace(',', '').replace('%', '').strip())
            except:
                return 0.0

        _asset_rows = []
        try:
            _amt_row  = summary_start_row + 1
            _pft_row  = summary_start_row + 2
            _pct_row  = summary_start_row + 3
            for _cat, _col, _hover, _color in _cat_meta:
                _amt = _parse_num(df_dash.iloc[_amt_row, _col])
                _pft = _parse_num(df_dash.iloc[_pft_row, _col])
                _pct = _parse_num(df_dash.iloc[_pct_row, _col])
                _asset_rows.append({"category": _cat, "amount": _amt, "profit": _pft, "return_pct": _pct, "hover": _hover, "color": _color})
        except Exception as _e:
            # fallback: 하드코딩값
            _asset_rows = [
                {"category": "주식",  "amount": 1974918892, "profit": 255389985,  "return_pct": 14.85,  "hover": "hover-stock", "color": "#1e90ff"},
                {"category": "금",    "amount": 142910490,  "profit": -17897045,  "return_pct": -11.13, "hover": "hover-gold",  "color": "#f1c40f"},
                {"category": "채권",  "amount": 17516025,   "profit": -260227,    "return_pct": -1.46,  "hover": "hover-bond",  "color": "#00d8d6"},
                {"category": "코인",  "amount": 298825354,  "profit": -71356901,  "return_pct": -19.28, "hover": "hover-coin",  "color": "#FF6B00"},
                {"category": "현금성","amount": 396232726,  "profit": 0,          "return_pct": 0.0,    "hover": "hover-cash",  "color": "#6c5ce7"},
            ]
        df_asset = pd.DataFrame([
            {"category": "주식", "amount": _asset_rows[0]["amount"], "profit": _asset_rows[0]["profit"], "return_pct": _asset_rows[0]["return_pct"], "hover": "hover-stock", "color": "#1e90ff"},
            {"category": "금", "amount": _asset_rows[1]["amount"], "profit": _asset_rows[1]["profit"], "return_pct": _asset_rows[1]["return_pct"], "hover": "hover-gold", "color": "#f1c40f"},
            {"category": "채권", "amount": _asset_rows[2]["amount"], "profit": _asset_rows[2]["profit"], "return_pct": _asset_rows[2]["return_pct"], "hover": "hover-bond", "color": "#00d8d6"},
            {"category": "코인", "amount": _asset_rows[3]["amount"], "profit": _asset_rows[3]["profit"], "return_pct": _asset_rows[3]["return_pct"], "hover": "hover-coin", "color": "#FF6B00"},
            {"category": "현금성", "amount": _asset_rows[4]["amount"], "profit": _asset_rows[4]["profit"], "return_pct": _asset_rows[4]["return_pct"], "hover": "hover-cash", "color": "#6c5ce7"},
        ])
        import random
        cards_html = ""
        for _, row in df_asset.iterrows():
            p_sign = "+" if row['profit'] > 0 else ""
            c_class = "profit-positive" if row['profit'] > 0 else ("profit-negative" if row['profit'] < 0 else "")
            
            ret_pct = row['return_pct']
            
            # Generate mock SVG sparkline based on return
            pts = []
            x_step = 60 / 5
            y_start = 20 if ret_pct >= 0 else 10
            y_curr = y_start
            pts.append(f"0,{y_curr}")
            
            # simple random walk that trends up or down
            for step in range(1, 6):
                trend = -3 if ret_pct >= 0 else 3
                noise = random.uniform(-4, 4)
                y_curr += trend + noise
                pts.append(f"{step * x_step:.1f},{y_curr:.1f}")
            
            path_d = "M " + " L ".join(pts)
            
            if ret_pct > 0:
                stroke_color = "#FF4B4B" # Red
            elif ret_pct < 0:
                stroke_color = "#00BFFF" # Blue
            else:
                stroke_color = "#A0A0A0" # Gray
            
            # Using shadow filter for a neon effect on the line
            sparkline = f'''
            <div style="position: absolute; right: 20px; top: 50%; transform: translateY(-50%); opacity: 0.9;">
                <svg width="70" height="40" viewBox="0 0 60 30" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="{path_d}" stroke="{stroke_color}" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0px 0px 3px {stroke_color});"/>
                </svg>
            </div>
            '''
            
            cards_html += f'''<div class="glass-card asset-card {row['hover']}" style="position: relative; padding-right: 90px;"><div style="font-size: 13px; color: #A0A0A0; font-weight: bold; margin-bottom: 5px;">🔹{row['category']}</div><div style="font-size: 26px; font-weight: 900; color: #FFFFFF; margin-bottom: 5px; white-space: nowrap;">₩{int(row['amount']):,}</div><div class="{c_class}">{p_sign}{int(row['profit']):,} ({p_sign}{row['return_pct']}%)</div>{sparkline}</div>'''
        st.markdown(f'<div class="swipe-wrapper" style="position:relative;"><div class="swipe-container">{cards_html}</div><div class="swipe-glow-left hidden"></div><div class="swipe-glow-right hidden"></div></div>', unsafe_allow_html=True)

        import streamlit.components.v1 as components
        components.html('''
        <script>
        const doc = window.parent.document;
        const container = doc.querySelector('.swipe-container');
        
        if (!doc.getElementById('swipe-glow-style')) {
            const style = doc.createElement('style');
            style.id = 'swipe-glow-style';
            style.innerHTML = `
            .swipe-container::-webkit-scrollbar { display: none !important; }
            .swipe-container { -ms-overflow-style: none; scrollbar-width: none; }
            .swipe-glow-right, .swipe-glow-left {
                position: absolute;
                top: 50% !important;
                width: 16px !important;
                height: 16px !important;
                pointer-events: none;
                opacity: 1;
                transition: opacity 0.3s ease-in-out;
                background: none !important;
                border-radius: 0 !important;
                z-index: 50;
            }
            /* Right Chevron */
            .swipe-glow-right {
                right: 25px;
                border-top: 4px solid rgba(180,130,255,0.9);
                border-right: 4px solid rgba(180,130,255,0.9);
                border-left: none; border-bottom: none;
                animation: neon-chevron-right 1.2s infinite alternate ease-in-out;
            }
            /* Left Chevron */
            .swipe-glow-left {
                left: 25px;
                border-bottom: 4px solid rgba(180,130,255,0.9);
                border-left: 4px solid rgba(180,130,255,0.9);
                border-top: none; border-right: none;
                animation: neon-chevron-left 1.2s infinite alternate ease-in-out;
            }
            .swipe-glow-right.hidden, .swipe-glow-left.hidden {
                opacity: 0 !important;
            }
            @keyframes neon-chevron-right {
                from { opacity: 0.3; filter: drop-shadow(0 0 2px rgba(180,130,255,0.4)); transform: translateY(-50%) rotate(45deg) translateX(-3px) translateY(-3px); }
                to { opacity: 1; filter: drop-shadow(0 0 10px rgba(180,130,255,1)); transform: translateY(-50%) rotate(45deg) translateX(3px) translateY(3px); }
            }
            @keyframes neon-chevron-left {
                from { opacity: 0.3; filter: drop-shadow(0 0 2px rgba(180,130,255,0.4)); transform: translateY(-50%) rotate(45deg) translateX(3px) translateY(3px); }
                to { opacity: 1; filter: drop-shadow(0 0 10px rgba(180,130,255,1)); transform: translateY(-50%) rotate(45deg) translateX(-3px) translateY(-3px); }
            }
            `;
            doc.head.appendChild(style);
        }

        const overlayRight = doc.querySelector('.swipe-glow-right');
        const overlayLeft = doc.querySelector('.swipe-glow-left');
        const firstCard = container.querySelector('.asset-card');

        if (container && firstCard && overlayRight && overlayLeft) {
            const updateGlowBounds = () => {
                const top = firstCard.offsetTop;
                const height = firstCard.offsetHeight;
                overlayRight.style.top = top + 'px';
                overlayRight.style.height = height + 'px';
                overlayLeft.style.top = top + 'px';
                overlayLeft.style.height = height + 'px';
            };
            
            const checkScroll = () => {
                if (container.scrollLeft + container.clientWidth >= container.scrollWidth - 10) {
                    overlayRight.classList.add('hidden');
                } else {
                    overlayRight.classList.remove('hidden');
                }
                
                if (container.scrollLeft <= 10) {
                    overlayLeft.classList.add('hidden');
                } else {
                    overlayLeft.classList.remove('hidden');
                }
            };
            
            container.addEventListener('scroll', checkScroll);
            window.parent.addEventListener('resize', () => {
                updateGlowBounds();
                checkScroll();
            });
            setTimeout(() => { updateGlowBounds(); checkScroll(); }, 200);
            setTimeout(() => { updateGlowBounds(); checkScroll(); }, 1000); 
            
            // Keyboard Navigation Setup
            const cards = container.querySelectorAll('.asset-card');
            cards.forEach(card => {
                card.setAttribute('tabindex', '0');
                card.style.outline = 'none'; // Hide default focus outline for aesthetics
                card.addEventListener('click', () => card.focus());
            });
            container.setAttribute('tabindex', '0');
            container.style.outline = 'none';

            if (doc.swipeKeydownHandler) {
                doc.removeEventListener('keydown', doc.swipeKeydownHandler);
            }
            doc.swipeKeydownHandler = (e) => {
                if (container.contains(doc.activeElement) || doc.activeElement === container) {
                    if (e.key === 'ArrowRight') {
                        e.preventDefault();
                        container.scrollBy({left: 280, behavior: 'smooth'}); // card width ~280
                    } else if (e.key === 'ArrowLeft') {
                        e.preventDefault();
                        container.scrollBy({left: -280, behavior: 'smooth'});
                    }
                }
            };
            doc.addEventListener('keydown', doc.swipeKeydownHandler);
        }
        
        // Remove old buttons if they exist
        const oldLeft = doc.getElementById('custom-carousel-btn-left');
        const oldRight = doc.getElementById('custom-carousel-btn-right');
        if(oldLeft) oldLeft.parentElement.remove();
        </script>
        ''', height=0)


    
    with col_right:
        if not df_dash.empty and len(df_dash) >= summary_start_row + 8:
            df_summary_main = df_dash.iloc[summary_start_row+1:summary_start_row+5, 0:7].copy()
            cols_main = df_dash.iloc[summary_start_row, 0:7].tolist()
            cols_main = ["" if str(c).strip() == '0.0' else c for c in cols_main]
            df_summary_main.columns = cols_main
            df_summary_main.set_index(df_summary_main.columns[0], inplace=True)
            
            df_summary_sub = df_dash.iloc[summary_start_row+5:summary_start_row+9, 0:7].copy()
            cols_sub = df_dash.iloc[summary_start_row, 0:7].tolist()
            cols_sub = ["" if str(c).strip() == '0.0' else c for c in cols_sub]
            df_summary_sub.columns = cols_sub
            df_summary_sub.set_index(df_summary_sub.columns[0], inplace=True)
            df_summary_sub.index = [str(df_dash.iloc[summary_start_row+5, 0]), str(df_dash.iloc[summary_start_row+6, 0]), str(df_dash.iloc[summary_start_row+7, 0]), str(df_dash.iloc[summary_start_row+8, 0])]
            
            try:
                cats = df_summary_main.columns[1:].tolist()
                amounts = df_summary_main.iloc[0, 1:].apply(lambda x: float(str(x).replace(',', '')) if str(x).strip() != '' else 0).tolist()
                profits = df_summary_main.iloc[1, 1:].apply(lambda x: float(str(x).replace(',', '')) if str(x).strip() != '' else 0).tolist()
                
                df_asset_dynamic = pd.DataFrame({"category": cats, "amount": amounts, "profit": profits})
                import plotly.graph_objects as go
                # Render Waterfall directly
                

                # Render Sunburst directly
                corp_amts = df_summary_sub.iloc[0, 1:].apply(lambda x: float(str(x).replace(',', '')) if str(x).strip() != '' else 0).tolist()
                indi_amts = df_summary_sub.iloc[2, 1:].apply(lambda x: float(str(x).replace(',', '')) if str(x).strip() != '' else 0).tolist()
                labels = ["총자산"]
                parents = [""]
                values = [0]
                colors = [""]
                color_map = {'주식': '#1e3799', '금': '#f1c40f', '채권': '#00d8d6', '코인': '#FF9900', '현금성': '#6c5ce7', '개인': '#1A112A', '법인': '#2D1F44'}
                for cat in cats:
                    labels.append(cat)
                    parents.append("총자산")
                    values.append(0)
                    colors.append(color_map.get(cat, '#888888'))
                for i, cat in enumerate(cats):
                    if indi_amts[i] > 0:
                        labels.append(f"개인_{cat}")
                        parents.append(cat)
                        values.append(indi_amts[i])
                        colors.append(color_map['개인'])
                    if corp_amts[i] > 0:
                        labels.append(f"법인_{cat}")
                        parents.append(cat)
                        values.append(corp_amts[i])
                        colors.append(color_map['법인'])
                fig_sb = go.Figure(go.Sunburst(labels=labels, parents=parents, values=values, marker=dict(colors=colors, line=dict(color='rgba(0,0,0,0)')), textinfo="label+percent parent", insidetextorientation='radial'))
                fig_sb.update_layout(title=dict(text="자산 배분 현황", font=dict(color="#FF9900", size=16)), margin=dict(t=50, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=450)
                st.plotly_chart(fig_sb, use_container_width=True)
            except Exception as e:
                st.error(f"차트 렌더링 에러: {e}")
                
    with st.expander("📊 현황 요약 보기"):
        def apply_black_style(df, is_main=True):
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            for r_idx, row_name in enumerate(df.index):
                for c_idx, col_name in enumerate(df.columns):
                    val = df.iat[r_idx, c_idx]
                    bg_color = '#150d1e'
                    text_color = 'white'
                    font_weight = 'normal'
                    is_negative = isinstance(val, str) and str(val).strip().startswith('-')
                    is_positive_num = False
                    try:
                        num_val = float(str(val).replace(',', '').replace('%', '').strip())
                        if num_val > 0: is_positive_num = True
                    except: pass
                    if "수익률" in str(row_name):
                        if is_negative: text_color = '#FF1493'
                        elif is_positive_num: text_color = '#00FFFF'
                    elif "평가손익" in str(row_name): text_color = 'white'
                    else:
                        if is_negative: text_color = '#FF1493'
                    if is_main and r_idx == 0 and c_idx == 0:
                        text_color = '#FF9900'
                        font_weight = 'bold'
                    styles.iat[r_idx, c_idx] = f'background-color: {bg_color}; color: {text_color}; font-weight: {font_weight}; border: 1px solid #2D1F44; text-align: right;'
            return styles
        
        table_styles = [{'selector': 'th', 'props': [('background-color', '#1A112A'), ('color', '#a0a0a0'), ('border', '1px solid #2D1F44'), ('text-align', 'center'), ('font-weight', 'normal')]}, {'selector': 'th.row_heading', 'props': [('background-color', '#1A112A'), ('color', '#d0d0d0'), ('text-align', 'left')]}]
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div style='font-size: 14px; color: #a0a0a0; font-weight: bold; margin-bottom: 10px;'>▪ 현황 요약</div>", unsafe_allow_html=True)
            st.dataframe(df_summary_main.style.apply(apply_black_style, is_main=True, axis=None).pipe(format_styler).set_table_styles(table_styles), use_container_width=True)
        with c2:
            st.markdown("<div style='font-size: 14px; color: #a0a0a0; font-weight: bold; margin-bottom: 10px;'>▪ 주체별 구분 (법인/개인)</div>", unsafe_allow_html=True)
            st.dataframe(df_summary_sub.style.apply(apply_black_style, is_main=False, axis=None).pipe(format_styler).set_table_styles(table_styles), use_container_width=True)
elif menu == "매매 기록":
    urls_dict = {
        "DASHBOARD": URL_DASHBOARD,
        "ACCOUNT": URL_ACCOUNT,
        "RECORDS": URL_RECORDS,
        "DAILY": URL_PNL_DAILY,
        "MONTHLY": URL_PNL_MONTHLY
    }
    render_trade_records(urls_dict)




if __name__ == "__main__":
    pass  # In Streamlit, no main block is strictly necessary for inline scripts