import plotly.express as px
import streamlit as st

from data_loader import load
from ui import BLUE, COLORS, ORANGE, show

R = load()["R"]
S = R[R["started"] & (R["grid"] >= 1)].copy()
S["win"] = S["position"] == 1

by = S[S["grid"] <= 10].groupby("grid")["win"].agg(["mean", "count"]).reset_index()
pole = by.iloc[0]
dec = (S[S["grid"].isin([1, 2])].groupby(["decade", "grid"])["win"].agg(["mean", "count"]).reset_index())
dec["출발"] = dec["grid"].map({1: "폴포지션(1번)", 2: "2번 출발"})
d_pole = dec[dec["grid"] == 1].set_index("decade")["mean"]

st.title("🥇 폴포지션이면 우승하나?")
st.info(f"1번 출발자의 우승 비율은 전체 평균 **{pole['mean']:.0%}** ({int(pole['count']):,}번 출발 중). "
        f"시대별로는 {d_pole.index[0]} **{d_pole.iloc[0]:.0%}** → {d_pole.index[-1]} **{d_pole.iloc[-1]:.0%}** 입니다.")

st.subheader("출발 순위별 우승 확률 (1~10번)")
by["text"] = by.apply(lambda r: f"{r['mean']:.1%}<br>{int(r['count'])}회", axis=1)
fig = px.bar(by, x="grid", y=by["mean"] * 100, text="text", color_discrete_sequence=[BLUE])
fig.update_traces(textposition="outside", cliponaxis=False)
fig.update_xaxes(title="출발 순위", dtick=1)
fig.update_yaxes(title="우승 확률(%)", ticksuffix="%", range=[0, by["mean"].max() * 100 * 1.25])
show(fig)

st.subheader("시대별: 폴포지션과 2번 출발의 우승 확률")
fig = px.line(dec, x="decade", y=dec["mean"] * 100, color="출발", markers=True,
              color_discrete_sequence=[BLUE, ORANGE], custom_data=["count"])
fig.update_traces(hovertemplate="%{x}: %{y:.1f}% (n=%{customdata[0]})")
fig.update_xaxes(title="연대")
fig.update_yaxes(title="우승 확률(%)", ticksuffix="%", rangemode="tozero")
show(fig)
st.caption("출발 순위 0(피트레인 출발·기록 없음)은 제외했습니다. 2020s는 진행 중인 시즌이 포함됩니다. 한 레이스에서 한 명만 우승하므로 모든 순위의 확률 합은 100%입니다.")
