import streamlit as st
import plotly.express as px
import numpy as np
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

country = st.sidebar.selectbox("Страна", ["All"] + countries)
process = st.sidebar.selectbox(
    "Способ обработки",
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
    if len(df) < 3:
        st.info("Нужно ≥ 3 образцов для проекции. Расширьте фильтр.")
        st.stop()
    else:
        method = st.selectbox("Метод проекции", ["t-SNE", "UMAP"])
        try:
            emb_df = tsne_3d(df) if method == "t-SNE" else umap_3d(df)
            emb_df["country"] = df["country_of_origin"].values

            lot_repr = np.where(
                df["lot_number"].isna(),
                "ID_" + df.index.astype(str),
                df["lot_number"].astype(str)
            )
            emb_df["label"] = (
                lot_repr
                + " · "
                + df["farm_name"].fillna("").astype(str)
                + " · "
                + df["total_cup_points"].round(1).astype(str)
            )
            emb_df["score"]  = df["total_cup_points"].round(1)
            emb_df["method"] = df["processing_method"].fillna("Unknown")

            fig = px.scatter_3d(
                emb_df,
                x="x", y="y", z="z",
                color="country",
                hover_name="label",
                hover_data={
                    "country": True,
                    "score":  True,
                    "method": True
                },
                opacity=0.7,
                height=600,
            )
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)
        except ValueError as e:
            st.warning(str(e))

with tab_detail:
    st.subheader("Детальный просмотр образца")
    if df.empty:
        st.info("Нет данных для отображения.")
        st.stop()

    lot_repr = np.where(
        df["lot_number"].isna(),
        "ID_" + df.index.astype(str),
        df["lot_number"].astype(str)
    )

    df["label"] = (
        lot_repr
        + " · "
        + df["farm_name"].fillna("").astype(str)
        + " · "
        + df["total_cup_points"].round(1).astype(str)
    )

    sample_label = st.selectbox("Выберите образец", df["label"])
    row = df.loc[df["label"] == sample_label].squeeze()

    spider_chart(row)

    st.markdown("##### What-if / Что будет, если")
    aroma   = st.slider("Аромат (Aroma)",   0.0, 10.0, float(row["aroma"]),   0.25)
    acidity = st.slider("Кислотность (Acidity)", 0.0, 10.0, float(row["acidity"]), 0.25)
    predicted = predict_score(row, aroma, acidity)
    delta = predicted - row["total_cup_points"]
    st.metric("Прогноз оценки", f"{predicted:.2f}", delta=f"{delta:+.2f}")