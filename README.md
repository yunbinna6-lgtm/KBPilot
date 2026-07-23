# ✈️ KB LIFE OS: Financial Pilot

> **2026 KB AI Challenge 출품작**
>
> 고객의 최종 재무 목표를 향해 안전하게 비행하는 초개인화 AI 자산관리 및 리스크 방어 플랫폼입니다.

## 🌟 프로젝트 소개 (Introduction)
**KB AI Pilot**은 단순한 자산 증식을 넘어, 고객의 '현금흐름'과 '리스크 관리'에 초점을 맞춘 최상위 VIP 전담 AI PB 서비스입니다. 사용자는 목적지(재무 목표)만 설정하면 됩니다. 나머지는 AI Pilot이 금융감독원, 한국은행의 실시간 데이터를 바탕으로 최적의 비행 경로를 탐색하고, 난기류(위기 상황) 발생 시 즉각적인 컨틴전시 플랜을 가동합니다.

## 🚀 핵심 기능 (Key Features)

### 1. 🧭 Auto Pilot (일상 금융 조종석)
* **리스크 기반 맞춤형 조언:** Gemini AI가 사용자의 투자 성향(DNA)과 목표를 분석하여 냉철한 실무적 조언을 제공합니다.
* **행동 유도형(Call To Action) 상품 추천:** 금융감독원 오픈 API를 연동하여 실제 KB국민은행 상품 중 가장 적합한 단 1개의 상품을 추천하고, XAI(설명 가능한 AI) 기반으로 추천 근거(수익성 방어, 리스크 관리, 목표 기여도)를 제시합니다.

### 2. 📊 Financial Twin (가상 재무 분신 시뮬레이터)
* **멀티버스 자산 시뮬레이션:** 과거 시장 데이터를 바탕으로 A안(안정형: 예적금), B안(도전형: S&P500), C안(소비형: 인플레이션)의 10년 뒤 자산 변화를 시각화(`Altair`)합니다.
* **MDD (최대 낙폭) 리스크 지표:** 단순 수익률뿐만 아니라 과거 최대 낙폭 리스크를 수치화하여 고객에게 직관적인 경각심을 제공합니다.

### 3. 🚨 Recovery Mode (위기 복구 및 컨틴전시 플랜)
* **거시경제 지표 모니터링:** 한국은행 API를 통해 실시간 기준금리 추이를 제공합니다.
* **위기 돌파 4단계 솔루션:** 실직, 의료비, 대출 금리 급등 등의 재무 위기 발생 시, 유동성 확보부터 목표 재조정까지의 구체적인 '여신심사 및 위기관리역' 리포트를 생성합니다.
* **반응형 HTML 리포트 다운로드:** 생성된 위기 극복 플랜을 가독성 높은 디자인이 적용된 HTML 웹 문서 포맷으로 즉시 다운로드할 수 있습니다.

## 🛠 기술 스택 (Tech Stack)
* **Language:** Python
* **Framework:** Streamlit (다크 모드 및 Custom CSS 애니메이션 적용)
* **AI/LLM:** Google Gemini Flash
* **Data/Visualization:** Pandas, Altair, FinanceDataReader
* **External API:** 한국은행 ECOS API, 금융감독원 금융상품 API

## ⚙️ 설치 및 실행 방법 (Installation & Run)

### 1. Repository Clone
```bash
git clone https://github.com/yunbinna6-lgtm/KB-Pilot.git
cd KB-Pilot
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 (Secrets) 설정
프로젝트 루트 경로에 `.streamlit` 폴더를 생성하고, `secrets.toml` 파일을 만들어 아래 API 키를 입력합니다. (해당 파일은 Git에 업로드되지 않습니다.)
```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "Your_Gemini_API_Key"
BOK_API_KEY = "Your_Bank_of_Korea_API_Key"
FSS_API_KEY = "Your_FSS_API_Key"
```

### 4. 애플리케이션 실행
```bash
streamlit run app.py
```

## 💡 배포 (Deployment)
이 프로젝트는 **Streamlit Community Cloud**를 통해 배포되도록 최적화되어 있습니다. 배포 시 Advanced Settings의 Secrets 탭에 위 환경변수 항목을 동일하게 등록하여 안전하게 서비스할 수 있습니다.

---
*Made for 2026 KB AI Challenge*