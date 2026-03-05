import streamlit as st
import pandas as pd
import time
# 이전 단계에서 만든 케이카 크롤러 모듈을 불러옵니다.
from kcar_playwright_interceptor import intercept_kcar_api 

# 페이지 기본 설정
st.set_page_config(page_title="내 차 가치 분석기", page_icon="🚗", layout="wide")

st.title("🚗 K Car 중고차 감가 방어율 분석기")
st.markdown("현업의 API 통신 방식으로 실제 100% 직영 매물 데이터를 수집하여 분석합니다.")

# --- UI 레이아웃 구성 ---
with st.sidebar:
    st.header("설정 (Settings)")
    target_car = st.text_input("분석할 차종을 입력하세요", placeholder="예: 그랜저, 아반떼", value="그랜저", key="car_search_input1")
    
    # 신차 가격 입력 (감가율 계산용)
    new_car_price = st.number_input(
        "해당 차종의 신차 가격 (만 원)", 
        min_value=1000, max_value=20000, value=3500, step=100
    )
    
    analyze_btn = st.button("분석 시작", type="primary", use_container_width=True)

# --- 분석 로직 ---
if analyze_btn:
    if not target_car:
        st.warning("차종을 먼저 입력해 주세요!")
    else:
        st.info(f"K Car API에서 '{target_car}' 매물 데이터를 실시간으로 가져오는 중입니다...")
        
        # 실제 API 크롤링 함수 호출
        # (시각적 효과를 위해 임의의 딜레이를 줍니다)
        with st.spinner("데이터 파싱 중..."):
            time.sleep(1) 
            prices_list = intercept_kcar_api(target_car)
        
        if not prices_list:
            st.error("데이터를 수집하지 못했습니다. 검색어가 정확한지, 또는 K Car 서버가 응답하는지 확인해 주세요.")
        else:
            st.success("데이터 수집 완료!")
            
            # --- 결과 계산 ---
            total_count = len(prices_list)
            avg_used_price = sum(prices_list) / total_count
            
            # 감가율 계산 (신차가격 대비 중고차가격 비율)
            # API에서 가격을 만원 단위로 가져왔다고 가정 (예: 2500)
            retention_rate = (avg_used_price / new_car_price) * 100
            depreciation_rate = 100 - retention_rate

            # --- 시각적 결과 출력 ---
            col1, col2, col3 = st.columns(3)
            
            col1.metric(
                label="분석된 직영 매물 수", 
                value=f"{total_count} 대"
            )
            col2.metric(
                label="평균 중고 시세", 
                value=f"{avg_used_price:,.0f} 만 원"
            )
            
            # 방어율이 70% 이상이면 초록색 화살표(방어 성공), 아니면 빨간색(감가 큼)
            retention_color = "normal" if retention_rate >= 70 else "inverse"
            col3.metric(
                label="가치 보존율 (감가 방어율)", 
                value=f"{retention_rate:.1f} %",
                delta=f"감가율 -{depreciation_rate:.1f}%",
                delta_color=retention_color
            )
            
            st.divider()
            
            # 수집된 원본 데이터를 판다스 데이터프레임으로 변환하여 표 형태로 제공
            st.subheader("📋 수집된 가격 데이터 원본 (Raw Data)")
            df = pd.DataFrame(prices_list, columns=["매물 가격 (만 원)"])
            # 데이터가 너무 길 수 있으니 스크롤을 주거나 요약해서 보여줍니다.
            st.dataframe(df, use_container_width=True)
            
            # (선택) 시각화: 가격 분포 히스토그램
            st.subheader("📊 매물 가격 분포도")
            st.bar_chart(df["매물 가격 (만 원)"].value_counts().sort_index())