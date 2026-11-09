import plotly.express as px
import streamlit as st

from data_loader import load
from ui import BLUE, show, table

d = load()
R, races, ds, cs, fin = d["R"], d["races"], d["ds"], d["cs"], d["fin"]
st.title("📚 기록")
st.caption("1950년부터 지금까지의 모든 레이스 결과를 연도와 레이스로 찾아봅니다.")

has = races[races["raceId"].isin(R["raceId"])]
year = st.selectbox("연도", sorted(has["year"].unique(), reverse=True))
ry = has[has["year"] == year].sort_values("round")
label = ry.apply(lambda r: f"{int(r['round'])}R · {r['name']} ({r['date']:%m-%d})", axis=1)
pick = st.selectbox("레이스", label.tolist(), index=len(ry) - 1)
race = ry.iloc[label.tolist().index(pick)]

rr = R[R["raceId"] == race["raceId"]].sort_values("positionOrder")
st.subheader(f"{race['name']} {int(year)} 결과")
out = rr[["positionText", "driver", "team", "grid", "laps", "time", "points", "status"]].copy()
out.columns = ["순위", "드라이버", "팀", "출발", "랩", "기록", "포인트", "상태"]
table(out)

last_id = ry.iloc[-1]["raceId"]
st.subheader(f"{int(year)} 시즌 순위 (마지막으로 기록된 라운드 기준)")
a, b = st.columns(2)
s1 = ds[ds["raceId"] == last_id].sort_values("position").head(10)[["position", "driver", "points", "wins"]]
s1.columns = ["순위", "드라이버", "포인트", "우승"]
a.markdown("**드라이버**")
with a:
    table(s1)
s2 = cs[cs["raceId"] == last_id].sort_values("position")[["position", "team", "points", "wins"]]
s2.columns = ["순위", "팀", "포인트", "우승"]
b.markdown("**팀**" if len(s2) else "**팀** (이 해는 팀 순위가 없습니다)")
if len(s2):
    with b:
        table(s2)

st.subheader("드라이버 찾기")
S = R[R["started"]]
names = sorted(S["driver"].unique())
default = names.index("Max Verstappen") if "Max Verstappen" in names else 0
who = st.selectbox("드라이버 (이름을 입력해 검색)", names, index=default)
m = S[S["driver"] == who]
ids, ymax = m["driverId"].unique(), d["ymax"]
champ = ds.merge(fin, on="raceId").query("position == 1 and driverId in @ids and year < @ymax")
c = st.columns(5)
c[0].metric("활동 시즌", f"{int(m['year'].min())}–{int(m['year'].max())}")
c[1].metric("출전", len(m))
c[2].metric("우승", int((m["position"] == 1).sum()))
c[3].metric("포디움", int((m["position"] <= 3).sum()))
c[4].metric("챔피언", len(champ))
wy = m.groupby("year")["points"].sum().reset_index()
fig = px.bar(wy, x="year", y="points", color_discrete_sequence=[BLUE])
fig.update_xaxes(title="연도")
fig.update_yaxes(title="시즌 포인트(합)")
show(fig, 300)
