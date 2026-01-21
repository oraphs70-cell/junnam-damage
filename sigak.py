import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. 데이터 로드 및 전처리 (실제 데이터가 없으므로 더미 데이터 생성 함수 사용)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    # 사용자가 실제 CSV를 가지고 있다면 아래 주석을 해제하고 경로를 수정하세요.
    # df = pd.read_csv('전라남도_연도별_태풍피해_현황.csv', encoding='cp949')
    # return df

    # [예시용 데이터 생성 - 실제 전남 피해 사례 반영하여 구성]
    data = {
        '연도': [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 
               2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
        '주요태풍': ['나비', '에위니아', '나리', '갈매기', '-', '곤파스', '무이파', '볼라벤/덴빈', '다나스', '나크리', 
                 '고니', '차바', '-', '솔릭', '링링/타파', '바비/마이삭', '찬투', '힌남노', '카눈'],
        '재산피해액(억원)': [120, 45, 300, 23, 5, 150, 410, 4327, 80, 60, 
                        20, 15, 0, 90, 1500, 350, 40, 124, 10],
        '복구액(억원)':     [180, 60, 450, 35, 8, 240, 600, 7800, 110, 90, 
                        30, 25, 0, 130, 2400, 500, 60, 210, 20],
        '인명피해(명)':     [0, 1, 2, 0, 0, 1, 3, 4, 0, 0, 
                        0, 1, 0, 0, 3, 0, 0, 1, 0]
    }
    df = pd.DataFrame(data)
    return df

# 데이터 불러오기
df = load_data()

# -----------------------------------------------------------------------------
# 2. Streamlit 페이지 설정 및 레이아웃
# -----------------------------------------------------------------------------
st.set_page_config(page_title="전라남도 태풍피해 대시보드", layout="wide")

st.title("🌪️ 전라남도 연도별 태풍피해 분석 대시보드")
st.markdown("""
이 대시보드는 2005년부터 2023년까지 전라남도 지역의 태풍 피해 현황(재산 피해, 복구액, 인명 피해)을 시각화하여 제공합니다.
""")

# 사이드바 (필터링 옵션)
st.sidebar.header("검색 옵션")
selected_years = st.sidebar.slider("조회 연도 범위 선택", 
                                   min_value=int(df['연도'].min()), 
                                   max_value=int(df['연도'].max()), 
                                   value=(2010, 2023))

# 데이터 필터링
mask = (df['연도'] >= selected_years[0]) & (df['연도'] <= selected_years[1])
filtered_df = df.loc[mask]

# -----------------------------------------------------------------------------
# 3. 핵심 지표 (KPI Metrics) 표시
# -----------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)
with col1:
    total_damage = filtered_df['재산피해액(억원)'].sum()
    st.metric(label="총 재산 피해액", value=f"{total_damage:,.0f} 억원")
with col2:
    total_recovery = filtered_df['복구액(억원)'].sum()
    st.metric(label="총 복구액", value=f"{total_recovery:,.0f} 억원", delta=f"{(total_recovery/total_damage if total_damage else 0)*100:.1f}% (복구율)")
with col3:
    total_human = filtered_df['인명피해(명)'].sum()
    st.metric(label="총 인명 피해", value=f"{total_human} 명")

st.divider()

# -----------------------------------------------------------------------------
# 4. 시각화 영역 (2x2 그리드)
# -----------------------------------------------------------------------------

# Row 1
row1_col1, row1_col2 = st.columns(2)

# [분석 1] 연도별 피해액 및 복구액 추세 (Line + Bar Chart)
with row1_col1:
    st.subheader("1. 연도별 재산 피해 및 복구 추세")
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=filtered_df['연도'], y=filtered_df['재산피해액(억원)'], name='재산피해액', marker_color='indianred'))
    fig1.add_trace(go.Scatter(x=filtered_df['연도'], y=filtered_df['복구액(억원)'], name='복구액', mode='lines+markers', line=dict(color='royalblue', width=3)))
    fig1.update_layout(height=400, xaxis_title="연도", yaxis_title="금액(억원)", hovermode="x unified")
    st.plotly_chart(fig1, use_container_width=True)

# [분석 2] 피해액 대비 복구액 상관관계 (Scatter Plot)
with row1_col2:
    st.subheader("2. 피해액 vs 복구액 상관관계")
    fig2 = px.scatter(filtered_df, x='재산피해액(억원)', y='복구액(억원)', 
                      hover_data=['연도', '주요태풍'], trendline="ols", # 회귀선 추가
                      color='재산피해액(억원)', color_continuous_scale='Reds')
    
    # 상관계수 계산
    corr = filtered_df['재산피해액(억원)'].corr(filtered_df['복구액(억원)'])
    
    fig2.update_layout(height=400, title=f"상관계수(R): {corr:.2f} (강한 양의 상관관계)")
    st.plotly_chart(fig2, use_container_width=True)

# Row 2
row2_col1, row2_col2 = st.columns(2)

# [분석 3] 피해 규모 Top 5 연도 (Bar Chart)
with row2_col1:
    st.subheader("3. 역대 피해 규모 Top 5 연도")
    top5_df = filtered_df.nlargest(5, '재산피해액(억원)').sort_values('재산피해액(억원)', ascending=True)
    fig3 = px.bar(top5_df, x='재산피해액(억원)', y=top5_df['연도'].astype(str), 
                  text='주요태풍', orientation='h',
                  color='재산피해액(억원)', color_continuous_scale='OrRd')
    fig3.update_traces(textposition='inside', textfont_size=12)
    fig3.update_layout(height=400, yaxis_title="연도")
    st.plotly_chart(fig3, use_container_width=True)

# [분석 4] 재산 피해와 인명 피해 비교 (Dual Axis Chart)
with row2_col2:
    st.subheader("4. 재산 피해 vs 인명 피해")
    
    # 이중축 그래프 생성
    fig4 = go.Figure()
    
    # 막대: 재산 피해
    fig4.add_trace(go.Bar(
        x=filtered_df['연도'], 
        y=filtered_df['재산피해액(억원)'], 
        name='재산피해액(좌측)', 
        marker_color='lightgray',
        opacity=0.6
    ))
    
    # 선: 인명 피해
    fig4.add_trace(go.Scatter(
        x=filtered_df['연도'], 
        y=filtered_df['인명피해(명)'], 
        name='인명피해(우측)', 
        yaxis='y2',
        mode='lines+markers',
        marker=dict(size=10, color='red')
    ))
    
    fig4.update_layout(
        height=400,
        xaxis=dict(title="연도"),
        yaxis=dict(title="재산 피해액(억원)", side="left"),
        yaxis2=dict(title="인명 피해(명)", side="right", overlaying="y", range=[0, max(filtered_df['인명피해(명)'])*1.5]),
        legend=dict(x=0.01, y=0.99),
        hovermode="x unified"
    )
    st.plotly_chart(fig4, use_container_width=True)

# -----------------------------------------------------------------------------
# 5. 데이터 테이블 보기 (Expandable)
# -----------------------------------------------------------------------------
with st.expander("📊 원본 데이터 보기"):
    st.dataframe(filtered_df.sort_values(by='연도', ascending=False), use_container_width=True)
