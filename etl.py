import os
import sys
import sqlite3
import pandas as pd
import re

# Reconfigure stdout to use UTF-8 to prevent UnicodeEncodeError when printing checkmark on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Check if the source CSV file exists before attempting to read it
if not os.path.exists("telecom_churn.csv"):
    print("Error: The source file 'telecom_churn.csv' was not found in the current directory.")
    exit(1)

# STEP 1 — LOAD
# Read the CSV file into a Pandas DataFrame
df = pd.read_csv("telecom_churn.csv")

# Print the total number of rows loaded and the list of column names
print(f"Total rows loaded: {len(df)}")
print(f"Column names: {list(df.columns)}")

# STEP 2 — CLEAN
# Convert any whitespace-only values in TotalCharges to 0.0
df['TotalCharges'] = df['TotalCharges'].apply(lambda x: '0.0' if pd.isna(x) or str(x).strip() == '' else x)

# Strip leading and trailing whitespace from all string columns
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].astype(str).str.strip()

# Drop rows where customerID or Churn is null or empty string
df = df[df['customerID'].notna() & (df['customerID'] != '')]
df = df[df['Churn'].notna() & (df['Churn'] != '')]

# Convert TotalCharges values to floats row-by-row to handle potential conversion errors
total_charges_floats = []
for val in df['TotalCharges']:
    try:
        total_charges_floats.append(float(val))
    except (ValueError, TypeError):
        # Set value to 0.0 if conversion fails on a row and continue
        total_charges_floats.append(0.0)
df['TotalCharges'] = total_charges_floats

# Print the number of rows remaining after cleaning
print(f"Rows remaining after cleaning: {len(df)}")

# STEP 3 — STANDARDIZE
# Regex pattern replacement to convert PascalCase/camelCase columns to snake_case
new_cols = []
for col in df.columns:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', col)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    s2 = s2.replace('i_d', 'id').replace('customerid', 'customer_id')
    new_cols.append(s2)
df.columns = new_cols

# Map text churn values to binary integers
df['churn'] = df['churn'].map({'Yes': 1, 'No': 0})

# Select only the columns required by the database schema
db_columns = ['customer_id', 'gender', 'senior_citizen', 'tenure', 'monthly_charges', 'total_charges', 'churn']
df = df[db_columns]

# STEP 4 — LOAD INTO SQLITE
try:
    # Connect to the SQLite database file
    conn = sqlite3.connect("customerpulse.db")
    cursor = conn.cursor()
    
    # Drop the existing customers table if it already exists
    cursor.execute("DROP TABLE IF EXISTS customers")
    
    # Create the customers table with the enforced schema
    cursor.execute("""
    CREATE TABLE customers (
        customer_id TEXT PRIMARY KEY,
        gender TEXT,
        senior_citizen INTEGER,
        tenure INTEGER,
        monthly_charges REAL,
        total_charges REAL,
        churn INTEGER
    )
    """)
    conn.commit()
    
    # Write the dataframe contents to the customers table
    df.to_sql("customers", conn, if_exists="append", index=False)
    
    # Close the database connection
    conn.close()
except sqlite3.Error as e:
    # Print the error message if any SQLite write operation fails
    print(f"SQLite Write Failed: {e}")
    raise e

# STEP 5 — LOG
# Print the structured success log in the requested format
print("✓ ETL Complete")
print(f"✓ Rows Loaded: {len(df)}")
print("✓ Database: customerpulse.db")
print("✓ Table: customers")
print(f"✓ Columns: {list(df.columns)}")
