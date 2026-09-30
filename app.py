import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
import streamlit as st

st.set_page_config(page_title="Heart Disease Risk", page_icon="❤️", layout="centered")


@st.cache_resource
def load_model():
    return joblib.load("models/heart_disease_model.joblib")


saved = load_model()
model = saved["model"]
threshold = saved["threshold"]


@st.cache_resource
def load_explainer():
    return shap.TreeExplainer(model.named_steps["model"])


explainer = load_explainer()

CP_OPTIONS = {
    "Typical angina": 1,
    "Atypical angina": 2,
    "Non-anginal pain": 3,
    "Asymptomatic (no chest pain)": 4,
}
RESTECG_OPTIONS = {
    "Normal": 0,
    "ST-T wave abnormality": 1,
    "Left ventricular hypertrophy": 2,
}
SLOPE_OPTIONS = {
    "Upsloping": 1,
    "Flat": 2,
    "Downsloping": 3,
}
THAL_OPTIONS = {
    "Normal": 3.0,
    "Fixed defect": 6.0,
    "Reversible defect": 7.0,
}

FRIENDLY_NAMES = {
    "age": "Age",
    "sex": "Sex",
    "trestbps": "Resting blood pressure",
    "chol": "Cholesterol",
    "fbs": "Fasting blood sugar > 120",
    "thalach": "Max heart rate",
    "exang": "Chest pain during exercise",
    "oldpeak": "ST depression",
    "ca": "Vessels colored by fluoroscopy",
    "cp_1": "Chest pain: typical angina",
    "cp_2": "Chest pain: atypical angina",
    "cp_3": "Chest pain: non-anginal",
    "cp_4": "Chest pain: asymptomatic",
    "restecg_0": "Resting ECG: normal",
    "restecg_1": "Resting ECG: ST-T abnormality",
    "restecg_2": "Resting ECG: LV hypertrophy",
    "slope_1": "ST slope: upsloping",
    "slope_2": "ST slope: flat",
    "slope_3": "ST slope: downsloping",
    "thal_3.0": "Thalassemia: normal",
    "thal_6.0": "Thalassemia: fixed defect",
    "thal_7.0": "Thalassemia: reversible defect",
}

st.title("Heart Disease Risk Predictor")
st.write("Enter a patient's clinical test results to estimate their risk of heart disease.")

with st.form("patient_form"):
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Age", min_value=20, max_value=100, value=55)
        sex = st.selectbox("Sex", ["Male", "Female"])
        cp = st.selectbox("Chest pain type", list(CP_OPTIONS.keys()))
        trestbps = st.number_input("Resting blood pressure (mm Hg)", min_value=80, max_value=220, value=130)
        chol = st.number_input("Cholesterol (mg/dl)", min_value=100, max_value=600, value=240)
        fbs = st.selectbox("Fasting blood sugar above 120 mg/dl?", ["No", "Yes"])
        restecg = st.selectbox("Resting ECG result", list(RESTECG_OPTIONS.keys()))

    with col2:
        thalach = st.number_input("Max heart rate during stress test", min_value=60, max_value=220, value=150)
        exang = st.selectbox("Chest pain during exercise?", ["No", "Yes"])
        oldpeak = st.number_input("ST depression (oldpeak)", min_value=0.0, max_value=7.0, value=1.0, step=0.1)
        slope = st.selectbox("ST segment slope", list(SLOPE_OPTIONS.keys()))
        ca = st.selectbox("Major vessels colored by fluoroscopy", [0, 1, 2, 3])
        thal = st.selectbox("Thalassemia test result", list(THAL_OPTIONS.keys()))

    submitted = st.form_submit_button("Predict risk")

if submitted:
    patient = pd.DataFrame([{
        "age": age,
        "sex": 1 if sex == "Male" else 0,
        "cp": CP_OPTIONS[cp],
        "trestbps": trestbps,
        "chol": chol,
        "fbs": 1 if fbs == "Yes" else 0,
        "restecg": RESTECG_OPTIONS[restecg],
        "thalach": thalach,
        "exang": 1 if exang == "Yes" else 0,
        "oldpeak": oldpeak,
        "slope": SLOPE_OPTIONS[slope],
        "ca": float(ca),
        "thal": THAL_OPTIONS[thal],
    }])

    prob = model.predict_proba(patient)[:, 1][0]

    st.subheader("Result")
    st.metric("Estimated risk of heart disease", f"{prob:.0%}")

    if prob >= threshold:
        st.error(f"Flagged for further evaluation: the estimated risk is at or above the {threshold:.0%} screening cutoff.")
    else:
        st.success(f"Not flagged: the estimated risk is below the {threshold:.0%} screening cutoff.")

    st.caption(
        f"The cutoff is set at {threshold:.0%} instead of 50% on purpose: missing a sick patient "
        "is more dangerous than a false alarm, so the model leans toward caution."
    )

    preprocess = model.named_steps["preprocess"]
    feature_names = [name.split("__")[1] for name in preprocess.get_feature_names_out()]
    patient_transformed = pd.DataFrame(preprocess.transform(patient), columns=feature_names)

    explanation = explainer(patient_transformed)[0]

    input_display = {
        "age": str(age),
        "sex": sex,
        "trestbps": str(trestbps),
        "chol": str(chol),
        "fbs": fbs,
        "thalach": str(thalach),
        "exang": exang,
        "oldpeak": f"{oldpeak:.1f}",
        "ca": str(ca),
    }

    labels = []
    for name, value in zip(feature_names, patient_transformed.iloc[0]):
        if name in input_display:
            labels.append(input_display[name])
        else:
            labels.append("Yes" if value == 1 else "No")

    explanation.data = np.array(labels, dtype=object)
    explanation.feature_names = [FRIENDLY_NAMES.get(name, name) for name in feature_names]

    st.subheader("Why this result?")
    st.write("Red bars pushed the risk **up**, blue bars pushed it **down**. Longer bars had more influence.")

    shap.plots.waterfall(explanation, max_display=10, show=False)
    fig = plt.gcf()
    st.pyplot(fig)
    plt.close(fig)

    st.caption(
        "A low score does not rule out heart disease. This tool is an educational project "
        "and supports clinical judgment; it does not replace it."
    )