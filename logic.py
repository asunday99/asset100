import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
import json
import os
import urllib.request
import requests

CONFIG_FILE = "config.json"

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
            
            if len(xlf_c) >= 2 and len(qqq_c) >= 2:
                xlf_today = xlf_c.iloc[-1]
                qqq_today = qqq_c.iloc[-1]
                xlf_yest = xlf_c.iloc[-2]
                qqq_yest = qqq_c.iloc[-2]
            
            if not pd.isna(xlf_today) and not pd.isna(qqq_today):
                today_ratio = xlf_today / qqq_today
                yest_ratio = xlf_yest / qqq_yest
                changes['XLF'] = today_ratio - yest_ratio
    except:
        pass
    return changes

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
    
    krx_dict = get_all_krx_tickers()
    if clean_name in krx_dict:
        return krx_dict[clean_name]
        
    for k, v in krx_dict.items():
        if k in clean_name or clean_name in k:
            return v
            
    try:
        import urllib.parse
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
            if str(col).strip() in ('날짜', 'date', 'Date', '날짜_str'):
                continue
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
    for r in range(min(20, len(df))):
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

        if not hist.empty and 'High' in hist and 'QQQ' in hist['High']:
            high = hist['High']['QQQ'].dropna()
            low = hist['Low']['QQQ'].dropna()
            close = hist['Close']['QQQ'].dropna()
            if len(close) > 28:
                up_move = high.diff()
                down_move = -low.diff()
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
    return data

def format_num(val):
    if pd.isna(val) or str(val).strip() in ['', 'nan', 'NaN', 'None']:
        return "0"
    try:
        v = float(str(val).replace(',', ''))
        if abs(v) >= 100000000:
            return f"{v/100000000:,.1f}억"
        elif abs(v) >= 10000:
            return f"{v/10000:,.0f}만"
        else:
            return f"{v:,.0f}"
    except:
        return str(val)

def format_kr_amount(val):
    if pd.isna(val): return "0원"
    try:
        v = float(str(val).replace(',', ''))
        return f"{v:,.0f}원"
    except:
        return str(val)

def safe_int_float(val):
    try:
        return float(str(val).replace(',', ''))
    except:
        return 0.0

def get_color_by_value(val):
    try:
        v = float(str(val).replace(',', ''))
        if v > 0: return "#FF4B4B"
        if v < 0: return "#4B9FFF"
        return "white"
    except:
        return "white"

@st.cache_data(ttl=300)
def load_records_data(url):
    return load_and_clean_data(url)

@st.cache_data(ttl=3600)
def get_cached_previous_close(ticker):
    if not ticker: return None
    try:
        hist = yf.download(ticker, period="5d", progress=False)
        if not hist.empty and len(hist) >= 2:
            return hist['Close'].iloc[-2].item()
    except Exception:
        pass
    return None

def _clean_withdrawals_memos(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    df_clean = df.copy()
    for col in df_clean.columns:
        c_str = str(col).replace(" ", "")
        if "출금" in c_str or "메모" in c_str:
            df_clean = df_clean.drop(columns=[col], errors="ignore")
    return df_clean

def _style_pnl_dataframe(df: pd.DataFrame):
    def color_pnl(val):
        if isinstance(val, (int, float)):
            if val > 0: return "color: #ff4757; font-weight: bold;"
            if val < 0: return "color: #1e90ff; font-weight: bold;"
        return ""
    
    styler = df.style
    numeric_cols = df.select_dtypes(include=["float", "int"]).columns
    styler = styler.format("{:,.0f}", subset=numeric_cols, na_rep="")
    
    pnl_cols = [c for c in df.columns if "손익" in str(c) or "수익" in str(c)]
    if pnl_cols:
        styler = styler.map(color_pnl, subset=pnl_cols)
        
    styler = styler.set_table_styles([
        {"selector": "table", "props": [("background-color", "#111111"), ("border-collapse", "collapse"), ("color", "white")]},
        {"selector": "th, td", "props": [("border", "1px solid #333333"), ("padding", "8px"), ("text-align", "right")]},
        {"selector": "th", "props": [("background-color", "#0A0A0C"), ("color", "#FF9900"), ("text-align", "center"), ("font-weight", "bold")]},
    ])
    return styler
