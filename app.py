import streamlit as st

from ui import header, style

st.set_page_config(page_title="F1 대시보드", page_icon="🏁", layout="wide")

pages = [
    st.Page("views/home.py", title="최신", icon="🏁", default=True),
    st.Page("views/archive.py", title="기록", icon="📚"),
    st.Page("views/analysis.py", title="분석", icon="🔎"),  # 질문 8개가 하위 탭으로 들어 있음
]
pg = st.navigation(pages, position="hidden")  # 기본 탭 바는 숨기고 F1 아래에 직접 그림
style()
header()
with st.container(horizontal=True, gap="small", key="tabbar"):
    for p in pages:
        st.page_link(p, width="content")
pg.run()
