import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine

load_dotenv(".env", override=True)


def get_setting(name):
    value = os.getenv(name)
    if value is None:
        value = st.secrets[name]
    return value


@st.cache_resource
def get_engine():
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=get_setting("DB_USER"),
        password=get_setting("DB_PASSWORD"),
        host=get_setting("DB_HOST"),
        port=int(get_setting("DB_PORT")),
        database=get_setting("DB_NAME"),
        query={"sslmode": get_setting("DB_SSLMODE")},
    )
    return create_engine(url, pool_pre_ping=True)


@st.cache_data(ttl=600)
def run_query(sql):
    return pd.read_sql(sql, get_engine())