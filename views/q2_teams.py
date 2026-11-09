import pandas as pd
import plotly.express as px
import streamlit as st

from data_loader import load
from ui import BLUE, COLORS, GRAY, show, table

d = load()
R, cs, fin, ymax = d["R"], d["cs"], d["fin"], d["ymax"]

champ = cs.merge(fin, on="raceId").query("position == 1").sort_values("year")
done = champ[champ["year"] < ymax]
titles = done.groupby("team").size().sort_values(ascending=False)

W = R[R["position"] == 1].drop_duplicates(["raceId", "constructorId"])
top = W["team"].value_counts().head(7).index.tolist()
W = W.assign(팀=W["team"].where(W["team"].isin(top), "기타"))
dw = W.groupby(["decade", "팀"]).size().reset_index(name="우승")

st.title("🏆 시대별 최강팀은?")
st.info(f"팀 챔피언십({int(done['year'].min())}년~)에서 가장 많이 우승한 팀은 **{titles.index[0]}**({titles.iloc[0]}회), "
        f"그다음은 {titles.index[1]}({titles.iloc[1]}회)입니다.")

st.subheader("팀 챔피언십 우승 횟수 (상위 10)")
t = titles.head(10).reset_index()
t.columns = ["팀", "횟수"]
fig = px.bar(t, x="횟수", y="팀", orientation="h", text="횟수", color_discrete_sequence=[BLUE])
fig.update_yaxes(autorange="reversed", title="")
show(fig)

st.subheader("연대별 그랑프리 우승 수 (상위 7팀 + 기타)")
order = top + ["기타"]
cmap = {t: COLORS[i] for i, t in enumerate(top)} | {"기타": GRAY}
fig = px.bar(dw, x="decade", y="우승", color="팀", color_discrete_map=cmap, category_orders={"팀": order})
fig.update_xaxes(title="연대")
fig.update_yaxes(title="우승 수")
show(fig, 420)

st.subheader("연도별 챔피언 팀")
tab = done[["year", "team", "points"]].sort_values("year", ascending=False)
tab.columns = ["연도", "챔피언 팀", "포인트"]
table(tab, height=300)
cur = champ[champ["year"] == ymax]
if len(cur):
    st.caption(f"{ymax}년은 진행 중이라 위 표에서 제외했습니다 (현재 1위: {cur.iloc[0]['team']}).")
