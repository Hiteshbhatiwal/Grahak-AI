import sqlite3
import pandas as pd
import sys

# Ensure UTF-8 output encoding is configured on Windows environments to prevent character encode errors
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def generate_email(customer_row):
    """
    Generates a personalized, dynamic retention email template based on customer details,
    value tier, and recommended action for Grahak AI.
    
    Parameters:
        customer_row (pd.Series or dict): Row of customer features
        
    Returns:
        str: Formatted email body text
    """
    customer_id = customer_row.get("customer_id", "Customer")
    risk_cat = customer_row.get("risk_category", "Unknown Risk")
    clv = customer_row.get("projected_clv", 0.0)
    action = customer_row.get("recommended_action", "Customer Appreciation Email")
    val_seg = customer_row.get("value_segment", "Standard")

    # Define customized messaging based on recommended retention actions
    if action == "Premium Discount":
        reward_details = "a premium 20% discount on your contract fee for the next 12 months as a thank you for your continued partnership."
    elif action == "Feedback Survey":
        reward_details = "a brief feedback survey to help us improve. To show our appreciation, we have applied a ₹1,000 credit to your next invoice."
    elif action == "Loyalty Points":
        reward_details = "500 bonus loyalty points credited directly to your account, redeemable for updates and select vendor benefits."
    else:
        reward_details = "priority status in our customer service queue for all your future interactions with our support team."

    email_body = f"""Subject: Supporting your journey with Grahak AI (Account: {customer_id})

Dear Customer {customer_id},

Here at Grahak AI, we highly value your business. We notice you are currently in our {val_seg} segment with a projected customer value of ₹{clv:,.2f}. 

To ensure we are meeting all your needs, we would like to offer you {reward_details}

Our team is dedicated to your success. If you have any questions or feedback, please reply directly to this email.

Sincerely,
Customer Success Team
Grahak AI
"""
    return email_body


def process_retention_pipeline(db_path="customerpulse.db"):
    """
    Executes the ETL, decision logic, and calculation pipeline for the retention engine.
    
    Parameters:
        db_path (str): Path to SQLite database file
        
    Returns:
        tuple: (retention_cards_df, summary_dict)
    """
    # PART 1: Data Layer - Connect and Load
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM clv_features", conn)

    # Filter for high risk or high revenue at risk customers
    df_filtered = df[
        (df["risk_category"] == "High Risk") | (df["revenue_at_risk"] > 500)
    ].copy()

    # PART 2 & PART 3: Decision Engine and Retention Card Generation
    actions = []
    priorities = []
    probabilities = []

    for idx, row in df_filtered.iterrows():
        rc = row["risk_category"]
        clv = row["projected_clv"]

        if rc == "High Risk" and clv > 5000:
            actions.append("Premium Discount")
            priorities.append("Critical")
            probabilities.append(0.70)
        elif rc == "High Risk" and clv <= 5000:
            actions.append("Feedback Survey")
            priorities.append("High")
            probabilities.append(0.45)
        elif rc == "Medium Risk":
            actions.append("Loyalty Points")
            priorities.append("Medium")
            probabilities.append(0.30)
        else:
            actions.append("Customer Appreciation Email")
            priorities.append("Low")
            probabilities.append(0.15)

    df_filtered["recommended_action"] = actions
    df_filtered["priority"] = priorities
    df_filtered["recovery_probability"] = probabilities

    # Select columns specified for the retention_cards DataFrame
    retention_cards = df_filtered[
        [
            "customer_id",
            "risk_category",
            "projected_clv",
            "revenue_at_risk",
            "recommended_action",
            "priority",
            "recovery_probability",
            "value_segment",
        ]
    ].copy()

    # PART 4: Revenue Recovery Forecast Calculations
    retention_cards["expected_revenue_recovered"] = (
        retention_cards["revenue_at_risk"]
        * retention_cards["recovery_probability"]
    ).round(2)

    total_revenue_at_risk = retention_cards["revenue_at_risk"].sum()
    total_expected_recovery = retention_cards["expected_revenue_recovered"].sum()
    total_customers_targeted = len(retention_cards)

    # PART 6: Database Output - Save retention_cards to table
    retention_cards.to_sql("retention_cards", conn, if_exists="replace", index=False)
    conn.close()

    # Create summary metrics dictionary
    summary = {
        "total_revenue_at_risk": total_revenue_at_risk,
        "total_expected_recovery": total_expected_recovery,
        "total_customers_targeted": total_customers_targeted,
    }

    return retention_cards, summary


if __name__ == "__main__":
    try:
        # Run the full pipeline
        retention_cards, summary = process_retention_pipeline()

        # PART 7: Console Report
        print("===== GRAHAK AI RETENTION ENGINE =====")
        print(f"Customers Targeted: {summary['total_customers_targeted']}")
        print(f"Revenue At Risk: ₹{summary['total_revenue_at_risk']:,.2f}")
        print(f"Expected Revenue Recovery: ₹{summary['total_expected_recovery']:,.2f}")
        print()

        print("--- Top 10 Highest Priority Customers ---")
        # Define priority sorting score to map Critical -> 1, High -> 2, Medium -> 3, Low -> 4
        priority_map = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
        retention_cards["priority_score"] = retention_cards["priority"].map(priority_map)
        
        # Sort by priority tier and descending revenue at risk
        top_10 = retention_cards.sort_values(
            by=["priority_score", "revenue_at_risk"], 
            ascending=[True, False]
        ).head(10).copy()

        # Format printing output
        top_10_print = top_10[
            [
                "customer_id",
                "risk_category",
                "projected_clv",
                "revenue_at_risk",
                "recommended_action",
                "priority",
                "recovery_probability",
            ]
        ].copy()

        top_10_print["projected_clv"] = top_10_print["projected_clv"].apply(lambda x: f"₹{x:,.2f}")
        top_10_print["revenue_at_risk"] = top_10_print["revenue_at_risk"].apply(lambda x: f"₹{x:,.2f}")
        top_10_print["recovery_probability"] = top_10_print["recovery_probability"].apply(lambda x: f"{x * 100:.0f}%")

        print(top_10_print.to_string(index=False))
        print()
        print("✓ retention_cards table saved to customerpulse.db")

    except Exception as e:
        print(f"Error executing retention engine: {e}")
        sys.exit(1)
