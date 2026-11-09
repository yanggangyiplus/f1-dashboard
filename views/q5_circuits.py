import plotly.express as px
import streamlit as st

from data_loader import load
from ui import BLUE, show, table

d = load()
R, circuits = d["R"], d["circuits"]

st.title("🗺️ 순위 변동이 가장 큰 서킷은?")
y0, y1 = st.slider("기간", 1950, d["ymax"], (2000, d["ymax"]))
min_r = st.slider("최소 개최 횟수", 1, 20, 5)

S = R[R["started"] & R["classified"] & (R["grid"] >= 1) & R["year"].between(y0, y1)].copy()
S["변동"] = (S["grid"] - S["position"]).abs()
g = S.groupby("circuitId").agg(개최=("raceId", "nunique"), 평균변동=("변동", "mean")).reset_index()
g = g[g["개최"] >= min_r].merge(circuits[["circuitId", "name", "location", "country", "lat", "lng"]], on="circuitId")
g["평균변동"] = g["평균변동"].round(2)
g = g.sort_values("평균변동", ascending=False)

if g.empty:
    st.warning("조건에 맞는 서킷이 없습니다. 기간을 넓히거나 최소 개최 횟수를 낮춰 보세요.")
    st.stop()
hi, lo = g.iloc[0], g.iloc[-1]
st.info(f"{y0}~{y1}년 완주자 기준, 출발 순위와 결승 순위의 차이가 가장 큰 곳은 **{hi['name']}** (평균 {hi['평균변동']}자리), "
        f"가장 작은 곳은 **{lo['name']}** ({lo['평균변동']}자리)입니다.")

a, b = st.columns(2)
for col, title, df, asc in [(a, "변동이 큰 서킷 15", g.head(15), False), (b, "변동이 작은 서킷 15", g.tail(15).iloc[::-1], True)]:
    fig = px.bar(df, x="평균변동", y="name", orientation="h", text="평균변동", color_discrete_sequence=[BLUE],
                 hover_data=["개최"])
    fig.update_yaxes(autorange="reversed", title="")
    fig.update_xaxes(title="평균 순위 변동(자리)")
    col.markdown(f"**{title}**")
    with col:
        show(fig, 460)

st.subheader("지도")
fig = px.scatter_geo(g, lat="lat", lon="lng", size="평균변동", hover_name="name",
                     hover_data=["country", "개최", "평균변동"], projection="natural earth",
                     color_discrete_sequence=[BLUE])
fig.update_traces(marker=dict(line=dict(width=1, color="white")))
show(fig, 450)
with st.expander("표로 보기"):
    table(g[["name", "country", "개최", "평균변동"]].rename(columns={"name": "서킷", "country": "나라"}))
st.caption("평균 순위 변동 = |출발 순위 − 결승 순위|의 평균(완주자만). 실제 추월 횟수가 아니라 대리 지표이고, 시대마다 출전 대수가 달라서 기간을 고정해 비교하는 것이 좋습니다.")
