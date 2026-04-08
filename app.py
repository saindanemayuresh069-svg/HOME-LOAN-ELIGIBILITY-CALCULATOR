import streamlit as st
from calculator import home_loan_calculator

# Page config
st.set_page_config(
    page_title="Home Loan Eligibility Calculator",
    page_icon="🏠",
    layout="wide"
)

# Styling
st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}
.stButton>button {
    background-color: #1f77b4;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
}
.stMetric {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([1.5, 5])

with col1:
    try:
        st.image("logo.png", width=120)
    except:
        pass

with col2:
    st.markdown("""
    <h1>🏠 Home Loan Eligibility Calculator</h1>
    <p>Developed by <b><i>Mayuresh Saindane</i></b></p>
    """, unsafe_allow_html=True)

# Tabs
tab1, tab2 = st.tabs(["Calculator", "FOIR Settings"])

# FOIR SETTINGS TAB
with tab2:
    st.subheader("FOIR Settings")

    st.write("""
    Default Rules:
    - <50K → 40%
    - 50K–1L → 50%
    - >1L → 60%
    - Cap: 55% (<75K), 60% otherwise
    """)

    override = st.checkbox("Override FOIR")

    custom_foir = None

    if override:
        custom_foir = st.slider("Set FOIR (%)", 10, 60, 50)
        st.warning("Custom FOIR Applied")

    st.session_state["custom_foir"] = custom_foir

# CALCULATOR TAB
with tab1:

    left, right = st.columns([2, 1])

    with left:
        st.subheader("Enter Details")

        income = st.number_input("Gross Income (₹)", value=0)
        obligations = st.number_input("Existing EMI (₹)", value=0)
        age = st.number_input("Age", value=30)
        roi = st.number_input("Interest Rate (%)", value=8.5)

        emp_type = st.selectbox("Employment Type", ["government", "private"])

        st.markdown("### Rental Income")
        rental_income = st.number_input("Rental Income (₹)", value=0)
        rental_type = st.selectbox("Rental Type", ["None", "notary", "registered"])

        st.markdown("### Incentive Income")
        incentive_type = st.selectbox("Incentive Type", ["None", "monthly", "yearly"])

        monthly_incentives = []
        y1 = y2 = y3 = 0

        if incentive_type == "monthly":
            for i in range(6):
                val = st.number_input(f"Month {i+1}", value=0)
                monthly_incentives.append(val)

        elif incentive_type == "yearly":
            y1 = st.number_input("Year 1", value=0)
            y2 = st.number_input("Year 2", value=0)
            y3 = st.number_input("Year 3", value=0)

        calculate = st.button("Calculate Eligibility")

    with right:
        st.subheader("Results")

        if calculate:
            data = {
                "gross_income": income,
                "obligations": obligations,
                "age": age,
                "roi": roi,
                "employment_type": emp_type,
                "rental_income": rental_income,
                "rental_type": rental_type,
                "incentive_type": incentive_type,
                "monthly_incentives": monthly_incentives,
                "y1": y1,
                "y2": y2,
                "y3": y3,
                "custom_foir": st.session_state.get("custom_foir")
            }

            result = home_loan_calculator(data)

            if result["eligible"]:
                st.success("✅ Eligible")

                col1, col2 = st.columns(2)
                col3, col4 = st.columns(2)

                col1.metric("Loan Amount", f"₹ {result['loan']}")
                col2.metric("EMI", f"₹ {result['emi']}")
                col3.metric("FOIR", f"{result['foir']}%")
                col4.metric("Tenure", f"{result['tenure']} yrs")

                st.metric("Additional Income", f"₹ {result['additional_income']}")

            else:
                st.error(result["reason"])

# Footer
st.markdown("""
---
<center>Developed by <b><i>Mayuresh Saindane</i></b></center>
""", unsafe_allow_html=True)
