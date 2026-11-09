import streamlit as st

from ui import style

st.set_page_config(page_title="F1 대시보드", page_icon="🏁", layout="wide")

pages = [
    st.Page("views/home.py", title="최신", icon="🏁", default=True),
    st.Page("views/archive.py", title="기록", icon="📚"),
    st.Page("views/q1_pole.py", title="폴포지션", icon="🥇"),
    st.Page("views/q2_teams.py", title="최강팀", icon="🏆"),
    st.Page("views/q3_goat.py", title="GOAT", icon="🐐"),
    st.Page("views/q4_dnf.py", title="리타이어", icon="💥"),
    st.Page("views/q5_circuits.py", title="서킷", icon="🗺️"),
    st.Page("views/q6_age.py", title="나이", icon="🎂"),
    st.Page("views/q7_rain.py", title="날씨", icon="🌧️"),
    st.Page("views/q8_tyre.py", title="타이어", icon="🛞"),
]
style()
st.navigation(pages, position="top").run()
