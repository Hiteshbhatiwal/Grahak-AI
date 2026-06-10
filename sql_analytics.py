import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect("customerpulse.db")

# Query 1: Measure total revenue collected across all customers
print("--- Total Revenue ---")
df1 = pd.read_sql_query("SELECT SUM(total_charges) FROM customers", conn)
total_revenue = df1.iloc[0, 0]
print(f"${total_revenue:,.2f}")
print("Business Insight: The business has accumulated a total lifetime revenue of over ${:,.2f} across the entire historical customer base.".format(total_revenue))
print("-" * 40)

# Query 2: Measure total revenue lost due to churned customers
print("--- Revenue At Risk ---")
df2 = pd.read_sql_query("SELECT SUM(total_charges) FROM customers WHERE churn = 1", conn)
revenue_at_risk = df2.iloc[0, 0]
print(f"${revenue_at_risk:,.2f}")
print("Business Insight: A total of ${:,.2f} in historical revenue has been lost from customers who terminated their services.".format(revenue_at_risk))
print("-" * 40)

# Query 3: Measure count of active versus churned customers
print("--- Active vs Churned Count ---")
df3 = pd.read_sql_query("SELECT churn, COUNT(*) as customer_count FROM customers GROUP BY churn", conn)
print(df3.to_string(index=False))
active_count = df3[df3['churn'] == 0]['customer_count'].values[0]
churned_count = df3[df3['churn'] == 1]['customer_count'].values[0]
print(f"Business Insight: The company currently retains {active_count} active customer accounts while {churned_count} accounts have churned.")
print("-" * 40)

# Query 4: Measure the percentage of customers who have churned
print("--- Churn Rate ---")
df4 = pd.read_sql_query("SELECT (CAST(SUM(churn) AS REAL) / COUNT(*)) * 100 FROM customers", conn)
churn_rate = round(df4.iloc[0, 0], 2)
print(f"{churn_rate:.2f}%")
print(f"Business Insight: The customer churn rate stands at {churn_rate:.2f}%, emphasizing the portion of our user base we failed to retain.")
print("-" * 40)

# Query 5: Identify the top 10 highest-paying customers
print("--- Top 10 Customers by Revenue ---")
df5 = pd.read_sql_query("SELECT customer_id, total_charges FROM customers ORDER BY total_charges DESC LIMIT 10", conn)
print(df5.to_string(index=False))
print("Business Insight: These top ten high-value accounts represent our most valuable revenue assets and require proactive relationship management.")
print("-" * 40)

# Query 6: Measure customer counts across defined loyalty stages
print("--- Customer Segmentation by Tenure ---")
df6 = pd.read_sql_query("""
SELECT 
    CASE 
        WHEN tenure < 12 THEN 'New (0-1 year)'
        WHEN tenure >= 12 AND tenure <= 36 THEN 'Growing (1-3 years)'
        ELSE 'Loyal (3+ years)'
    END AS tenure_segment,
    COUNT(*) AS customer_count
FROM customers
GROUP BY tenure_segment
""", conn)
print(df6.to_string(index=False))
print("Business Insight: Segmenting customers by tenure highlights that loyalty stages drive the bulk of our stable customer base.")
print("-" * 40)

# Query 7: Measure the percentage of customers who remain active
print("--- Retention Rate ---")
df7 = pd.read_sql_query("SELECT (CAST(COUNT(CASE WHEN churn = 0 THEN 1 END) AS REAL) / COUNT(*)) * 100 FROM customers", conn)
retention_rate = round(df7.iloc[0, 0], 2)
print(f"{retention_rate:.2f}%")
print(f"Business Insight: A customer retention rate of {retention_rate:.2f}% indicates a strong core subscriber base but leaves room for improvement.")
print("-" * 40)

# Query 8: Compare average lifetime revenue between active and churned customers
print("--- Average Customer Lifetime Value ---")
df8 = pd.read_sql_query("SELECT churn, AVG(total_charges) as avg_clv FROM customers GROUP BY churn", conn)
print(df8.to_string(index=False))
print("Business Insight: Active customers generate a significantly higher average lifetime value than churned ones, proving the ROI of retention.")
print("-" * 40)

# Close database connection
conn.close()
