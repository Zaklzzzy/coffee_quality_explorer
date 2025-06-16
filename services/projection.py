import pandas as pd
import streamlit as st
from sklearn.manifold import TSNE
import umap

FEATURES = ["aroma", "flavor", "aftertaste", "acidity", "body", "balance"]

def _safe_len(df: pd.DataFrame) -> int:
    return len(df.dropna(subset=FEATURES))

@st.cache_data(show_spinner=True)
def tsne_3d(df: pd.DataFrame) -> pd.DataFrame:
    n = _safe_len(df)
    if n < 4:
        raise ValueError("t-SNE требует ≥ 4 строк данных.")
    perp = max(5, min(50, (n // 3)))
    emb = TSNE(
        n_components=3,
        perplexity=perp,
        random_state=42,
        learning_rate="auto",
    ).fit_transform(df[FEATURES].values)
    return pd.DataFrame(emb, columns=["x", "y", "z"])

@st.cache_data(show_spinner=True)
def umap_3d(df: pd.DataFrame) -> pd.DataFrame:
    n = _safe_len(df)
    if n < 3:
        raise ValueError("UMAP требует ≥ 3 строк данных.")
    n_neighbors = max(2, min(15, n // 2))
    reducer = umap.UMAP(
        n_components=3,
        n_neighbors=n_neighbors,
        random_state=42,
    )
    emb = reducer.fit_transform(df[FEATURES].values)
    return pd.DataFrame(emb, columns=["x", "y", "z"])
