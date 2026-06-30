import streamlit as st
import pandas as pd
import yfinance as yf

MACRO_TITLE_MAP = {
    '[誘멸뎅10?꾧뎅梨꾧툑由?': '[誘멸뎅10?꾧뎅梨꾧툑由?',
    '誘멸뎅10?꾧뎅梨꾧툑由?: '[誘멸뎅10?꾧뎅梨꾧툑由?',
    '[?λ떒湲?湲덈━李?': '[?λ떒湲?湲덈━李?',
    '?λ떒湲?湲덈━李?: '[?λ떒湲?湲덈━李?',
    '[USD/KRW ?섏쑉]': '[USD/KRW ?섏쑉]',
    'USD/KRW ?섏쑉': '[USD/KRW ?섏쑉]',
    '[USD/JPY ?섏쑉]': '[USD/JPY ?섏쑉]',
    'USD/JPY ?섏쑉': '[USD/JPY ?섏쑉]',
    '[vix吏??': '[vix吏??',
    'vix吏??: '[vix吏??',
    '[?섏씠?쇰뱶 ?ㅽ봽?덈뱶]': '[?섏씠?쇰뱶 ?ㅽ봽?덈뱶]',
    '?섏씠?쇰뱶 ?ㅽ봽?덈뱶': '[?섏씠?쇰뱶 ?ㅽ봽?덈뱶]',
    '[XLF-QQQ愿대━??': '[XLF-QQQ愿대━??',
    'XLF-QQQ愿대━??: '[XLF-QQQ愿대━??',
    '[ADX 異붿꽭媛뺣룄]': '[ADX 異붿꽭媛뺣룄]',
    'ADX 異붿꽭媛뺣룄': '[ADX 異붿꽭媛뺣룄]',
    '[ADX(QQQ異붿꽭媛뺣룄)]': '[ADX 異붿꽭媛뺣룄]',
    '[?щ윭?몃뜳??': '[DXY]',
    '[DXY]': '[DXY]',
    'DXY': '[DXY]',
    '[?쇰낯10?꾧뎅梨꾧툑由?': '[?쇰낯10?꾧뎅梨꾧툑由?',
    '?쇰낯10?꾧뎅梨꾧툑由?: '[?쇰낯10?꾧뎅梨꾧툑由?',
    '[?쇰낯湲덈━]': '[?쇰낯10?꾧뎅梨꾧툑由?',
    '?쇰낯湲덈━': '[?쇰낯10?꾧뎅梨꾧툑由?'
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
            
            if len(usd_c) >= 2: changes['[USD/KRW ?섏쑉]'] = usd_c.iloc[-1] - usd_c.iloc[-2]
            if len(jpy_c) >= 2: changes['[USD/JPY ?섏쑉]'] = jpy_c.iloc[-1] - jpy_c.iloc[-2]
            if len(vix_c) >= 2: changes['[vix吏??'] = vix_c.iloc[-1] - vix_c.iloc[-2]
            if len(tnx_c) >= 2: changes['[誘멸뎅10?꾧뎅梨꾧툑由?'] = tnx_c.iloc[-1] - tnx_c.iloc[-2]
            
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

st.set_page_config(page_title="湲덉쑖 ?먯궛 ??쒕낫??, layout="wide", initial_sidebar_state="collapsed")

# === [蹂댁븞 PIN ?좉툑 ?붾㈃ 濡쒖쭅] ===
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('''
    <style>
    /* 諛곌꼍: ?꾩쟾??釉붾옓?먯꽌 ?꾩＜ 源딆? ?⑥깋 洹몃씪?곗씠??*/
    .stApp {
        background: radial-gradient(circle at center, #0a0a1a 0%, #000000 100%);
    }
    
    /* ?붾㈃ 以묒븰 而⑦뀒?대꼫 */
    .pin-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 15vh;
        color: white;
    }
    
    /* ?쇨킅 ?먮㈇ ?좊땲硫붿씠???뺤쓽 (?곕낫??& 二쇳솴 誘뱀뒪) */
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

    /* ??댄? ?띿뒪??(?곗깋 湲곕낯 + ?쇨킅 ?좊땲硫붿씠?? */
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

    /* ?낅젰李???醫곴쾶 以묒븰 ?뺣젹 */
    div[data-testid="stTextInput"] {
        width: 300px !important;
        margin: 0 auto !important;
    }
    
    /* ?띿뒪???명뭼 ?붿옄??*/
    div[data-baseweb="input"] {
        background-color: rgba(20, 20, 30, 0.8) !important;
        border: 1px solid rgba(184, 154, 255, 0.3) !important;
        border-radius: 20px !important;
        transition: all 0.3s ease;
    }
    
    /* ?띿뒪???명뭼 ?ъ빱????二쇳솴???ㅼ삩 ??*/
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
        <div class="pin-subtitle">4?먮━ 蹂댁븞 PIN???낅젰?섏꽭??/div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.write("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pin = st.text_input("PIN", type="password", label_visibility="collapsed", key="pin_input")
        if pin:
            app_pin = ""
            try:
                # secrets?먯꽌 PIN??媛?몄샂. ?놁쑝硫?"1234"
                app_pin = str(st.secrets.get("APP_PIN", "1234"))
            except:
                app_pin = "1234"
                
            if pin == app_pin:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("??鍮꾨?踰덊샇媛 ??몄뒿?덈떎.")
    st.stop()
# =================================


# ?ъ씠踰꾪럱??& Glassmorphism 湲濡쒕쾶 CSS 二쇱엯
st.markdown("""
<style>
    /* Glassmorphism 移대뱶 而⑦뀒?대꼫 */
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

    /* ?듭떖 寃곌낵媛??띿뒪??(?ㅼ삩 湲濡쒖슦 ?④낵) */
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

    /* ?쒕툕 ??댄? 諛??쇰꺼 */
    .sub-label {
        font-size: 1.2rem;
        color: #A0A0A0;
        text-align: center;
        margin-bottom: 5px;
    }

    /* Streamlit ?щ씪?대뜑 ?뚮쭏 而ㅼ뒪? (CSS override) */

    /* ???붿옄??而ㅼ뒪? */
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
    st.error("Google Sheets URL ?ㅼ젙???꾩슂?⑸땲?? `.streamlit/secrets.toml` ?뚯씪???뺤씤?댁＜?몄슂.")
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
        "?좏뵆": "AAPL", "?뚯뒳??: "TSLA", "?붾퉬?붿븘": "NVDA", 
        "留덉씠?щ줈?뚰봽??: "MSFT", "留덉냼": "MSFT", "?뚰뙆踰?: "GOOGL", "援ш?": "GOOGL",
        "?꾨쭏議?: "AMZN", "硫뷀?": "META", "?섏씠?ㅻ턿": "META", "?룻뵆由?뒪": "NFLX",
        "?붾??곗뼱": "PLTR", "?먯씠?좊뵒": "AMD", "?명뀛": "INTC",
        "?꾩뺨": "QCOM", "釉뚮줈?쒖뺨": "AVGO", "ASML": "ASML",
        "?쇰씪?대┫由?: "LLY", "?몃낫?몃뵒?ㅽ겕": "NVO",
        "?뚯뒳?쇰え?곗뒪": "TSLA", "?ㅽ?踰낆뒪": "SBUX", "肄붿뭅肄쒕씪": "KO",
        "鍮꾪듃肄붿씤": "BTC-USD", "?대뜑由ъ?": "ETH-USD",
        "?ㅽ럹?댁뒪X": "SPCX"
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
    if not url or url.startswith("?ш린??):
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
            if '0' == c_str.strip() or 'Unnamed: 0' in c_str or '李⑦듃' in c_str or '(??' in c_str:
                cols_to_drop.append(c)
            elif isinstance(c, tuple):
                if any(str(x).strip() == '0' or 'Unnamed: 0' in str(x) or '李⑦듃' in str(x) or '(??' in str(x) for x in c):
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
        st.error(f"?곗씠??濡쒕뱶 ?먮윭: {e}")
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
    st.title("?뮕 ?댁슜 留ㅻ돱??)
    st.markdown('''
    <div style="background-color: #1A112A; padding: 15px; border-radius: 10px; border: 1px solid #333; margin-bottom: 20px;">
        <h5 style="color: #FF9900; margin-top: 0;">燧뉛툘 ?몄뀡(Notion)????ν븯??諛⑸쾿</h5>
        <ol style="color: #d0d0d0; line-height: 1.6; font-size: 13px; padding-left: 15px;">
            <li>?꾨옒 <b>?ㅼ슫濡쒕뱶</b> 踰꾪듉?쇰줈 <code>.md</code> ?뚯씪??諛쏆뒿?덈떎.</li>
            <li>?몄뀡 鍮??섏씠吏??<b>?쒕옒洹????쒕∼</b> ?섎㈃ ?꾨즺!</li>
        </ol>
    </div>
    ''', unsafe_allow_html=True)
    
    manual_md = '''
# ?뱢 媛쒖씤 二쇱떇 諛??먯궛 愿由???쒕낫???댁슜 留ㅻ돱??
蹂???쒕낫?쒕뒗 援ш? ?ㅽ봽?덈뱶?쒗듃? ?곕룞?섏뿬 ?섏쓽 紐⑤뱺 ?먯궛 ?먮쫫怨??쒖옣 吏?쒕? ?뚯븙?섍퀬, 泥닿퀎?곸씤 留ㅻℓ 湲곕줉 諛?紐⑥쓽 ?ъ옄瑜?吏?먰븯???댁엯?덈떎.

---

## 0. ?쒖옉?섍린 ?꾩뿉: 援ш? ?쒗듃 ?곕룞 ?뵎
媛쒖씤 ?먯궛 ?곗씠?곌? ??λ맂 援ш? ?ㅽ봽?덈뱶?쒗듃瑜?媛??癒쇱? ?곌껐?댁빞 ?⑸땲??
1. ??醫뚯륫???ъ씠?쒕컮 硫붾돱 ?섎떒?먯꽌 `Google Sheets URL ?낅젰` 移몄쓣 李얠뒿?덈떎.
2. **<span style="color: #4ade80; font-weight: bold;">蹂몄씤??援ш? ?쒗듃 二쇱냼(URL)瑜?蹂듭궗?섏뿬 遺숈뿬?ｊ린</span>** ?⑸땲??
3. ?낅젰 利됱떆 紐⑤뱺 ?뺣낫媛 ??쒕낫?쒖뿉 ?ㅼ떆媛꾩쑝濡??곕룞?⑸땲??

---

## 1. ??쒕낫??(Dashboard) ?뱤
?꾩옱 ?먯궛 珥앺빀怨?紐⑺몴 ?ъ꽦瑜? 洹몃━怨??쒖옣 ?먮쫫???쒕늿??蹂대뒗 ?붾㈃?낅땲??

* **紐⑺몴 ?ㅼ젙**: 理쒖긽?⑥뿉??**<span style="color: #4ade80; font-weight: bold;">紐⑺몴 湲덉븸</span>**怨?**<span style="color: #4ade80; font-weight: bold;">紐⑺몴??/span>**???낅젰?섎㈃ ?ъ꽦瑜?%)怨?D-Day媛 ?먮룞 怨꾩궛?⑸땲??
* **?먯궛 ?붿빟**: ?먯궛 珥앹븸 諛??ъ옄 鍮꾩쨷???꾨꽋 李⑦듃濡??쒓났?⑸땲??
* **嫄곗떆 寃쎌젣 & 怨듯룷?먯슃吏??*: 肄붿뒪?? ?섏뒪?? ?섏쑉 ???듭떖 吏?쒖? ?쒖옣 ?щ━瑜??쒓났?⑸땲??

## 2. 利앷텒怨꾩쥖?꾪솴 (Account Status) ?뮳
援ш? ?쒗듃??湲곕줉??媛?怨꾩쥖蹂?蹂댁쑀 醫낅ぉ???ㅼ떆媛??됯?湲덉븸怨??섏씡瑜좎쓣 ?쒓났?⑸땲??

## 3. 留ㅻℓ 湲곕줉 (Trade Records) ?랃툘
* **留ㅻℓ 罹섎┛??*: ?대쾲 ???щ젰???쇰퀎 ?ㅽ쁽 ?먯씡???쒖떆?⑸땲?? (?섏씡? ?곸깋, ?먯떎? 泥?깋)
* **留ㅻℓ 湲곕줉**: ?곸꽭 留ㅻℓ ?댁뿭???쒕줈 ?뺤씤?⑸땲??
* **紐⑥쓽怨꾩궛**: 媛?곸쓽 **<span style="color: #4ade80; font-weight: bold;">留ㅼ닔 ?섎웾 諛??④?</span>**瑜??쒖뿉 吏곸젒 ?낅젰??蹂댁꽭?? ?덉긽 湲덉븸怨??섏씡瑜좎씠 利됱떆 ?먮룞 怨꾩궛?⑸땲??
* **?듭젅/?먯젅 怨꾩궛湲?*: ?쒖뿉 ?먰븯??**<span style="color: #4ade80; font-weight: bold;">紐⑺몴 ?섏씡瑜?%)怨??섎씫瑜?%)</span>**???낅젰?섎㈃ ?뺥솗??留ㅻ룄 ?④?瑜??곗텧??以띾땲??

## 4. ?먯씡 ?꾪솴 (PnL Status) ?뮥
* **?쇰퀎 ?먯씡**: 留ㅼ씪留ㅼ씪???섏씡/?먯떎 諛??낆텧湲??댁뿭???뚯븙?⑸땲??
* **?붾퀎 ?먯씡**: ???⑥쐞 ?꾩쟻 ?먯씡 ?쒖? 留됰???李⑦듃瑜??쒓났?⑸땲??
'''
    st.download_button(
        label="?뱿 留ㅻ돱???ㅼ슫濡쒕뱶 (.md)",
        data=manual_md,
        file_name="stock_dashboard_manual.md",
        mime="text/markdown",
        use_container_width=True
    )
    st.markdown("---")
    st.markdown(manual_md)
# ----------------------------

menu_options = ["??쒕낫??, "留ㅻℓ 湲곕줉"]

if "menu_selection" not in st.session_state:
    page_from_url = st.query_params.get("page", "??쒕낫??)
    st.session_state.menu_selection = page_from_url if page_from_url in menu_options else "??쒕낫??
if "record_tab" not in st.session_state:
    st.session_state.record_tab = "留ㅻℓ 罹섎┛??
if "pnl_tab" not in st.session_state:
    st.session_state.pnl_tab = "?쇰퀎 ?먯씡"

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
    """?レ옄/臾몄옄??媛믪쓣 泥쒕떒??肄ㅻ쭏 ?щ㎎?쇰줈 蹂??"""
    if val == "-":
        return "-"
    val_str = str(val).strip()
    prefix = ""
    for sym in ["+", "-", "??, "??]:
        if val_str.startswith(sym):
            prefix = sym
            break
    try:
        fval = float(
            val_str.replace(",", "").replace("%", "")
            .replace("+", "").replace("-", "")
            .replace("??, "").replace("??, "")
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
    """DataFrame Styler??泥쒕떒??肄ㅻ쭏 ?щ㎎ ?곸슜."""
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
    """湲덉븸????留??⑥쐞 ?쒓뎅???щ㎎?쇰줈 蹂??"""
    if abs(val) >= 100_000_000:
        return f"{val/100_000_000:,.1f}?? if val % 100_000_000 != 0 else f"{val/100_000_000:,.0f}??
    elif abs(val) >= 10_000:
        return f"{val/10_000:,.0f}留?
    return f"{val:,.0f}"

def safe_int_float(val, default=0) -> float:
    """?덉쟾???レ옄 蹂?? ?ㅽ뙣 ??default 諛섑솚."""
    try:
        return float(str(val).replace(",", "").strip())
    except (ValueError, TypeError):
        return default

def get_color_by_value(val) -> str:
    """?묒닔=?곸깋, ?뚯닔=泥?깋, 0=?곗깋 諛섑솚."""
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
    """留ㅻℓ 湲곕줉 ?곗씠??濡쒕뱶 (罹먯떆 ?곸슜)."""
    return load_and_clean_data(url)

def render_trade_records(urls: dict):
    """留ㅻℓ 湲곕줉 ??- 誘몃옒?먯뀑 ?ㅽ???UI"""
    import datetime
    
    # ?? ?몄뀡 ?곹깭 珥덇린????????????????????????????????????????????
    if "trade_view_mode" not in st.session_state:
        st.session_state.trade_view_mode = "?붾퀎"
    if "trade_nav_year" not in st.session_state:
        st.session_state.trade_nav_year = datetime.date.today().year
    if "trade_nav_month" not in st.session_state:
        st.session_state.trade_nav_month = datetime.date.today().month
    if "show_perf_chart" not in st.session_state:
        st.session_state.show_perf_chart = False
    if "record_tab" not in st.session_state:
        st.session_state.record_tab = "留ㅻℓ 罹섎┛??

    # ?? 理쒕? ???쒗븳 ???????????????????????????????????????????????
    st.markdown("""
    <style>
    /* 留ㅻℓ湲곕줉 ???붾㈃??쓣 860px濡??쒗븳 */
    @media screen and (min-width: 860px) {
        .block-container {
            max-width: 860px !important;
        }
    }
    </style>
    <div style="max-width: 860px; margin: 0 auto;">
    """, unsafe_allow_html=True)

        # ?? 留ㅻℓ 罹섎┛??/ 留ㅻℓ 湲곕줉 ?쒕툕???????????????????????????????
    # -- Toss Style Bar Chart --
    try:
        import pandas as pd
        import datetime
        date_col = df_monthly.columns[0]
        profit_col = next((c for c in df_monthly.columns if '?ㅽ쁽?먯씡' in str(c).replace(' ', '')), df_monthly.columns[2])
        
        # Extract 2026 data
        year_data = df_monthly[df_monthly[date_col].astype(str).str.contains(str(datetime.date.today().year), na=False)].copy()
        
        monthly_profits = {i: 0 for i in range(1, 13)}
        for r in range(len(year_data)):
            d_str = str(year_data.iloc[r][date_col])
            val_str = str(year_data.iloc[r][profit_col]).replace(',', '')
            try:
                m = int(d_str.split('-')[1].replace('??,'').strip())
                monthly_profits[m] = int(float(val_str))
            except: pass
            
        max_profit = max(max(monthly_profits.values()), 1)
        
        bars_html = ""
        for m in range(1, 13):
            p = monthly_profits[m]
            height_pct = max(min(int((p / max_profit) * 100), 100), 5) if p > 0 else 2
            color = "#FF6B00" if p > 0 else "#333"
            
            # Add text label for p (in 10,000s: 留뚯썝)
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
                    ?ы빐 ?ъ꽦???ㅽ쁽?섏씡?<br>
                    <span style='font-size:20px;'>{year_profit:,}???댁뿉??/span>
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
                    ?ы빐 ?ㅽ쁽?섏씡瑜좎? <span style='font-size:20px; color:#8A2BE2;'>{ytd_return}</span> ?댁뿉??br>
                    <span style='font-size:13px; color:#A0A0A0; font-weight:normal;'>??異붿꽭?쇰㈃ ?곕쭚源뚯? {expected_return} ?덉긽?쇱슂</span>
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
                <h4 style='color:#FF9900; margin-top:0; margin-bottom:20px; font-size:16px;'>?ъ꽦 紐⑺몴</h4>
                <div style='display:flex; justify-content:space-between; margin-bottom:12px;'>
                    <div style='color:#a0a0a0; font-size:13px;'>留ㅼ썡 ?ъ꽦???섏씡瑜?/div>
                    <div style='color:white; font-size:14px; font-weight:bold;'>{monthly_target_pct_str}</div>
                </div>
                <div style='display:flex; justify-content:space-between; margin-bottom:12px;'>
                    <div style='color:#a0a0a0; font-size:13px;'>留ㅼ씪 ?ъ꽦???섏씡瑜?/div>
                    <div style='color:white; font-size:14px; font-weight:bold;'>{daily_target_pct_str}</div>
                </div>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div style='color:#a0a0a0; font-size:13px;'>留ㅼ씪 ?ъ꽦???ㅽ쁽湲덉븸</div>
                    <div style='color:#FF9900; font-size:15px; font-weight:bold;'>{daily_target_amt_str}??/div>
                </div>
            </div>
            
            <!-- Right Box: Actual -->
            <div style='flex:1; background-color:#16102b; border:1px solid #2a1b42; border-radius:12px; padding:20px;'>
                <h4 style='color:#b89aff; margin-top:0; margin-bottom:20px; font-size:16px;'>?ㅽ쁽 ?섏씡</h4>
                <div style='display:flex; justify-content:space-between; margin-bottom:12px;'>
                    <div style='color:#a0a0a0; font-size:13px;'>?꾩썡 ?ㅽ쁽 ?섏씡瑜?/div>
                    <div style='color:white; font-size:14px; font-weight:bold;'>{prev_profit_pct_str}</div>
                </div>
                <div style='display:flex; justify-content:space-between; margin-bottom:12px;'>
                    <div style='color:#a0a0a0; font-size:13px;'>?꾩썡 ?ㅽ쁽 ?섏씡湲?/div>
                    <div style='color:white; font-size:14px; font-weight:bold;'>{prev_profit_amt_str}</div>
                </div>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div style='color:#a0a0a0; font-size:13px;'>?뱀썡 ?ㅽ쁽 ?섏씡瑜?/div>
                    <div style='background-color:#10b981; color:white; padding:4px 8px; border-radius:6px; font-size:14px; font-weight:bold;'>{curr_profit_pct_str}</div>
                </div>
            </div>
        </div>
        """
        import re; st.markdown(re.sub(r'\n\s+', ' ', summary_html), unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error rendering toss chart: {e}")

    st.markdown("---")
    with st.expander("??留ㅻℓ 罹섎┛??, expanded=True):
        df_rec = load_records_data(urls.get("RECORDS", ""))
        _render_trade_calendar(df_rec)

    # ?? ?듭젅/?먯젅 怨꾩궛湲?????????????????????????????????????????
    st.markdown("---")
    _render_profit_loss_calculator()

    st.markdown('</div>', unsafe_allow_html=True)
\

def _render_trade_calendar(df_rec: pd.DataFrame):
    """留ㅻℓ 罹섎┛???뚮뜑留?"""
    today = datetime.date.today()
    year, month = today.year, today.month
    st.subheader(f"?뱟 {year}??{month}??)

    kr_holidays = holidays.KR()
    daily_pnl_dict: dict = {}

    if not df_rec.empty:
        try:
            df_rec["怨꾩쥖"]    = df_rec["怨꾩쥖"].astype(str).str.strip()
            df_rec["?좎쭨_str"] = df_rec["?좎쭨"].astype(str).str.strip()
            is_mock  = (df_rec["怨꾩쥖"] == "紐⑥쓽怨꾩궛") | (df_rec["?좎쭨_str"] == "紐⑥쓽怨꾩궛")
            df_real  = df_rec[~is_mock].copy()

            if "?좎쭨" in df_real.columns and "李⑥씡?ㅽ쁽湲덉븸" in df_real.columns:
                df_real["date"] = pd.to_datetime(
                    df_real["?좎쭨_str"].str.replace(" ", ""), format="%y.%m.%d.", errors="coerce"
                ).dt.date
                df_real["李⑥씡?ㅽ쁽湲덉븸"] = pd.to_numeric(
                    df_real["李⑥씡?ㅽ쁽湲덉븸"].astype(str).str.replace(",", ""), errors="coerce"
                ).fillna(0)
                daily_pnl_dict = df_real.groupby("date")["李⑥씡?ㅽ쁽湲덉븸"].sum().to_dict()
        except Exception as e:
            logger.warning("罹섎┛???곗씠???뚯떛 ?ㅽ뙣: %s", e)
            st.warning(f"?좑툘 罹섎┛???곗씠???뚯떛 ?ㅽ뙣: {e}")

    monthly_total = sum(v for k, v in daily_pnl_dict.items() if k.year == year and k.month == month)
    color = get_color_by_value(monthly_total)
    st.markdown(
        f'<div style="text-align:right;margin-bottom:10px;">'
        f'<span style="color:#a0a0a0;font-size:15px;">?뱀썡 珥앹넀?? </span>'
        f'<span style="color:{color};font-size:22px;font-weight:bold;">{monthly_total:,.0f} ??/span></div>',
        unsafe_allow_html=True,
    )

    cal   = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdatescalendar(year, month)

    html_str = '<table style="width:100%;table-layout:fixed;border-collapse:collapse;border:1px solid #333;">'
    html_str += "<tr>"
    for day_name in ["??, "??, "??, "??, "紐?, "湲?, "??]:
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
                formatted_val = "?댁옣"
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
    """留ㅻℓ 湲곕줉 ??諛?紐⑥쓽怨꾩궛 ?뚮뜑留?"""
    if df_rec.empty:
        st.info("留ㅻℓ 湲곕줉 ?곗씠?곌? ?놁뒿?덈떎.")
        return

    df_rec = df_rec.drop(columns=[c for c in df_rec.columns if "湲고?" in str(c)], errors="ignore")
    df_rec["怨꾩쥖"] = df_rec["怨꾩쥖"].astype(str).str.strip()
    df_rec["?좎쭨"] = df_rec["?좎쭨"].astype(str).str.strip()
    is_mock = (df_rec["怨꾩쥖"] == "紐⑥쓽怨꾩궛") | (df_rec["?좎쭨"] == "紐⑥쓽怨꾩궛")
    df_real = df_rec[~is_mock]
    df_mock = df_rec[is_mock]

    numeric_cols = df_rec.select_dtypes(include=["float", "int"]).columns.tolist()

    def apply_style(df_to_style: pd.DataFrame):
        styler         = df_to_style.style
        num_cols_here  = [c for c in numeric_cols if c in df_to_style.columns]
        if "?섏씡瑜? in num_cols_here:
            styler = styler.format("{:,.2f}", subset=["?섏씡瑜?], na_rep="")
            others = [c for c in num_cols_here if c != "?섏씡瑜?]
            if others:
                styler = styler.format("{:,.0f}", subset=others, na_rep="")
        elif num_cols_here:
            styler = styler.format("{:,.0f}", subset=num_cols_here, na_rep="")

        if "李⑥씡?ㅽ쁽湲덉븸" in df_to_style.columns:
            def color_profit(val):
                if isinstance(val, (int, float)):
                    if val > 0: return "background-color: #990000;"
                    if val < 0: return "background-color: #1155cc;"
                return ""
            styler = styler.map(color_profit, subset=["李⑥씡?ㅽ쁽湲덉븸"])

        if "?좎쭨" in df_to_style.columns and len(df_to_style) > 0:
            try:
                dates = pd.to_datetime(
                    df_to_style["?좎쭨"].astype(str).str.replace(" ", ""), format="%y.%m.%d.", errors="coerce"
                )
                max_date_str = (
                    df_to_style.loc[dates.idxmax(), "?좎쭨"] if dates.notna().any()
                    else df_to_style["?좎쭨"].max()
                )

                def highlight_recent(row):
                    return ["background-color: #38761d;" if str(row.get("?좎쭨", "")) == str(max_date_str) else ""] * len(row)
                styler = styler.apply(highlight_recent, axis=1)
            except Exception as e:
                logger.warning("理쒖떊 ?좎쭨 ?섏씠?쇱씠???ㅽ뙣: %s", e)
        return styler

    st.subheader("?뱥 留ㅻℓ 湲곕줉")
    if not df_real.empty:
        st.dataframe(apply_style(df_real), use_container_width=True, hide_index=True)
    else:
        st.info("?ㅼ젣 留ㅻℓ 湲곕줉???놁뒿?덈떎.")

    st.markdown("---")
    st.subheader("?뮕 紐⑥쓽怨꾩궛")
    mock_cols = ["醫낅ぉ紐?, "留ㅼ닔_?섎웾", "留ㅼ닔_?④?", "留ㅼ닔_湲덉븸", "留ㅻ룄_?섎웾", "留ㅻ룄_?④?", "留ㅻ룄_湲덉븸", "留ㅻℓ鍮꾩슜", "李⑥씡?ㅽ쁽湲덉븸", "?섏씡瑜?]

    if "mock_data" not in st.session_state:
        st.session_state.mock_data = df_mock[[c for c in mock_cols if c in df_mock.columns]].copy()

    edited_mock = st.data_editor(
        apply_style(st.session_state.mock_data),
        num_rows="dynamic", hide_index=True, use_container_width=True,
        disabled=["留ㅼ닔_湲덉븸", "留ㅻ룄_湲덉븸", "李⑥씡?ㅽ쁽湲덉븸", "?섏씡瑜?],
        key="mock_data_editor",
    )

    changed = False
    for i, row in edited_mock.iterrows():
        try:
            b_qty = safe_int_float(row.get("留ㅼ닔_?섎웾", 0))
            old_b = safe_int_float(st.session_state.mock_data.at[i, "留ㅼ닔_?섎웾"]) if i in st.session_state.mock_data.index else 0
            s_qty = b_qty if b_qty != old_b else safe_int_float(row.get("留ㅻ룄_?섎웾", 0))
            if b_qty != old_b:
                edited_mock.at[i, "留ㅻ룄_?섎웾"] = s_qty
                changed = True

            b_prc = safe_int_float(row.get("留ㅼ닔_?④?", 0))
            s_prc = safe_int_float(row.get("留ㅻ룄_?④?", 0))
            cost  = safe_int_float(row.get("留ㅻℓ鍮꾩슜", 0))
            n_buy  = b_qty * b_prc
            n_sell = s_qty * s_prc
            n_prof = n_sell - n_buy - cost
            n_rate = (n_prof / n_buy * 100) if n_buy > 0 else 0.0

            if (abs(safe_int_float(row.get("留ㅼ닔_湲덉븸", 0)) - n_buy) > 0.01 or
                abs(safe_int_float(row.get("留ㅻ룄_湲덉븸", 0)) - n_sell) > 0.01 or
                abs(safe_int_float(row.get("李⑥씡?ㅽ쁽湲덉븸", 0)) - n_prof) > 0.01 or
                abs(safe_int_float(row.get("?섏씡瑜?, 0)) - n_rate) > 0.01):
                edited_mock.at[i, "留ㅼ닔_湲덉븸"]    = n_buy
                edited_mock.at[i, "留ㅻ룄_湲덉븸"]    = n_sell
                edited_mock.at[i, "李⑥씡?ㅽ쁽湲덉븸"] = n_prof
                edited_mock.at[i, "?섏씡瑜?]       = n_rate
                changed = True
        except Exception as e:
            logger.warning("紐⑥쓽怨꾩궛 ??%d 怨꾩궛 ?ㅽ뙣: %s", i, e)

    if edited_mock.isnull().values.any():
        edited_mock = edited_mock.fillna(0)
        if "醫낅ぉ紐? in edited_mock.columns:
            edited_mock["醫낅ぉ紐?] = edited_mock["醫낅ぉ紐?].replace(0, "")
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
    """?듭젅/?먯젅 怨꾩궛湲??뚮뜑留?"""
    st.subheader("?? ?듭젅/?먯젅 怨꾩궛湲?)
    col_input, col_up, col_down = st.columns([1, 1.5, 1.5])

    with col_input:
        stock_name  = st.text_input("醫낅ぉ紐?(?낅젰 ??Enter)", value="SK?섏씠?됱뒪")
        auto_ticker = get_ticker_from_name(stock_name)
        # ?뱀젙 醫낅ぉ ?대갚 泥섎━
        FALLBACK_TICKERS = {"SK?섏씠?됱뒪": "000660", "?쇱꽦?꾩옄": "005930"}
        if auto_ticker == stock_name and stock_name in FALLBACK_TICKERS:
            auto_ticker = FALLBACK_TICKERS[stock_name]

        ticker_symbol = st.text_input("?쇳썑 ?뚯씠?몄뒪 ?곗빱", value=auto_ticker)

        is_foreign = bool(ticker_symbol) and not (
            ticker_symbol.endswith(".KS") or ticker_symbol.endswith(".KQ") or
            (ticker_symbol.isdigit() and len(ticker_symbol) == 6)
        )

        prev_close = None
        if ticker_symbol:
            prev_close = get_cached_previous_close(ticker_symbol)
            if prev_close is None:
                st.warning(f"?좑툘 ?꾩씪 醫낃? 議고쉶 ?ㅽ뙣 ({ticker_symbol}). ?섎룞?쇰줈 ?낅젰?섍굅???곗빱瑜??뺤씤??二쇱꽭??")

        if prev_close is None:
            prev_close = 150.0 if is_foreign else 215_000.0

        if is_foreign:
            st.markdown(f"<div style='font-size:14px;font-weight:600;color:#FF9900;margin-top:25px;'>?꾩씪 醫낃?: ${prev_close:,.2f}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='font-size:14px;font-weight:600;color:#FF9900;margin-top:25px;'>?꾩씪 醫낃?: {prev_close:,.0f} ??/div>", unsafe_allow_html=True)

    # ?섏씡瑜??뚯씠釉?珥덇린??    
    up_rates_list = st.session_state.get('config', {}).get("up_rates", [4.0, 6.0, 8.0, 10.0, 12.0, 20.0])
    down_rates_list = st.session_state.get('config', {}).get("down_rates", [-3.0, -5.0, -7.0, -10.0, -15.0, -20.0])

    if "up_rates_df" not in st.session_state:
        st.session_state.up_rates_df = pd.DataFrame({
            "?섏씡瑜?%)": up_rates_list,
            "紐⑺몴 媛寃?: [0.0] * len(up_rates_list),
            "紐⑺몴 ?먯씡": [0.0] * len(up_rates_list)
        })
    if "down_rates_df" not in st.session_state:
        st.session_state.down_rates_df = pd.DataFrame({
            "?섎씫瑜?%)": down_rates_list,
            "?먯젅 媛寃?: [0.0] * len(down_rates_list),
            "?덉긽 ?먯씡": [0.0] * len(down_rates_list)
        })

    price_format = "{:,.2f}" if is_foreign else "{:,.0f}"
    up_prices   = prev_close * (1 + st.session_state.up_rates_df["?섏씡瑜?%)"] / 100.0)
    down_prices = prev_close * (1 + st.session_state.down_rates_df["?섎씫瑜?%)"] / 100.0)

    st.session_state.up_rates_df["紐⑺몴 媛寃?]  = up_prices.round(2) if is_foreign else up_prices.astype(int)
    st.session_state.down_rates_df["?먯젅 媛寃?] = down_prices.round(2) if is_foreign else down_prices.astype(int)

    with col_up:
        edited_up = st.data_editor(
            st.session_state.up_rates_df.style.format(formatter={"紐⑺몴 媛寃?: price_format}),
            use_container_width=True, hide_index=True, num_rows="dynamic",
            column_config={"?섏씡瑜?%)": st.column_config.NumberColumn(format="%.1f%%")},
            disabled=["紐⑺몴 媛寃?], key="up_rates_editor",
        )
    with col_down:
        edited_down = st.data_editor(
            st.session_state.down_rates_df.style.format(formatter={"?먯젅 媛寃?: price_format}),
            use_container_width=True, hide_index=True, num_rows="dynamic",
            column_config={"?섎씫瑜?%)": st.column_config.NumberColumn(format="%.1f%%")},
            disabled=["?먯젅 媛寃?], key="down_rates_editor",
        )

    # 蹂寃?媛먯? ?????(rerun 議곌굔 紐낇솗??
    changed_rates = False
    if not edited_up.equals(st.session_state.up_rates_df):
        st.session_state.up_rates_df = edited_up
        st.session_state.config["up_rates"] = edited_up["?섏씡瑜?%)"].tolist()
        changed_rates = True
    if not edited_down.equals(st.session_state.down_rates_df):
        st.session_state.down_rates_df = edited_down
        st.session_state.config["down_rates"] = edited_down["?섎씫瑜?%)"].tolist()
        changed_rates = True

    if changed_rates:
        save_config(st.session_state.config)
        st.rerun()  # 蹂寃??쒖뿉留?rerun (臾댄븳 猷⑦봽 諛⑹?)

# =============================================================================
# ?? ??4: ?먯씡 ?꾪솴 ??
# =============================================================================
def _clean_withdrawals_memos(df: pd.DataFrame) -> pd.DataFrame:
    """異쒓툑/硫붾え 而щ읆 ?뺤젣."""
    if df.empty:
        return df
    df = df.copy()  # ?먮낯 遺덈? (in-place ?섏젙 諛⑹?)
    first_col = df.columns[0]
    df = df[~df[first_col].astype(str).str.strip().isin(["0.0", "0"])]
    for col in df.columns:
        if "Unnamed" in str(col):
            df = df.rename(columns={col: "鍮꾧퀬"})
    if "鍮꾧퀬" in df.columns:
        df["鍮꾧퀬"] = df["鍮꾧퀬"].apply(lambda x: "" if str(x).strip() in {"0.0", "0", "nan", "NaN"} else x)
    for col in df.columns:
        if "異쒓툑" in str(col):
            df[col] = df[col].apply(lambda x: "" if x in {0, 0.0} else x)
    return df

def _style_pnl_dataframe(df: pd.DataFrame):
    """?먯씡 DataFrame ?ㅽ??쇰쭅."""
    first_col = df.columns[0]

    def style_logic(styler):
        def row_style(row):
            if str(row[first_col]).strip() == "珥앷퀎":
                return ["background-color: #2b2e35; font-weight: bold;"] * len(row)
            return [""] * len(row)
        styler = styler.apply(row_style, axis=1)

        def color_profit_loss(val):
            if isinstance(val, (int, float)):
                if val > 0: return "color: #ff4757;"
                if val < 0: return "color: #1e90ff;"
            return ""

        for col in df.columns:
            if "?먯씡" in str(col) or "?섏씡" in str(col):
                styler = styler.map(color_profit_loss, subset=[col])
            elif "異쒓툑" in str(col):
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
    """?먯씡 留됰? 李⑦듃 ?뚮뜑留?"""
    if df.empty:
        st.info("李⑦듃 ?곗씠?곌? ?놁뒿?덈떎.")
        return
    try:
        date_col   = df.columns[0]
        profit_col = next((c for c in df.columns if "?ㅽ쁽?먯씡" in str(c).replace(" ", "")), None)
        if not profit_col:
            profit_col = next((c for c in df.columns if "?먯씡" in str(c)), None)
        if not profit_col:
            st.warning("?먯씡 而щ읆??李얠쓣 ???놁뒿?덈떎.")
            return

        df_chart = df[df[date_col].astype(str).str.strip() != "珥앷퀎"].copy()
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
        logger.error("?먯씡 李⑦듃 ?뚮뜑留??ㅽ뙣: %s", e)
        st.error(f"??李⑦듃 ?뚮뜑留??ㅽ뙣: {e}")

def render_pnl(urls: dict):
    """?먯씡 ?꾪솴 ???뚮뜑留?"""
    pnl_tab = option_menu(
        None, ["?쇰퀎 ?먯씡", "?붾퀎 ?먯씡"],
        icons=['', '', ''],
        default_index=0 if st.session_state.pnl_tab == "?쇰퀎 ?먯씡" else 1,
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

    if pnl_tab == "?쇰퀎 ?먯씡":
        df_daily = load_and_clean_data(urls.get("DAILY", ""))
        if not df_daily.empty:
            df_daily = _clean_withdrawals_memos(df_daily)
            st.markdown("<br><h4 style='color:#FF9900;'>?뱤 ?쇰퀎 ?ㅽ쁽?먯씡 異붿씠</h4>", unsafe_allow_html=True)
            _render_pnl_bar_chart(df_daily, "?쇰퀎 ?ㅽ쁽?먯씡")
            with st.expander("?뱥 ?쇰퀎 ?먯씡 ?곸꽭 ??, expanded=False):
                st.dataframe(_style_pnl_dataframe(df_daily), use_container_width=True, hide_index=True)
        else:
            st.info("?쇰퀎 ?먯씡 ?곗씠?곕? 遺덈윭?ㅼ? 紐삵뻽?듬땲??")

    elif pnl_tab == "?붾퀎 ?먯씡":
        df_monthly = load_and_clean_data(urls.get("MONTHLY", ""))
        if not df_monthly.empty:
            df_monthly = _clean_withdrawals_memos(df_monthly)
            st.markdown("<br><h4 style='color:#FF9900;'>?뱤 ?붾퀎 ?ㅽ쁽?먯씡 異붿씠</h4>", unsafe_allow_html=True)
            _render_pnl_bar_chart(df_monthly, "?붾퀎 ?ㅽ쁽?먯씡")
            with st.expander("?뱥 ?붾퀎 ?먯씡 ?곸꽭 ??, expanded=False):
                st.dataframe(_style_pnl_dataframe(df_monthly), use_container_width=True, hide_index=True)
        else:
            st.info("?붾퀎 ?먯씡 ?곗씠?곕? 遺덈윭?ㅼ? 紐삵뻽?듬땲??")

# =============================================================================
# ?? ??5: ?쒕??덉씠????
# =============================================================================

if menu == "??쒕낫??:
    
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
    
    if not df_daily.empty:
        try:
            profit_col = next((c for c in df_daily.columns if '?ㅽ쁽?먯씡' in str(c).replace(' ', '')), df_daily.columns[2])
            val_str = str(df_daily.iloc[0][profit_col]).replace(',', '')
            today_profit = int(float(val_str))
        except:
            pass
            
    if not df_monthly.empty:
        try:
            profit_col = next((c for c in df_monthly.columns if '?ㅽ쁽?먯씡' in str(c).replace(' ', '')), df_monthly.columns[2])
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
        
    
    # ?숈쟻 ?뚯떛?쇰줈 ?꾪솴 ?붿빟 ?뚯씠釉?李얘린
    summary_start_row = 7
    if not df_dash.empty:
        for r in range(len(df_dash)):
            if '?꾪솴?붿빟' in str(df_dash.iloc[r, 0]).replace(' ', ''):
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

    # --- ?ㅼ꺑 2 UI ?쒖옉 ---
    

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
<div class="neon-text" style="font-size:42px;">??int(total_assets):,}</div>
<div style="font-size:16px; color:#A0A0A0; margin-top:5px; margin-bottom: 25px;">?뱀썡 ?ㅽ쁽?섏씡 <span style="color:{month_color};">{month_sign}{month_profit:,}??/span></div>
        
<div style="width:100%; background-color:rgba(255,255,255,0.05); border-radius:10px; height:8px; margin-top:20px; margin-bottom:10px; overflow:hidden;">
<div style="width:{ach}%; background:linear-gradient(90deg, #FF6B00, #FF9900); height:100%; border-radius:10px;"></div>
</div>
<div style="font-size:15px; color:#E0E0E0; font-weight:bold; display:flex; flex-wrap:nowrap; justify-content:space-between; align-items:center; letter-spacing:0.5px; gap: 4px;">
<span style="color:#FF9900; font-weight:900; font-size:14px; white-space:nowrap;">{ach:.2f}% ?ъ꽦</span>
<div style="display:flex; align-items:center; flex-wrap:nowrap; gap:6px;">
<span style="font-size:12px;">紐⑺몴 {formatted_gs_val}??/span>
<span style="font-size:11px; color:#FFFFFF; background-color:rgba(255,255,255,0.15); padding:2px 6px; border-radius:10px; white-space:nowrap;">D-{d_days_dynamic}</span>
</div>
</div>
    </div>''', unsafe_allow_html=True)
        
        with st.expander("?숋툘 紐⑺몴 ?ъ꽕??, expanded=False):
            st.components.v1.html('''<script>
const elements = parent.document.querySelectorAll('div[data-testid="stExpander"] details summary p');
elements.forEach(el => {
    if (el.innerText.includes("紐⑺몴 ?ъ꽕??)) {
        el.style.fontSize = "70%";
        el.style.opacity = "0.7";
    }
});
</script>''', height=0)
            sc1, sc2 = st.columns(2)
            with sc1:
                new_amt = st.number_input("紐⑺몴 湲덉븸 (??", value=int(st.session_state.gs_val * 100000000), step=100000000)
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
                    "?뱟 紐⑺몴???щ젰 (?좏깮)",
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

        # -- 留ㅽ겕濡?吏??expander --
        with st.expander("?뱤 留ㅽ겕濡?吏??, expanded=False):
            try:
                macro_changes = get_macro_changes()
                pairs = []
                
                # 媛뺢굔???곗씠?고뻾 異붿텧 (?ㅻ뜑 臾댁떆)
                for lc, vc in [(13, 14), (15, 16)]:
                    for row_i in range(min(15, len(df_dash))):
                        try:
                            raw_lbl = str(df_dash.iloc[row_i, lc]).replace('[','').replace(']','').strip()
                            val = str(df_dash.iloc[row_i, vc]).strip()
                            if raw_lbl and raw_lbl != 'nan' and 'Unnamed' not in raw_lbl and val and val != 'nan' and val != '0.0':
                                pairs.append((raw_lbl, val))
                        except: pass
                
                # ?쒖꽌 蹂댁옣???꾪빐 以묐났 ?쒓굅 諛?8媛쒕쭔 ?좏깮
                TARGET_ORDER = [
                    '[誘멸뎅10?꾧뎅梨꾧툑由?', '[?λ떒湲?湲덈━李?', '[USD/KRW ?섏쑉]', '[USD/JPY ?섏쑉]',
                    '[?쇰낯10?꾧뎅梨꾧툑由?', '[DXY]', '[XLF-QQQ愿대━??', '[ADX 異붿꽭媛뺣룄]',
                    '[?섏씠?쇰뱶 ?ㅽ봽?덈뱶]', '[vix吏??'
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
                        mapped_vals[t] = "濡쒕뱶 以?.."
                        
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
                
                # ?쒖꽌??留욎떠 3以꾨줈 ?섎닎
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
                st.error(f"留ㅽ겕濡?吏??濡쒕뵫 ?ㅽ뙣: {e}")


        # -- New Trend Graphs --

        # --- 二쇱떇 留ㅼ엯 ?먭툑 諛??섏씡瑜?留덉뒪??怨듭떇 怨꾩궛 ---
        stock_eval_amt = 0
        stock_eval_pnl = 0
        stock_principal = 0
        if not df_dash.empty:
            try:
                stock_eval_amt = float(str(df_dash.iloc[8, 2]).replace(',', ''))
                stock_eval_pnl = float(str(df_dash.iloc[9, 2]).replace(',', ''))
                stock_principal = stock_eval_amt - stock_eval_pnl
            except Exception as e:
                pass
                
        # 1. ?ы빐 ?ㅽ쁽 ?섏씡瑜?%)
        if stock_principal > 0:
            ytd_realized_pct = f"{(year_profit / stock_principal) * 100:,.2f}%"
        else:
            ytd_realized_pct = "?먭툑 ?뚯닔 ?꾨즺 ??"
            
        # 2. ?곕쭚 ?덉긽 ?섏씡瑜?%)
        cur_month = max(datetime.date.today().month, 1)
        if stock_principal > 0:
            expected_pct = f"{( ((year_profit / cur_month) * 12) / stock_principal) * 100:,.2f}%"
        else:
            expected_pct = "?먭툑 ?뚯닔 ?꾨즺 ??"
            
        # 3. ?ы빐 珥??섏씡瑜?%)
        if stock_principal > 0:
            ytd_total_pct_val = ((year_profit + stock_eval_pnl) / stock_principal) * 100
            ytd_total_pct = f"{ytd_total_pct_val:,.2f}%"
        else:
            ytd_total_pct_val = 0
            ytd_total_pct = "?먭툑 ?뚯닔 ?꾨즺 ??"

        # --- Trend Graphs Data Prep ---
        import plotly.graph_objects as go
        
        try:
            date_col = df_monthly.columns[0]
            total_profit_col = df_monthly.columns[4] # 珥앹넀??(?ㅽ쁽+?됯?)
            
            # ?ы빐 ?곗씠??異붿텧 ???쒓컙???뺣젹
            year_data = df_monthly[df_monthly[date_col].astype(str).str.contains(str(datetime.date.today().year), na=False)].copy()
            # Sort by date implicitly by reversing if it's descending
            # Usually recent is top. Let's sort by parsed month.
            
            trend_months = []
            trend_profits = []
            
            for r in range(len(year_data)):
                d_str = str(year_data.iloc[r][date_col])
                val_str = str(year_data.iloc[r][total_profit_col]).replace(',', '')
                try:
                    m = int(d_str.split('-')[1].replace('??,'').strip())
                    trend_months.append(m)
                    trend_profits.append(float(val_str))
                except: pass
                
            # Zip and sort by month
            sorted_data = sorted(zip(trend_months, trend_profits))
            trend_months = [f"{m}?? for m, p in sorted_data]
            trend_profits = [p for m, p in sorted_data]
            
            # ?꾩쟻 怨꾩궛
            cum_profits = []
            curr_sum = 0
            for p in trend_profits:
                curr_sum += p
                cum_profits.append(curr_sum)
                
            # ?섏씡瑜?怨꾩궛 (?꾩쟻 珥앹닔??/ 二쇱떇 留ㅼ엯 ?먭툑)
            if stock_principal > 0:
                trend_pcts = [(cp / stock_principal) * 100 for cp in cum_profits]
            else:
                trend_pcts = [0 for cp in cum_profits]
                
            # Chart 1: 珥앹닔??異붿씠
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(x=trend_months, y=cum_profits, mode='lines+markers',
                                      line=dict(color='#FF9900', width=3),
                                      marker=dict(size=8, color='#FF9900'),
                                      fill='tozeroy', fillcolor='rgba(255,153,0,0.1)',
                                      name='?꾩쟻 珥앹닔??))
            fig1.update_layout(title="?ы빐 ?ъ꽦??珥앹닔??異붿씠",
                               paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               font=dict(color='white'),
                               xaxis=dict(showgrid=False),
                               yaxis=dict(showgrid=True, gridcolor='#333'),
                               margin=dict(l=20, r=20, t=40, b=20))
                               
            # Chart 2: 珥??섏씡瑜?異붿씠
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=trend_months, y=trend_pcts, mode='lines+markers',
                                      line=dict(color='#8A2BE2', width=3),
                                      marker=dict(size=8, color='#8A2BE2'),
                                      fill='tozeroy', fillcolor='rgba(138,43,226,0.1)',
                                      name='珥??섏씡瑜?%)'))
            fig2.update_layout(title="?ы빐 珥??섏씡瑜?%) 異붿씠",
                               paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               font=dict(color='white'),
                               xaxis=dict(showgrid=False),
                               yaxis=dict(showgrid=True, gridcolor='#333'),
                               margin=dict(l=20, r=20, t=40, b=20))
                               
            st.markdown(f'''
            <div style="background-color:#16102b; padding:15px; border-radius:10px; margin-bottom:20px;">
                <div style="font-size:14px; color:#a0a0a0; margin-bottom:5px;">?ы빐 珥??섏씡瑜?(留덉뒪??</div>
                <div style="font-size:24px; color:#b89aff; font-weight:bold;">{ytd_total_pct}</div>
                <div style="font-size:12px; color:#888; margin-top:5px;">(?ы빐 ?꾩쟻 ?ㅽ쁽?먯씡 + ?됯??먯씡) 湲곗?</div>
            </div>
            ''', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(fig1, use_container_width=True)
            with c2:
                st.plotly_chart(fig2, use_container_width=True)
                
        except Exception as e:
            st.error(f"異붿씠 洹몃옒???뚮뜑留??먮윭: {e}")



                
    
        
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
        elif val_str.startswith('??): prefix = "??
        elif val_str.startswith('??): prefix = "??
        
        try:
            fval = float(val_str.replace(',', '').replace('%', '').replace('+', '').replace('-', '').replace('??, '').replace('??, ''))
            
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
        if '-' in val_str or '?? in val_str: return '#1e90ff'
        if '+' in val_str or '?? in val_str: return '#ff4757'
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
        # 援ш? ?쒗듃 ??쒕낫????뿉???먯궛 移대뱶 ?곗씠???숈쟻 ?뚯떛
        # 援ъ“: summary_start_row 湲곗? ?ㅻ뜑??row+0, ?됯?湲덉븸=row+1, ?됯??먯씡=row+2, ?섏씡瑜?row+3
        # 而щ읆: col0=??ぉ紐? col1=珥앺빀怨? col2=二쇱떇, col3=湲? col4=梨꾧텒, col5=肄붿씤, col6=?꾧툑??        _cat_meta = [
            ("二쇱떇",  2, "hover-stock", "#1e90ff"),
            ("湲?,    3, "hover-gold",  "#f1c40f"),
            ("梨꾧텒",  4, "hover-bond",  "#00d8d6"),
            ("肄붿씤",  5, "hover-coin",  "#FF6B00"),
            ("?꾧툑??,6, "hover-cash",  "#6c5ce7"),
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
            # fallback: ?섎뱶肄붾뵫媛?            _asset_rows = [
                {"category": "二쇱떇",  "amount": 1974918892, "profit": 255389985,  "return_pct": 14.85,  "hover": "hover-stock", "color": "#1e90ff"},
                {"category": "湲?,    "amount": 142910490,  "profit": -17897045,  "return_pct": -11.13, "hover": "hover-gold",  "color": "#f1c40f"},
                {"category": "梨꾧텒",  "amount": 17516025,   "profit": -260227,    "return_pct": -1.46,  "hover": "hover-bond",  "color": "#00d8d6"},
                {"category": "肄붿씤",  "amount": 298825354,  "profit": -71356901,  "return_pct": -19.28, "hover": "hover-coin",  "color": "#FF6B00"},
                {"category": "?꾧툑??,"amount": 396232726,  "profit": 0,          "return_pct": 0.0,    "hover": "hover-cash",  "color": "#6c5ce7"},
            ]
        df_asset = pd.DataFrame([
            {"category": "二쇱떇", "amount": _asset_rows[0]["amount"], "profit": _asset_rows[0]["profit"], "return_pct": _asset_rows[0]["return_pct"], "hover": "hover-stock", "color": "#1e90ff"},
            {"category": "湲?, "amount": _asset_rows[1]["amount"], "profit": _asset_rows[1]["profit"], "return_pct": _asset_rows[1]["return_pct"], "hover": "hover-gold", "color": "#f1c40f"},
            {"category": "梨꾧텒", "amount": _asset_rows[2]["amount"], "profit": _asset_rows[2]["profit"], "return_pct": _asset_rows[2]["return_pct"], "hover": "hover-bond", "color": "#00d8d6"},
            {"category": "肄붿씤", "amount": _asset_rows[3]["amount"], "profit": _asset_rows[3]["profit"], "return_pct": _asset_rows[3]["return_pct"], "hover": "hover-coin", "color": "#FF6B00"},
            {"category": "?꾧툑??, "amount": _asset_rows[4]["amount"], "profit": _asset_rows[4]["profit"], "return_pct": _asset_rows[4]["return_pct"], "hover": "hover-cash", "color": "#6c5ce7"},
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
            
            cards_html += f'''<div class="glass-card asset-card {row['hover']}" style="position: relative; padding-right: 90px;"><div style="font-size: 13px; color: #A0A0A0; font-weight: bold; margin-bottom: 5px;">?뵻{row['category']}</div><div style="font-size: 26px; font-weight: 900; color: #FFFFFF; margin-bottom: 5px; white-space: nowrap;">??int(row['amount']):,}</div><div class="{c_class}">{p_sign}{int(row['profit']):,} ({p_sign}{row['return_pct']}%)</div>{sparkline}</div>'''
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
                labels = ["珥앹옄??]
                parents = [""]
                values = [0]
                colors = [""]
                color_map = {'二쇱떇': '#1e3799', '湲?: '#f1c40f', '梨꾧텒': '#00d8d6', '肄붿씤': '#FF9900', '?꾧툑??: '#6c5ce7', '媛쒖씤': '#1A112A', '踰뺤씤': '#2D1F44'}
                for cat in cats:
                    labels.append(cat)
                    parents.append("珥앹옄??)
                    values.append(0)
                    colors.append(color_map.get(cat, '#888888'))
                for i, cat in enumerate(cats):
                    if indi_amts[i] > 0:
                        labels.append(f"媛쒖씤_{cat}")
                        parents.append(cat)
                        values.append(indi_amts[i])
                        colors.append(color_map['媛쒖씤'])
                    if corp_amts[i] > 0:
                        labels.append(f"踰뺤씤_{cat}")
                        parents.append(cat)
                        values.append(corp_amts[i])
                        colors.append(color_map['踰뺤씤'])
                fig_sb = go.Figure(go.Sunburst(labels=labels, parents=parents, values=values, marker=dict(colors=colors, line=dict(color='rgba(0,0,0,0)')), textinfo="label+percent parent", insidetextorientation='radial'))
                fig_sb.update_layout(title=dict(text="?먯궛 諛곕텇 ?꾪솴", font=dict(color="#FF9900", size=16)), margin=dict(t=50, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=450)
                st.plotly_chart(fig_sb, use_container_width=True)
            except Exception as e:
                st.error(f"李⑦듃 ?뚮뜑留??먮윭: {e}")
                
    with st.expander("?뱤 ?꾪솴 ?붿빟 蹂닿린"):
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
                    if "?섏씡瑜? in str(row_name):
                        if is_negative: text_color = '#FF1493'
                        elif is_positive_num: text_color = '#00FFFF'
                    elif "?됯??먯씡" in str(row_name): text_color = 'white'
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
            st.markdown("<div style='font-size: 14px; color: #a0a0a0; font-weight: bold; margin-bottom: 10px;'>???꾪솴 ?붿빟</div>", unsafe_allow_html=True)
            st.dataframe(df_summary_main.style.apply(apply_black_style, is_main=True, axis=None).pipe(format_styler).set_table_styles(table_styles), use_container_width=True)
        with c2:
            st.markdown("<div style='font-size: 14px; color: #a0a0a0; font-weight: bold; margin-bottom: 10px;'>??二쇱껜蹂?援щ텇 (踰뺤씤/媛쒖씤)</div>", unsafe_allow_html=True)
            st.dataframe(df_summary_sub.style.apply(apply_black_style, is_main=False, axis=None).pipe(format_styler).set_table_styles(table_styles), use_container_width=True)
elif menu == "留ㅻℓ 湲곕줉":
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
