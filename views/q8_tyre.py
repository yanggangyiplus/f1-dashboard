import plotly.express as px
import streamlit as st

from data_loader import load
from ui import BLUE, COLORS, GRAY, show

d = load()
R, t = d["R"], d["tyre"].dropna(subset=["compound"])
cmap = {"SOFT": COLORS[7], "MEDIUM": COLORS[3], "HARD": GRAY, "INTERMEDIATE": COLORS[5]}
order = ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE"]

cp = t.groupby("compound").agg(스틴트=("stint", "size"), 평균랩=("lapsOnTire", "mean")).reindex(order).reset_index()
cp["평균랩"] = cp["평균랩"].round(1)

per = t.groupby(["raceId", "driverId"]).agg(스틴트수=("stint", "max"), 시작=("compound", "first")).reset_index()
P = per.merge(R[["raceId", "driverId", "grid", "position", "classified"]], on=["raceId", "driverId"])
P = P[P["classified"] & (P["grid"] >= 1)].assign(정차=lambda x: x["스틴트수"] - 1, 득실=lambda x: x["grid"] - x["position"])
stops = P[P["정차"].between(0, 4)].groupby("정차").agg(n=("position", "size"), 평균순위=("position", "mean"), 포디움=("position", lambda s: (s <= 3).mean() * 100)).reset_index()
start = P.groupby("시작").agg(n=("position", "size"), 득실=("득실", "mean")).reindex(order).dropna().reset_index()

st.title("🛞 타이어 전략은 결과를 바꾸나?")
st.warning(f"타이어 데이터는 **{t['raceId'].nunique()}개 레이스**(2025~2026 시즌의 일부)뿐입니다. 아래는 상관관계이고 전략의 효과를 증명하지 않습니다.")
longest = cp.loc[cp["평균랩"].idxmax()]
st.info(f"스틴트가 가장 긴 타이어는 **{longest['compound']}** (평균 {longest['평균랩']}랩), "
        f"가장 많이 쓴 타이어는 **{cp.loc[cp['스틴트'].idxmax(), 'compound']}** ({int(cp['스틴트'].max())}스틴트)입니다.")

a, b = st.columns(2)
fig = px.bar(cp, x="compound", y="평균랩", text="평균랩", color="compound", color_discrete_map=cmap, category_orders={"compound": order})
fig.update_layout(showlegend=False)
fig.update_xaxes(title="타이어 종류")
fig.update_yaxes(title="스틴트 평균 길이(랩)")
a.markdown("**타이어별 스틴트 평균 길이**")
with a:
    show(fig)
cp["text"] = cp["스틴트"].astype(int).astype(str)
fig = px.bar(cp, x="compound", y="스틴트", text="text", color="compound", color_discrete_map=cmap, category_orders={"compound": order})
fig.update_layout(showlegend=False)
fig.update_xaxes(title="타이어 종류")
fig.update_yaxes(title="스틴트 수")
b.markdown("**타이어별 사용 횟수**")
with b:
    show(fig)

st.subheader("피트스톱 횟수별 결과 (완주자)")
stops["text"] = stops.apply(lambda r: f"{r['평균순위']:.1f}위<br>{int(r['n'])}명", axis=1)
fig = px.bar(stops, x="정차", y="평균순위", text="text", color_discrete_sequence=[BLUE])
fig.update_traces(textposition="outside", cliponaxis=False)
fig.update_xaxes(title="피트스톱 횟수", dtick=1)
fig.update_yaxes(title="평균 결승 순위", range=[0, stops["평균순위"].max() * 1.25])
show(fig)

st.subheader("시작 타이어별 순위 득실 (출발 순위 − 결승 순위, +면 상승)")
start["text"] = start.apply(lambda r: f"{r['득실']:+.1f}<br>{int(r['n'])}명", axis=1)
fig = px.bar(start, x="시작", y="득실", text="text", color="시작", color_discrete_map=cmap, category_orders={"시작": order})
fig.update_traces(textposition="outside", cliponaxis=False)
fig.update_layout(showlegend=False)
fig.update_xaxes(title="시작 타이어")
fig.update_yaxes(title="평균 순위 득실(자리)")
show(fig)
st.caption("피트 횟수와 시작 타이어는 순위·팀 전력·날씨와 얽혀 있어, 이 차이를 전략의 효과로 읽으면 안 됩니다.")
