import pandas as pd
import plotly.express as px
import streamlit as st

from data_loader import load
from ui import BLUE, ORANGE, show, table

R = load()["R"]
S = R[R["started"] & R["dob"].notna()].copy()
S["나이"] = (S["date"] - S["dob"]).dt.days / 365.25
W = S[S["position"] == 1].drop_duplicates(["raceId", "driverId"])

bins = [0, 20, 25, 30, 35, 40, 100]
labels = ["~19", "20~24", "25~29", "30~34", "35~39", "40+"]
S["연령대"] = pd.cut(S["나이"], bins=bins, labels=labels, right=False)
rate = S.groupby("연령대", observed=True)["position"].agg(starts="size", wins=lambda s: int((s == 1).sum())).reset_index()
rate["승률"] = rate["wins"] / rate["starts"] * 100
best = rate.loc[rate["승률"].idxmax()]
young, old = W.nsmallest(1, "나이").iloc[0], W.nlargest(1, "나이").iloc[0]

st.title("🎂 몇 살에 가장 잘 이기나?")
st.info(f"우승 나이의 중앙값은 **{W['나이'].median():.1f}세**, 출전 대비 우승 비율이 가장 높은 연령대는 **{best['연령대']}세**({best['승률']:.1f}%)입니다. "
        f"최연소 우승은 {young['driver']}({young['나이']:.1f}세), 최고령은 {old['driver']}({old['나이']:.1f}세).")

st.subheader("우승 당시 나이 분포")
fig = px.histogram(W, x="나이", nbins=40, color_discrete_sequence=[BLUE])
fig.update_xaxes(title="우승 당시 나이(세)")
fig.update_yaxes(title="우승 수")
show(fig)

st.subheader("연령대별 우승 확률 (출전 대비)")
rate["text"] = rate.apply(lambda r: f"{r['승률']:.1f}%<br>{int(r['starts']):,}출전", axis=1)
fig = px.bar(rate, x="연령대", y="승률", text="text", color_discrete_sequence=[BLUE])
fig.update_traces(textposition="outside", cliponaxis=False)
fig.update_xaxes(title="출전 당시 나이")
fig.update_yaxes(title="우승 확률(%)", ticksuffix="%", range=[0, rate["승률"].max() * 1.25])
show(fig)

a, b = st.columns(2)
cols = ["driver", "나이", "race", "year"]
ren = {"driver": "드라이버", "race": "레이스", "year": "연도"}
a.markdown("**최연소 우승 5**")
with a:
    table(W.nsmallest(5, "나이")[cols].round({"나이": 1}).rename(columns=ren))
b.markdown("**최고령 우승 5**")
with b:
    table(W.nlargest(5, "나이")[cols].round({"나이": 1}).rename(columns=ren))
st.caption("생년월일이 기록된 드라이버만 포함합니다(전체의 약 98%). 나이는 레이스 날짜 − 생년월일입니다.")
