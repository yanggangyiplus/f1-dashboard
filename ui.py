import streamlit as st

# 검증된 기본 범주 팔레트(라이트): 파랑, 주황, 청록, 노랑, 분홍, 초록, 보라, 빨강
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
BLUE, ORANGE, GRAY = COLORS[0], COLORS[1], "#9a9a96"

CSS = """
<style>
.stApp::before {content:""; position:fixed; top:0; left:0; right:0; height:3px; background:#e10600; z-index:999999;}
.block-container {padding-top:2.4rem; max-width:1240px;}
h1 {font-weight:800 !important; letter-spacing:-0.02em;}
h3 {margin-top:1.8rem !important; font-weight:700 !important;}
[data-testid="stMetric"] {background:rgba(128,128,128,.08); border:1px solid rgba(128,128,128,.22);
    border-radius:14px; padding:14px 18px;}
[data-testid="stMetricValue"] {font-size:1.55rem; font-weight:700;}
[data-testid="stMetricLabel"] p {font-size:.8rem; letter-spacing:.04em; opacity:.7;}
[data-testid="stAlert"] {border:none; border-left:4px solid #2a78d6; border-radius:12px; background:rgba(42,120,214,.10);}
[data-testid="stDataFrame"] {border-radius:12px; overflow:hidden;}
[data-testid="stCaptionContainer"] {opacity:.75;}
</style>
"""


def style():
    st.markdown(CSS, unsafe_allow_html=True)


def show(fig, height=380):
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10), height=height, legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        barcornerradius=4, bargap=0.25, font=dict(size=13), hoverlabel=dict(font_size=13),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.18)", zeroline=False)
    st.plotly_chart(fig, width="stretch")


def table(df, **kw):
    st.dataframe(df, hide_index=True, width="stretch", **kw)
