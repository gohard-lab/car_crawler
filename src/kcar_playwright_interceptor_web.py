import streamlit as st
import pandas as pd
import time
import sys
import asyncio
import io
import os


from tracker_web import log_app_usage

# ✅ 변경 후 (최초 1회 접속 시에만 실행됨)
if "has_logged_execution" not in st.session_state:
    # 함수가 성공했는지(True) 로딩 때문에 실패했는지(False) 결과를 받습니다.
    is_logged = log_app_usage("Kcar_crawler", "crawler_stated")
    
    # 완전히 DB 기록에 성공했을 때만 도장을 쾅 찍어줍니다!
    if is_logged:
        st.session_state["has_logged_execution"] = True


# 스트림릿 클라우드 깡통 서버에 크롬 브라우저를 강제로 설치하게 만드는 마법의 주문
os.system("playwright install chromium")

# --- [윈도우 환경 Streamlit + Playwright 충돌 방지 코드] ---
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
# -----------------------------------------------------------

from playwright.sync_api import sync_playwright

# --- 1. Playwright API 인터셉트 엔진 (업그레이드 버전) ---
# --- 1. Playwright API 인터셉트 엔진 (정문 돌파 완성형) ---
def intercept_kcar_api(keyword):
    """메인 페이지로 진입하여 고유한 Placeholder를 찾아 검색하는 안정적인 방식"""
    time.sleep(1) 
    
    with sync_playwright() as p:
        # 브라우저가 움직이는 것을 볼 수 있도록 당분간 False 유지
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        target_api_pattern = "**/search/list**"

        try:
            print(f"[{keyword}] 정문(메인 페이지)으로 진입합니다...")
            # 1. 메인 페이지로 정상 접속
            page.goto("https://www.kcar.com", timeout=30000)
            
            # 2. [핵심] 찾아오신 placeholder를 이용해 사람처럼 정확히 검색창 타겟팅
            # 팝업이 떠 있어도 뚫고 들어가서 입력할 수 있도록 설계된 Playwright의 강력한 기능입니다.
            search_input = page.get_by_placeholder("차량을 검색하세요.")
            
            # 검색창이 화면에 나타날 때까지 최대 10초 대기
            search_input.wait_for(state="visible", timeout=10000)
            
            # 검색어 입력
            search_input.fill(keyword)
            print("검색어 입력 완료. 엔터키를 누르고 암호화 통신을 기다립니다...")
            
            # 3. 엔터키 입력과 동시에 API 통신 낚아채기
            with page.expect_response(target_api_pattern, timeout=15000) as response_info:
                search_input.press("Enter")
            
            response = response_info.value
            
            if response.ok:
                data = response.json()
                rows = data.get('data', {}).get('rows', [])
                
                parsed_data = []
                for car in rows:
                    brand = car.get('mnuftrNm', '브랜드불명')
                    model = car.get('grdNm') or car.get('carNm', '모델명불명') 
                    
                    # [추가된 부분] 연식 데이터 추출
                    # API 응답 구조에 따라 연식을 나타내는 키값이 다를 수 있습니다. (예: prdYy, mnfctYy, yy 등)
                    # 실제 응답 JSON을 F12로 확인하여 정확한 영문 키값을 맞춰주어야 합니다.
                    raw_year = car.get('mfgDt') or car.get('mnfctYy', '연식불명')
                    
                    # 만약 연식이 '202205' 처럼 6자리로 온다면 '2022년' 형태로
                    # (데이터가 4자리 이상일 경우 앞의 4자리만 가져와서 '년'을 붙여줍니다)
                    # [수정된 부분] 6자리 문자열을 '0000년 00월' 형태로 예쁘게 자르기
                    if isinstance(raw_year, str) and raw_year.isdigit():
                        if len(raw_year) >= 6:
                            # 앞 4자리(년)와 그다음 2자리(월)를 잘라서 조합합니다.
                            display_year = f"{raw_year[:4]}년 {raw_year[4:6]}월"
                        elif len(raw_year) == 4:
                            # 혹시 서버가 4자리(년도)만 보냈을 경우의 방어 코드
                            display_year = f"{raw_year}년"
                        else:
                            display_year = raw_year
                    else:
                        display_year = str(raw_year)
                    
                    price_str = car.get('rentPriceAvc') or car.get('prc', '0')
                    price_int = int(str(price_str).replace(',', '')) if str(price_str).isdigit() else 0
                    
                    if price_int > 0:
                        parsed_data.append({
                            "브랜드": brand, 
                            "모델명": model,
                            "연식": display_year, # <--- 딕셔너리에 연식 항목 추가
                            "매물 가격 (만 원)": price_int
                        })
                        
                return parsed_data
            else:
                return None
                
        except Exception as e:
            print(f"\n[크롤링 상세 에러 분석]: {e}")
            return None
        finally:
            time.sleep(2) 
            browser.close()

# --- 2. Streamlit 웹 대시보드 UI ---
st.set_page_config(page_title="내 차 가치 분석기", page_icon="🚗", layout="wide")

st.title("🚗 K Car 중고차 감가 방어율 분석기 (Playwright 엔진)")
st.markdown("현업의 API 통신 가로채기 방식으로 실제 100% 직영 매물 데이터를 동적 수집하여 분석합니다.")

with st.sidebar:
    st.header("설정 (Settings)")
    target_car = st.text_input("분석할 차종을 입력하세요", placeholder="예: 그랜저, 아반떼", value="그랜저")
    
    new_car_price = st.number_input(
        "해당 차종의 신차 출고가 (만 원)", 
        min_value=1000, max_value=20000, value=3500, step=100
    )
    
    analyze_btn = st.button("데이터 탈취 및 분석 시작", type="primary", use_container_width=True)

if analyze_btn:
    if not target_car:
        st.warning("차종을 먼저 입력해 주세요!")
    else:
        # st.spinner를 통해 브라우저가 뒤에서 통신을 가로채는 동안 예쁜 로딩 화면을 보여줍니다.
        with st.spinner(f"투명 브라우저가 '{target_car}' 데이터를 암호화망을 뚫고 가로채는 중입니다..."):
            car_data_list = intercept_kcar_api(target_car)
        
        if not car_data_list:
            st.error("데이터를 수집하지 못했습니다. 검색어가 정확한지 확인해 주세요.")
        else:
            st.success("네트워크 날치기 성공! 데이터를 화면에 출력합니다.")
            
            # --- 결과 계산 로직 ---
            df = pd.DataFrame(car_data_list)
            
            # 파이썬 데이터프레임의 기본 인덱스(0부터 시작)를 1부터 시작하도록 강제 변경합니다.
            df.index = range(1, len(df) + 1)
            
            total_count = len(df)
            avg_used_price = df["매물 가격 (만 원)"].mean()
            
            retention_rate = (avg_used_price / new_car_price) * 100
            depreciation_rate = 100 - retention_rate

            # --- 시각적 결과 출력 ---
            col1, col2, col3 = st.columns(3)
            
            col1.metric(label="분석된 직영 매물 수", value=f"{total_count} 대")
            col2.metric(label="평균 중고 시세", value=f"{avg_used_price:,.0f} 만 원")
            
            retention_color = "normal" if retention_rate >= 70 else "inverse"
            col3.metric(
                label="가치 보존율 (감가 방어율)", 
                value=f"{retention_rate:.1f} %",
                delta=f"감가율 -{depreciation_rate:.1f}%",
                delta_color=retention_color
            )
            
            st.divider()
            
            st.subheader("📋 수집된 가격 데이터 원본 (Raw Data)")
            st.dataframe(df, use_container_width=True)
            
            # st.subheader("📊 매물 가격 분포도")
            # st.bar_chart(df["매물 가격 (만 원)"].value_counts().sort_index())
            
            # --- [수정된 코드] 직관적인 개별 매물 가격 비교 ---
            st.subheader("📊 개별 매물 가격 비교")
            
            # 파이썬 리스트 내포(List Comprehension)를 사용해 "1번 차량, 2번 차량..." 이름표를 만듭니다.
            df.index = [f"{i+1}번 차량" for i in range(len(df))]
            
            # 이제 value_counts()를 빼고 가격 자체를 지정하면, 
            # 가로축은 'x번 차량', 세로축은 '가격'인 직관적인 막대그래프가 솟아오릅니다.
            st.bar_chart(df["매물 가격 (만 원)"])

            # --- [추가된 부분] 엑셀 다운로드 기능 ---
            st.divider() # 화면에 예쁜 가로줄 긋기
            st.subheader("💾 데이터 내보내기")
            
            # 판다스 데이터프레임(df)을 메모리(BytesIO) 상의 엑셀 파일로 변환합니다.
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='중고차_시세_데이터')
            
            # Streamlit이 제공하는 다운로드 버튼 UI 생성
            st.download_button(
                label="📥 엑셀 파일로 결과 다운로드",
                data=buffer.getvalue(),
                file_name=f"{target_car}_중고차_시세.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )            