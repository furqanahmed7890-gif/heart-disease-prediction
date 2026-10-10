import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine

load_dotenv(".env", override=True)

local_engine = create_engine(URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME"),
))

neon_engine = create_engine(URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("NEON_USER"),
    password=os.getenv("NEON_PASSWORD"),
    host=os.getenv("NEON_HOST"),
    port=5432,
    database=os.getenv("NEON_DB"),
    query={"sslmode": "require"},
))

df = pd.read_sql("SELECT * FROM patients", local_engine)
df.to_sql("patients", neon_engine, if_exists="replace", index=False)

check = pd.read_sql("SELECT COUNT(*) AS patients FROM patients", neon_engine)
print("Rows in Neon:", int(check["patients"].iloc[0]))