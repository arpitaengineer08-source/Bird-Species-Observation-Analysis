"""
Aviary Insights — Bird Species Observation Dashboard
------------------------------------------------------
Nature / Editorial-Premium themed Streamlit + Plotly dashboard with a
light/dark toggle, magazine-style typography, and data-driven narrative callouts.

Run with:
    pip install -r requirements.txt
    streamlit run streamlit_dashboard.py

Expects `Bird_Combined_Cleaned.csv` in the same folder.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Aviary Insights | Bird Observation Dashboard", page_icon="🕊️", layout="wide", initial_sidebar_state="expanded")

# ==================================================================
# THEME DEFINITIONS
# ==================================================================
LIGHT = {
    "bg_from": "#faf7f0", "bg_to": "#efe7d4", "ink": "#20241f", "muted": "#6f6656",
    "card_bg": "#fffdf8", "card_border": "rgba(32,36,31,0.09)", "shadow": "rgba(32,36,31,0.10)",
    "sidebar_from": "#1f3327", "sidebar_to": "#12201a", "divider": "rgba(185,141,45,0.45)",
    "gold": "#b98d2d", "forest": "#2f6d4f", "forest_light": "#6faa86",
    "grassland": "#c99a2e", "grassland_light": "#e2bf6b", "rust": "#9c3b26",
    "texture": "rgba(32,36,31,0.035)", "sidebar_text": "#eef3ee",
}
DARK = {
    "bg_from": "#141b16", "bg_to": "#0c110d", "ink": "#f3ede0", "muted": "#b6ad9b",
    "card_bg": "#1c2620", "card_border": "rgba(243,237,224,0.09)", "shadow": "rgba(0,0,0,0.55)",
    "sidebar_from": "#0d150f", "sidebar_to": "#070b08", "divider": "rgba(217,174,90,0.45)",
    "gold": "#d9ae5a", "forest": "#57a97b", "forest_light": "#87cba2",
    "grassland": "#dcb464", "grassland_light": "#efd393", "rust": "#e2795a",
    "texture": "rgba(243,237,224,0.045)", "sidebar_text": "#eef3ee",
}

# ==================================================================
# DATA
# ==================================================================
@st.cache_data
def load_data():
    return pd.read_csv("Bird_Combined_Cleaned.csv", parse_dates=["Date"])

df = load_data()

# ==================================================================
# SIDEBAR — MODE TOGGLE + FILTERS
# ==================================================================
st.sidebar.markdown("### 🕊️ Aviary Insights")
dark_mode = st.sidebar.toggle("🌙 Dark mode", value=False)
T = DARK if dark_mode else LIGHT

st.sidebar.markdown("---")
st.sidebar.markdown("**Filters**")
habitats = st.sidebar.multiselect("Habitat", options=sorted(df["Habitat"].dropna().unique()), default=sorted(df["Habitat"].dropna().unique()))
admin_units = st.sidebar.multiselect("Administrative Unit", options=sorted(df["Admin_Unit_Code"].dropna().unique()), default=sorted(df["Admin_Unit_Code"].dropna().unique()))
years = st.sidebar.multiselect("Year", options=sorted(df["Year"].dropna().unique()), default=sorted(df["Year"].dropna().unique()))
seasons = st.sidebar.multiselect("Season", options=sorted(df["Season"].dropna().unique()), default=sorted(df["Season"].dropna().unique()))
watchlist_only = st.sidebar.checkbox("🛡️ Show only PIF Watchlist species", value=False)
st.sidebar.markdown("---")
st.sidebar.caption("Data: NPS Bird Monitoring Program · Forest & Grassland units")

filtered = df[df["Habitat"].isin(habitats) & df["Admin_Unit_Code"].isin(admin_units) & df["Year"].isin(years) & df["Season"].isin(seasons)]
if watchlist_only:
    filtered = filtered[filtered["PIF_Watchlist_Status"] == True]  # noqa: E712

HABITAT_COLORS = {"Forest": T["forest"], "Grassland": T["grassland"]}

# ==================================================================
# CSS — dense, no blank lines (Streamlit's markdown parser breaks <style>
# blocks that contain blank lines by injecting <p> tags into them)
# ==================================================================
css = f"""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] {{ font-family: 'Poppins', sans-serif; }}
.stApp {{
background-color: {T["bg_from"]};
background-image: repeating-linear-gradient(135deg, {T["texture"]} 0px, {T["texture"]} 1px, transparent 1px, transparent 42px), linear-gradient(180deg, {T["bg_from"]} 0%, {T["bg_to"]} 100%);
}}
#MainMenu, footer, header {{visibility: hidden;}}
::-webkit-scrollbar {{ width: 9px; height: 9px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {T["gold"]}; border-radius: 10px; }}
@keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: translateY(0); }} }}
.hero {{
background: linear-gradient(120deg, {T["forest"]} 0%, {T["forest_light"]} 55%, {T["grassland"]} 100%);
border-radius: 6px; padding: 2.6rem 2.8rem; margin-bottom: 1.8rem; position: relative; overflow: hidden;
box-shadow: 0 14px 34px {T["shadow"]}; animation: fadeInUp 0.7s ease both; border-bottom: 4px solid {T["gold"]};
}}
.hero::after {{ content: "❦"; position: absolute; right: 40px; top: 50%; transform: translateY(-50%); font-size: 6rem; color: white; opacity: 0.16; }}
.hero .kicker {{ color: rgba(255,255,255,0.85); font-size: 0.74rem; letter-spacing: 0.22em; text-transform: uppercase; font-weight: 600; margin-bottom: 0.6rem; }}
.hero h1 {{ font-family: 'Fraunces', serif; color: white; font-size: 2.7rem; font-weight: 700; margin: 0 0 0.5rem 0; letter-spacing: -0.5px; }}
.hero p {{ color: rgba(255,255,255,0.94); font-size: 1.05rem; margin: 0; max-width: 620px; line-height: 1.55; font-weight: 400; }}
.hero .dropcap {{ font-family: 'Fraunces', serif; font-size: 2.6rem; float: left; line-height: 0.8; margin: 0.1rem 0.35rem 0 0; color: white; font-weight: 700; }}
.kpi-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.6rem; }}
.kpi-card {{
background: {T["card_bg"]}; border-radius: 4px; padding: 1.25rem 1.4rem; border: 1px solid {T["card_border"]};
border-top: 3px solid {T["gold"]}; box-shadow: 0 6px 18px {T["shadow"]}; transition: transform 0.18s ease, box-shadow 0.18s ease;
animation: fadeInUp 0.7s ease both;
}}
.kpi-card:hover {{ transform: translateY(-4px); box-shadow: 0 14px 26px {T["shadow"]}; }}
.kpi-card:nth-child(1) {{ animation-delay: 0.05s; }}
.kpi-card:nth-child(2) {{ animation-delay: 0.12s; }}
.kpi-card:nth-child(3) {{ animation-delay: 0.19s; }}
.kpi-card:nth-child(4) {{ animation-delay: 0.26s; }}
.kpi-value {{ font-family: 'Fraunces', serif; font-size: 2.5rem; font-weight: 700; color: {T["ink"]}; line-height: 1; }}
.kpi-label {{ font-size: 0.72rem; color: {T["muted"]}; text-transform: uppercase; letter-spacing: 0.12em; margin-top: 0.5rem; font-weight: 600; }}
.section-card {{
background: {T["card_bg"]}; border-radius: 4px; padding: 1.4rem 1.5rem 0.7rem 1.5rem; border: 1px solid {T["card_border"]};
box-shadow: 0 6px 16px {T["shadow"]}; margin-bottom: 1.15rem;
}}
.tab-heading {{ margin: 0.4rem 0 1.4rem 0; }}
.tab-kicker {{ font-size: 0.74rem; letter-spacing: 0.2em; text-transform: uppercase; color: {T["gold"]}; font-weight: 700; margin-bottom: 0.3rem; }}
.tab-title {{ font-family: 'Fraunces', serif; font-size: 1.7rem; font-weight: 600; color: {T["ink"]}; }}
.tab-rule {{ height: 1px; background: {T["divider"]}; margin-top: 0.7rem; }}
.chart-title {{
font-family: 'Fraunces', serif; font-size: 1.05rem; font-weight: 600; color: {T["ink"]};
padding-left: 0.7rem; border-left: 3px solid {T["gold"]}; margin: 0.2rem 0 0.9rem 0;
}}
.callout {{
border-left: 3px solid {T["rust"]}; background: transparent; padding: 0.55rem 0 0.55rem 1rem;
font-family: 'Fraunces', serif; font-style: italic; font-size: 1.02rem; color: {T["ink"]}; margin: 0.4rem 0 1.3rem 0;
}}
.callout .src {{ display: block; font-family: 'Poppins', sans-serif; font-style: normal; font-size: 0.72rem; color: {T["muted"]}; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.3rem; }}
.stTabs [data-baseweb="tab-list"] {{ gap: 1.6rem; background: transparent; border-bottom: 1px solid {T["divider"]}; padding-bottom: 0; }}
.stTabs [data-baseweb="tab"] {{
background: transparent !important; border-radius: 0; padding: 10px 2px; font-weight: 600; letter-spacing: 0.04em;
text-transform: uppercase; font-size: 0.74rem; color: {T["muted"]} !important; border-bottom: 2px solid transparent;
}}
.stTabs [aria-selected="true"] {{ color: {T["ink"]} !important; border-bottom: 2px solid {T["gold"]} !important; }}
section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, {T["sidebar_from"]} 0%, {T["sidebar_to"]} 100%); }}
section[data-testid="stSidebar"] * {{ color: {T["sidebar_text"]} !important; }}
section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{ background-color: {T["forest_light"]} !important; }}
hr {{ border-color: {T["divider"]}; }}
h1, h2, h3 {{ color: {T["ink"]}; }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ==================================================================
# CHART THEMING HELPER
# ==================================================================
def chart(fig, **kwargs):
    fig.update_layout(
        font=dict(family="Poppins, sans-serif", color=T["ink"], size=13),
        title_font=dict(family="Fraunces, serif", size=16, color=T["ink"]),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor=T["card_border"], zerolinecolor=T["card_border"], color=T["muted"]),
        yaxis=dict(gridcolor=T["card_border"], zerolinecolor=T["card_border"], color=T["muted"]),
        legend=dict(font=dict(color=T["ink"])),
        margin=dict(t=40, l=10, r=10, b=10),
    )
    fig.update_layout(**kwargs)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def tab_heading(kicker, title):
    st.markdown(f'<div class="tab-heading"><div class="tab-kicker">{kicker}</div><div class="tab-title">{title}</div><div class="tab-rule"></div></div>', unsafe_allow_html=True)


def chart_title(text):
    st.markdown(f'<div class="chart-title">{text}</div>', unsafe_allow_html=True)


def callout(quote, source):
    st.markdown(f'<div class="callout">"{quote}"<span class="src">{source}</span></div>', unsafe_allow_html=True)

# ==================================================================
# HERO
# ==================================================================
st.markdown("""
<div class="hero">
<div class="kicker">NPS Bird Monitoring · Forest vs Grassland</div>
<h1>Aviary Insights</h1>
<p><span class="dropcap">A</span>n editorial field guide to species diversity, seasonal movement, and conservation priorities — drawn from thousands of real observations across forest and grassland habitats.</p>
</div>
""", unsafe_allow_html=True)

# ==================================================================
# KPI ROW
# ==================================================================
n_obs = len(filtered)
n_species = filtered["Scientific_Name"].nunique()
n_units = filtered["Admin_Unit_Code"].nunique()
n_watchlist = filtered.loc[filtered["PIF_Watchlist_Status"] == True, "Common_Name"].nunique()  # noqa: E712

st.markdown(f"""
<div class="kpi-row">
<div class="kpi-card"><div class="kpi-value">{n_obs:,}</div><div class="kpi-label">Total Observations</div></div>
<div class="kpi-card"><div class="kpi-value">{n_species}</div><div class="kpi-label">Unique Species</div></div>
<div class="kpi-card"><div class="kpi-value">{n_units}</div><div class="kpi-label">Administrative Units</div></div>
<div class="kpi-card"><div class="kpi-value">{n_watchlist}</div><div class="kpi-label">Watchlist Species</div></div>
</div>
""", unsafe_allow_html=True)

# ==================================================================
# TABS
# ==================================================================
tab_overview, tab_temporal, tab_spatial, tab_species, tab_env, tab_behavior, tab_observer, tab_conservation, tab_data = st.tabs(
    ["Overview", "Temporal", "Spatial", "Species", "Environment", "Behavior", "Observer", "Conservation", "Raw Data"]
)

# ---------- Overview ----------
with tab_overview:
    tab_heading("01 · The Big Picture", "Overview")
    if len(filtered) > 0:
        top_row = filtered["Common_Name"].value_counts()
        if len(top_row) > 0:
            callout(f"{top_row.index[0]} is the most frequently recorded species in the current selection, spotted {top_row.iloc[0]:,} times.", "Auto-generated from filtered data")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        chart_title("Habitat Split")
        habitat_counts = filtered["Habitat"].value_counts().reset_index()
        habitat_counts.columns = ["Habitat", "Count"]
        fig = px.pie(habitat_counts, names="Habitat", values="Count", hole=0.6, color="Habitat", color_discrete_map=HABITAT_COLORS)
        fig.update_traces(textinfo="percent+label")
        chart(fig, showlegend=False, height=320)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        chart_title("Species Richness by Habitat")
        species_habitat = filtered.groupby("Habitat")["Scientific_Name"].nunique().reset_index(name="Unique_Species")
        fig = px.bar(species_habitat, x="Habitat", y="Unique_Species", color="Habitat", color_discrete_map=HABITAT_COLORS, text="Unique_Species")
        fig.update_traces(textposition="outside")
        chart(fig, showlegend=False, height=320)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    chart_title("Top 10 Most Frequently Observed Species")
    top_overall = filtered["Common_Name"].value_counts().head(10).reset_index()
    top_overall.columns = ["Common_Name", "Count"]
    fig = px.bar(top_overall, x="Count", y="Common_Name", orientation="h", color="Count", color_continuous_scale=[T["forest_light"], T["forest"]])
    fig.update_yaxes(categoryorder="total ascending", title="")
    chart(fig, coloraxis_showscale=False, height=380)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Temporal ----------
with tab_temporal:
    tab_heading("02 · Rhythms Through Time", "Temporal Patterns")
    season_counts_all = filtered["Season"].value_counts()
    if len(season_counts_all) > 0:
        callout(f"{season_counts_all.index[0]} sees the most bird activity, accounting for {season_counts_all.iloc[0]:,} of the recorded observations.", "Auto-generated from filtered data")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        chart_title("Observations by Season")
        season_counts = filtered.groupby(["Season", "Habitat"]).size().reset_index(name="Count")
        fig = px.bar(season_counts, x="Season", y="Count", color="Habitat", barmode="group", color_discrete_map=HABITAT_COLORS, category_orders={"Season": ["Spring", "Summer", "Fall", "Winter"]})
        chart(fig, height=320)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        chart_title("Observations by Year")
        year_counts = filtered.groupby(["Year", "Habitat"]).size().reset_index(name="Count")
        fig = px.line(year_counts, x="Year", y="Count", color="Habitat", markers=True, color_discrete_map=HABITAT_COLORS)
        chart(fig, height=320)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    chart_title("Observations by Month")
    month_counts = filtered.dropna(subset=["Month_Name"]).groupby(["Month_Name", "Habitat"]).size().reset_index(name="Count")
    month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    fig = px.bar(month_counts, x="Month_Name", y="Count", color="Habitat", barmode="group", color_discrete_map=HABITAT_COLORS, category_orders={"Month_Name": month_order})
    chart(fig, height=320, xaxis_title="")
    st.markdown('</div>', unsafe_allow_html=True)
    if "Start_Hour" in filtered.columns:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        chart_title("Observation Start Hour Distribution")
        fig = px.histogram(filtered.dropna(subset=["Start_Hour"]), x="Start_Hour", color="Habitat", barmode="group", nbins=24, color_discrete_map=HABITAT_COLORS)
        chart(fig, height=300)
        st.markdown('</div>', unsafe_allow_html=True)

# ---------- Spatial ----------
with tab_spatial:
    tab_heading("03 · Mapping the Territory", "Spatial Distribution")
    admin_rich = filtered.groupby("Admin_Unit_Code")["Scientific_Name"].nunique().sort_values(ascending=False)
    if len(admin_rich) > 0:
        callout(f"{admin_rich.index[0]} leads in biodiversity with {admin_rich.iloc[0]} unique species recorded within its plots.", "Auto-generated from filtered data")
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    chart_title("Unique Species by Administrative Unit")
    admin_species = filtered.groupby(["Admin_Unit_Code", "Habitat"])["Scientific_Name"].nunique().reset_index(name="Unique_Species")
    fig = px.bar(admin_species, x="Admin_Unit_Code", y="Unique_Species", color="Habitat", barmode="group", color_discrete_map=HABITAT_COLORS)
    chart(fig, height=320, xaxis_title="")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    chart_title("Top 15 Plots by Unique Species Count")
    top_plots = filtered.groupby("Plot_Name")["Scientific_Name"].nunique().sort_values(ascending=False).head(15).reset_index(name="Unique_Species")
    fig = px.bar(top_plots, x="Unique_Species", y="Plot_Name", orientation="h", color="Unique_Species", color_continuous_scale=[T["grassland_light"], T["grassland"]])
    fig.update_yaxes(categoryorder="total ascending", title="")
    chart(fig, coloraxis_showscale=False, height=420)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    chart_title("Total Observations by Administrative Unit")
    admin_obs = filtered.groupby(["Admin_Unit_Code", "Habitat"]).size().reset_index(name="Observations")
    fig = px.bar(admin_obs, x="Admin_Unit_Code", y="Observations", color="Habitat", barmode="stack", color_discrete_map=HABITAT_COLORS)
    chart(fig, height=320, xaxis_title="")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Species ----------
with tab_species:
    tab_heading("04 · Field Notes", "Species Analysis")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        chart_title("Identification Method")
        fig = px.histogram(filtered, x="ID_Method", color="Habitat", barmode="group", color_discrete_map=HABITAT_COLORS)
        chart(fig, height=300, xaxis_title="")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        chart_title("Sex Ratio")
        fig = px.histogram(filtered, x="Sex", color="Habitat", barmode="group", color_discrete_map=HABITAT_COLORS)
        chart(fig, height=300, xaxis_title="")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    chart_title("Unique Species Detected by Visit Number")
    visit_species = filtered.groupby("Visit")["Scientific_Name"].nunique().reset_index(name="Unique_Species")
    fig = px.bar(visit_species, x="Visit", y="Unique_Species", color="Unique_Species", color_continuous_scale=[T["forest_light"], T["rust"]])
    chart(fig, coloraxis_showscale=False, height=300)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    chart_title("Species Breakdown")
    species_table = filtered.groupby(["Common_Name", "Scientific_Name", "Habitat"]).size().reset_index(name="Observations").sort_values("Observations", ascending=False)
    st.dataframe(species_table, use_container_width=True, height=300, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Environment ----------
with tab_env:
    tab_heading("05 · Conditions in the Field", "Environmental Factors")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        chart_title("Temperature Distribution")
        fig = px.histogram(filtered, x="Temperature", color="Habitat", nbins=30, barmode="overlay", opacity=0.65, color_discrete_map=HABITAT_COLORS)
        chart(fig, height=300)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        chart_title("Humidity Distribution")
        fig = px.histogram(filtered, x="Humidity", color="Habitat", nbins=30, barmode="overlay", opacity=0.65, color_discrete_map=HABITAT_COLORS)
        chart(fig, height=300)
        st.markdown('</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        chart_title("Sky Condition")
        sky_counts = filtered.groupby(["Sky", "Habitat"]).size().reset_index(name="Count")
        fig = px.bar(sky_counts, x="Count", y="Sky", color="Habitat", orientation="h", color_discrete_map=HABITAT_COLORS)
        chart(fig, height=300, yaxis_title="")
        st.markdown('</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        chart_title("Disturbance Effect")
        disturbance_counts = filtered.groupby(["Disturbance", "Habitat"]).size().reset_index(name="Count")
        fig = px.bar(disturbance_counts, x="Count", y="Disturbance", color="Habitat", orientation="h", color_discrete_map=HABITAT_COLORS)
        chart(fig, height=300, yaxis_title="")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    chart_title("Temperature vs Humidity")
    fig = px.scatter(filtered, x="Temperature", y="Humidity", color="Habitat", opacity=0.55, color_discrete_map=HABITAT_COLORS)
    chart(fig, height=380)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Behavior ----------
with tab_behavior:
    tab_heading("06 · Up Close", "Distance & Behavior")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        chart_title("Observation Distance")
        fig = px.histogram(filtered, x="Distance", color="Habitat", barmode="group", color_discrete_map=HABITAT_COLORS)
        chart(fig, height=320, xaxis_title="")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        chart_title("Flyover Frequency")
        fig = px.histogram(filtered, x="Flyover_Observed", color="Habitat", barmode="group", color_discrete_map=HABITAT_COLORS)
        chart(fig, height=320, xaxis_title="")
        st.markdown('</div>', unsafe_allow_html=True)

# ---------- Observer ----------
with tab_observer:
    tab_heading("07 · The Watchers", "Observer Trends")
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    chart_title("Observations Logged per Observer")
    observer_counts = filtered["Observer"].value_counts().reset_index()
    observer_counts.columns = ["Observer", "Observations"]
    fig = px.bar(observer_counts, x="Observer", y="Observations", color="Observations", color_continuous_scale=[T["forest_light"], T["rust"]])
    chart(fig, coloraxis_showscale=False, height=320, xaxis_title="")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    chart_title("Unique Species Detected per Observer")
    observer_species = filtered.groupby("Observer")["Scientific_Name"].nunique().reset_index(name="Unique_Species")
    fig = px.bar(observer_species, x="Observer", y="Unique_Species", color="Unique_Species", color_continuous_scale=[T["grassland_light"], T["forest"]])
    chart(fig, coloraxis_showscale=False, height=320, xaxis_title="")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Conservation ----------
with tab_conservation:
    tab_heading("08 · A Call to Protect", "Conservation Insights")
    watchlist_df = filtered[filtered["PIF_Watchlist_Status"] == True]  # noqa: E712
    if len(watchlist_df) > 0:
        wl_top = watchlist_df["Common_Name"].value_counts()
        callout(f"{wl_top.index[0]} is the most frequently observed species on the PIF Watchlist, with {wl_top.iloc[0]} sightings in this selection.", "Auto-generated from filtered data")
    st.markdown(f"""
<div class="kpi-row" style="grid-template-columns: repeat(2, 1fr);">
<div class="kpi-card"><div class="kpi-value">{len(watchlist_df):,}</div><div class="kpi-label">Watchlist Observations</div></div>
<div class="kpi-card"><div class="kpi-value">{watchlist_df['Common_Name'].nunique()}</div><div class="kpi-label">Watchlist Species</div></div>
</div>
""", unsafe_allow_html=True)
    if len(watchlist_df) > 0:
        c1, c2 = st.columns([1.4, 1])
        with c1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            chart_title("PIF Watchlist Species Observed")
            wl_counts = watchlist_df["Common_Name"].value_counts().reset_index()
            wl_counts.columns = ["Common_Name", "Count"]
            fig = px.bar(wl_counts, x="Count", y="Common_Name", orientation="h", color_discrete_sequence=[T["rust"]])
            fig.update_yaxes(categoryorder="total ascending", title="")
            chart(fig, height=380)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            chart_title("By Habitat")
            wl_habitat = watchlist_df.groupby("Habitat").size().reset_index(name="Count")
            fig = px.pie(wl_habitat, names="Habitat", values="Count", hole=0.55, color="Habitat", color_discrete_map=HABITAT_COLORS)
            chart(fig, height=380)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No watchlist species in the current filter selection.")
    if "Regional_Stewardship_Status" in filtered.columns:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        chart_title("Regional Stewardship Priority Species")
        steward_counts = filtered.groupby(["Regional_Stewardship_Status", "Habitat"]).size().reset_index(name="Count")
        fig = px.bar(steward_counts, x="Regional_Stewardship_Status", y="Count", color="Habitat", barmode="group", color_discrete_map=HABITAT_COLORS)
        chart(fig, height=300, xaxis_title="")
        st.markdown('</div>', unsafe_allow_html=True)

# ---------- Raw Data ----------
with tab_data:
    tab_heading("09 · The Ledger", "Raw Data")
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.download_button("⬇ Download filtered data as CSV", data=filtered.to_csv(index=False).encode("utf-8"), file_name="bird_observations_filtered.csv", mime="text/csv")
    st.markdown('</div>', unsafe_allow_html=True)
