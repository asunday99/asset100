import streamlit as st
import pandas as pd
import yfinance as yf

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from logic import *
import yfinance as yf
import numpy as np
import datetime
import calendar
import holidays
import urllib.request
import io
import requests
import json
from streamlit_option_menu import option_menu
import plotly.express as px
import logging
logger = __import__('logging').getLogger(__name__)

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
        background: #000000;
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
    @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@700&display=swap');

    /* Force pure black background */
    .stApp, [data-testid="stAppViewContainer"] {
        background: #000000 !important;
        background-color: #000000 !important;
    }
    
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

    @keyframes neonPulseBlueWhite {
        0%, 100% {
            text-shadow: 0 0 10px rgba(138, 180, 248, 0.8), 0 0 20px rgba(138, 180, 248, 0.6), 0 0 30px rgba(138, 180, 248, 0.4);
            color: #E6F0FF;
            opacity: 1;
        }
        50% {
            text-shadow: 0 0 5px rgba(138, 180, 248, 0.5), 0 0 10px rgba(138, 180, 248, 0.3);
            color: #C0D8FF;
            opacity: 0.85;
        }
    }

    @keyframes progressBarPulse {
        0%, 100% { box-shadow: 0 0 10px rgba(255, 218, 185, 0.8), 0 0 20px rgba(255, 218, 185, 0.5); }
        50% { box-shadow: 0 0 5px rgba(255, 218, 185, 0.4), 0 0 10px rgba(255, 218, 185, 0.2); }
    }
    
    .progress-fill-peach {
        background: linear-gradient(90deg, #A07855, #FFBCA5, #FFF0E6);
        height: 100%;
        border-radius: 8px;
        position: absolute;
        top: 0;
        left: 0;
        animation: progressBarPulse 2s infinite ease-in-out;
    }

    .progress-track-blue {
        width: 100%;
        border-radius: 8px;
        height: 8px;
        margin-top: 15px;
        margin-bottom: 12px;
        position: relative;
        background-color: rgba(100, 181, 246, 0.45);
        box-shadow: inset 0 0 10px rgba(100, 181, 246, 0.8), 0 0 5px rgba(100, 181, 246, 0.4);
    }

    .glass-card-premium-blue {
        position: relative;
        background: 
            radial-gradient(ellipse 120px 8px at 50% 0%, rgba(240, 248, 255, 1.0) 0%, rgba(220, 240, 255, 0.6) 50%, transparent 100%),
            radial-gradient(ellipse 120px 8px at 0% 0%, rgba(240, 248, 255, 1.0) 0%, rgba(220, 240, 255, 0.6) 50%, transparent 100%),
            radial-gradient(ellipse 120px 8px at 100% 0%, rgba(240, 248, 255, 1.0) 0%, rgba(220, 240, 255, 0.6) 50%, transparent 100%),
            linear-gradient(180deg, rgba(10, 20, 40, 0.05) 0%, rgba(5, 10, 20, 0.3) 100%);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border: 1px solid rgba(138, 180, 248, 0.8);
        border-top: 2px solid rgba(255, 255, 255, 0.9);
        border-radius: 12px;
        box-shadow: 
            inset 0 0 60px rgba(138, 180, 248, 0.7), 
            inset 0 0 15px rgba(255, 255, 255, 0.4), 
            0 10px 40px rgba(0,0,0,0.9);
        transition: all 0.3s ease;
    }
    
    .glass-card-premium-blue::before {
        content: '';
        position: absolute;
        top: 6px;
        left: 6px;
        right: 6px;
        bottom: 6px;
        border: 1px solid rgba(138, 180, 248, 0.4);
        border-radius: 8px;
        pointer-events: none;
    }

    .neon-pulse-blue {
        font-family: 'Oswald', sans-serif;
        font-size: 46px;
        font-weight: 800;
        text-align: center;
        margin: 15px 0 25px 0;
        letter-spacing: 3px;
        animation: neonPulseBlueWhite 3.0s infinite ease-in-out;
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

# 로직 함수는 logic.py에서 import 됨
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
            background-color: #000000;
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
            background-color: #000000;
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
        "container": {
            "padding": "0!important", 
            "background-color": "transparent", 
            "border": "none", 
            "margin-bottom": "25px", 
            "max-width": "250px", 
            "margin-left": "0"
        },
        "icon": {"display": "none"}, 
        "nav-link": {
            "font-size": "16px", 
            "font-weight": "500", 
            "text-align": "center", 
            "margin":"0px", 
            "padding": "8px 0px", 
            "--hover-color": "transparent", 
            "color": "#7a828e", 
            "border-radius": "0px"
        },
        "nav-link-selected": {
            "background-color": "transparent", 
            "color": "#e5e7eb", 
            "font-weight": "bold", 
            "border-bottom": "2px solid #8ab4f8",
            "box-shadow": "0px 10px 15px -10px rgba(138, 180, 248, 0.5)"
        },
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

# 포맷팅 및 유틸 함수들은 logic.py에서 import 됨

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
    /* 매매기록 탭 반응형 너비 */
    .block-container {
        max-width: min(1200px, 90vw) !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    </style>
    <div style="width: 100%;">
    """, unsafe_allow_html=True)

    # ── 이번 달 수익 계산 (매매기록 시트에서 직접 집계, 날짜 정확 연동) ────────────────
    import datetime as _dt
    _month_profit = 0
    _today = _dt.date.today()
    try:
        _df_rec_hdr = load_records_data(urls.get("RECORDS", ""))
        if not _df_rec_hdr.empty and "날짜" in _df_rec_hdr.columns and "차익실현금액" in _df_rec_hdr.columns:
            _df_rec_hdr["계좌"] = _df_rec_hdr["계좌"].astype(str).str.strip()
            _df_rec_hdr["날짜"] = _df_rec_hdr["날짜"].astype(str).str.strip()
            # 모의계산 제외
            _hdr_real = _df_rec_hdr[
                (_df_rec_hdr["계좌"] != "모의계산") & (_df_rec_hdr["날짜"] != "모의계산")
            ].copy()
            _hdr_real["_hdr_date"] = pd.to_datetime(
                _hdr_real["날짜"].str.replace(" ", ""), format="%y.%m.%d.", errors="coerce"
            ).dt.date
            _hdr_real["차익실현금액"] = pd.to_numeric(
                _hdr_real["차익실현금액"].astype(str).str.replace(",", ""), errors="coerce"
            ).fillna(0)
            # 오늘 날짜와 일치하는 행만 합산 (연/월 정확 매칭)
            _this_month_hdr = _hdr_real[
                _hdr_real["_hdr_date"].apply(
                    lambda d: d is not None and not pd.isna(d)
                    and d.year == _today.year and d.month == _today.month
                )
            ]
            _month_profit = int(_this_month_hdr["차익실현금액"].sum())
    except Exception:
        _month_profit = 0

    if _month_profit > 0:
        _profit_text = f"+{_month_profit:,}원"
        _profit_color = "#FF4B4B"
        _msg = "벌고 있어요! 🚀"
        _expander_title = f"📅 이번 달 팔아서 +{_month_profit:,}원 벌고 있어요!"
    elif _month_profit < 0:
        _profit_text = f"{_month_profit:,}원"
        _profit_color = "#4B9FFF"
        _msg = "빠졌어요 💧"
        _expander_title = f"📅 이번 달 팔았는데 {_month_profit:,}원 빠졌어요"
    else:
        _profit_text = "0원"
        _profit_color = "#A0A0A0"
        _msg = "아직 0원이에요"
        _expander_title = f"📅 이번 달 아직 매도 수익 0원이에요"

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
  <div style='color:#A0A0B0; font-size:14px; letter-spacing:2px; margin-bottom:10px;'>이번 달 팔아서 번 돈</div>
  <div style='color:{_profit_color}; font-size:44px; font-weight:900; letter-spacing:-1px; margin-bottom:8px;'>{_profit_text}</div>
  <div style='color:#d0d0d0; font-size:18px; font-weight:500;'>{_msg}</div>
</div>
""", unsafe_allow_html=True)

    # ── 매매 캘린더 ─────────────────────────────────────────────────
    with st.expander(_expander_title, expanded=False):
        df_rec = load_records_data(urls.get("RECORDS", ""))
        _render_trade_calendar(df_rec)

    # ── 연간 실현수익 & 수익률 버블차트 (좌우 병렬) ─────────────────────────────────────────
    try:
        import datetime as _dt2
        import math as _math

        # ── 1) 일별 시트에서 월별 실현손익 집계 ──
        _df_daily_chart = load_and_clean_data(urls.get("DAILY", ""))
        _year_profit_c = 0
        _monthly_profits_c = {i: 0 for i in range(1, 13)}
        if not _df_daily_chart.empty:
            _dc2 = _df_daily_chart.columns[0]
            _pc2 = next((c for c in _df_daily_chart.columns if "실현손익" in str(c).replace(" ", "")), None)
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

        # ── 2) 매매기록 시트에서 월별 수익률 & 건수 집계 ──
        _df_rec_chart = load_records_data(urls.get("RECORDS", ""))
        _monthly_rates_c2 = {i: [] for i in range(1, 13)}
        _monthly_counts_c2 = {i: 0 for i in range(1, 13)}
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
                    _monthly_counts_c2[_rm] += 1

        # 월별 평균 수익률
        _monthly_avg_rates2 = {}
        for _mi in range(1, 13):
            if _monthly_rates_c2[_mi]:
                _monthly_avg_rates2[_mi] = sum(_monthly_rates_c2[_mi]) / len(_monthly_rates_c2[_mi])
            else:
                _monthly_avg_rates2[_mi] = 0.0

        # YTD 전체 평균
        _all_rates2 = [r for rates in _monthly_rates_c2.values() for r in rates]
        _ytd_val = sum(_all_rates2) / len(_all_rates2) if _all_rates2 else 0.0
        _ytd = f"{_ytd_val:.2f}%"

        # ── 3) 버블차트 SVG 생성 함수 ──
        def _make_bubble_svg(data_dict, count_dict, color_pos, color_neg, y_label, fmt_val):
            """data_dict: {month: value}, count_dict: {month: count}
            color_pos/neg: 양수/음수 버블 색상
            y_label: Y축 단위 표시
            fmt_val: value 포맷 함수
            반환: SVG 문자열"""
            W, H = 460, 200
            PAD_L, PAD_R, PAD_T, PAD_B = 48, 16, 16, 32
            plot_w = W - PAD_L - PAD_R
            plot_h = H - PAD_T - PAD_B

            months_with_data = [m for m in range(1, 13) if data_dict.get(m, 0) != 0]
            if not months_with_data:
                return f'<svg width="{W}" height="{H}"><text x="{W//2}" y="{H//2}" fill="#666" text-anchor="middle" font-size="13">데이터 없음</text></svg>'

            all_vals = [abs(data_dict.get(m, 0)) for m in range(1, 13) if data_dict.get(m, 0) != 0]
            max_val = max(all_vals) if all_vals else 1
            max_count = max((count_dict.get(m, 0) for m in range(1, 13)), default=1)
            max_count = max(max_count, 1)

            # 최소/최대 버블 반경
            R_MIN, R_MAX = 8, 32

            # X 위치: 1~12월 균등 분포
            def x_pos(m):
                return PAD_L + int((m - 1) / 11.0 * plot_w) if len(months_with_data) > 1 else PAD_L + plot_w // 2

            # Y 위치: 값에 비례 (양수=위, 음수=아래)
            y_vals = [data_dict.get(m, 0) for m in range(1, 13)]
            y_min = min(y_vals + [0])
            y_max = max(y_vals + [0])
            y_range = max(y_max - y_min, 1)

            def y_pos(v):
                return PAD_T + int((1 - (v - y_min) / y_range) * plot_h)

            svg = f'<svg width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">'
            # 배경
            svg += f'<rect width="{W}" height="{H}" fill="#111" rx="10"/>'
            # 0선
            y0 = y_pos(0)
            svg += f'<line x1="{PAD_L}" y1="{y0}" x2="{W-PAD_R}" y2="{y0}" stroke="#444" stroke-width="1" stroke-dasharray="4,3"/>'
            # 버블 & 라벨
            for m in range(1, 13):
                v = data_dict.get(m, 0)
                cnt = count_dict.get(m, 0)
                if v == 0 and cnt == 0:
                    # 월 라벨만
                    svg += f'<text x="{x_pos(m)}" y="{H-PAD_B+14}" fill="#555" text-anchor="middle" font-size="10">{m}</text>'
                    continue
                cx = x_pos(m)
                cy = y_pos(v)
                r = R_MIN + int((cnt / max_count) * (R_MAX - R_MIN))
                clr = color_pos if v >= 0 else color_neg
                # 버블 (반투명)
                svg += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{clr}" fill-opacity="0.75" stroke="{clr}" stroke-width="1.5"/>'
                # 값 라벨 (버블 위)
                lbl = fmt_val(v)
                svg += f'<text x="{cx}" y="{cy - r - 4}" fill="{clr}" text-anchor="middle" font-size="9" font-weight="bold">{lbl}</text>'
                # 건수 라벨 (버블 안)
                if cnt > 0:
                    svg += f'<text x="{cx}" y="{cy + 4}" fill="white" text-anchor="middle" font-size="9" font-weight="bold">{cnt}건</text>'
                # 월 라벨
                svg += f'<text x="{cx}" y="{H-PAD_B+14}" fill="#aaa" text-anchor="middle" font-size="10">{m}월</text>'
            # Y축 단위
            svg += f'<text x="{PAD_L-4}" y="{PAD_T+8}" fill="#666" text-anchor="end" font-size="9">{y_label}</text>'
            svg += '</svg>'
            return svg

        # ── 4) 차트1 버블 SVG (실현손익, 건수=월별 매도건수) ──
        _svg1 = _make_bubble_svg(
            _monthly_profits_c,
            _monthly_counts_c2,
            "#FF6B00", "#4B9FFF",
            "만원",
            lambda v: f"{int(v/10000):,}만" if abs(v) >= 10000 else f"{int(v):,}"
        )

        # ── 5) 차트2 버블 SVG (수익률, 버블크기=실현금액) ──
        # 버블크기용 count_dict를 실현금액 기준으로 대체
        _profit_as_count = {m: max(int(abs(_monthly_profits_c.get(m, 0)) / 1000000), 1)
                            if _monthly_avg_rates2.get(m, 0) != 0 else 0
                            for m in range(1, 13)}
        _svg2 = _make_bubble_svg(
            _monthly_avg_rates2,
            _profit_as_count,
            "#8A2BE2", "#4B9FFF",
            "%",
            lambda v: f"{v:.1f}%"
        )

        # ── 6) 좌우 병렬 HTML 렌더링 ──
        _chart_html = f"""
<div style='display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap;'>
  <div style='flex:1;min-width:300px;background:#111;border-radius:12px;padding:18px 16px 12px 16px;'>
    <div style='color:#FF6B00;font-size:13px;font-weight:bold;margin-bottom:4px;'>&#128200; 올해 팔아서 실제로 번 돈은</div>
    <div style='color:white;font-size:22px;font-weight:900;margin-bottom:12px;'>{_year_profit_c:,}원 이에요</div>
    {_svg1}
    <div style='color:#666;font-size:10px;margin-top:6px;text-align:right;'>버블 크기 = 매도 건수</div>
  </div>
  <div style='flex:1;min-width:300px;background:#111;border-radius:12px;padding:18px 16px 12px 16px;'>
    <div style='color:#8A2BE2;font-size:13px;font-weight:bold;margin-bottom:4px;'>&#128201; 올해 평균 수익률은</div>
    <div style='color:white;font-size:22px;font-weight:900;margin-bottom:12px;'>{_ytd} 이에요</div>
    {_svg2}
    <div style='color:#666;font-size:10px;margin-top:6px;text-align:right;'>버블 크기 = 실현금액 규모</div>
  </div>
</div>
"""
        st.markdown(_chart_html, unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown("---")
    _render_profit_loss_calculator()

    st.markdown('</div>', unsafe_allow_html=True)


def _render_trade_calendar(df_rec: pd.DataFrame):
    """매매 캘린더 렌더링 - 화살표 버튼으로 월 이동, 1개 달력 표시."""
    today = datetime.date.today()
    kr_holidays = holidays.KR()
    daily_pnl_dict: dict = {}

    # ── 데이터 파싱 ──────────────────────────────────────────────────
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

    # ── session_state로 현재 표시 월 관리 ───────────────────────────
    # ── 절대 연월 방식으로 변경 (오류 방지) ──
    _CAL_YEAR_KEY  = "_trade_cal_year"
    _CAL_MONTH_KEY = "_trade_cal_month"
    _MIN_YEAR, _MIN_MONTH = 2026, 1
    _MAX_YEAR, _MAX_MONTH = today.year, today.month  # 상한 = 오늘 달

    # A 방식: 버튼 조작 플래그가 없으면 오늘 달로 초기화
    # 버튼이 클릭되면 _CAL_NAV_FLAG를 True로 설정하고, 다음 렬더링에서 플래그를 사용 후 해제
    _CAL_NAV_FLAG = "_trade_cal_navigated"
    if not st.session_state.get(_CAL_NAV_FLAG, False):
        # 네비게이션 중이 아니면 항상 오늘 달로 리셋
        st.session_state[_CAL_YEAR_KEY]  = _MAX_YEAR
        st.session_state[_CAL_MONTH_KEY] = _MAX_MONTH
    # 플래그 해제 (다음 렬더링에서는 다시 초기화 대상)
    st.session_state[_CAL_NAV_FLAG] = False

    _disp_year  = st.session_state[_CAL_YEAR_KEY]
    _disp_month = st.session_state[_CAL_MONTH_KEY]

    # 화살표 버튼
    _prev_disabled = (_disp_year, _disp_month) <= (_MIN_YEAR, _MIN_MONTH)
    _next_disabled = (_disp_year, _disp_month) >= (_MAX_YEAR, _MAX_MONTH)

    _col_prev, _col_title, _col_next = st.columns([1, 6, 1])
    with _col_prev:
        if st.button("◄", key="_cal_prev_btn", help="이전 달", disabled=_prev_disabled):
            _nm = _disp_month - 1
            _ny = _disp_year
            if _nm < 1:
                _nm = 12
                _ny -= 1
            st.session_state[_CAL_YEAR_KEY]  = _ny
            st.session_state[_CAL_MONTH_KEY] = _nm
            st.session_state[_CAL_NAV_FLAG]  = True  # 네비게이션 플래그 설정
            st.rerun()
    with _col_next:
        if st.button("►", key="_cal_next_btn", help="다음 달", disabled=_next_disabled):
            _nm = _disp_month + 1
            _ny = _disp_year
            if _nm > 12:
                _nm = 1
                _ny += 1
            st.session_state[_CAL_YEAR_KEY]  = _ny
            st.session_state[_CAL_MONTH_KEY] = _nm
            st.session_state[_CAL_NAV_FLAG]  = True  # 네비게이션 플래그 설정
            st.rerun()

    # 표시월 재가져오기 (rerun 후)
    _disp_year  = st.session_state[_CAL_YEAR_KEY]
    _disp_month = st.session_state[_CAL_MONTH_KEY]

    with _col_title:
        _monthly_total_nav = sum(v for k, v in daily_pnl_dict.items() if k.year == _disp_year and k.month == _disp_month)
        _nav_color = "#FF4B4B" if _monthly_total_nav > 0 else ("#4B9FFF" if _monthly_total_nav < 0 else "#888")
        _nav_sign  = "+" if _monthly_total_nav > 0 else ""
        st.markdown(
            f"<div style='text-align:center;font-size:16px;font-weight:900;color:#fff;padding-top:6px;'>"
            f"{_disp_year}년 {_disp_month}월 "
            f"<span style='color:{_nav_color};font-size:14px;'>({_nav_sign}{_monthly_total_nav:,.0f}원)</span></div>",
            unsafe_allow_html=True
        )

    # ── 달력 HTML 생성 ─────────────────────────────────────────────
    cal_obj = calendar.Calendar(firstweekday=6)
    weeks = cal_obj.monthdatescalendar(_disp_year, _disp_month)

    tbl  = '<table style="width:100%;table-layout:fixed;border-collapse:collapse;border:1px solid #333;margin-top:8px;">'
    tbl += "<tr>"
    for day_name in ["일", "월", "화", "수", "목", "금", "토"]:
        tbl += f'<th style="background-color:#000000;color:#FF9900;padding:6px 2px;border:1px solid #2b2e35;text-align:center;font-size:12px;">{day_name}</th>'
    tbl += "</tr>"
    for week in weeks:
        tbl += "<tr>"
        for d in week:
            day_text   = str(d.day) if d.month == _disp_month else " "
            style_date = "height:24px;background-color:#111111;color:#FF9900;font-weight:bold;text-align:left;padding:3px 4px;border:1px solid #2b2e35;font-size:11px;"
            tbl += f'<td style="{style_date}">{day_text}</td>'
        tbl += "</tr><tr>"
        for d in week:
            if d.month == _disp_month and d in daily_pnl_dict:
                val = daily_pnl_dict[d]
                val_color     = get_color_by_value(val)
                formatted_val = f"{val:,.0f}" if val != 0 else "&nbsp;"
            elif d.month == _disp_month and d in kr_holidays:
                val_color     = "#888888"
                formatted_val = "휴장"
            else:
                val_color     = "white"
                formatted_val = "&nbsp;"
            style_data = f"height:60px;background-color:#000000;color:{val_color};border:1px solid #2b2e35;text-align:center;vertical-align:middle;padding:3px;font-size:12px;font-weight:bold;"
            tbl += f'<td style="{style_data}">{formatted_val}</td>'
        tbl += "</tr>"
    tbl += "</table>"
    st.markdown(tbl, unsafe_allow_html=True)

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


# get_cached_previous_close는 logic.py에서 import 됨

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
# 손익 테이블 스타일링 함수는 logic.py에서 import 됨

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
    
    # ── 대시보드 반응형 1열 레이아웃 CSS ──
    st.markdown("""
    <style>
    .block-container {
        max-width: min(1200px, 90vw) !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    .asset-card-stack { width: 100%; margin-bottom: 12px; position: relative; }
    </style>
    """, unsafe_allow_html=True)
    if True:  # 대시보드 1열 시작
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

        st.markdown(f'''<div class='glass-card-premium-blue' style='padding: 24px; padding-bottom:10px; margin-bottom: 0;'>
<div style="text-align:center; padding-top:10px;">
<div style="font-size:15px; color:#8ab4f8; font-weight:bold; margin-bottom:6px; letter-spacing:1px;">목표 {formatted_gs_val}억 &nbsp;|&nbsp; <span style="color:#FFFFFF; background-color:rgba(138,180,248,0.2); padding:2px 10px; border-radius:10px; font-weight:900;">D-{d_days_dynamic}</span></div>
<div class="neon-pulse-blue">₩{int(total_assets):,}</div>
        
<div class="progress-track-blue">
<div class="progress-fill-peach" style="width:{ach}%;"></div>
</div>
<div style="font-size:13px; color:#A0C0FF; font-weight:bold; display:flex; flex-wrap:nowrap; justify-content:flex-start; align-items:center; letter-spacing:0.5px;">
<span style="color:#A0C0FF;">{ach:.2f}% 달성</span>
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
            import re as _re
            _today = datetime.date.today()
            _cur_year = _today.year

            # ── 일별 시트에서 월별 자산이액 증감 계산 (실현+평가 자연 반영) ──
            _dash_monthly_profits = {i: 0 for i in range(1, 13)}
            _dash_monthly_rates = {i: 0.0 for i in range(1, 13)}
            _dash_year_total = 0

            if not df_daily.empty:
                _dd = df_daily.copy()
                _dc_d = _dd.columns[0]
                _ac_d = next((c for c in _dd.columns if '당일자산' in str(c).replace(' ','') or '자산이액' in str(c).replace(' ','')), _dd.columns[1])
                _dd['_date'] = pd.to_datetime(_dd[_dc_d].astype(str).str.replace(' ',''), format='%y.%m.%d.', errors='coerce')
                _dd['_asset'] = pd.to_numeric(_dd[_ac_d].astype(str).str.replace(',',''), errors='coerce').fillna(0)
                _dd = _dd.dropna(subset=['_date'])
                _dd = _dd[_dd['_asset'] > 0]
                _dd_year = _dd[_dd['_date'].dt.year == _cur_year].sort_values('_date')

                # 전년도 마지막 자산이액 (기준점)
                _dd_prev = _dd[_dd['_date'].dt.year == _cur_year - 1].sort_values('_date')
                _prev_year_last_asset = int(_dd_prev.iloc[-1]['_asset']) if len(_dd_prev) > 0 else 0

                # 월별 마지막 자산이액 집계
                _monthly_last_asset = {}
                for _m in range(1, 13):
                    _m_rows = _dd_year[_dd_year['_date'].dt.month == _m]
                    if len(_m_rows) > 0:
                        _monthly_last_asset[_m] = int(_m_rows.sort_values('_date').iloc[-1]['_asset'])

                # 월별 손익 = 당월말 자산 - 전월말 자산
                _sorted_months = sorted(_monthly_last_asset.keys())
                for _idx, _m in enumerate(_sorted_months):
                    if _idx == 0:
                        _base = _prev_year_last_asset
                    else:
                        _base = _monthly_last_asset.get(_sorted_months[_idx - 1], 0)
                    _cur_asset = _monthly_last_asset[_m]
                    _pnl = _cur_asset - _base
                    _dash_monthly_profits[_m] = _pnl
                    if _base > 0:
                        _dash_monthly_rates[_m] = (_pnl / _base) * 100
                    _dash_year_total += _pnl

            # ── 차트 데이터 준비 ──
            _cur_total_asset = _monthly_last_asset.get(max(_monthly_last_asset.keys()), total_assets) if _monthly_last_asset else total_assets
            _goal_amount = gs_val * 100000000 if gs_val > 0 else 10000000000
            _monthly_ach = {_m: (_a / _goal_amount) * 100 for _m, _a in _monthly_last_asset.items()}
            _cur_ach = (total_assets / _goal_amount) * 100 if _goal_amount > 0 else 0

            # ── SVG Area Line Chart 생성 함수 ──
            def _make_area_svg(data_dict, c_left, c_right, y_fmt, chart_idx):
                W, H = 460, 200
                PAD_L, PAD_R, PAD_T, PAD_B = 48, 16, 20, 36
                plot_w = W - PAD_L - PAD_R
                plot_h = H - PAD_T - PAD_B
                months = sorted([m for m in range(1, 13) if data_dict.get(m, 0) > 0])
                if not months:
                    return f'<svg width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="transparent" rx="10"/><text x="{W//2}" y="{H//2}" fill="#555" text-anchor="middle" font-size="13">데이터 없음</text></svg>'
                vals = [data_dict.get(m, 0) for m in months]
                y_max = max(vals) * 1.15 if max(vals) > 0 else 1
                def xp(idx): return PAD_L + int(idx / max(len(months) - 1, 1) * plot_w)
                def yp(v): return PAD_T + int((1 - v / y_max) * plot_h)
                pts = [(xp(i), yp(data_dict.get(m, 0))) for i, m in enumerate(months)]
                area_pts = f"{PAD_L},{H-PAD_B} " + " ".join(f"{x},{y}" for x, y in pts) + f" {pts[-1][0]},{H-PAD_B}"
                line_pts = " ".join(f"{x},{y}" for x, y in pts)
                
                grad_id = f"grad_{chart_idx}"
                mask_id = f"mask_{chart_idx}"
                svg = f'<svg width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">'
                svg += f'<defs>'
                svg += f'  <linearGradient id="{grad_id}" x1="0%" y1="0%" x2="100%" y2="0%">'
                svg += f'    <stop offset="0%" stop-color="{c_left}"/>'
                svg += f'    <stop offset="100%" stop-color="{c_right}"/>'
                svg += f'  </linearGradient>'
                svg += f'  <radialGradient id="light_{chart_idx}" cx="100%" cy="0%" r="80%">'
                svg += f'    <stop offset="0%" stop-color="#ffffff" stop-opacity="0.85"/>'
                svg += f'    <stop offset="100%" stop-color="transparent" stop-opacity="0.0"/>'
                svg += f'  </radialGradient>'
                svg += f'  <linearGradient id="fade_{mask_id}" x1="0%" y1="0%" x2="0%" y2="100%">'
                svg += f'    <stop offset="0%" stop-color="white" stop-opacity="1.0"/>'
                svg += f'    <stop offset="40%" stop-color="white" stop-opacity="0.7"/>'
                svg += f'    <stop offset="85%" stop-color="white" stop-opacity="0.0"/>'
                svg += f'    <stop offset="100%" stop-color="white" stop-opacity="0.0"/>'
                svg += f'  </linearGradient>'
                svg += f'  <mask id="{mask_id}">'
                svg += f'    <rect width="{W}" height="{H}" fill="url(#fade_{mask_id})" />'
                svg += f'  </mask>'
                svg += f'</defs>'
                svg += f'<rect width="{W}" height="{H}" fill="transparent" rx="10"/>'
                for gi in range(5):
                    gy = PAD_T + int(gi / 4 * plot_h)
                    svg += f'<line x1="{PAD_L}" y1="{gy}" x2="{W-PAD_R}" y2="{gy}" stroke="#333" stroke-width="1"/>'
                svg += f'<polygon points="{area_pts}" fill="url(#{grad_id})" mask="url(#{mask_id})"/>'
                svg += f'<polygon points="{area_pts}" fill="url(#light_{chart_idx})" mask="url(#{mask_id})"/>'
                svg += f'<polyline points="{line_pts}" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="filter:drop-shadow(0 0 4px rgba(255,255,255,0.6))"/>'
                for i, (m, (x, y)) in enumerate(zip(months, pts)):
                    svg += f'<circle cx="{x}" cy="{y}" r="4" fill="#ffffff" stroke="#111" stroke-width="1.5"/>'
                    lbl = y_fmt(data_dict.get(m, 0))
                    svg += f'<text x="{x}" y="{y-8}" fill="#ffffff" text-anchor="middle" font-size="11" font-weight="bold">{lbl}</text>'
                    svg += f'<text x="{x}" y="{H-PAD_B+14}" fill="#888" text-anchor="middle" font-size="11">{m}월</text>'
                svg += '</svg>'
                return svg

            _svg_d1 = _make_area_svg(_monthly_last_asset, "#AA46D6", "#70D1FC", lambda v: f"{v/100000000:.1f}억", 1)
            _svg_d2 = _make_area_svg(_monthly_ach, "#C04DFF", "#F5B5DD", lambda v: f"{v:.1f}%", 2)

            _charts_html = f"""
<div style='display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap;'>
  <div style='flex:1;min-width:280px;background:#000000;border:1px solid rgba(255, 218, 185, 0.5);border-radius:12px;padding:18px 16px 12px 16px;'>
    <div style='margin-bottom:16px; white-space:nowrap;'>
      <span style='color:#FFDAB9; font-size:14px; font-weight:300;'>&#128200; 총 금융자산은 </span>
      <span style='color:#1A112A; font-size:20px; font-weight:900;'>{_cur_total_asset:,}</span>
      <span style='color:#FFDAB9; font-size:14px; font-weight:300;'> 원 이에요</span>
    </div>
    {_svg_d1}
    <div style='color:#555;font-size:10px;margin-top:4px;text-align:right;'>월말 자산 추이</div>
  </div>
  <div style='flex:1;min-width:280px;background:#000000;border:1px solid rgba(255, 218, 185, 0.5);border-radius:12px;padding:18px 16px 12px 16px;'>
    <div style='margin-bottom:16px; white-space:nowrap;'>
      <span style='color:#FFDAB9; font-size:14px; font-weight:300;'>&#127919; 목표의 </span>
      <span style='color:#1A112A; font-size:20px; font-weight:900;'>{_cur_ach:.2f}</span>
      <span style='color:#FFDAB9; font-size:14px; font-weight:300;'> % 달성 중이에요</span>
    </div>
    {_svg_d2}
    <div style='color:#555;font-size:10px;margin-top:4px;text-align:right;'>월별 목표 달성률 추이</div>
  </div>
</div>
"""
            import re; st.markdown(re.sub(r'\n\s+', ' ', _charts_html), unsafe_allow_html=True)



            
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

    if True:  # 자산카드 1열 블록
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
            
            cards_html += f'''<div class="glass-card asset-card {row['hover']}" style="position:relative;padding-right:90px;"><div style="font-size:13px;color:#A0A0A0;font-weight:bold;margin-bottom:5px;">🔹{row['category']}</div><div style="font-size:26px;font-weight:900;color:#FFFFFF;margin-bottom:5px;white-space:nowrap;">₩{int(row['amount']):,}</div><div class="{c_class}">{p_sign}{int(row['profit']):,} ({p_sign}{row['return_pct']}%)</div>{sparkline}</div>'''
        # 가로 스크롤 + chevron 표시
        st.markdown(
            f'<div class="swipe-wrapper" style="position:relative;">'
            f'<div class="swipe-container">{cards_html}</div>'
            f'<div class="swipe-glow-left hidden"></div>'
            f'<div class="swipe-glow-right hidden"></div>'
            f'</div>',
            unsafe_allow_html=True
        )

        import streamlit.components.v1 as components
        components.html('''
        <script>
        (function(){
            const doc = window.parent.document;
            const container = doc.querySelector('.swipe-container');
            if (!container) return;
            if (!doc.getElementById('swipe-glow-style')) {
                const style = doc.createElement('style');
                style.id = 'swipe-glow-style';
                style.innerHTML = `
                .swipe-container::-webkit-scrollbar { display: none !important; }
                .swipe-container { -ms-overflow-style: none; scrollbar-width: none; }
                .swipe-glow-right, .swipe-glow-left {
                    position: absolute; top: 50% !important;
                    width: 16px !important; height: 16px !important;
                    pointer-events: none; opacity: 1;
                    transition: opacity 0.3s ease-in-out;
                    background: none !important; border-radius: 0 !important; z-index: 50;
                }
                .swipe-glow-right {
                    right: 25px;
                    border-top: 4px solid rgba(180,130,255,0.9);
                    border-right: 4px solid rgba(180,130,255,0.9);
                    border-left: none; border-bottom: none;
                    animation: neon-chevron-right 1.2s infinite alternate ease-in-out;
                }
                .swipe-glow-left {
                    left: 25px;
                    border-bottom: 4px solid rgba(180,130,255,0.9);
                    border-left: 4px solid rgba(180,130,255,0.9);
                    border-top: none; border-right: none;
                    animation: neon-chevron-left 1.2s infinite alternate ease-in-out;
                }
                .swipe-glow-right.hidden, .swipe-glow-left.hidden { opacity: 0 !important; }
                @keyframes neon-chevron-right {
                    from { opacity:0.3; transform:translateY(-50%) rotate(45deg) translateX(-3px); }
                    to   { opacity:1;   transform:translateY(-50%) rotate(45deg) translateX(3px); filter:drop-shadow(0 0 10px rgba(180,130,255,1)); }
                }
                @keyframes neon-chevron-left {
                    from { opacity:0.3; transform:translateY(-50%) rotate(45deg) translateX(3px); }
                    to   { opacity:1;   transform:translateY(-50%) rotate(45deg) translateX(-3px); filter:drop-shadow(0 0 10px rgba(180,130,255,1)); }
                }
                `;
                doc.head.appendChild(style);
            }
            const overlayRight = doc.querySelector('.swipe-glow-right');
            const overlayLeft  = doc.querySelector('.swipe-glow-left');
            const firstCard    = container.querySelector('.asset-card');
            if (container && firstCard && overlayRight && overlayLeft) {
                const updateBounds = () => {
                    overlayRight.style.top = firstCard.offsetTop + 'px';
                    overlayRight.style.height = firstCard.offsetHeight + 'px';
                    overlayLeft.style.top  = firstCard.offsetTop + 'px';
                    overlayLeft.style.height = firstCard.offsetHeight + 'px';
                };
                const checkScroll = () => {
                    if (container.scrollLeft + container.clientWidth >= container.scrollWidth - 10)
                        overlayRight.classList.add('hidden');
                    else overlayRight.classList.remove('hidden');
                    if (container.scrollLeft <= 10) overlayLeft.classList.add('hidden');
                    else overlayLeft.classList.remove('hidden');
                };
                container.addEventListener('scroll', checkScroll);
                window.parent.addEventListener('resize', () => { updateBounds(); checkScroll(); });
                setTimeout(() => { updateBounds(); checkScroll(); }, 300);
                setTimeout(() => { updateBounds(); checkScroll(); }, 1200);
            }
        })();
        </script>
        ''', height=0)


    
    if True:  # 도넛 차트 1열 블록
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
                
    with st.expander("📊 현황 요약 보기", expanded=False):
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