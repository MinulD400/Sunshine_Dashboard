"""Sunshine Forecast Lab - Streamlit dashboard
Reads the CSV files exported by the Colab notebook (folder: dashboard_data/).
Run:  streamlit run app.py
"""
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(page_title="Sunshine Forecast Lab", page_icon="☀️", layout="wide",
                   initial_sidebar_state="collapsed")

# ------------------------------------------------------------------ palette
BG, CARD, CARD2, LINE = "#0B1020", "#131B33", "#1A2444", "#26315A"
TXT, MUTED = "#EDEFF7", "#9AA3BF"
SUN, CORAL, SKY, VIOLET, SLATE = "#FFB84D", "#FF7A59", "#5CC8FF", "#A78BFF", "#8E97B3"
FAMCOL = {"Bagging": SKY, "Boosting": SUN, "Stacking": VIOLET, "Reference": SLATE, "Baseline": "#5A6385"}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stApp {{ font-family: 'Poppins', sans-serif; }}
.stApp {{ background: {BG}; color: {TXT}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1280px; }}
/* hero */
.hero {{ position: relative; overflow: hidden; border-radius: 26px; padding: 38px 42px 34px 42px; margin-bottom: 22px;
  background: radial-gradient(900px 380px at 88% 118%, rgba(255,122,89,.55), rgba(255,122,89,0) 62%),
              radial-gradient(520px 300px at 12% -20%, rgba(92,200,255,.18), rgba(92,200,255,0) 70%),
              linear-gradient(135deg, #0E1530 0%, #1B1745 55%, #2B1B45 100%);
  border: 1px solid {LINE}; }}
.hero .sun {{ position:absolute; right:56px; bottom:-62px; width:230px; height:230px; border-radius:50%;
  background: radial-gradient(circle at 50% 45%, #FFE29A 0%, {SUN} 45%, {CORAL} 100%); filter: blur(.4px);
  box-shadow: 0 0 120px 40px rgba(255,150,80,.35); }}
.hero .arc {{ position:absolute; right:0; bottom:0; width:520px; height:140px; opacity:.55; }}
.kicker {{ font-size:12px; letter-spacing:.16em; text-transform:uppercase; color:{SUN}; font-weight:600; margin-bottom:8px; }}
.hero h1 {{ font-size:40px; line-height:1.1; font-weight:800; margin:0 0 10px 0; color:#fff; max-width:760px; }}
.hero p {{ color:#C7CCE3; font-size:15px; max-width:640px; margin:0; line-height:1.6; }}
.chips {{ margin-top:18px; display:flex; gap:8px; flex-wrap:wrap; }}
.chip {{ font-size:12px; padding:5px 12px; border-radius:999px; background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.14); color:#E6E9F7; }}
/* cards */
.kpis {{ display:grid; grid-template-columns: repeat(5, 1fr); gap:14px; margin: 4px 0 8px 0; }}
.kpi {{ background:{CARD}; border:1px solid {LINE}; border-radius:18px; padding:18px 18px 16px 18px; }}
.kpi .l {{ font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; color:{MUTED}; font-weight:600; }}
.kpi .v {{ font-size:30px; font-weight:700; margin-top:6px; color:#fff; line-height:1.1; }}
.kpi .s {{ font-size:12px; color:{MUTED}; margin-top:6px; }}
.kpi.hot {{ background: linear-gradient(160deg, #2A2250, #3A2350); border-color:#4A3A7A; }}
.kpi.hot .v {{ color:{SUN}; }}
.card {{ background:{CARD}; border:1px solid {LINE}; border-radius:18px; padding:20px 22px; margin-bottom:14px; }}
.card h4 {{ margin:0 0 6px 0; font-size:16px; font-weight:600; color:#fff; }}
.card p, .card li {{ color:#C7CCE3; font-size:13.5px; line-height:1.65; }}
.find {{ display:flex; gap:14px; align-items:flex-start; padding:12px 0; border-bottom:1px solid {LINE}; }}
.find:last-child {{ border-bottom:none; }}
.find .n {{ min-width:30px; height:30px; border-radius:50%; background:{SUN}; color:#241a05; font-weight:700; display:flex; align-items:center; justify-content:center; font-size:13px; }}
.find .t {{ color:#DDE1F2; font-size:14px; line-height:1.55; }}
.find .t b {{ color:#fff; }}
.sec {{ font-size:22px; font-weight:700; margin: 26px 0 4px 0; color:#fff; }}
.sub {{ color:{MUTED}; font-size:13.5px; margin-bottom:12px; max-width:760px; }}
/* table */
table.lb {{ width:100%; border-collapse:separate; border-spacing:0 6px; font-size:13px; }}
table.lb th {{ text-align:left; color:{MUTED}; font-weight:600; font-size:11.5px; letter-spacing:.06em; text-transform:uppercase; padding:4px 12px; }}
table.lb td {{ background:{CARD}; padding:10px 12px; color:#E6E9F7; }}
table.lb tr td:first-child {{ border-radius:12px 0 0 12px; font-weight:600; }}
table.lb tr td:last-child {{ border-radius:0 12px 12px 0; }}
table.lb tr.top td {{ background:#2A2250; }}
.fam {{ font-size:11px; padding:3px 10px; border-radius:999px; font-weight:600; color:#0B1020; }}
.bar {{ height:8px; border-radius:6px; background:{CARD2}; width:110px; display:inline-block; vertical-align:middle; margin-right:8px; overflow:hidden; }}
.bar i {{ display:block; height:100%; border-radius:6px; }}
/* tabs */
.stTabs [data-baseweb="tab-list"] {{ gap:6px; background:{CARD}; padding:6px; border-radius:16px; border:1px solid {LINE}; }}
.stTabs [data-baseweb="tab"] {{ height:42px; border-radius:11px; padding:0 24px !important; color:{MUTED}; font-weight:600; font-size:14px; background:transparent; }}
.stTabs [aria-selected="true"] {{ background:linear-gradient(135deg,{SUN},{CORAL}) !important; color:#1a1208 !important; }}
.stTabs [data-baseweb="tab"] > div, .stTabs [data-baseweb="tab"] p {{ padding:0 4px; white-space:nowrap; }}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display:none; }}
/* widgets */
label, .stSelectbox label, .stSlider label, .stMultiSelect label, .stRadio label {{ color:{MUTED} !important; font-size:12.5px !important; font-weight:500; }}
div[data-baseweb="select"] > div {{ background:{CARD}; border-color:{LINE}; border-radius:12px; }}
.stSlider [data-baseweb="slider"] div[role="slider"] {{ background:{SUN}; }}
@media (max-width: 900px) {{ .kpis {{ grid-template-columns: repeat(2, 1fr); }} .hero h1 {{ font-size:28px; }} .hero .sun {{ display:none; }} }}
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
    st.error("Could not find the `dashboard_data` folder next to app.py. Copy the CSV files exported by the "
             "Colab notebook into a folder called dashboard_data. Details: " + str(e))
    st.stop()

PCOLS = {c[2:].replace("_", " "): c for c in P.columns if c.startswith("p_")}
ENS = R[R.family.isin(["Bagging", "Boosting", "Stacking"])].sort_values("auc", ascending=False)
BEST = ENS.iloc[0]
BASE = R[R.family == "Baseline"].iloc[0]
LR = R[R.model == "Logistic Regression"].iloc[0] if (R.model == "Logistic Regression").any() else None
N_DAYS, N_ROWS = P.day.nunique(), len(P)
FAMAVG = R[R.family != "Baseline"].groupby("family")[["accuracy", "auc"]].mean()


def show(fig, h=380):
    fig.update_layout(height=h, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Poppins, sans-serif", color=TXT, size=12),
                      margin=dict(l=10, r=10, t=36, b=10), legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
                      hoverlabel=dict(bgcolor=CARD2, font_color=TXT))
    fig.update_xaxes(gridcolor=LINE, zerolinecolor=LINE, linecolor=LINE)
    fig.update_yaxes(gridcolor=LINE, zerolinecolor=LINE, linecolor=LINE)
    try:
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def roc_points(y, s, n=160):
    o = np.argsort(-s)
    y = y[o]
    tpr = np.cumsum(y) / max(y.sum(), 1)
    fpr = np.cumsum(1 - y) / max((1 - y).sum(), 1)
    i = np.linspace(0, len(y) - 1, min(n, len(y))).astype(int)
    return np.r_[0, fpr[i]], np.r_[0, tpr[i]]


# ------------------------------------------------------------------ hero
st.markdown(f"""
<div class="hero">
  <div class="sun"></div>
  <svg class="arc" viewBox="0 0 520 140" preserveAspectRatio="none"><path d="M0 138 C 120 138, 150 14, 260 14 S 400 138, 520 138" fill="none" stroke="#FFD28A" stroke-width="2" stroke-dasharray="3 7"/></svg>
  <div class="kicker">Ensemble learning · Sri Lanka</div>
  <h1>Sunshine Forecast Lab</h1>
  <p>Can bagging, boosting and stacking tell us whether the sun an hour from now will be strong enough
  for solar power? Real minute-by-minute readings from a floating-solar station at Castlereigh Reservoir, 2024 to 2026.</p>
  <div class="chips"><span class="chip">☀️ Predict 1 hour ahead</span><span class="chip">🌲 Bagging</span>
  <span class="chip">⚡ Boosting</span><span class="chip">🧩 Stacking</span><span class="chip">📅 Tested on days the models never saw</span></div>
</div>
""", unsafe_allow_html=True)

t1, t2, t3, t4, t5, t6 = st.tabs(["Overview", "Model arena", "Day explorer", "What drives it", "Hybrid forecast", "About"])

# ------------------------------------------------------------------ 1 overview
with t1:
    hy_base = HY.iloc[0]; hy_best = HY.iloc[-1]
    gain_acc = (BEST.accuracy - BASE.accuracy) * 100
    st.markdown(f"""
    <div class="kpis">
      <div class="kpi hot"><div class="l">Best ensemble</div><div class="v">{BEST.model}</div><div class="s">highest ROC-AUC of the ensembles</div></div>
      <div class="kpi"><div class="l">ROC-AUC</div><div class="v">{BEST.auc:.3f}</div><div class="s">1.0 is perfect, 0.5 is a coin flip</div></div>
      <div class="kpi"><div class="l">Accuracy</div><div class="v">{BEST.accuracy*100:.1f}%</div><div class="s">{gain_acc:+.1f} pts vs "same as now" rule</div></div>
      <div class="kpi"><div class="l">Sunlight forecast error</div><div class="v">{hy_best.MAE:.0f} W/m²</div><div class="s">hybrid, vs {hy_base.MAE:.0f} for "same as now"</div></div>
      <div class="kpi"><div class="l">Unseen test days</div><div class="v">{N_DAYS}</div><div class="s">{N_ROWS:,} ten-minute forecasts</div></div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1.35, 1])
    with c1:
        st.markdown('<div class="sec">Leaderboard</div><div class="sub">Every model, ranked by ROC-AUC on days it never saw during training.</div>', unsafe_allow_html=True)
        rows = ""
        lo = max(0.5, R.auc.min() - 0.03)
        for i, r in R.sort_values("auc", ascending=False).reset_index(drop=True).iterrows():
            w = int(100 * (r.auc - lo) / max(1e-9, (R.auc.max() - lo)))
            col = FAMCOL.get(r.family, SLATE)
            rows += (f"<tr class='{'top' if i == 0 else ''}'><td>{i+1}. {r.model}</td>"
                     f"<td><span class='fam' style='background:{col}'>{r.family}</span></td>"
                     f"<td>{r.accuracy:.3f}</td><td>{r.f1:.3f}</td>"
                     f"<td><span class='bar'><i style='width:{max(w,4)}%;background:{col}'></i></span><b>{r.auc:.3f}</b></td>"
                     f"<td>{r.seconds:.1f}s</td></tr>")
        st.markdown(f"<table class='lb'><tr><th>Model</th><th>Family</th><th>Accuracy</th><th>F1</th><th>ROC-AUC</th><th>Train time</th></tr>{rows}</table>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="sec">Family showdown</div><div class="sub">Average ROC-AUC of each ensemble family.</div>', unsafe_allow_html=True)
        fa = FAMAVG.sort_values("auc")
        fig = go.Figure(go.Bar(x=fa.auc, y=fa.index, orientation="h", marker_color=[FAMCOL.get(f, SLATE) for f in fa.index],
                               text=[f"{v:.3f}" for v in fa.auc], textposition="outside", cliponaxis=False))
        fig.update_xaxes(range=[max(0.5, fa.auc.min() - 0.04), min(1, fa.auc.max() + 0.03)])
        show(fig, 300)

    st.markdown('<div class="sec">What we found</div>', unsafe_allow_html=True)
    f4 = ""
    if LR is not None:
        f4 = (f"<b>A simple model is hard to beat.</b> Logistic regression reaches ROC-AUC {LR.auc:.3f}"
              + (", level with or above the best ensemble." if LR.auc >= BEST.auc - 0.002 else f", {abs(BEST.auc-LR.auc)*100:.1f} points below the best ensemble."))
    items = [
        f"<b>The baseline is already decent.</b> “The next hour will be like now” scores ROC-AUC {BASE.auc:.3f} and accuracy {BASE.accuracy*100:.1f}%. This is the number every model must beat.",
        f"<b>{BEST.model} is the best ensemble</b> with ROC-AUC {BEST.auc:.3f}, which is {(BEST.auc-BASE.auc)*100:+.1f} points against the baseline.",
        "<b>Family averages (ROC-AUC):</b> " + ", ".join(f"{k.lower()} {v:.3f}" for k, v in FAMAVG.auc.sort_values(ascending=False).items()) + ".",
        f4,
        f"<b>The hybrid</b> (Random Forest + neural network) predicts sunlight with an average error of {hy_best.MAE:.0f} W/m², against {hy_base.MAE:.0f} for “same as now”.",
    ]
    html = "".join(f'<div class="find"><div class="n">{i+1}</div><div class="t">{t}</div></div>' for i, t in enumerate([x for x in items if x]))
    st.markdown(f'<div class="card">{html}</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------ 2 arena
with t2:
    st.markdown('<div class="sec">Model arena</div><div class="sub">Pick a score, compare the ROC curves, and move the decision threshold to see how mistakes change.</div>', unsafe_allow_html=True)
    a1, a2 = st.columns([1, 1])
    with a1:
        metric = st.radio("Score to compare", ["auc", "accuracy", "f1", "precision", "recall"], horizontal=True, format_func=str.upper)
        r = R.sort_values(metric)
        fig = go.Figure(go.Bar(x=r[metric], y=r.model, orientation="h", marker_color=[FAMCOL.get(f, SLATE) for f in r.family],
                               text=[f"{v:.3f}" for v in r[metric]], textposition="outside", cliponaxis=False))
        fig.update_xaxes(range=[max(0, r[metric].min() - 0.06), min(1.02, r[metric].max() + 0.05)])
        show(fig, 430)
    with a2:
        pick = st.multiselect("ROC curves", list(PCOLS), default=[m for m in [BEST.model, "Logistic Regression", "Stacking"] if m in PCOLS][:3])
        y = P.good.values.astype(int)
        fig = go.Figure()
        fpr, tpr = roc_points(y, (P.kt.clip(0, 1.5) / 1.5).values)
        fig.add_scatter(x=fpr, y=tpr, name="Same-as-now rule", line=dict(color="#5A6385", dash="dot", width=2))
        pal = [SUN, SKY, VIOLET, CORAL, "#7EE0A8", "#FFD6A0"]
        for i, m in enumerate(pick):
            fpr, tpr = roc_points(y, P[PCOLS[m]].values)
            fig.add_scatter(x=fpr, y=tpr, name=m, line=dict(color=pal[i % len(pal)], width=3))
        fig.add_scatter(x=[0, 1], y=[0, 1], name="Coin flip", line=dict(color=LINE, dash="dash"))
        fig.update_xaxes(title="False alarms (poor sun called good)"); fig.update_yaxes(title="Good sun found")
        show(fig, 430)

    st.markdown('<div class="sec">Mistake explorer</div><div class="sub">A higher threshold makes the model stricter about calling the sun “good”.</div>', unsafe_allow_html=True)
    b1, b2 = st.columns([1, 1.2])
    with b1:
        mm = st.selectbox("Model", list(PCOLS), index=list(PCOLS).index(BEST.model) if BEST.model in PCOLS else 0)
        th = st.slider("Decision threshold", 0.10, 0.90, 0.50, 0.01)
        pr = (P[PCOLS[mm]].values >= th).astype(int)
        tp = int(((pr == 1) & (y == 1)).sum()); fp = int(((pr == 1) & (y == 0)).sum())
        fn = int(((pr == 0) & (y == 1)).sum()); tn = int(((pr == 0) & (y == 0)).sum())
        acc = (tp + tn) / len(y); prec = tp / max(tp + fp, 1); rec = tp / max(tp + fn, 1)
        st.markdown(f"""<div class="kpis" style="grid-template-columns:repeat(3,1fr)">
        <div class="kpi"><div class="l">Accuracy</div><div class="v">{acc*100:.1f}%</div></div>
        <div class="kpi"><div class="l">Precision</div><div class="v">{prec*100:.1f}%</div><div class="s">when it says good, it is right</div></div>
        <div class="kpi"><div class="l">Recall</div><div class="v">{rec*100:.1f}%</div><div class="s">of real good-sun times found</div></div></div>""", unsafe_allow_html=True)
    with b2:
        z = [[tn, fp], [fn, tp]]
        fig = go.Figure(go.Heatmap(z=z, x=["Says poor", "Says good"], y=["Really poor", "Really good"], colorscale=[[0, CARD2], [1, SUN]],
                                   showscale=False, text=[[f"{v:,}" for v in row] for row in z], texttemplate="%{text}",
                                   textfont=dict(size=20, color="#fff")))
        fig.update_yaxes(autorange="reversed")
        show(fig, 300)

# ------------------------------------------------------------------ 3 day explorer
with t3:
    st.markdown('<div class="sec">Day explorer</div><div class="sub">Pick any test day. The top chart shows real sunlight one hour after each forecast against the hybrid forecast. The bottom chart shows how likely the model thought good sun was.</div>', unsafe_allow_html=True)
    swing = P.dropna(subset=["swing"]).copy()
    top_days = swing.loc[swing.groupby("day").swing.apply(lambda s: s.abs().idxmax())].assign(a=lambda d: d.swing.abs()).sort_values("a", ascending=False)
    days = sorted(P.day.unique())
    d1, d2 = st.columns([1, 1])
    with d1:
        day = st.selectbox("Day", days, index=days.index(top_days.iloc[0].day) if len(top_days) else 0)
    with d2:
        model = st.selectbox("Model for the probability line", list(PCOLS), index=list(PCOLS).index("Stacking") if "Stacking" in PCOLS else 0)
    dd = P[P.day == day].sort_values("time")
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.55, 0.45], vertical_spacing=0.08,
                        subplot_titles=("Sunlight one hour later (W/m²)", "Chance of good sun, as forecast"))
    fig.add_scatter(x=dd.time, y=dd.ghi_next, name="Real", line=dict(color=SUN, width=3), fill="tozeroy", fillcolor="rgba(255,184,77,.12)", row=1, col=1)
    if "hybrid_ghi" in dd:
        fig.add_scatter(x=dd.time, y=dd.hybrid_ghi, name="Hybrid forecast", line=dict(color=SKY, width=2.5), row=1, col=1)
    fig.add_scatter(x=dd.time, y=dd[PCOLS[model]], name=f"{model} chance", line=dict(color=VIOLET, width=3), row=2, col=1)
    fig.add_scatter(x=dd.time, y=dd.good, name="Really good sun", line=dict(color="#7EE0A8", width=1.5, shape="hv"), fill="tozeroy", fillcolor="rgba(126,224,168,.10)", row=2, col=1)
    ev = dd[dd.swing.abs() >= 0.4]
    if len(ev):
        fig.add_scatter(x=ev.time, y=ev[PCOLS[model]], mode="markers", name="Cloud event", marker=dict(size=11, color=CORAL, line=dict(color="#fff", width=1.5)), row=2, col=1)
    fig.update_yaxes(range=[0, 1.05], row=2, col=1)
    fig.update_annotations(font=dict(size=12, color=MUTED))
    show(fig, 560)
    k1, k2, k3 = st.columns(3)
    k1.markdown(f'<div class="kpi"><div class="l">Forecasts that day</div><div class="v">{len(dd)}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi"><div class="l">Share really good sun</div><div class="v">{dd.good.mean()*100:.0f}%</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi"><div class="l">Cloud events</div><div class="v">{len(ev)}</div><div class="s">chance jumped by 0.4 or more in 10 min</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="sec">Cloud-event detector</div><div class="sub">The ten moments when the forecast chance of good sun changed the most within a day.</div>', unsafe_allow_html=True)
    tt = top_days.head(10)
    rows = "".join(f"<tr><td>{r.time:%Y-%m-%d %H:%M}</td><td>{r.swing:+.2f}</td><td>{'Sun cleared' if r.swing > 0 else 'Cloud arrived'}</td><td>{'good' if r.good == 1 else 'poor'}</td></tr>" for r in tt.itertuples())
    st.markdown(f"<table class='lb'><tr><th>When</th><th>Change in chance</th><th>What happened</th><th>Real sun an hour later</th></tr>{rows}</table>", unsafe_allow_html=True)

# ------------------------------------------------------------------ 4 clues
FRIENDLY = {"kt": "Sunniness right now", "kt_l1": "Sunniness 10 min ago", "kt_l3": "Sunniness 30 min ago", "kt_l6": "Sunniness 1 hour ago",
            "kt_mean6": "Average sunniness, last hour", "kt_std6": "How jumpy the last hour was", "kt_trend": "Change in last 10 min",
            "tod_sin": "Time of day (a)", "tod_cos": "Time of day (b)", "month": "Month", "doy_sin": "Season (a)", "doy_cos": "Season (b)",
            "ghi": "Sunlight now (W/m²)", "dni": "Direct sunlight", "dhi": "Diffuse sunlight", "diffuse_frac": "Cloudiness (diffuse share)",
            "temp": "Temperature", "rh": "Humidity", "press": "Air pressure", "temp_chg": "Temperature change, 1 h", "rh_chg": "Humidity change, 1 h",
            "press_chg": "Pressure change, 1 h", "ws": "Wind speed", "wd_sin": "Wind direction (a)", "wd_cos": "Wind direction (b)",
            "rain": "Rain, last 10 min", "rain_1h": "Rain, last hour"}
with t4:
    st.markdown('<div class="sec">What drives the forecast</div><div class="sub">How much each clue helped the Random Forest and XGBoost. “Sunniness” means sunlight compared with a clear sky at that time of day (1.0 is a perfectly clear sky).</div>', unsafe_allow_html=True)
    f = FI.copy(); f.index = [FRIENDLY.get(i, i) for i in f.index]
    f = f.assign(avg=f.mean(axis=1)).sort_values("avg").tail(15).drop(columns="avg")
    fig = go.Figure()
    for col, c in zip(f.columns, [SKY, SUN]):
        fig.add_bar(y=f.index, x=f[col], name=col, orientation="h", marker_color=c)
    fig.update_layout(barmode="group"); show(fig, 560)
    top5 = FI.mean(axis=1).sort_values(ascending=False).head(5).index
    st.markdown('<div class="card"><h4>Top five clues</h4><p>' + " · ".join(f"<b>{FRIENDLY.get(i, i)}</b>" for i in top5) +
                '</p><p>If the top clues are about how sunny it has just been and how fast that is changing, the models learned real weather behaviour. Clues that say similar things share their importance, so do not read the exact order too strictly.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec">Does time of day matter?</div>', unsafe_allow_html=True)
    bb = B.drop(columns="rows", errors="ignore")
    fig = go.Figure()
    for col, c in zip(bb.columns, [SLATE, VIOLET, SUN]):
        fig.add_bar(x=bb.index, y=bb[col], name=col, marker_color=c)
    fig.update_layout(barmode="group"); fig.update_yaxes(range=[max(0.5, bb.min().min() - 0.05), 1.0], title="accuracy")
    show(fig, 340)

# ------------------------------------------------------------------ 5 hybrid
with t5:
    st.markdown('<div class="sec">Hybrid forecast: how much sun?</div><div class="sub">A Random Forest and a small neural network each predict the sunlight an hour ahead. The hybrid is their average.</div>', unsafe_allow_html=True)
    h1, h2 = st.columns([1, 1])
    with h1:
        rows = "".join(f"<tr class='{'top' if i == len(HY)-1 else ''}'><td>{r.model}</td><td>{r.MAE:.1f}</td><td>{r.RMSE:.1f}</td><td>{r.R2:.3f}</td></tr>" for i, r in HY.reset_index(drop=True).iterrows())
        st.markdown(f"<table class='lb'><tr><th>Model</th><th>Average error (W/m²)</th><th>RMSE</th><th>R²</th></tr>{rows}</table>", unsafe_allow_html=True)
        st.markdown('<div class="card"><h4>How to read it</h4><p><b>Average error</b> is how many W/m² the forecast is off by, on average. <b>RMSE</b> punishes big misses more. <b>R²</b> is the share of the ups and downs of the sunlight that the model explains (1 is perfect).</p></div>', unsafe_allow_html=True)
    with h2:
        if "hybrid_ghi" in P:
            s = P.dropna(subset=["hybrid_ghi", "ghi_next"]).sample(min(4000, len(P)), random_state=1)
            fig = go.Figure(go.Scattergl(x=s.ghi_next, y=s.hybrid_ghi, mode="markers", marker=dict(size=4, color=SKY, opacity=.35)))
            m = float(max(s.ghi_next.max(), s.hybrid_ghi.max()))
            fig.add_scatter(x=[0, m], y=[0, m], line=dict(color=SUN, dash="dash"), name="Perfect")
            fig.update_xaxes(title="Real sunlight (W/m²)"); fig.update_yaxes(title="Hybrid forecast (W/m²)"); fig.update_layout(showlegend=False)
            show(fig, 400)
    if "hybrid_ghi" in P:
        P2 = P.assign(hr=P.time.dt.hour, err=(P.hybrid_ghi - P.ghi_next).abs()).groupby("hr").err.mean()
        fig = go.Figure(go.Bar(x=P2.index, y=P2.values, marker_color=SUN))
        fig.update_xaxes(title="Hour of day"); fig.update_yaxes(title="Average error (W/m²)")
        st.markdown('<div class="sec">When is it hardest?</div>', unsafe_allow_html=True)
        show(fig, 300)

# ------------------------------------------------------------------ 6 about
with t6:
    st.markdown('<div class="sec">About this project</div>', unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        st.markdown("""<div class="card"><h4>The question</h4><p>Solar farms and the power grid need to know how sunny the next hour will be.
        We ask: <b>will the sunlight one hour from now be at least half of a clear-sky reading for that time of day?</b>
        We also forecast the sunlight itself in W/m².</p></div>
        <div class="card"><h4>The data</h4><p>Minute-by-minute readings from an automatic solar and weather station at Castlereigh Reservoir, Sri Lanka,
        collected for 24 months and published by the World Bank through ENERGYDATA.info. We average them into 10-minute rows
        and use sunlight, temperature, humidity, pressure, wind and rain.</p></div>""", unsafe_allow_html=True)
    with cb:
        st.markdown("""<div class="card"><h4>How we kept it honest</h4><ul>
        <li>We split by <b>whole days</b>: the oldest 75% of days train, the newest 25% test.</li>
        <li>The clear-sky reference is learned from training days only.</li>
        <li>Night is removed, because it would make every score look better than it is.</li>
        <li>Every ensemble is compared with a simple “same as now” rule and with logistic regression.</li></ul></div>
        <div class="card"><h4>Limits</h4><ul>
        <li>One site only, so this is not a forecast for all of Sri Lanka.</li>
        <li>Ten-minute rows from one day look alike, so small score gaps between ensembles are not strong evidence.</li>
        <li>No satellite or cloud images, only the station readings.</li></ul></div>""", unsafe_allow_html=True)
