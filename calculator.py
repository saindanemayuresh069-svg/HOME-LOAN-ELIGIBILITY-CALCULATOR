def calculate_additional_income(data):

    rental_income = data.get("rental_income", 0)
    rental_type = data.get("rental_type", "None")

    if rental_type == "notary":
        rental_considered = rental_income * 0.5
    elif rental_type == "registered":
        rental_considered = rental_income * 0.75
    else:
        rental_considered = 0

    incentive_type = data.get("incentive_type", "None")

    if incentive_type == "yearly":
        y1 = data.get("y1", 0)
        y2 = data.get("y2", 0)
        y3 = data.get("y3", 0)
        incentive_income = (y1 + y2 + y3) / 36

    elif incentive_type == "monthly":
        m_values = data.get("monthly_incentives", [])
        if len(m_values) == 6:
            avg_6 = sum(m_values) / 6
            incentive_income = avg_6 * 0.5
        else:
            incentive_income = 0
    else:
        incentive_income = 0

    return rental_considered + incentive_income


def home_loan_calculator(data):

    income = data["gross_income"]
    obligations = data["obligations"]
    age = data["age"]
    roi = data["roi"]
    emp_type = data["employment_type"]

    additional_income = calculate_additional_income(data)
    total_income = income + additional_income

    max_age = 65 if emp_type == "government" else 60
    tenure = max_age - age

    if tenure <= 0:
        return {"eligible": False, "reason": "Age exceeds eligibility"}

    if total_income < 50000:
        base_foir = 0.40
    elif total_income < 100000:
        base_foir = 0.50
    else:
        base_foir = 0.60

    foir_cap = 0.55 if total_income < 75000 else 0.60
    foir = min(base_foir, foir_cap)

    emi = (total_income * foir) - obligations

    if emi <= 0:
        return {"eligible": False, "reason": "High obligations"}

    r = roi / (12 * 100)
    n = tenure * 12
    loan = emi * ((1 - (1 + r) ** (-n)) / r)

    return {
        "eligible": True,
        "loan": round(loan, 2),
        "emi": round(emi, 2),
        "foir": round(foir * 100, 2),
        "tenure": tenure,
        "additional_income": round(additional_income, 2)
    }
