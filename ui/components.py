import streamlit as st
import pandas as pd
import plotly.express as px

def kpi_cards(kpi: dict) -> None:
    col1, col2, col3 = st.columns(3)
    col1.metric("Средний балл", kpi["avg_score"])
    col2.metric("Образцов",     kpi["sample_count"])
    col3.metric("Методов обраб.", len(kpi["process_share"]))

def spider_chart(row: pd.Series) -> None:
    fig = px.line_polar(
        r=row[["aroma", "flavor", "aftertaste", "acidity", "body", "balance"]],
        theta=["Aroma", "Flavor", "Aftertaste", "Acidity", "Body", "Balance"],
        line_close=True,
        template="plotly_white",
    )
    fig.update_traces(fill='toself')
    st.plotly_chart(fig, use_container_width=True)
