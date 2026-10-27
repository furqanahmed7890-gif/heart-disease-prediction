"""Exports the patients table to app_data/patients.csv.

The app uses it when no database is configured (for example the public demo), running the same SQL
against an in-memory SQLite copy.
"""
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine

SNAPSHOT = Path(__file__).parent / "app_data"

load_dotenv(".env", override=True)
engine = create_engine(URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME"),
))

SNAPSHOT.mkdir(exist_ok=True)
df = pd.read_sql("SELECT * FROM patients", engine)
df.to_csv(SNAPSHOT / "patients.csv", index=False)
print(f"patients: {len(df)} rows")
