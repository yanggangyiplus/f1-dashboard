import plotly.express as px
import streamlit as st

from data_loader import load
from ui import BLUE, ORANGE, show, table

d = load()
R, w, races = d["R"], d["weather"], d["races"]
S = R[R["raceId"].isin(w["raceId"])]
mv = S[S["started"] & S["classified"] & (S["grid"] >= 1)].assign(변동=lambda x: (x["grid"] - x["position"]).abs()).groupby("raceId")["변동"].mean()
dn = S[S["started"]].groupby("raceId")["dnf"].mean() * 100
m = w.assign(변동=w["raceId"].map(mv), 리타이어=w["raceId"].map(dn)).merge(races[["raceId", "name", "date", "year"]], on="raceId")
m["날씨"] = m["rainfall"].map({True: "비 옴", False: "비 안 옴"})
g = m.groupby("날씨").agg(레이스=("raceId", "size"), 변동=("변동", "mean"), 리타이어=("리타이어", "mean")).reset_index()

st.title("🌧️ 비가 오면 결과가 뒤집히나?")
st.warning(f"날씨 데이터는 **{len(w)}개 레이스**({int(m['year'].min())}~{int(m['year'].max())}, {m['date'].max():%Y-%m-%d}까지)뿐입니다. 표본이 작아서 결론이 약합니다.")
if set(g["날씨"]) == {"비 옴", "비 안 옴"}:
    r_, d_ = g.set_index("날씨").loc["비 옴"], g.set_index("날씨").loc["비 안 옴"]
    st.info(f"비 온 레이스({int(r_['레이스'])}개)는 평균 순위 변동 **{r_['변동']:.1f}자리**, 리타이어 **{r_['리타이어']:.1f}%**; "
            f"비 안 온 레이스({int(d_['레이스'])}개)는 **{d_['변동']:.1f}자리**, **{d_['리타이어']:.1f}%** 입니다.")

cmap = {"비 옴": BLUE, "비 안 옴": ORANGE}
a, b = st.columns(2)
for col, y, title, unit in [(a, "변동", "평균 순위 변동 (자리)", ""), (b, "리타이어", "리타이어 비율 (%)", "%")]:
    g["text"] = g.apply(lambda r: f"{r[y]:.1f}{unit}<br>{int(r['레이스'])}개 레이스", axis=1)
    fig = px.bar(g, x="날씨", y=y, text="text", color="날씨", color_discrete_map=cmap)
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title="")
    fig.update_yaxes(title=title, range=[0, g[y].max() * 1.3])
    col.markdown(f"**{title}**")
    with col:
        show(fig)

st.subheader("레이스별 값")
fig = px.scatter(m, x="변동", y="리타이어", color="날씨", color_discrete_map=cmap, hover_name="name", hover_data=["date"])
fig.update_traces(marker=dict(size=10, line=dict(width=1.5, color="white")))
fig.update_xaxes(title="평균 순위 변동(자리)")
fig.update_yaxes(title="리타이어 비율(%)", ticksuffix="%")
show(fig)
st.caption("순위 변동 = |출발 순위 − 결승 순위|의 평균(완주자만). 비 여부는 weather 표의 rainfall 값입니다. 상관일 뿐 원인은 아닙니다.")
