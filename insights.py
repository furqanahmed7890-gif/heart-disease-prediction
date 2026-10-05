import streamlit as st

from db import run_query

st.title("Data Insights")
st.write(
    "Findings from 297 patients in the UCI Cleveland heart disease dataset. "
    "Every chart below is generated live from a SQL query against PostgreSQL."
)

overview = run_query("""
    SELECT
        COUNT(*) AS patients,
        ROUND(AVG(target) * 100, 1) AS disease_rate_pct,
        ROUND(AVG(age), 1) AS avg_age
    FROM patients
""")

col1, col2, col3 = st.columns(3)
col1.metric("Patients", int(overview["patients"].iloc[0]))
col2.metric("With heart disease", f"{float(overview['disease_rate_pct'].iloc[0])}%")
col3.metric("Average age", float(overview["avg_age"].iloc[0]))


def show_chart(title, sql, x_col, takeaway):
    st.subheader(title)
    data = run_query(sql)
    st.bar_chart(data, x=x_col, y="disease_rate_pct", x_label="", y_label="Disease rate (%)", horizontal=True)
    st.write(takeaway)
    with st.expander("See the data and SQL"):
        st.dataframe(data, hide_index=True)
        st.code(sql, language="sql")


show_chart(
    "Disease rate by chest pain type",
    """
SELECT
    CASE cp
        WHEN 1 THEN '1. Typical angina'
        WHEN 2 THEN '2. Atypical angina'
        WHEN 3 THEN '3. Non-anginal pain'
        ELSE '4. Asymptomatic'
    END AS chest_pain_type,
    COUNT(*) AS patients,
    ROUND(AVG(target) * 100, 1) AS disease_rate_pct
FROM patients
GROUP BY cp
ORDER BY cp
""",
    "chest_pain_type",
    "Patients with **no chest pain** had the highest disease rate. This likely reflects "
    "referral bias: every patient was sent for cardiac testing, so those without pain "
    "were referred for other warning signs.",
)

show_chart(
    "Disease rate by sex",
    """
SELECT
    CASE WHEN sex = 1 THEN 'Male' ELSE 'Female' END AS sex_label,
    COUNT(*) AS patients,
    ROUND(AVG(target) * 100, 1) AS disease_rate_pct
FROM patients
GROUP BY sex
""",
    "sex_label",
    "Men had a disease rate of XX.X%, about twice the rate for women (XX.X%). Women make up "
    "only about a third of the dataset, so their estimate is less certain.",
)

show_chart(
    "Disease rate by age group",
    """
SELECT
    CASE
        WHEN age < 45 THEN '1. Under 45'
        WHEN age < 55 THEN '2. 45-54'
        WHEN age < 65 THEN '3. 55-64'
        ELSE '4. 65+'
    END AS age_group,
    COUNT(*) AS patients,
    ROUND(AVG(target) * 100, 1) AS disease_rate_pct
FROM patients
GROUP BY age_group
ORDER BY age_group
""",
    "age_group",
    "Risk rises steadily through age 64. The dip at 65+ is based on only 41 patients "
    "and likely reflects referral patterns, so it should be read with caution.",
)