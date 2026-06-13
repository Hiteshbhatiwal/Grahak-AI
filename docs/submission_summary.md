# Hackathon Submission Summary: Grahak AI

## 1. Problem Statement
In the subscription economy, customer cancellation (churn) represents a silent leak in business revenue. Companies often realize a customer is leaving only after they have canceled their contract or service. Standard practices rely on reactive methods, general promotions, or generic customer support outreach that fail to differentiate customer value, causing wasted loyalty budget and lost revenue.

---

## 2. Business Challenge
* **Reactive Retention:** Most retention campaigns are launched after cancellation notices, leaving minimal time to recover.
* **Misaligned Offers:** High-value enterprise customers and low-value accounts receive the same discounts, decreasing profit margins.
* **Lack of ROI Metrics:** Businesses cannot trace how many risk dollars were protected by a specific retention campaign, leaving marketing efficiency in a black box.

---

## 3. Proposed Solution
**Grahak AI** is a proactive, closed-loop customer retention intelligence platform. It automates data ingestion, applies multidimensional customer risk scoring, calculates projected customer lifetime value (CLV), prioritizes high-value accounts at risk, and generates personalized retention email strategies automatically. 

---

## 4. Technology Stack
* **Frontend Web Application:** Streamlit
* **Styling & Theme:** Vanilla CSS with custom glassmorphism, warm light beige canvas, and deep navy highlights
* **Core Languages:** Python 3.8+
* **Database & Query Ingestion:** SQLite3
* **Data Processing & Analytics:** Pandas, NumPy
* **Visualization Engine:** Plotly Express

---

## 5. Innovation
* **Closed-loop System:** Replaces disconnected tools with a unified database pipeline where churn scores, lifetime values, and retention actions are written back to a single SQLite database (`customerpulse.db`), making it accessible for reporting.
* **Value-guided Recommendations:** Recommends campaigns using a combination of churn scores and projected CLV, ensuring costly retention budgets (e.g., Premium 20% Discounts) are reserved exclusively for High-Value, High-Risk accounts.
* **Embedded Pitch Mode:** Built-in Executive presentation mode directly inside the dashboard app, making it ready to pitch to stakeholders and judges.

---

## 6. Key Features
* **Interactive Workspace:** Allows customer relationship managers to view specific customer cards, analyze churn risk flags, and examine generated campaign emails.
* **Dynamic Email Generation:** Automatic creation of tailored email copy corresponding to the recommended campaign action (Premium Discount, Loyalty Points, Feedback Survey).
* **Live Revenue Protection Timeline:** Visualization showing the path from identifying risk to calculating the expected recovery dollar values.
* **Revenue Metrics Visualization:** Plotly bar and pie charts showing risk distribution across customer segments.

---

## 7. Revenue Impact
* **₹648.96 Lakh** in total revenue currently identified as at risk.
* **₹194.69 Lakh** in expected revenue recovered through optimized campaign outreach.
* **30% Cohort Recovery Rate** calculated dynamically based on campaign recommendations and risk category response rates.

---

## 8. Future Scope
* **Real-time Event Streaming:** Connect to Apache Kafka or AWS Kinesis to trigger retention recommendations instantly when a user exhibits bad product interaction signals.
* **LLM Engine Integration:** Upgrade template-based campaigns to LLM agent calls (e.g., Vertex AI Gemini API) for hyper-personalized, dynamic email generation.
* **Multi-Warehouse Integrations:** Native support for Databricks, Snowflake, and Google BigQuery.
