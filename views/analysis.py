import runpy
from pathlib import Path

import streamlit as st

# 질문 8개를 이 탭 안의 하위 탭으로 보여준다 (각 파일은 기존 그대로 실행)
SUB = [
    ("🥇 폴포지션", "q1_pole.py"), ("🏆 최강팀", "q2_teams.py"), ("🐐 GOAT", "q3_goat.py"),
    ("💥 리타이어", "q4_dnf.py"), ("🗺️ 서킷", "q5_circuits.py"), ("🎂 나이", "q6_age.py"),
    ("🌧️ 날씨", "q7_rain.py"), ("🛞 타이어", "q8_tyre.py"),
]
here = Path(__file__).parent
for tab, (_, f) in zip(st.tabs([n for n, _ in SUB]), SUB):
    with tab:
        runpy.run_path(str(here / f))
