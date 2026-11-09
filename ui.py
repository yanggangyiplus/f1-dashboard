import streamlit as st

# 검증된 기본 범주 팔레트(라이트): 파랑, 주황, 청록, 노랑, 분홍, 초록, 보라, 빨강
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
BLUE, ORANGE, GRAY = COLORS[0], COLORS[1], "#9a9a96"


def show(fig, height=380):
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=height, legend_title_text="")
    st.plotly_chart(fig, width="stretch")


def table(df, **kw):
    st.dataframe(df, hide_index=True, width="stretch", **kw)
