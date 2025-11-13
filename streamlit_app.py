import streamlit as st
import pandas as pd
import numpy as np
import io

# Try to import Altair for nicer charts; fall back gracefully if unavailable
try:
    import altair as alt
except Exception:
    alt = None

st.set_page_config(page_title="성적 시각화 앱", layout="wide")

st.title("📊 성적 시각화 앱")
st.write("CSV로 성적 데이터를 업로드하면 기초 통계와 여러 차트를 자동으로 생성합니다.")

# CSV 파일 업로드
st.header("1️⃣ CSV 파일 업로드")
uploaded_csv = st.file_uploader("성적 CSV 파일 선택", type=["csv"], accept_multiple_files=False)

if uploaded_csv is not None:
    # CSV 파일 읽기
    try:
        bytes_data = uploaded_csv.getvalue()
        df = pd.read_csv(io.BytesIO(bytes_data))
    except Exception as e:
        st.error(f"CSV를 읽는 중 오류가 발생했습니다: {e}")
        st.stop()

    # 데이터 미리보기
    st.subheader("📋 데이터 미리보기")
    st.write(f"**파일명:** {uploaded_csv.name} | **행 수:** {len(df)} | **열 수:** {len(df.columns)}")
    st.dataframe(df.head(10))

    # 숫자형 컬럼 감지
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # 숫자형 컬럼이 없으면 사용자가 선택
    if not numeric_cols:
        st.warning("⚠️ 숫자형 컬럼이 감지되지 않았습니다. 점수로 사용할 컬럼을 선택하세요.")
        all_cols = df.columns.tolist()
        select_cols = st.multiselect("점수 컬럼 선택 (강제 변환)", all_cols)
        if select_cols:
            for c in select_cols:
                df[c] = pd.to_numeric(df[c], errors='coerce')
            numeric_cols = [c for c in select_cols if pd.api.types.is_numeric_dtype(df[c])]
    else:
        select_cols = st.multiselect("시각화할 숫자 컬럼 선택", numeric_cols, default=numeric_cols)

    if not select_cols:
        st.info("ℹ️ 시각화할 숫자 컬럼을 선택해주세요.")
        st.stop()

    # 데이터 전처리
    proc_df = df.copy()
    proc_df = proc_df.dropna(subset=select_cols, how='all')

    # 기초 통계
    st.header("2️⃣ 기초 통계")
    stats = proc_df[select_cols].describe().T
    stats = stats[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
    st.table(stats.round(2))

    # 학생별 평균 (이름 컬럼이 있을 경우)
    name_col = None
    for candidate in ['name', 'Name', '학생', 'student', 'Student', 'NAME']:
        if candidate in proc_df.columns:
            name_col = candidate
            break

    if name_col:
        proc_df['평균'] = proc_df[select_cols].mean(axis=1)
        st.subheader("👥 학생별 평균 점수")
        st.dataframe(proc_df[[name_col, '평균']].round(2))

    # 차트 섹션
    st.header("3️⃣ 시각화")
    st.write("각 차트명을 클릭하여 펼친 후 변수를 선택하면 맞춤형 그래프를 생성합니다.")

    # ===== 1. 히스토그램 =====
    with st.expander("📊 히스토그램 (Histogram)"):
        col1, col2 = st.columns(2)
        with col1:
            hist_col = st.selectbox("히스토그램 변수 선택", select_cols, key="hist_var")
        with col2:
            hist_bins = st.slider("Bin 수", 5, 50, 20, key="hist_bins")
        
        if hist_col:
            hist_data = proc_df[[hist_col]].dropna()
            if len(hist_data) > 0:
                if alt is not None:
                    hist = alt.Chart(hist_data).mark_bar().encode(
                        alt.X(f'{hist_col}:Q', bin=alt.Bin(maxbins=hist_bins), title=hist_col),
                        y='count():Q',
                        tooltip=[f'{hist_col}:Q', 'count():Q']
                    ).properties(title=f"{hist_col} 분포 (히스토그램)", width=700, height=400)
                    st.altair_chart(hist, use_container_width=True)
                else:
                    st.write(f"📈 {hist_col} 히스토그램")
                    st.bar_chart(pd.cut(hist_data[hist_col], bins=hist_bins).value_counts().sort_index())
            else:
                st.warning(f"⚠️ {hist_col}에 유효한 데이터가 없습니다.")

    # ===== 2. 막대그래프 =====
    with st.expander("📈 막대그래프 (Bar Chart)"):
        col1, col2 = st.columns(2)
        with col1:
            bar_col = st.selectbox("막대그래프 변수 선택", select_cols, key="bar_var")
        with col2:
            bar_agg = st.radio("집계 방식", ["평균", "합계", "최댓값", "최솟값"], horizontal=True, key="bar_agg")
        
        if bar_col:
            agg_map = {"평균": "mean", "합계": "sum", "최댓값": "max", "최솟값": "min"}
            agg_func = agg_map[bar_agg]
            bar_value = proc_df[bar_col].agg(agg_func)
            
            if alt is not None:
                bar_df = pd.DataFrame({
                    '변수': [bar_col],
                    '값': [bar_value]
                })
                bar = alt.Chart(bar_df).mark_bar(color='steelblue').encode(
                    x=alt.X('변수:N', title=''),
                    y=alt.Y('값:Q', title=bar_agg),
                    tooltip=['변수:N', '값:Q']
                ).properties(title=f"{bar_col} - {bar_agg}", width=500, height=400)
                st.altair_chart(bar, use_container_width=True)
            else:
                st.metric(f"{bar_col} ({bar_agg})", f"{bar_value:.2f}")

    # ===== 3. 산점도 =====
    with st.expander("🔵 산점도 (Scatter Plot)"):
        col1, col2 = st.columns(2)
        with col1:
            scatter_x = st.selectbox("X축 변수 선택", select_cols, key="scatter_x")
        with col2:
            scatter_y = st.selectbox("Y축 변수 선택", select_cols, 
                                    index=min(1, len(select_cols)-1), key="scatter_y")
        
        if scatter_x and scatter_y:
            scatter_data = proc_df[[scatter_x, scatter_y]].dropna()
            if len(scatter_data) > 0:
                if alt is not None:
                    scatter = alt.Chart(scatter_data).mark_circle(size=100).encode(
                        x=alt.X(f'{scatter_x}:Q', title=scatter_x),
                        y=alt.Y(f'{scatter_y}:Q', title=scatter_y),
                        tooltip=[scatter_x, scatter_y]
                    ).properties(title=f"{scatter_x} vs {scatter_y}", width=700, height=400)
                    st.altair_chart(scatter, use_container_width=True)
                else:
                    st.write(f"🔵 {scatter_x} vs {scatter_y}")
                    st.dataframe(scatter_data)
            else:
                st.warning(f"⚠️ 유효한 데이터가 없습니다.")

    # ===== 4. 상자 그림 =====
    with st.expander("📦 상자 그림 (Box Plot)"):
        box_col = st.selectbox("상자 그림 변수 선택", select_cols, key="box_var")
        
        if box_col:
            box_data = proc_df[[box_col]].dropna()
            if len(box_data) > 0:
                if alt is not None:
                    box = alt.Chart(box_data).mark_boxplot(extent='min-max').encode(
                        y=alt.Y(f'{box_col}:Q', title=box_col),
                        tooltip=[f'{box_col}:Q']
                    ).properties(title=f"{box_col} 분포 (상자 그림)", width=400, height=400)
                    st.altair_chart(box, use_container_width=True)
                else:
                    st.write(f"📦 {box_col} 통계")
                    st.dataframe(box_data.describe().round(2))
            else:
                st.warning(f"⚠️ {box_col}에 유효한 데이터가 없습니다.")

    # 데이터 다운로드
    st.header("4️⃣ 데이터 다운로드")
    csv = proc_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 처리된 CSV 다운로드",
        data=csv,
        file_name=f"processed_{uploaded_csv.name}",
        mime='text/csv'
    )

else:
    st.info("📁 위에서 성적 CSV 파일을 선택해주세요.\n예시 파일 포맷: `name, math, english, science, history`")
