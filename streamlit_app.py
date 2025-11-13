import streamlit as st
import pandas as pd
import numpy as np

st.title("🎈 My new app")
st.write("Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/).")

st.header("1. Basic text elements")
st.write("이것은 일반 텍스트일까요. ¹")
st.markdown("**Markdown** 예시 — 굵은 글씨와 링크 사용 가능. ²")
st.caption("보조 설명(캡션) 예시. ³")

st.header("2. Layout & Widgets")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("이름을 입력하세요", value="사용자")
    st.write(f"안녕하세요, {name}! ⁴")
    agree = st.checkbox("동의합니다")
with col2:
    option = st.selectbox("옵션 선택", ["옵션 A", "옵션 B", "옵션 C"])
    st.metric("온도", "20 °C", delta="+1.2 °C")

st.header("3. Interactive widgets")
age = st.slider("나이", 0, 100, 30)
st.write(f"선택한 나이: {age} ⁵")
choice = st.radio("하나 선택", ["첫번째", "두번째"]) 
multi = st.multiselect("여러 개 선택", ["사과", "바나나", "체리"], ["사과"]) 
st.write("선택 결과:", choice, multi)

st.header("4. Data display")
df = pd.DataFrame(np.random.randn(10, 3), columns=["a", "b", "c"])
st.dataframe(df)
st.table(df.describe())

st.header("5. Charts")
st.line_chart(df)
st.bar_chart(df['a'].abs())

st.header("6. Media & File upload")
uploaded = st.file_uploader("파일 업로드")
if uploaded:
    st.write("업로드된 파일:", uploaded.name)
st.image("https://static.streamlit.io/examples/dice.jpg", caption="샘플 이미지 (외부 URL) ¹⁰")

st.header("7. Extras")
with st.expander("펼치기 (Expander)"):
    st.write("숨겨진 내용 예시. ¹¹")
code = """def hello():
    print('hello')
"""
st.code(code, language='python')
progress = st.progress(0)
for i in range(100):
    progress.progress(i + 1)

st.markdown("---")
st.markdown(
    "¹ 일반 텍스트 — 간단한 문장 표시\n"
    "² Markdown — 굵은 글씨, 링크, 리스트 등 사용 가능\n"
    "³ Caption — 보조 설명 텍스트\n"
    "⁴ Text input — 사용자 입력을 받아 화면에 반영\n"
    "⁵ Slider — 범위 입력에 적합, 수치 선택 용도\n"
    "⁶ Dataframe / Table — 표 형식 데이터 표시\n"
    "⁷ Line chart — 연속형/시계열 데이터 시각화\n"
    "⁸ Bar chart — 범주형 데이터 시각화\n"
    "⁹ File uploader — 사용자 파일 업로드 처리\n"
    "¹⁰ Image — 이미지 표시 (로컬 또는 URL)\n"
    "¹¹ Expander — 접기/펼치기 컨테이너\n"
    "¹² Code — 코드 블록 하이라이팅\n"
)
