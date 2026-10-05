import os

import streamlit as st

st.title("About This Project")

st.markdown("""
This app predicts the risk of heart disease from 13 clinical measurements, explains each
prediction, and presents findings from the underlying data. It was built as an end-to-end
portfolio project covering data storage, analysis, machine learning, and deployment.

### The data
The [UCI Heart Disease dataset](https://archive.ics.uci.edu/dataset/45/heart+disease)
(Cleveland subset): 303 patients referred for cardiac testing. After removing 6 rows with
missing values, 297 patients remain, 46% of whom had heart disease. The original 0–4
severity score was converted to a yes/no target, because the higher severity levels have
too few patients to model reliably.

### How the model was built
1. **Stored** the cleaned data in PostgreSQL using SQLAlchemy.
2. **Explored** it with SQL and Python to find patterns and data quality issues.
3. **Held out** 20% of patients as a final test set the model never saw during training.
4. **Compared** a "lazy guesser" baseline, logistic regression, and XGBoost.
   Cross-validation showed logistic regression and XGBoost were statistically tied
   (about 81% accuracy). XGBoost was chosen for its slightly more stable results.
5. **Lowered the decision threshold** from 50% to 35%, chosen using training data only,
   because missing a sick patient is more harmful than a false alarm.
6. **Explained** predictions with SHAP, so every result shows which measurements drove it.

### Results
| Measure | Cross-validated (training data) | Held-out test set (60 patients) |
|---|---|---|
| Accuracy | ~81% | 90% |
| Recall (sick patients caught) | ~82% | 89% |
| Precision (flags that were correct) | ~77% | 89% |
| ROC AUC | — | 0.92 |

The test set scores are higher than cross-validation, which suggests the test split was a
relatively easy draw. The cross-validated numbers are the more reliable estimate.
""")

st.markdown("### What drives the model's predictions")
if os.path.exists("images/shap_summary.png"):
    st.image("images/shap_summary.png")
st.markdown("""
The strongest signals are the number of blocked vessels on imaging, asymptomatic chest pain,
thalassemia test results, and ST depression during exercise. These match established
clinical risk factors, which suggests the model learned meaningful patterns.
""")

st.markdown("""
### Limitations
- **Small dataset.** 297 patients from a single clinic, collected in the 1980s.
- **Referred patients only.** Everyone in the data was already suspected of heart disease,
  so the model is not suited to screening the general public.
- **Relies on hospital tests.** The strongest inputs come from stress tests and imaging.
- **Women are underrepresented**, so predictions for women are less certain.
- **Some patients look healthy on every test** yet have disease. No model trained on these
  13 measurements can reliably catch them.
- **Not a medical device.** This is an educational project and has not been clinically validated.

### Tech stack
Python, pandas, PostgreSQL, SQLAlchemy, scikit-learn, XGBoost, SHAP, Streamlit

### Source code
[github.com/furqanahmed7890-gif/heart-disease-prediction](https://github.com/furqanahmed7890-gif/heart-disease-prediction)
""")