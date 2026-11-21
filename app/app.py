"""Sunshine Forecast Lab - presentation dashboard.
Reads the CSV files in dashboard_data/.   Run:  python -m streamlit run app.py
"""
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(page_title="Sunshine Forecast Lab", page_icon="☀️", layout="wide",
                   initial_sidebar_state="collapsed")

# ------------------------------------------------------------------ palette (dark warm charcoal + sun)
PAGE, CARD, LINE = "#14110F", "#1E1A17", "#3A322B"
INK, SOFT, FAINT = "#F5EDE0", "#D2C5B3", "#A39581"
GOLD, ORANGE, TEAL, PLUM, GREY = "#F2B01E", "#FF7A45", "#3FB5C9", "#B091D6", "#8E857A"
GREEN = "#6CCB95"
FAMCOL = {"Bagging": TEAL, "Boosting": GOLD, "Stacking": PLUM, "Reference": GREY, "Baseline": GREY}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"], .stApp {{ font-family:'DM Sans',sans-serif; color:{INK}; font-size:17px; }}
.stApp {{ background:{PAGE}; }}
#MainMenu, footer, header {{ visibility:hidden; }}
.block-container {{ padding:2rem 3.5rem 6rem 3.5rem; max-width:1500px; }}
[data-testid="stVerticalBlock"] {{ gap:1.4rem; }}

/* hero */
.hero {{ position:relative; overflow:hidden; border-radius:16px; padding:30px 40px; margin-bottom:8px;
  background:linear-gradient(100deg,#FFE9A8 0%,#FFD166 55%,#F6A93B 100%); min-height:150px; }}
.hero svg {{ position:absolute; right:0; bottom:0; height:100%; width:55%; }}
.hero .in {{ position:relative; z-index:2; max-width:620px; }}
.hero h1 {{ font-size:36px; font-weight:700; margin:0 0 8px 0; color:#2B1A08; letter-spacing:-.02em; line-height:1.05; }}
.hero p {{ font-size:15.5px; line-height:1.55; margin:0; color:#4A3417; }}
.hero .meta {{ margin-top:12px; font-size:12.5px; font-weight:700; letter-spacing:.07em; text-transform:uppercase; color:#7A4B0B; }}

/* tab bar: full width, grouped on one background, built from the nav radio */
.st-key-nav {{ width:100%; margin:10px 0 28px 0; }}
.st-key-nav div[role="radiogroup"] {{ display:grid !important; grid-template-columns:repeat(6,minmax(0,1fr)); gap:6px !important; width:100%;
  background:{CARD}; border:1px solid {LINE}; border-radius:14px; padding:6px; box-sizing:border-box; }}
.st-key-nav label {{ position:relative; width:100%; height:46px; margin:0 !important; padding:0 8px !important; display:flex !important;
  justify-content:center; align-items:center; border-radius:12px; background:transparent !important; border:none !important; cursor:pointer; }}
.st-key-nav label > div:first-child {{ display:none !important; }}
.st-key-nav label > div {{ background:transparent !important; width:auto !important; justify-content:center; }}
.st-key-nav label p {{ font-size:15px !important; font-weight:600; color:{SOFT} !important; text-align:center; margin:0; }}
.st-key-nav label:hover {{ background:#2A231E !important; }}
.st-key-nav label:hover p {{ color:{INK} !important; }}
.st-key-nav label:has(input:checked) {{ background:{GOLD} !important; box-shadow:0 4px 14px rgba(242,176,30,.28); }}
.st-key-nav label:has(input:checked) p {{ color:#2B1A08 !important; }}

/* other controls */
div[role="radiogroup"] {{ gap:12px !important; flex-wrap:wrap; }}
.stRadio:not(.st-key-nav) label[data-baseweb="radio"] {{ background:{CARD}; border:1px solid {LINE}; border-radius:10px; padding:9px 20px !important; margin:0 !important; }}
.stRadio:not(.st-key-nav) label[data-baseweb="radio"]:has(input:checked) {{ background:{GOLD}; border-color:{GOLD}; }}
.stRadio:not(.st-key-nav) label[data-baseweb="radio"]:has(input:checked) p {{ color:#2B1A08 !important; }}
.stRadio:not(.st-key-nav) label[data-baseweb="radio"] > div:first-child {{ display:none !important; }}
.stRadio [data-testid="stWidgetLabel"] {{ margin-bottom:14px; }}
.stRadio [data-testid="stWidgetLabel"] label {{ background:transparent !important; border:none !important; padding:0 !important; }}
.stRadio label p {{ font-size:16px; font-weight:600; }}
div[data-baseweb="select"] > div {{ background:{CARD} !important; border:1px solid {LINE} !important; border-radius:10px !important; min-height:50px; font-size:16.5px; }}
label p, [data-testid="stCaptionContainer"] {{ color:{SOFT} !important; font-size:16px !important; font-weight:500; }}

/* blocks */
.h2 {{ font-size:30px; font-weight:700; margin:0 0 6px 0; letter-spacing:-.01em; }}
.sub {{ color:{SOFT}; font-size:18px; margin:0 0 24px 0; max-width:900px; line-height:1.5; }}
.gap {{ height:44px; }}
.kpis {{ display:grid; grid-template-columns:repeat(4,1fr); gap:20px; margin-bottom:12px; }}
.kpi {{ background:{CARD}; border:1px solid {LINE}; border-radius:14px; padding:16px 22px; }}
.kpi.main {{ background:#3A2A10; border-color:{GOLD}; }}
.kpi .l {{ font-size:12.5px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; color:{FAINT}; }}
.kpi .v {{ font-size:28px; font-weight:700; margin-top:4px; line-height:1.1; }}
.kpi .s {{ font-size:14px; color:{SOFT}; margin-top:4px; }}
.kpi.main .v {{ color:{GOLD}; }}
.panel {{ background:{CARD}; border:1px solid {LINE}; border-radius:16px; padding:30px 34px; }}
.panel h4 {{ margin:0 0 12px 0; font-size:22px; font-weight:700; }}
.panel p, .panel li {{ color:{SOFT}; font-size:18px; line-height:1.65; }}
.point {{ display:flex; gap:18px; padding:16px 0; border-bottom:1px solid {LINE}; font-size:18px; line-height:1.6; }}
.point:last-child {{ border-bottom:none; }}
.point .n {{ flex:0 0 auto; width:32px; height:32px; border-radius:50%; background:{GOLD}; color:#2B1A08; font-weight:700; font-size:15px; display:flex; align-items:center; justify-content:center; margin-top:2px; }}

table.t {{ width:100%; border-collapse:collapse; background:{CARD}; border:1px solid {LINE}; border-radius:16px; overflow:hidden; font-size:17px; }}
table.t th {{ text-align:left; padding:16px 20px; font-size:13.5px; letter-spacing:.06em; text-transform:uppercase; color:{FAINT}; background:#2A231E; font-weight:600; }}
table.t td {{ padding:16px 20px; border-top:1px solid {LINE}; }}
table.t tr.top td {{ background:#3A2A10; font-weight:600; }}
.num {{ font-family:'DM Mono',monospace; }}
.fam {{ display:inline-block; font-size:14px; font-weight:700; padding:4px 13px; border-radius:99px; color:#1A1208; }}
@media (max-width:1100px) {{ .kpis {{ grid-template-columns:repeat(2,1fr); }} .hero svg {{ display:none; }} .hero h1 {{ font-size:34px; }}
  .st-key-nav div[role="radiogroup"] {{ grid-template-columns:repeat(3,minmax(0,1fr)); }} }}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------ data
@st.cache_data
def load():
    d = Path(__file__).parent / "dashboard_data"
    R = pd.read_csv(d / "model_results.csv")
    P = pd.read_csv(d / "test_predictions.csv")
    P = P.rename(columns={P.columns[0]: "time"})
    P["time"] = pd.to_datetime(P["time"])
    FI = pd.read_csv(d / "feature_importance.csv", index_col=0)
    B = pd.read_csv(d / "accuracy_by_time_of_day.csv", index_col=0)
    HY = pd.read_csv(d / "hybrid_results.csv")
    return R, P, FI, B, HY


try:
    R, P, FI, B, HY = load()
except Exception as e:
    st.error("Could not load the `dashboard_data` folder next to app.py. Details: " + str(e))
    st.stop()

PCOLS = {c[2:].replace("_", " "): c for c in P.columns if c.startswith("p_")}
ENS = R[R.family.isin(["Bagging", "Boosting", "Stacking"])].sort_values("auc", ascending=False)
BEST = ENS.iloc[0]
BASE = R[R.family == "Baseline"].iloc[0]
LR = R[R.model == "Logistic Regression"].iloc[0] if (R.model == "Logistic Regression").any() else None
N_DAYS, N_ROWS = P.day.nunique(), len(P)
FAMAVG = R[R.family != "Baseline"].groupby("family")[["accuracy", "auc"]].mean()
GRID = "#2E2722"


def show(fig, h=420, legend="top"):
    leg = dict(orientation="h", bgcolor="rgba(0,0,0,0)", font=dict(size=15, color=INK))
    leg.update(dict(yanchor="bottom", y=1.04, xanchor="left", x=0) if legend == "top"
               else dict(yanchor="top", y=-0.16, xanchor="left", x=0))
    fig.update_layout(height=h, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="DM Sans, sans-serif", color=SOFT, size=15),
                      margin=dict(l=10, r=10, t=60 if legend == "top" else 30, b=80 if legend != "top" else 10),
                      legend=leg, hoverlabel=dict(bgcolor=CARD, font_color=INK, font_size=14, bordercolor=LINE))
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=LINE, linecolor=LINE, tickfont=dict(color=SOFT, size=14), title_font=dict(size=15))
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=LINE, linecolor=LINE, tickfont=dict(color=SOFT, size=14), title_font=dict(size=15))
    try:
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def head(title, sub=""):
    st.markdown(f'<div class="h2">{title}</div><div class="sub">{sub}</div>', unsafe_allow_html=True)


def gap():
    st.markdown('<div class="gap"></div>', unsafe_allow_html=True)


def roc_points(y, s, n=160):
    o = np.argsort(-s)
    y = y[o]
    tpr = np.cumsum(y) / max(y.sum(), 1)
    fpr = np.cumsum(1 - y) / max((1 - y).sum(), 1)
    i = np.linspace(0, len(y) - 1, min(n, len(y))).astype(int)
    return np.r_[0, fpr[i]], np.r_[0, tpr[i]]


# ------------------------------------------------------------------ hero
panels = "".join(
    f'<polygon points="{x},168 {x+78},168 {x+92},196 {x+14},196" fill="#1B5F73" stroke="#9FD3E0" stroke-width="1.5"/>'
    f'<line x1="{x+26}" y1="168" x2="{x+40}" y2="196" stroke="#9FD3E0" stroke-width="1"/>'
    f'<line x1="{x+52}" y1="168" x2="{x+66}" y2="196" stroke="#9FD3E0" stroke-width="1"/>'
    for x in range(40, 560, 100))
rays = "".join(f'<line x1="430" y1="70" x2="{430 + 120*np.cos(a):.0f}" y2="{70 + 120*np.sin(a):.0f}" stroke="#FFF3C4" stroke-width="3" stroke-linecap="round" opacity=".7"/>'
               for a in np.linspace(0, 2 * np.pi, 17)[:-1])
st.markdown(f"""
<div class="hero">
  <svg viewBox="0 0 600 220" preserveAspectRatio="xMaxYMax slice" xmlns="http://www.w3.org/2000/svg">
    {rays}
    <circle cx="430" cy="70" r="46" fill="#FFF6D6"/><circle cx="430" cy="70" r="34" fill="#FFB703"/>
    <rect x="0" y="164" width="600" height="60" fill="#2C8AA3"/>
    <rect x="0" y="164" width="600" height="3" fill="#9FD3E0" opacity=".6"/>
    {panels}
  </svg>
  <div class="in">
    <h1>Sunshine Forecast Lab</h1>
    <p>Will the sun an hour from now be strong enough for solar power? Ensemble models tested on real readings
    from the floating solar station at Castlereigh Reservoir, Sri Lanka.</p>
    <div class="meta">Bagging · Boosting · Stacking</div>
  </div>
</div>
""", unsafe_allow_html=True)

NAV = [":material/wb_sunny: Overview", ":material/leaderboard: Models", ":material/calendar_month: Day explorer",
       ":material/thermostat: Key clues", ":material/solar_power: Sunlight forecast", ":material/menu_book: About"]
page = st.radio("Section", NAV, horizontal=True, key="nav", label_visibility="collapsed")

# ------------------------------------------------------------------ 1 overview
if page == NAV[0]:
    hy_base, hy_best = HY.iloc[0], HY.iloc[-1]
    gain = (BEST.accuracy - BASE.accuracy) * 100
    st.markdown(f"""
    <div class="kpis">
      <div class="kpi main"><div class="l">Best ensemble</div><div class="v">{BEST.model}</div><div class="s">highest ROC-AUC</div></div>
      <div class="kpi"><div class="l">ROC-AUC</div><div class="v">{BEST.auc:.3f}</div><div class="s">1.0 perfect · 0.5 coin flip</div></div>
      <div class="kpi"><div class="l">Accuracy</div><div class="v">{BEST.accuracy*100:.1f}%</div><div class="s">{gain:+.1f} points vs “same as now”</div></div>
      <div class="kpi"><div class="l">Sunlight error</div><div class="v">{hy_best.MAE:.0f} W/m²</div><div class="s">hybrid, vs {hy_base.MAE:.0f} for “same as now”</div></div>
    </div>
    """, unsafe_allow_html=True)
    gap()

    c1, c2 = st.columns([1.4, 1], gap="large")
    with c1:
        head("Leaderboard", f"Ranked by ROC-AUC on {N_DAYS} days the models never saw.")
        rows = ""
        for i, r in R.sort_values("auc", ascending=False).reset_index(drop=True).iterrows():
            rows += (f"<tr class='{'top' if i == 0 else ''}'><td>{i+1}. {r.model}</td>"
                     f"<td><span class='fam' style='background:{FAMCOL.get(r.family, GREY)}'>{r.family}</span></td>"
                     f"<td class='num'>{r.accuracy:.3f}</td><td class='num'>{r.auc:.3f}</td></tr>")
        st.markdown(f"<table class='t'><tr><th>Model</th><th>Family</th><th>Accuracy</th><th>ROC-AUC</th></tr>{rows}</table>", unsafe_allow_html=True)
    with c2:
        head("Family averages", "Mean ROC-AUC per ensemble family.")
        fa = FAMAVG.sort_values("auc")
        fig = go.Figure(go.Bar(x=fa.auc, y=fa.index, orientation="h", marker_color=[FAMCOL.get(f, GREY) for f in fa.index],
                               text=[f"{v:.3f}" for v in fa.auc], textposition="outside", cliponaxis=False,
                               textfont=dict(size=16, color=INK), width=0.55))
        fig.update_xaxes(range=[max(0.5, fa.auc.min() - 0.04), min(1, fa.auc.max() + 0.04)])
        show(fig, 340, legend="bottom")
    gap()

    head("What we found")
    f4 = ""
    if LR is not None:
        f4 = (f"<b>A simple model is hard to beat.</b> Logistic regression reaches ROC-AUC {LR.auc:.3f}"
              + (", level with the best ensemble." if LR.auc >= BEST.auc - 0.002 else f", {abs(BEST.auc-LR.auc)*100:.1f} points below the best ensemble."))
    items = [
        f"<b>The baseline is already decent.</b> “The next hour will be like now” scores ROC-AUC {BASE.auc:.3f} and {BASE.accuracy*100:.1f}% accuracy. Every model must beat this.",
        f"<b>{BEST.model} is the best ensemble</b> with ROC-AUC {BEST.auc:.3f}, {(BEST.auc-BASE.auc)*100:+.1f} points against the baseline.",
        f4,
        f"<b>The hybrid</b> (Random Forest + neural network) predicts sunlight with an average error of {hy_best.MAE:.0f} W/m², against {hy_base.MAE:.0f} for “same as now”.",
    ]
    body = "".join(f'<div class="point"><div class="n">{i+1}</div><div>{t}</div></div>' for i, t in enumerate([x for x in items if x]))
    st.markdown(f'<div class="panel">{body}</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------ 2 models
elif page == NAV[1]:
    head("Models", "Compare scores and ROC curves, then move the threshold to see how the mistakes change.")
    y = P.good.values.astype(int)
    a1, a2 = st.columns(2, gap="large")
    with a1:
        metric = st.radio("Score", ["auc", "accuracy", "f1", "precision", "recall"], horizontal=True, format_func=str.upper)
        r = R.sort_values(metric)
        fig = go.Figure(go.Bar(x=r[metric], y=r.model, orientation="h", marker_color=[FAMCOL.get(f, GREY) for f in r.family],
                               text=[f"{v:.3f}" for v in r[metric]], textposition="outside", cliponaxis=False,
                               textfont=dict(size=14, color=INK)))
        fig.update_xaxes(range=[max(0, r[metric].min() - 0.06), min(1.02, r[metric].max() + 0.07)])
        show(fig, 480, legend="bottom")
    with a2:
        pick = st.multiselect("Models on the ROC chart", list(PCOLS),
                              default=[m for m in [BEST.model, "Logistic Regression", "Stacking"] if m in PCOLS][:3])
        fig = go.Figure()
        fpr, tpr = roc_points(y, (P.kt.clip(0, 1.5) / 1.5).values)
        fig.add_scatter(x=fpr, y=tpr, name="Same as now", line=dict(color=GREY, dash="dot", width=2.5))
        pal = [GOLD, TEAL, PLUM, ORANGE, GREEN, "#D9B26F"]
        for i, m in enumerate(pick):
            fpr, tpr = roc_points(y, P[PCOLS[m]].values)
            fig.add_scatter(x=fpr, y=tpr, name=m, line=dict(color=pal[i % len(pal)], width=3.5))
        fig.add_scatter(x=[0, 1], y=[0, 1], name="Coin flip", line=dict(color=LINE, dash="dash", width=2))
        fig.update_xaxes(title="False alarms (poor sun called good)")
        fig.update_yaxes(title="Good sun found")
        show(fig, 480)
    gap()

    head("Mistake explorer", "A higher threshold makes the model stricter about calling the sun “good”.")
    b1, b2 = st.columns(2, gap="large")
    with b1:
        mm = st.selectbox("Model", list(PCOLS), index=list(PCOLS).index(BEST.model) if BEST.model in PCOLS else 0)
        th = st.slider("Decision threshold", 0.10, 0.90, 0.50, 0.01)
        pr = (P[PCOLS[mm]].values >= th).astype(int)
        tp = int(((pr == 1) & (y == 1)).sum()); fp = int(((pr == 1) & (y == 0)).sum())
        fn = int(((pr == 0) & (y == 1)).sum()); tn = int(((pr == 0) & (y == 0)).sum())
        acc = (tp + tn) / len(y); prec = tp / max(tp + fp, 1); rec = tp / max(tp + fn, 1)
        st.markdown(f"""<div class="kpis" style="grid-template-columns:repeat(3,1fr);margin-top:20px">
          <div class="kpi"><div class="l">Accuracy</div><div class="v">{acc*100:.1f}%</div></div>
          <div class="kpi"><div class="l">Precision</div><div class="v">{prec*100:.1f}%</div></div>
          <div class="kpi"><div class="l">Recall</div><div class="v">{rec*100:.1f}%</div></div></div>""", unsafe_allow_html=True)
    with b2:
        z = [[tn, fp], [fn, tp]]
        fig = go.Figure(go.Heatmap(z=z, x=["Says poor", "Says good"], y=["Really poor", "Really good"],
                                   colorscale=[[0, "#2A231E"], [1, "#C77D00"]], showscale=False, xgap=5, ygap=5,
                                   text=[[f"{v:,}" for v in row] for row in z], texttemplate="%{text}",
                                   textfont=dict(size=26, color="#FFFFFF")))
        fig.update_yaxes(autorange="reversed")
        show(fig, 340, legend="bottom")

# ------------------------------------------------------------------ 3 day explorer
elif page == NAV[2]:
    head("Day explorer", "Pick a test day. Top: real sunlight an hour after each forecast, against the hybrid forecast. Bottom: how likely the model thought good sun was.")
    swing = P.dropna(subset=["swing"]).copy()
    top_days = swing.loc[swing.groupby("day").swing.apply(lambda s: s.abs().idxmax())].assign(a=lambda d: d.swing.abs()).sort_values("a", ascending=False)
    days = sorted(P.day.unique())
    d1, d2 = st.columns(2, gap="large")
    with d1:
        day = st.selectbox("Day", days, index=days.index(top_days.iloc[0].day) if len(top_days) else 0)
    with d2:
        model = st.selectbox("Model for the probability line", list(PCOLS), index=list(PCOLS).index("Stacking") if "Stacking" in PCOLS else 0)
    dd = P[P.day == day].sort_values("time")
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.55, 0.45], vertical_spacing=0.16,
                        subplot_titles=("Sunlight one hour later (W/m²)", "Chance of good sun"))
    fig.add_scatter(x=dd.time, y=dd.ghi_next, name="Real sunlight", line=dict(color=GOLD, width=3.5), fill="tozeroy",
                    fillcolor="rgba(242,176,30,.15)", row=1, col=1)
    if "hybrid_ghi" in dd:
        fig.add_scatter(x=dd.time, y=dd.hybrid_ghi, name="Hybrid forecast", line=dict(color=TEAL, width=2.8), row=1, col=1)
    fig.add_scatter(x=dd.time, y=dd[PCOLS[model]], name=f"{model} chance", line=dict(color=PLUM, width=3), row=2, col=1)
    fig.add_scatter(x=dd.time, y=dd.good, name="Really good sun", line=dict(color=GREEN, width=1.6, shape="hv"),
                    fill="tozeroy", fillcolor="rgba(108,203,149,.12)", row=2, col=1)
    ev = dd[dd.swing.abs() >= 0.4]
    if len(ev):
        fig.add_scatter(x=ev.time, y=ev[PCOLS[model]], mode="markers", name="Cloud event",
                        marker=dict(size=12, color=ORANGE, line=dict(color="#fff", width=1.5)), row=2, col=1)
    fig.update_yaxes(range=[0, 1.05], row=2, col=1)
    for a in fig.layout.annotations:
        a.update(x=0, xanchor="left", font=dict(size=17, color=INK))
    show(fig, 680, legend="bottom")

# ------------------------------------------------------------------ 4 key clues
elif page == NAV[3]:
    FRIENDLY = {"kt": "Sunniness right now", "kt_l1": "Sunniness 10 min ago", "kt_l3": "Sunniness 30 min ago", "kt_l6": "Sunniness 1 hour ago",
                "kt_mean6": "Average sunniness, last hour", "kt_std6": "How jumpy the last hour was", "kt_trend": "Change in last 10 min",
                "tod_sin": "Time of day (a)", "tod_cos": "Time of day (b)", "month": "Month", "doy_sin": "Season (a)", "doy_cos": "Season (b)",
                "ghi": "Sunlight now (W/m²)", "dni": "Direct sunlight", "dhi": "Diffuse sunlight", "diffuse_frac": "Cloudiness (diffuse share)",
                "temp": "Temperature", "rh": "Humidity", "press": "Air pressure", "temp_chg": "Temperature change, 1 h", "rh_chg": "Humidity change, 1 h",
                "press_chg": "Pressure change, 1 h", "ws": "Wind speed", "wd_sin": "Wind direction (a)", "wd_cos": "Wind direction (b)",
                "rain": "Rain, last 10 min", "rain_1h": "Rain, last hour"}
    head("Key clues", "How much each clue helped Random Forest and XGBoost. “Sunniness” is sunlight compared with a clear sky at that time of day (1.0 is perfectly clear).")
    f = FI.copy(); f.index = [FRIENDLY.get(i, i) for i in f.index]
    f = f.assign(avg=f.mean(axis=1)).sort_values("avg").tail(12).drop(columns="avg")
    fig = go.Figure()
    for col, c in zip(f.columns, [TEAL, GOLD]):
        fig.add_bar(y=f.index, x=f[col], name=col, orientation="h", marker_color=c)
    fig.update_layout(barmode="group", bargap=0.35)
    show(fig, 620)

# ------------------------------------------------------------------ 5 sunlight forecast
elif page == NAV[4]:
    head("Sunlight forecast", "A Random Forest and a small neural network each predict the sunlight an hour ahead. The hybrid is their average.")
    h1, h2 = st.columns(2, gap="large")
    with h1:
        rows = "".join(f"<tr class='{'top' if i == len(HY)-1 else ''}'><td>{r.model}</td><td class='num'>{r.MAE:.1f}</td>"
                       f"<td class='num'>{r.RMSE:.1f}</td><td class='num'>{r.R2:.3f}</td></tr>" for i, r in HY.reset_index(drop=True).iterrows())
        st.markdown(f"<table class='t'><tr><th>Model</th><th>Avg error (W/m²)</th><th>RMSE</th><th>R²</th></tr>{rows}</table>", unsafe_allow_html=True)
    with h2:
        if "hybrid_ghi" in P:
            s = P.dropna(subset=["hybrid_ghi", "ghi_next"]).sample(min(4000, len(P)), random_state=1)
            fig = go.Figure(go.Scattergl(x=s.ghi_next, y=s.hybrid_ghi, mode="markers", name="Forecasts",
                                         marker=dict(size=5, color=TEAL, opacity=.4)))
            m = float(max(s.ghi_next.max(), s.hybrid_ghi.max()))
            fig.add_scatter(x=[0, m], y=[0, m], name="Perfect forecast", line=dict(color=GOLD, dash="dash", width=2.8))
            fig.update_xaxes(title="Real sunlight (W/m²)"); fig.update_yaxes(title="Hybrid forecast (W/m²)")
            show(fig, 460)

# ------------------------------------------------------------------ 6 about
else:
    head("About this project")
    ca, cb = st.columns(2, gap="large")
    with ca:
        st.markdown("""<div class="panel"><h4>The question</h4><p>Solar farms and the power grid need to know how sunny the next hour will be.
        We ask: <b>will the sunlight one hour from now be at least half of a clear-sky reading for that time of day?</b>
        We also forecast the sunlight itself in W/m².</p></div><div class="gap" style="height:28px"></div>
        <div class="panel"><h4>The data</h4><p>Minute-by-minute readings from a solar and weather station at Castlereigh Reservoir, Sri Lanka,
        over 24 months, published by the World Bank through ENERGYDATA.info. Averaged into 10-minute rows.</p></div>""", unsafe_allow_html=True)
    with cb:
        st.markdown("""<div class="panel"><h4>How we kept it honest</h4><ul>
        <li>Split by <b>whole days</b>: the oldest 75% train, the newest 25% test.</li>
        <li>Clear-sky reference learned from training days only.</li>
        <li>Night removed, because it would inflate every score.</li>
        <li>Compared with a “same as now” rule and logistic regression.</li></ul></div>
        <div class="gap" style="height:28px"></div>
        <div class="panel"><h4>Limits</h4><ul>
        <li>One site only, not all of Sri Lanka.</li>
        <li>Small score gaps between ensembles are not strong evidence.</li>
        <li>No satellite or cloud images, only station readings.</li></ul></div>""", unsafe_allow_html=True)

    st.markdown('<div class="gap" style="height:28px"></div>', unsafe_allow_html=True)
    cc, cd = st.columns(2, gap="large")
    with cc:
        st.markdown("""<div class="panel"><h4>Data files</h4>
        <p>The dashboard reads these files from <code>dashboard_data/</code>, all made by the training notebook:</p><ul>
        <li><b>model_results.csv</b>: accuracy, precision, recall, F1, AUC and training time for each model.</li>
        <li><b>test_predictions.csv</b>: every 10-minute test row with real sunlight, each model’s probability and the hybrid W/m² forecast.</li>
        <li><b>feature_importance.csv</b>: how much Random Forest and XGBoost rely on each input.</li>
        <li><b>accuracy_by_time_of_day.csv</b>: accuracy by hour block for the “same as now” rule, stacking and the best boosting model.</li>
        <li><b>hybrid_results.csv</b>: MAE, RMSE and R² for the W/m² forecasts.</li></ul></div>""", unsafe_allow_html=True)
    with cd:
        st.markdown("""<div class="panel"><h4>Credits</h4><ul>
        <li><b>Data:</b> Sri Lanka Solar Radiation Measurement Data, Castlereigh Reservoir station. World Bank / ESMAP,
        via <a href="https://energydata.info" target="_blank">ENERGYDATA.info</a> (CC BY 4.0).</li>
        <li><b>Models:</b> scikit-learn, XGBoost, LightGBM and CatBoost.</li>
        <li><b>Dashboard:</b> Streamlit, Plotly, pandas and NumPy.</li></ul></div>""", unsafe_allow_html=True)
