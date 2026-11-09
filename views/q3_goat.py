import plotly.express as px
import streamlit as st

from data_loader import load
from ui import BLUE, ORANGE, show, table

d = load()
R, ds, fin, ymax = d["R"], d["ds"], d["fin"], d["ymax"]
S = R[R["started"]]

g = S.groupby(["driverId", "driver"]).agg(
    출전=("raceId", "size"), 우승=("position", lambda s: int((s == 1).sum())),
    포디움=("position", lambda s: int((s <= 3).sum())),
    폴=("grid", lambda s: int((s == 1).sum())), 포인트=("points", "sum")).reset_index()
tit = ds.merge(fin, on="raceId").query("position == 1 and year < @ymax").groupby("driverId").size()
g["챔피언"] = g["driverId"].map(tit).fillna(0).astype(int)
g["승률%"] = (g["우승"] / g["출전"] * 100).round(1)

st.title("🐐 역대 최고 드라이버는?")
min_s = st.slider("최소 출전 수 (이보다 적게 뛴 선수는 비율이 왜곡되므로 제외)", 0, 300, 50, 10)
metric = st.selectbox("비교 기준", ["우승", "포디움", "챔피언", "폴", "승률%", "포인트"])
G = g[g["출전"] >= min_s].sort_values(metric, ascending=False)
top = G.iloc[0]
st.info(f"출전 {min_s}회 이상 중 **{metric}** 1위는 **{top['driver']}** ({top[metric]:g}). "
        f"기준을 바꾸면 순위가 달라집니다 — 한 가지 기준으로 '최고'를 정하기 어렵습니다.")

t15 = G.head(15)
fig = px.bar(t15, x=metric, y="driver", orientation="h", text=metric, color_discrete_sequence=[BLUE])
fig.update_yaxes(autorange="reversed", title="")
show(fig, 480)

st.subheader("출전 수 대비 우승")
fig = px.scatter(G, x="출전", y="우승", hover_name="driver", hover_data=["포디움", "챔피언"], color_discrete_sequence=[BLUE])
fig.update_traces(marker=dict(size=8, line=dict(width=1.5, color="white")))
lab = G.nlargest(8, "우승")
for _, r in lab.iterrows():
    fig.add_annotation(x=r["출전"], y=r["우승"], text=r["driver"], showarrow=False, yshift=12, font=dict(size=11))
show(fig, 430)
with st.expander("표로 보기"):
    table(G[["driver", "출전", "우승", "포디움", "폴", "챔피언", "승률%", "포인트"]].rename(columns={"driver": "드라이버"}))
st.caption("공동으로 차를 나눠 타던 초창기(1950~60년대) 기록은 한 레이스에 같은 차로 두 명이 올라 있을 수 있습니다. 챔피언은 시즌이 끝난 해만 셉니다.")
