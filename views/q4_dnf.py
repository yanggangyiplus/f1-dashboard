import plotly.express as px
import streamlit as st

from data_loader import load
from ui import BLUE, COLORS, GRAY, ORANGE, show

R = load()["R"]
S = R[R["started"]].copy()
CRASH = {"Accident", "Collision", "Spun off", "Collision damage"}
OTHER = {"Retired", "Not classified", "Disqualified", "Excluded", "Illness", "Driver unwell", "Injured", "Safety concerns", "Safety", "Fatal accident"}
S["사유"] = S["status"].map(lambda s: "사고·충돌" if s in CRASH else "기타" if s in OTHER else "기계·부품")

yr = S.groupby("year")["dnf"].mean().reset_index()
dc = S.groupby("decade")["dnf"].mean()
D = S[S["dnf"]].groupby(["decade", "사유"]).size().reset_index(name="n")
D["비율"] = D["n"] / D.groupby("decade")["n"].transform("sum") * 100

st.title("💥 리타이어는 얼마나, 왜 일어나나?")
st.info(f"리타이어 비율은 {dc.index[0]} **{dc.iloc[0]:.0%}** → {dc.index[-1]} **{dc.iloc[-1]:.0%}** 로 줄었습니다.")

st.subheader("연도별 리타이어 비율")
fig = px.line(yr, x="year", y=yr["dnf"] * 100, color_discrete_sequence=[BLUE])
fig.update_xaxes(title="연도")
fig.update_yaxes(title="출발 대비 리타이어(%)", ticksuffix="%", rangemode="tozero")
show(fig)

st.subheader("리타이어 사유 구성 (연대별)")
fig = px.bar(D, x="decade", y="비율", color="사유", color_discrete_map={"기계·부품": BLUE, "사고·충돌": ORANGE, "기타": GRAY},
             category_orders={"사유": ["기계·부품", "사고·충돌", "기타"]})
fig.update_xaxes(title="연대")
fig.update_yaxes(title="리타이어 중 비율(%)", ticksuffix="%")
show(fig)

st.subheader("가장 흔한 리타이어 사유 (상위 10)")
t = S[S["dnf"]]["status"].value_counts().head(10).reset_index()
t.columns = ["사유", "건수"]
fig = px.bar(t, x="건수", y="사유", orientation="h", text="건수", color_discrete_sequence=[BLUE])
fig.update_yaxes(autorange="reversed", title="")
show(fig)
st.caption("리타이어 = 레이스를 출발했으나 'R'(Retired)로 기록된 경우. 예선 탈락·불참·실격은 제외했습니다. "
           "사유 분류(기계·부품 / 사고·충돌 / 기타)는 status 이름을 키워드로 묶은 근사치입니다.")
