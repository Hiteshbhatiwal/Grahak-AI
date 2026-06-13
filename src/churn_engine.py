import sqlite3
import pandas as pd
import sys

# Reconfigure stdout to use UTF-8 to prevent UnicodeEncodeError when printing checkmark on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# PART 1: Connect to database and load customer data
conn = sqlite3.connect("data/customerpulse.db")
df = pd.read_sql_query("SELECT * FROM customers", conn)
print(f"Customers loaded: {len(df)}")

# PART 2: Feature engineering to create spend metrics and value segments
df['avg_monthly_spend'] = df.apply(
    lambda r: r['total_charges'] / r['tenure'] if r['tenure'] > 0 else r['monthly_charges'], 
    axis=1
).round(2)

df['spend_trend'] = df.apply(
    lambda r: r['monthly_charges'] / r['avg_monthly_spend'] if r['avg_monthly_spend'] > 0 else 1.0,
    axis=1
).round(2)

df['value_segment'] = df['total_charges'].apply(
    lambda tc: "High Value" if tc > 4000 else ("Mid Value" if tc >= 1500 else "Low Value")
)

# PART 3: Churn scoring based on tenure, spend trends, and monthly charges
churn_scores = []
risk_categories = []

for idx, row in df.iterrows():
    # Tenure score contribution
    t = row['tenure']
    if t < 12:
        score_a = 40
    elif 12 <= t <= 24:
        score_a = 25
    elif 25 <= t <= 48:
        score_a = 10
    else:
        score_a = 0
        
    # Spend trend score contribution
    st = row['spend_trend']
    if st < 0.8:
        score_b = 30
    elif 0.8 <= st <= 1.0:
        score_b = 15
    else:
        score_b = 0
        
    # Monthly charges score contribution
    mc = row['monthly_charges']
    if mc > 70:
        score_c = 20
    elif 40 <= mc <= 70:
        score_c = 10
    else:
        score_c = 0
        
    # Aggregate and cap the churn score at 100
    final_score = int(min(score_a + score_b + score_c, 100))
    churn_scores.append(final_score)
    
    # Assign risk category based on final score
    if final_score >= 70:
        risk_categories.append("High Risk")
    elif 40 <= final_score <= 69:
        risk_categories.append("Medium Risk")
    else:
        risk_categories.append("Low Risk")

df['churn_score'] = churn_scores
df['risk_category'] = risk_categories

# PART 4: Save features and scores to database and print reports
df.to_sql("customer_features", conn, if_exists="replace", index=False)
conn.close()

# Print reporting metrics
high_risk = len(df[df['risk_category'] == "High Risk"])
med_risk = len(df[df['risk_category'] == "Medium Risk"])
low_risk = len(df[df['risk_category'] == "Low Risk"])

print("\n--- Churn Score Distribution ---")
print(f"High Risk: {high_risk} customers")
print(f"Medium Risk: {med_risk} customers")
print(f"Low Risk: {low_risk} customers")

print("\n--- Top 10 Highest Risk Customers ---")
top_10 = df[['customer_id', 'tenure', 'total_charges', 'churn_score', 'risk_category']].sort_values(
    by=['churn_score', 'total_charges'], 
    ascending=[False, False]
).head(10)
print(top_10.to_string(index=False))

print("\n✓ customer_features table saved to data/customerpulse.db")
