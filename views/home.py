import plotly.express as px
import streamlit as st

from data_loader import load
from ui import BLUE, show, table

d = load()
R, races = d["R"], d["races"]
last = races[races["raceId"].isin(R["raceId"])].sort_values("date").iloc[-1]
rid = last["raceId"]
rr = R[R["raceId"] == rid].sort_values("positionOrder")
circ = d["circuits"].set_index("circuitId").loc[last["circuitId"]]

st.title(f"🏁 {last['name']}")
st.caption(f"{last['date']:%Y-%m-%d} · {circ['name']} ({circ['location']}, {circ['country']}) · {int(last['year'])}시즌 {int(last['round'])}라운드 — 데이터가 있는 가장 최근 레이스")

w = rr.iloc[0]
pole = rr[rr["grid"] == 1]
fl = rr[rr["rank"] == 1]
c = st.columns([1.1, 1.1, 1.6, 0.8, 0.8])
off = dict(delta_color="off", delta_arrow="off")  # 보조 문구를 카드 안에 넣되 화살표는 숨김
c[0].metric("우승", w["driver"], w["team"], **off)
c[1].metric("폴포지션", pole.iloc[0]["driver"] if len(pole) else "-", pole.iloc[0]["team"] if len(pole) else None, **off)
c[2].metric("최속 랩", fl.iloc[0]["driver"] if len(fl) else "-",
            f"{fl.iloc[0]['fastestLapTime']} · {fl.iloc[0]['team']}" if len(fl) else None, **off)
c[3].metric("완주 / 출발", f"{int(rr['classified'].sum())} / {int(rr['started'].sum())}", f"리타이어 {int(rr['dnf'].sum())}명", **off)
c[4].metric("폴 → 우승", "예" if len(pole) and pole.iloc[0]["driverId"] == w["driverId"] else "아니오", f"우승자 {int(w['grid'])}번 출발", **off)

st.subheader("레이스 결과")
out = rr[["positionText", "driver", "team", "grid", "laps", "time", "points", "status"]].copy()
out["grid"] = out["grid"].replace(0, "피트")
out.columns = ["순위", "드라이버", "팀", "출발", "랩", "기록", "포인트", "상태"]
table(out)

st.subheader(f"이 레이스 직후 챔피언십 순위 ({int(last['year'])})")
a, b = st.columns(2)
ds = d["ds"][d["ds"]["raceId"] == rid].sort_values("position").head(10)
fig = px.bar(ds, x="points", y="driver", orientation="h", text="points", color_discrete_sequence=[BLUE])
fig.update_yaxes(autorange="reversed", title="")
fig.update_xaxes(title="포인트")
a.markdown("**드라이버 상위 10**")
with a:
    show(fig)
cs = d["cs"][d["cs"]["raceId"] == rid].sort_values("position").head(10)
fig = px.bar(cs, x="points", y="team", orientation="h", text="points", color_discrete_sequence=[BLUE])
fig.update_yaxes(autorange="reversed", title="")
fig.update_xaxes(title="포인트")
b.markdown("**팀 상위 10**")
with b:
    show(fig)
