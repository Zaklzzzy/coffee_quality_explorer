import pathlib
import sqlite3
from typing import Tuple

import pandas as pd
import streamlit as st

DB_PATH = pathlib.Path("coffee.db")

@st.cache_resource
def get_conn() -> sqlite3.Connection:
    """
    Кешируемое соединение с SQLite
    """
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@st.cache_data(show_spinner=False)
def fetch_df(sql: str, params: Tuple = ()) -> pd.DataFrame:
    """
    Выполняет SELECT и возвращает DataFrame
    """
    return pd.read_sql_query(sql, get_conn(), params=params)
