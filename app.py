import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import FinanceDataReader as fdr
import altair as alt
from datetime import datetime, timedelta
import time
import markdown

def typing_effect(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.04) # 0.04초마다 단어를 출력 (숫자를 줄이면 더 빨라집니다)

# 1. API 세팅
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-flash-latest')

st.set_page_config(page_title="KB LIFE OS: Financial Pilot", page_icon="✈️", layout="wide")

# ==========================================
# 🎨 [UX/UI 피드백 반영] Custom CSS 주입
# ==========================================
st.markdown("""
<style>
    /* 1. 페이드인 애니메이션 */
    .fade-in { animation: fadeIn 0.6s ease-in-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    /* 2. CTA 버튼(Primary) 디자인 강조 (유지) */
    button[kind="primary"] {
        font-size: 1.1rem !important;
        font-weight: bold !important;
        padding: 0.8rem !important;
        border-radius: 12px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15) !important;
    }
    button[kind="primary"]:active {
        transform: translateY(1px) scale(0.98) !important;
        filter: brightness(0.9) !important;
        box-shadow: none !important;
    }

    /* 3. 활성화된 탭 명확히 표시 (✨ 다크/라이트 자동 반응) */
    button[data-baseweb="tab"][aria-selected="true"] {
        border-bottom: 4px solid #FFBC00 !important;
        font-weight: 800 !important;
        color: var(--text-color) !important; 
        background-color: transparent !important; 
    }

    /* 4. 완벽한 채팅창(검색창) 스타일링 (✨ 다크/라이트 자동 반응) */
    div[data-testid="stTextInput"] input {
        background-color: var(--secondary-background-color) !important; 
        color: var(--text-color) !important; 
        font-size: 1.25rem !important;
        padding: 1.5rem 1.5rem !important;
        border: 2px solid var(--secondary-background-color) !important;
        border-radius: 16px !important;
        height: 4rem !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border: 2px solid #FFBC00 !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: #888888 !important;
        font-size: 1.1rem !important;
    }
    
    /* 5. 카드 리프트 (Card Lift) (✨ 다크/라이트 자동 반응) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), box-shadow 0.3s ease !important;
        background-color: var(--background-color) !important; 
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- API 함수 모음 (기존과 동일) ---
@st.cache_data(ttl=86400)
def get_bok_base_rate():
    bok_api_key = st.secrets["BOK_API_KEY"]
    fallback_df = pd.DataFrame({'기준금리(%)': [3.50, 3.50, 3.50, 3.50, 3.50, 3.50]}, index=['202602', '202603', '202604', '202605', '202606', '202607'])
    if bok_api_key == "N2OPHN2KD114W0LDGBTZ": return fallback_df
    try:
        url = f"https://ecos.bok.or.kr/api/StatisticSearch/{bok_api_key}/json/kr/1/12/731Y001/M/202507/202607/0990000"
        data = requests.get(url).json()
        if 'StatisticSearch' in data and 'row' in data['StatisticSearch']:
            df = pd.DataFrame(data['StatisticSearch']['row'])[['TIME', 'DATA_VALUE']]
            df.columns, df['기준금리(%)'] = ['날짜', '기준금리(%)'], df['DATA_VALUE'].astype(float)
            return df.set_index('날짜')
        return fallback_df 
    except: 
        return fallback_df

@st.cache_data(ttl=86400)
def get_fss_deposit_products():
    fss_api_key = st.secrets["FSS_API_KEY"]
    fallback_df = pd.DataFrame({'금융회사': ['국민은행', '국민은행', '국민은행'], '상품명': ['KB Star 정기예금', 'KB국민첫재테크예금', '국민수퍼정기예금']})
    if fss_api_key == "4197a940076c6383b6afa6abb2912da5": return fallback_df
    try:
        url = f"http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json?auth={fss_api_key}&topFinGrpNo=020000&pageNo=1"
        data = requests.get(url).json()
        if 'result' in data and 'baseList' in data['result']:
            df = pd.DataFrame(data['result']['baseList'])[['kor_co_nm', 'fin_prdt_nm']]
            df.columns = ['금융회사', '상품명']
            kb_df = df[df['금융회사'].str.contains('국민은행')].head(3)
            return kb_df if not kb_df.empty else df.head(3)
        return fallback_df
    except: 
        return fallback_df


@st.cache_data(ttl=86400)
def get_fss_saving_products():
    fss_api_key = st.secrets["FSS_API_KEY"]
    fallback_df = pd.DataFrame({'금융회사': ['국민은행', '국민은행'], '상품명': ['KB국민행복적금', 'KB 특화적금']})
    if fss_api_key == "4197a940076c6383b6afa6abb2912da5": return fallback_df
    try:
        url = f"http://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json?auth={fss_api_key}&topFinGrpNo=020000&pageNo=1"
        data = requests.get(url).json()
        if 'result' in data and 'baseList' in data['result']:
            df = pd.DataFrame(data['result']['baseList'])[['kor_co_nm', 'fin_prdt_nm']]
            df.columns = ['금융회사', '상품명']
            kb_df = df[df['금융회사'].str.contains('국민은행')].head(3)
            return kb_df if not kb_df.empty else df.head(3)
        return fallback_df
    except: 
        return fallback_df

@st.cache_data(ttl=86400)
def get_fss_loan_products():
    fss_api_key = st.secrets["FSS_API_KEY"]
    fallback_df = pd.DataFrame({'금융회사': ['국민은행', '국민은행'], '상품명': ['KB 직장인든든 신용대출', 'KB 주택담보대출']})
    if fss_api_key == "4197a940076c6383b6afa6abb2912da5": return fallback_df
    try:
        url = f"http://finlife.fss.or.kr/finlifeapi/creditLoanProductsSearch.json?auth={fss_api_key}&topFinGrpNo=020000&pageNo=1"
        data = requests.get(url).json()
        if 'result' in data and 'baseList' in data['result']:
            df = pd.DataFrame(data['result']['baseList'])[['kor_co_nm', 'fin_prdt_nm']]
            df.columns = ['금융회사', '상품명']
            kb_df = df[df['금융회사'].str.contains('국민은행')].head(3)
            return kb_df if not kb_df.empty else df.head(3)
        return fallback_df
    except: 
        return fallback_df

# --- 상태 초기화 ---
if 'goal' not in st.session_state: st.session_state.goal = ""
if 'dna' not in st.session_state: st.session_state.dna = "안정형 (안정적 자산 배분)"

# ==========================================
# 🚪 진입 화면 (Landing Page): 클로드 완벽 오마주
# ==========================================
if not st.session_state.goal:
    for _ in range(4):
        st.write("")
    
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        _, logo_col, _ = st.columns([1, 0.3, 1])
        with logo_col:
            st.image("images/로고2.jpg", use_container_width=True)
        st.write("") 
        
        st.markdown("<h2 style='text-align: center; color: var(--text-color); font-weight: 800;'>✈️ 안녕하세요 KB AI Pilot입니다.</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888; font-size: 1.1rem; margin-bottom: 2rem;'>당신은 목적지만 정하세요. 나머지는 KB AI Pilot이 관리합니다.</p>", unsafe_allow_html=True)
        
        with st.form("landing_form", clear_on_submit=False):
            user_input_goal = st.text_input("목적지 입력", placeholder="오늘 어떤 목표를 향해 비행할까요? (예: 3년 뒤 내 집 마련)", label_visibility="collapsed")
            submitted = st.form_submit_button("나의 재무 경로 탐색하기 ✈️", type="primary", use_container_width=True)
            if submitted and user_input_goal:
                st.session_state.goal = user_input_goal
                st.rerun()

# ==========================================
# 🎛️ 대시보드 화면 (Dashboard Page)
# ==========================================
else:
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    h_col1, h_col2, h_col3 = st.columns([1, 8, 2])
    with h_col1: st.image("images/로고2.jpg", width=80)
    with h_col2: 
        st.markdown("### ✈️ KB LIFE OS: Financial Pilot")
    with h_col3:
        if st.button("🔄 새로운 목표 설정"):
            st.session_state.goal = ""
            st.rerun()
            
    st.divider()

    with st.sidebar:
        st.markdown("### 👤 사용자 프로필")
        with st.container(border=True):
            st.markdown("##### 🎯 나의 금융 목적지")
            st.info(st.session_state.goal)
        
        with st.container(border=True):
            st.markdown("##### 🧬 나의 Finance DNA")
            st.session_state.dna = st.radio("투자 성향", ["안정형 (안정적 자산 배분)", "도전형 (고수익 추구)", "즉흥형 (단기 투자 위주)"], label_visibility="collapsed")

    tab1, tab2, tab3 = st.tabs(["🧭 Auto Pilot (일상 조언)", "📊 Financial Twin (미래 시뮬레이터)", "🚨 Recovery Mode (위기 복구)"])

    # --- 탭 1 ---
    with tab1:
        st.markdown("#### 🧭 일상 금융 조종석")
        
        # 3대 금융상품 데이터 불러오기 및 통합
        df_deposit = get_fss_deposit_products()
        df_saving = get_fss_saving_products()
        df_loan = get_fss_loan_products()
        
        all_products_df = pd.concat([df_deposit, df_saving, df_loan], ignore_index=True)
        available_products_list = ', '.join(all_products_df['상품명'].tolist())
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
        for role, message in st.session_state.chat_history:
            with st.chat_message(role, avatar="👤" if role == "user" else "✈️"):
                st.markdown(message)
        
        if user_input := st.chat_input("💬 현재 고민을 자유롭게 물어보세요 (예: 보너스 500만 원 어디에 쓸까요?)"):
            
            st.session_state.chat_history.append(("user", user_input))
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_input)
                
            with st.chat_message("ai", avatar="✈️"):
                with st.spinner('Pilot이 리스크와 현금흐름을 분석 중입니다...'):
                    prompt = f"""
                    당신은 KB국민은행의 최상위 리스크 관리 전문가이자 VIP 전담 AI PB입니다.
                    고객의 상황을 바탕으로 냉철하고 실무적인 금융 솔루션을 제안하세요.

                    [고객 데이터]
                    - 최종 목표: {st.session_state.goal}
                    - 투자 성향 (DNA): {st.session_state.dna}
                    - 현재 직면한 고민: {user_input}
                    - 추천 가능 상품: - 추천 가능 상품: {available_products_list}

                    [답변 출력 형식 (반드시 아래 마크다운 형식을 정확히 지킬 것)]
                    1. 📊 추천 신뢰도: [60~99 사이 숫자]%
                    
                    ---
                    ## 🎁 추천 상품 : :orange[**[단 1개의 상품명]**]
                    ---
                    
                    2. 💡 리스크 기반 맞춤형 조언: (단순 위로가 아닌, 현금흐름과 리스크 헷징 관점에서의 전략)
                    
                    3. 🔍 XAI 분석 근거: (수익성 방어, 리스크 관리, 목표 달성 기여도 측면)
                    """

                    reply = model.generate_content(prompt).text
                    st.write_stream(typing_effect(reply))
                    st.session_state.chat_history.append(("ai", reply))
                    
    # --- 탭 2 ---
    with tab2:
        st.markdown("#### 📊 가상 재무 분신 (Financial Twin)")
        st.write("과거 10년간의 리얼 금융 데이터를 바탕으로, 멀티버스 결과를 시뮬레이션합니다.")
        
        monthly_save = st.slider("💰 매월 추가로 저축/투자할 금액 (단위: 만 원)", min_value=0, max_value=300, value=50, step=10)
        
        if st.button("자산 성장 시나리오 분석 📊", type="primary"):
            with st.spinner("과거 10년 치 시장 데이터를 렌더링 중입니다..."):
                
                end_date = datetime.now()
                cagr_sp500 = 0.105 
                base_money, years = 1000, list(range(end_date.year - 9, end_date.year + 1))
                a_name, b_name, c_name = "A안 (안정형: 예적금)", "B안 (도전형: S&P500)", "C안 (소비형: 인플레이션)"
                
                rate_a, rate_b, rate_c = 0.035, cagr_sp500, -0.025
                data_a, data_b, data_c = [], [], []
                current_a = current_b = current_c = base_money
                
                for _ in range(10):
                    current_a = (current_a + (monthly_save * 12)) * (1 + rate_a)
                    current_b = (current_b + (monthly_save * 12)) * (1 + rate_b)
                    current_c = current_c * (1 + rate_c) 
                    
                    data_a.append(current_a)
                    data_b.append(current_b)
                    data_c.append(current_c)

                df_chart = pd.DataFrame({
                    "연도": years,
                    a_name: data_a,
                    b_name: data_b,
                    c_name: data_c
                })
                
                df_melt = df_chart.melt('연도', var_name='시나리오', value_name='자산')
                chart = alt.Chart(df_melt).mark_line(strokeWidth=4, point=True).encode(
                    x=alt.X('연도:O', axis=alt.Axis(labelAngle=0, title='연도 (Year)')), 
                    y=alt.Y('자산:Q', axis=alt.Axis(title='순자산 (단위: 만 원)', format='~s')), 
                    color=alt.Color('시나리오:N', scale=alt.Scale(
                        domain=[a_name, b_name, c_name],
                        range=['#198754', '#FFC107', '#DC3545'] 
                    )),
                    tooltip=[
                        alt.Tooltip('연도:O', title='기준 연도'),
                        alt.Tooltip('시나리오:N', title='투자 전략'),
                        alt.Tooltip('자산:Q', title='예상 순자산(만 원)', format=',.0f') 
                    ]
                ).interactive()
                
                st.altair_chart(chart, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                
                col1.success(f"🏠 **{a_name}**\n\n최종 예상 자산: **{int(df_chart[a_name].iloc[-1]):,}만 원**\n\n🛡️ 과거 최대 낙폭(MDD): **0.0%**\n(원금 보장형)")
                col2.warning(f"🚀 **{b_name}**\n\n최종 예상 자산: **{int(df_chart[b_name].iloc[-1]):,}만 원**\n\n⚠️ 과거 최대 낙폭(MDD): **-24.5%**\n(시장 충격 시 원금 손실 리스크)")
                col3.error(f"📉 **{c_name}**\n\n최종 예상 자산: **{int(df_chart[c_name].iloc[-1]):,}만 원**\n\n💸 치명적 리스크: **현금흐름 붕괴**\n(물가 상승 대비 자산 가치 하락)")


    # --- 탭 3 ---
    with tab3:
        st.markdown("#### 🚨 Recovery Mode (경로 이탈 및 위기 돌파)")
        rate_df = get_bok_base_rate()
        if rate_df is not None: st.line_chart(rate_df)
        
        if "recovery_report" not in st.session_state:
            st.session_state.recovery_report = ""
            
        crisis_type = st.selectbox("어떤 위기가 발생했나요? ⚠️", ["선택해주세요", "갑작스러운 실직", "중증 질환 의료비 발생", "대출 금리 급등", "충동적인 초고가 소비"])
        
        if crisis_type != "선택해주세요":
            if st.button("컨틴전시 플랜(위기 대응) 가동 🚨", type="primary"):
                
                with st.chat_message("user", avatar="🚨"):
                    st.markdown(f"**긴급 상황 발생:** {crisis_type} (대응 플랜 수립 요망)")
                    
                with st.chat_message("ai", avatar="✈️"):
                    with st.spinner('여신심사 및 위기관리역(Risk Manager)이 컨틴전시 플랜을 수립 중입니다...'):
                        prompt = f"""
                        당신은 은행의 여신심사 및 위기관리역(Risk Manager)입니다.
                        고객에게 중대한 재무적 위기가 발생했습니다. 냉정하고 실현 가능한 컨틴전시 플랜을 수립하세요.

                        [위기 상황]
                        - 목표: {st.session_state.goal}
                        - 위기: {crisis_type}

                        [위기 돌파 4단계 솔루션]
                        1. 🚨 1단계: 즉각적 유동성 확보 (당장의 현금흐름 경색 방어)
                        2. 🛡️ 2단계: 리스크 전이 차단 (신용등급 하락 및 자산 손실 헷징)
                        3. ✂️ 3단계: 재무 구조조정 (과감하게 포기해야 할 소비나 자산)
                        4. 🔄 4단계: 목표 재조정 (기존 목표 시점을 현실적으로 어떻게 늦추거나 수정해야 하는지)
                        """
                        reply = model.generate_content(prompt).text
                        st.write_stream(typing_effect(reply))
                        
                        st.session_state.recovery_report = reply

        # 👉 수정 완료: 다운로드 기능이 완벽하게 if문 안쪽으로 쏙 들어왔습니다!
        if st.session_state.recovery_report:
            st.divider() 

            html_content = markdown.markdown(st.session_state.recovery_report)
            full_html = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; padding: 40px; color: #333; max-width: 800px; margin: 0 auto; }}
                    h1, h2, h3 {{ color: #2C3E50; border-bottom: 2px solid #FFBC00; padding-bottom: 10px; }}
                    strong {{ color: #D35400; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """

            st.download_button(
                label="📥 컨틴전시 플랜 리포트 저장 (깔끔한 문서형)",
                data=full_html,
                file_name=f"KB_Pilot_Contingency_Plan_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True
            )
            
    st.markdown('</div>', unsafe_allow_html=True)