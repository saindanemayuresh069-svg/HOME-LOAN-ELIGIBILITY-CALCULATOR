import streamlit as st
import pandas as pd
import uuid
import csv
import os
from datetime import datetime
from calculator import home_loan_calculator

st.set_page_config(page_title="Home Loan Eligibility Calculator", layout="wide")

# Dark Mode
dark_mode = st.toggle("🌙 Dark Mode")

if dark_mode:
    st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e222a; color: white; padding: 15px; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .main { background-color: #f5f7fa; }
    .stMetric { background-color: white; padding: 15px; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# Hover effect
st.markdown("""
<style>
.stMetric:hover {
    transform: scale(1.05);
    transition: 0.3s;
}
[data-testid="stMetricValue"] {
    font-size: 30px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# User ID
if "user_id" not in st.session_state:
    st.session_state["user_id"] = str(uuid.uuid4())[:8]

# Header
st.title("🏠 Home Loan Eligibility Calculator")
st.caption("Smart Credit Decision Engine powered by Policy Logic & Risk Analytics")
st.write("Developed by **_Mayuresh Saindane_**")
st.caption(f"User ID: {st.session_state['user_id']}")

# Tabs
tab1, tab2, tab3 = st.tabs(["Calculator", "FOIR Settings", "Admin Dashboard"])

# FOIR TAB
with tab2:
    override = st.checkbox("Enable FOIR Override")
    if override:
        st.session_state["custom_foir"] = st.slider("Set FOIR (%)", 10, 60, 50)
    else:
        st.session_state["custom_foir"] = None

# CALCULATOR
with tab1:

    left, right = st.columns([1.2, 1.8])

    with left:
        income = st.number_input("Gross Income (₹)", value=0)
        obligations = st.number_input("Existing EMI (₹)", value=0)
        age = st.number_input("Age", value=30)
        roi = st.number_input("Interest Rate (%)", value=8.5)
        emp_type = st.selectbox("Employment Type", ["government", "private"])

        rental_income = st.number_input("Rental Income (₹)", value=0)
        rental_type = st.selectbox("Rental Type", ["None", "notary", "registered"])

        incentive_type = st.selectbox("Incentive Type", ["None", "monthly", "yearly"])

        monthly_incentives = []
        y1 = y2 = y3 = 0

        if incentive_type == "monthly":
            for i in range(6):
                monthly_incentives.append(st.number_input(f"Month {i+1}", value=0))

        elif incentive_type == "yearly":
            y1 = st.number_input("Year 1", value=0)
            y2 = st.number_input("Year 2", value=0)
            y3 = st.number_input("Year 3", value=0)

        calculate = st.button("Calculate")

    with right:

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

                # KPI
                k1, k2, k3 = st.columns(3)
                k1.metric("💰 Eligible Loan Amount", f"₹ {int(result['loan']):,}")
                k2.metric("📊 Monthly EMI", f"₹ {int(result['emi']):,}")
                k3.metric("📈 FOIR Ratio", f"{result['foir']}%")

                st.markdown("---")

                # Decision Box
                st.markdown("### 🎯 Credit Decision")

                if result['foir'] <= 50:
                    st.markdown("<div style='background:#d4edda;padding:15px;border-radius:10px'><b>✅ Approved</b></div>", unsafe_allow_html=True)
                elif result['foir'] <= 60:
                    st.markdown("<div style='background:#fff3cd;padding:15px;border-radius:10px'><b>🟡 Refer</b></div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='background:#f8d7da;padding:15px;border-radius:10px'><b>❌ Rejected</b></div>", unsafe_allow_html=True)

                # Risk
                st.markdown("### ⚠️ Risk Assessment")
                if result['foir'] <= 40:
                    st.success("Low Risk")
                elif result['foir'] <= 55:
                    st.warning("Moderate Risk")
                else:
                    st.error("High Risk")

                st.markdown("---")

                # Chart
                df = pd.DataFrame({
                    "Category": ["Income", "EMI"],
                    "Amount": [income, result['emi']]
                })

                st.bar_chart(df.set_index("Category"), use_container_width=True)

                # Save
                file_exists = os.path.isfile("users_data.csv")

                with open("users_data.csv", "a", newline="") as file:
                    writer = csv.writer(file)

                    if not file_exists:
                        writer.writerow(["user_id", "loan", "emi", "foir", "timestamp"])

                    writer.writerow([
                        st.session_state["user_id"],
                        result["loan"],
                        result["emi"],
                        result["foir"],
                        datetime.now()
                    ])

# ADMIN DASHBOARD
with tab3:

    st.markdown("## 📊 Admin Analytics Dashboard")

    if os.path.exists("users_data.csv"):

        df = pd.read_csv("users_data.csv")

        if "user_id" not in df.columns:
            df["user_id"] = "unknown"

        a1, a2, a3, a4 = st.columns(4)

        a1.metric("Users", df["user_id"].nunique())
        a2.metric("Calculations", len(df))
        a3.metric("Avg Loan", f"₹ {int(df['loan'].mean()):,}")
        a4.metric("Avg FOIR", f"{round(df['foir'].mean(),2)}%")

        st.bar_chart(df["loan"])
        st.bar_chart(df["foir"])

        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        st.line_chart(df.set_index("timestamp")["loan"])

        st.dataframe(df)

    else:
        st.info("No data yet")
