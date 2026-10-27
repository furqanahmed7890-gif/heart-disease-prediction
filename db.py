import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.pool import StaticPool

load_dotenv(".env", override=True)

SNAPSHOT = Path(__file__).parent / "app_data"


def get_setting(name):
    value = os.getenv(name)
    if value is None:
        try:
            value = st.secrets.get(name)
        except FileNotFoundError:
            value = None
    return value


def using_postgres():
    return get_setting("DB_HOST") is not None


def data_source():
    return "PostgreSQL" if using_postgres() else "a SQLite snapshot of the PostgreSQL table"


def snapshot_engine():
    """In-memory SQLite copy of app_data/, used when no database is configured (e.g. the public demo)."""
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    for csv in SNAPSHOT.glob("*.csv"):
        pd.read_csv(csv).to_sql(csv.stem, engine, index=False)
    return engine


@st.cache_resource
def get_engine():
    if not using_postgres():
        return snapshot_engine()
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
