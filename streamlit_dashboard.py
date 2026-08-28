"""
Bird Species Observation Dashboard
-----------------------------------
Interactive Streamlit + Plotly dashboard for the cleaned bird monitoring dataset.

Run with:
    pip install streamlit plotly pandas
    streamlit run streamlit_dashboard.py

Expects `Bird_Combined_Cleaned.csv` (produced by Bird_Species_Analysis.ipynb)
in the same folder.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Bird Species Observation Dashboard", layout="wide")


@st.cache_data
def load_data():
    df = pd.read_csv("Bird_Combined_Cleaned.csv", parse_dates=["Date"])
    return df


df = load_data()

st.title("🐦 Bird Species Observation Dashboard")
st.caption("Forest vs Grassland habitats — NPS bird monitoring data")

# ---------------- Sidebar filters ----------------
st.sidebar.header("Filters")

habitats = st.sidebar.multiselect(
    "Habitat", options=sorted(df["Habitat"].dropna().unique()),
    default=sorted(df["Habitat"].dropna().unique())
)
admin_units = st.sidebar.multiselect(
    "Administrative Unit", options=sorted(df["Admin_Unit_Code"].dropna().unique()),
    default=sorted(df["Admin_Unit_Code"].dropna().unique())
)
years = st.sidebar.multiselect(
    "Year", options=sorted(df["Year"].dropna().unique()),
    default=sorted(df["Year"].dropna().unique())
)
seasons = st.sidebar.multiselect(
    "Season", options=sorted(df["Season"].dropna().unique()),
    default=sorted(df["Season"].dropna().unique())
)
watchlist_only = st.sidebar.checkbox("Show only PIF Watchlist species", value=False)

filtered = df[
    df["Habitat"].isin(habitats)
    & df["Admin_Unit_Code"].isin(admin_units)
    & df["Year"].isin(years)
    & df["Season"].isin(seasons)
]
if watchlist_only:
    filtered = filtered[filtered["PIF_Watchlist_Status"] == True]  # noqa: E712

# ---------------- KPI row ----------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Observations", f"{len(filtered):,}")
col2.metric("Unique Species", filtered["Scientific_Name"].nunique())
col3.metric("Admin Units", filtered["Admin_Unit_Code"].nunique())
col4.metric("Watchlist Species", filtered.loc[filtered["PIF_Watchlist_Status"] == True, "Common_Name"].nunique())  # noqa: E712

st.divider()

# ---------------- Row 1: Temporal ----------------
c1, c2 = st.columns(2)
with c1:
    season_counts = filtered.groupby(["Season", "Habitat"]).size().reset_index(name="Count")
    fig = px.bar(season_counts, x="Season", y="Count", color="Habitat", barmode="group",
                 category_orders={"Season": ["Spring", "Summer", "Fall", "Winter"]},
                 title="Observations by Season")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    year_counts = filtered.groupby(["Year", "Habitat"]).size().reset_index(name="Count")
    fig = px.line(year_counts, x="Year", y="Count", color="Habitat", markers=True,
                   title="Observations by Year")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Row 2: Species ----------------
c3, c4 = st.columns(2)
with c3:
    top_species = filtered["Common_Name"].value_counts().head(10).reset_index()
    top_species.columns = ["Common_Name", "Count"]
    fig = px.bar(top_species, x="Count", y="Common_Name", orientation="h",
                 title="Top 10 Most Observed Species")
    fig.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig, use_container_width=True)

with c4:
    admin_species = filtered.groupby(["Admin_Unit_Code", "Habitat"])["Scientific_Name"].nunique().reset_index(name="Unique_Species")
    fig = px.bar(admin_species, x="Admin_Unit_Code", y="Unique_Species", color="Habitat", barmode="group",
                 title="Unique Species by Administrative Unit")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Row 3: Environment ----------------
c5, c6 = st.columns(2)
with c5:
    fig = px.histogram(filtered, x="Temperature", color="Habitat", nbins=30, barmode="overlay",
                        opacity=0.6, title="Temperature Distribution")
    st.plotly_chart(fig, use_container_width=True)

with c6:
    disturbance_counts = filtered.groupby(["Disturbance", "Habitat"]).size().reset_index(name="Count")
    fig = px.bar(disturbance_counts, x="Count", y="Disturbance", color="Habitat", orientation="h",
                 title="Disturbance Effect on Observations")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Row 4: Conservation ----------------
st.subheader("Conservation Watchlist")
watchlist_df = filtered[filtered["PIF_Watchlist_Status"] == True]  # noqa: E712
if len(watchlist_df) > 0:
    wl_counts = watchlist_df["Common_Name"].value_counts().reset_index()
    wl_counts.columns = ["Common_Name", "Count"]
    fig = px.bar(wl_counts, x="Count", y="Common_Name", orientation="h",
                 title="PIF Watchlist Species Observed", color_discrete_sequence=["crimson"])
    fig.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No watchlist species in the current filter selection.")

# ---------------- Raw data ----------------
with st.expander("View filtered raw data"):
    st.dataframe(filtered)
