import pandas as pd
import streamlit as st
from sklearn.manifold import TSNE
import umap

FEATURES = ["aroma", "flavor", "aftertaste", "acidity", "body", "balance"]

@st.cache_data(show_spinner=True)
def tsne_3d(df: pd.DataFrame) -> pd.DataFrame:
    X = df[FEATURES].values
    emb = TSNE(n_components=3, perplexity=30, random_state=42).fit_transform(X)
    return pd.DataFrame(emb, columns=["x", "y", "z"])

@st.cache_data(show_spinner=True)
def umap_3d(df: pd.DataFrame) -> pd.DataFrame:
    X = df[FEATURES].values
    reducer = umap.UMAP(n_components=3, random_state=42)
    emb = reducer.fit_transform(X)
    return pd.DataFrame(emb, columns=["x", "y", "z"])
