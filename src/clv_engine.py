import sqlite3
import pandas as pd
import sys

# Reconfigure stdout to use UTF-8 to prevent UnicodeEncodeError when printing checkmark on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# PART 1: Connect to database and load engineered customer features
conn = sqlite3.connect("data/customerpulse.db")
df = pd.read_sql_query("SELECT * FROM customer_features", conn)
print(f"Records loaded: {len(df)}")

# PART 2: Perform CLV calculations including projected lifespan and risk metrics
df['estimated_lifespan_months'] = df.apply(
    lambda r: r['tenure'] + 24 if r['churn'] == 0 else r['tenure'],
    axis=1
)

df['projected_clv'] = (df['avg_monthly_spend'] * df['estimated_lifespan_months']).round(2)

def calculate_revenue_at_risk(row):
    rc = row['risk_category']
    ams = row['avg_monthly_spend']
    if rc == 'High Risk':
        return ams * 24
    elif rc == 'Medium Risk':
        return ams * 12
    else:
        return 0.0

df['revenue_at_risk'] = df.apply(calculate_revenue_at_risk, axis=1).round(2)

# PART 3: Save results to database and display formatted reports
df.to_sql("clv_features", conn, if_exists="replace", index=False)
conn.close()

# Format and print the CLV summary information
total_proj_rev = df['projected_clv'].sum()
total_rev_at_risk = df['revenue_at_risk'].sum()

active_avg_clv = df[df['churn'] == 0]['projected_clv'].mean()
if pd.isna(active_avg_clv):
    active_avg_clv = 0.0

churned_avg_clv = df[df['churn'] == 1]['projected_clv'].mean()
if pd.isna(churned_avg_clv):
    churned_avg_clv = 0.0

print("\n--- CLV Summary ---")
print(f"Total Projected Revenue: ${total_proj_rev:,.2f}")
print(f"Total Revenue At Risk: ${total_rev_at_risk:,.2f}")
print(f"Average CLV (Active Customers): ${active_avg_clv:,.2f}")
print(f"Average CLV (Churned Customers): ${churned_avg_clv:,.2f}")

# Format and print the top 10 customers by projected CLV
print("\n--- Top 10 Customers by Projected CLV ---")
top_10 = df[['customer_id', 'risk_category', 'projected_clv', 'revenue_at_risk', 'value_segment']].sort_values(
    by='projected_clv', 
    ascending=False
).head(10).copy()

top_10['projected_clv'] = top_10['projected_clv'].apply(lambda x: f"${x:,.2f}")
top_10['revenue_at_risk'] = top_10['revenue_at_risk'].apply(lambda x: f"${x:,.2f}")
print(top_10.to_string(index=False))

# Compute, format, and print the revenue at risk by segment
print("\n--- Revenue At Risk by Segment ---")
segment_df = df.groupby('risk_category').agg(
    customer_count=('customer_id', 'count'),
    total_revenue_at_risk=('revenue_at_risk', 'sum')
).reset_index()

segment_df = segment_df.sort_values(by='total_revenue_at_risk', ascending=False).copy()
segment_df['total_revenue_at_risk'] = segment_df['total_revenue_at_risk'].apply(lambda x: f"${x:,.2f}")
print(segment_df.to_string(index=False))

print("\n✓ clv_features table saved to data/customerpulse.db")
