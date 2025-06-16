import streamlit as st
from repository.database import fetch_df
from services.analytics import compute_kpi, predict_score
from services.projection import tsne_3d, umap_3d
from ui.components import kpi_cards, spider_chart

st.set_page_config("Coffee Quality Explorer", layout="wide")
st.title("☕ Coffee Quality Explorer")

# Sidebar filters
countries = fetch_df(
    "SELECT DISTINCT country_of_origin FROM arabica ORDER BY 1"
).squeeze().tolist()

country = st.sidebar.selectbox("Country", ["All"] + countries)
process = st.sidebar.selectbox(
    "Processing method",
    ["All"] + fetch_df(
        "SELECT DISTINCT processing_method FROM arabica WHERE processing_method IS NOT NULL"
    ).squeeze().tolist()
)

where, params = [], []
if country != "All":
    where.append("country_of_origin = ?")
    params.append(country)
if process != "All":
    where.append("processing_method = ?")
    params.append(process)

sql = "SELECT * FROM arabica"
if where:
    sql += " WHERE " + " AND ".join(where)

df = fetch_df(sql, tuple(params))

# Tabs
tab_overview, tab_cluster, tab_detail = st.tabs(["Overview", "Clusters", "Sample detail"])

with tab_overview:
    st.subheader("Обзор выборки")
    kpi_cards(compute_kpi(df))
    st.dataframe(df, use_container_width=True, height=400)

with tab_cluster:
    st.subheader("Кластеризация")
    method = st.selectbox("Метод проекции", ["t-SNE", "UMAP"])
    emb_df = tsne_3d(df) if method == "t-SNE" else umap_3d(df)
    emb_df["country"] = df["country_of_origin"].values

    fig = st.plotly_chart(
        __import__("plotly.express").express.scatter_3d(
            emb_df, x="x", y="y", z="z",
            color="country",
            size_max=6,
            opacity=0.7,
            height=600,
        ),
        use_container_width=True
    )

with tab_detail:
    st.subheader("Детальный просмотр образца")
    sample = st.selectbox("ID образца", df.index)
    row = df.loc[sample]
    spider_chart(row)

    st.markdown("##### What-if")
    aroma   = st.slider("Aroma",   0.0, 10.0, float(row["aroma"]),   0.25)
    acidity = st.slider("Acidity", 0.0, 10.0, float(row["acidity"]), 0.25)
    predicted = predict_score(row, aroma, acidity)
    st.metric("Прогноз оценки", predicted, delta=predicted - row["total_cup_points"])
