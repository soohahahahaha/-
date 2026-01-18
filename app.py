import streamlit as st
import pandas as pd
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="수하님의 제주 여행 플래너", page_icon="🌴", layout="wide")

# 보안 설정: st.secrets에서 API 키 호출
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Streamlit Secrets에 'GEMINI_API_KEY'를 설정해주세요.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

st.title("🌴 제주 여행 일정 확인 앱 (6-4 반 선생님 버전)")
st.markdown("공유해주신 구글 시트의 일정을 기반으로 일차별 상세 내용을 확인하세요.")

# 파일 업로드 (위에서 공유한 시트를 CSV나 XLSX로 다운로드하여 업로드하면 됩니다)
uploaded_file = st.file_uploader("제주 여행 일정 파일(CSV/XLSX)을 업로드하세요", type=['csv', 'xlsx'])

if uploaded_file:
    try:
        # 데이터 로드
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # '일차' 컬럼이 있는지 확인 (시트 내 '1일차', '2일차' 등 기준)
        # 만약 컬럼명이 다를 경우를 대비해 유연하게 처리
        day_col = None
        for col in df.columns:
            if '일차' in col or 'Day' in col:
                day_col = col
                break

        if day_col:
            days = df[day_col].unique()
            
            # 일차별로 탭 생성
            tabs = st.tabs([f"📅 {day}" for day in days])
            
            for i, day in enumerate(days):
                with tabs[i]:
                    day_data = df[df[day_col] == day].dropna(how='all', axis=1)
                    
                    st.subheader(f"📍 {day} 주요 일정")
                    st.dataframe(day_data, use_container_width=True)
                    
                    # Gemini-2.5-flash를 활용한 일정 요약 및 팁
                    st.divider()
                    if st.button(f"{day} AI 가이드 보기", key=f"btn_{day}"):
                        with st.spinner("AI가 일정을 분석 중입니다..."):
                            context = day_data.to_string()
                            prompt = f"""
                            당신은 전문 여행 가이드입니다. 아래의 {day} 여행 일정을 보고:
                            1. 이동 경로가 효율적인지 분석하고
                            2. 해당 일차에 방문하는 '우진해장국'이나 '순천미향' 같은 장소에 대한 간단한 팁을 알려줘.
                            3. 친구들과 함께하는 여행에 어울리는 밝은 톤으로 말해줘.
                            
                            일정 데이터:
                            {context}
                            """
                            response = model.generate_content(prompt)
                            st.info(response.text)
        else:
            st.warning("시트에서 '일차' 정보를 찾을 수 없습니다. 데이터 형식을 확인해 주세요.")
            st.dataframe(df)

    except Exception as e:
        st.error(f"파일 처리 중 오류 발생: {e}")
else:
    st.write("👈 왼쪽 상단에서 여행 일정 파일을 업로드하면 일차별 탭이 생성됩니다.")
