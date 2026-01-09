
# Recency, Frequency and Monetary (RFM) Analysis 

## Menu
 - Objective
 - What is RFM Analysis? My Approach to the project
 - Findings an Insights
 - Business Recommendations


## Objective

Many businesses stumble by treating all customers the same, leaning on generic marketing tactics and uniform messaging, yet struggle with flat revenue growth. The reality is, customers differ greatly in their value and behavior. RFM Analysis offers a clear, data-driven approach to identify the most valuable customers and decode their purchasing patterns.
In this project, as a Data Analyst at Needpam, I worked on a practical, step-by-step implementation of RFM Analysis using Python, equipping the marketing team to design targeted retention strategies and supercharge revenue growth.


 ## What is RFM Analysis?

RFM stands for Recency, Frequency, and Monetary. It’s a marketing analysis tool used to rank quantitatively and segment customers based on their purchasing habits. Here’s how it helps:
   
 - Recency (R): How recently did a customer make a purchase? The more recent their purchase, the more likely they are to respond to promotions.
 - Frequency (F): How often do they buy? Customers who buy more frequently are generally more engaged and loyal.
 - Monetary (M): How much do they spend? Customers who spend more money are often your most profitable.

By combining these three metrics, you can group customers into different segments and develop targeted strategies for each group.

#### Import the necessary libraries

```
import pandas as pd
from datetime import datetime as dt, timedelta
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors

```

#### Load and inspect the dataset

```
data = pd.read_csv(r"C:\Users\phabr\Downloads\online_retail_rfm_50k.csv")

print(" Dataset Loaded")
print(data.head())       # Display first 5 rows
print(data.tail())       # Display last 5 rows
print(data.info())       # Data types + missing values
print(data.describe())   # Numerical statistics

```
Dataset Loaded:

|InvoiceNo|StockCode|Description      |Quantity|InvoiceDate           |UnitPrice|CustomerID|Country            |
|--------|--------|---------------------------|--------|---------------------|--------|--------|----------------------|
|32062183 |30387470 |Anything Gift|6|2023-04-05 04:32:53|1.55|228989911 |United Kingdom|
|17870460 |35862507 |Tv Gift|10|2023-04-27 12:38:01|68.01|772492132 |United Kingdom|
|31648991 |91819864 |Mrs Gift|5|2023-04-21 06:12:08|47.58|608534700|United Kingdom|
|66898691|21535859 |May Gift|9|2023-03-10 19:20:11|8.30|380841810|United Kingdom|
|59508416|93622551 |Study Gift|6|2023-06-07 21:03:18|36.64|150595719 |United Kingdom|

#### Data Cleaning and Preparation

```
# Remove rows with missing CustomerID
data.dropna(subset=['CustomerID'], inplace=True)

# Ensure InvoiceDate is in datetime format
data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'])

# Remove duplicate InvoiceNo entries (if any)
data.drop_duplicates(subset=['InvoiceNo'], inplace=True)

# Calculate total amount per transaction
data['TotalAmount'] = data['Quantity'] * data['UnitPrice']

print("\n After cleaning:")
print(data.info())

# Reference Date for Recency Calculation
# If data were live, reference date = today; here, we take the day after last transaction
reference_date = data['InvoiceDate'].max() + timedelta(days=1)

```

#### Create RFM Table

Calculate RFM Values.
To perform the analysis, we calculate Recency, Frequency, and Monetary values for each customer.  

 - Recency: Set a snapshot date (latest date in the dataset plus one day). Subtract the customer’s most recent purchase date to get the days since their last purchase.  
 - Frequency: Count the total number of orders per customer.  
 - Monetary: Sum the total transaction amounts for each customer.


```
rfm = data.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (reference_date - x.max()).days,  # Recency: days since last purchase
    'InvoiceNo': 'count',                                      # Frequency: number of purchases
    'TotalAmount': 'sum'                                       # Monetary: total spend
})

# Rename columns for clarity
rfm.rename(
    columns={
        'InvoiceDate': 'Recency',
        'InvoiceNo': 'Frequency',
        'TotalAmount': 'Monetary'
    },
    inplace=True
)

```
RFM Table:

|CustomerID|Recency|Frequency|Monetary|
|--------|--------|--------|--------|
|100203220 |3|12|6372.48|
|100360402|23|14|8136.94|
|100460213|7|19| 11671.32|
|101018341 |3|13| 5300.86|
|101210606|4|17|9254.03|

#### Define R, F, M scoring functions

Now, we’ll transform the raw RFM values into scores (1-4) to create customer segments. The scoring is based on quartiles:

  - Recency: A lower Recency value (meaning a more recent purchase) gets a higher score. So, customers in the first quartile (least recent) get a score of 1, while those in the last quartile (most recent) get a score of 4.
  - Frequency and Monetary: The logic is reversed. A higher Frequency or Monetary value gets a higher score. Customers in the first quartile get a score of 1, while those in the last quartile get a score of 4.

Here’s how we can segment our customers:

```
# Calculate Quantiles

quantiles = rfm.quantile(q=[0.25, 0.50, 0.75])

def RScore(x, p, d):
    # Assign R, F, or M score based on quantiles
    if p == 'Recency':  # Lower recency = better score
        if x <= d[p][0.25]:
            return 4
        elif x <= d[p][0.50]:
            return 3
        elif x <= d[p][0.75]:
            return 2
        else:
            return 1
    else:  # Higher F and M = better score
        if x <= d[p][0.25]:
            return 1
        elif x <= d[p][0.50]:
            return 2
        elif x <= d[p][0.75]:
            return 3
        else:
            return 4


# Apply R, F, M scoring

rfm['R'] = rfm['Recency'].apply(RScore, args=('Recency', quantiles,))
rfm['F'] = rfm['Frequency'].apply(RScore, args=('Frequency', quantiles,))
rfm['M'] = rfm['Monetary'].apply(RScore, args=('Monetary', quantiles,))

# Create combined segment & score
rfm['RFM_Segment'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)
rfm['RFM_Score'] = rfm[['R', 'F', 'M']].sum(axis=1)

```

#### Assign segment labels (High, Mid, Low value customers)

```
def assign_segment(score):
    #Label customers based on RFM score
    if score < 5:
        return 'Low Value'
    elif score < 9:
        return 'Mid Value'
    else:
        return 'High Value'

rfm['RFM_Segment_Labels'] = rfm['RFM_Score'].apply(assign_segment)

print("\n RFM Segment Labels Assigned")
print(rfm.head())

```

RFM Segment Labels Assigned:

|CustomerID|Recency|Frequency|Monetary|R|F|M|RFM_Segment|RFM_Score|RFM_Segment_Labels|
|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|
|100203220 |3|12|6372.48|4|1|1|411|6|Mid Value|
|100360402|23|14|8136.94|1|1|2|112|4|Low Value|
|100460213|7|19| 11671.32|3|3|4|334|10|High Value|
|101018341 |3|13| 5300.86|4|1|1|411|6|Mid Value|
|101210606|4|17|9254.03|4|3|3|433|10|High Value|


#### Customers Distribution by Segment and Visualization - Bar Chart

```
segment_counts = rfm['RFM_Segment_Labels'].value_counts().reset_index()
segment_counts.columns = ['RFM_Segment', 'Count']
segment_counts = segment_counts.sort_values('RFM_Segment')

fig_bar = px.bar(
    segment_counts,
    x='RFM_Segment',
    y='Count',
    title='Customer Distribution by RFM Segment',
    labels={'RFM_Segment': 'RFM Segment', 'Count': 'Number of Customers'},
    color='RFM_Segment',
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig_bar.show()

```

## Findings and Insights

Based on the provided customer segmentation analysis, the customers have been categorized into three segments:

<img width="1433" height="565" alt="Screenshot 2025-11-03 134340" src="https://github.com/user-attachments/assets/1085ed99-bd24-43c6-b920-9187f5b17da9" />


 - High-Value Customers (1135, 37.83 % of the total)

These customers are the backbone of revenue, likely contributing the majority of profits (per the Pareto principle, ~20% of customers often drive ~80% of revenue).
They are loyal, engaged, and likely to respond well to upselling, cross-selling, or premium offerings (e.g., subscriptions, exclusive products).
Retention is critical: Losing these customers would significantly impact revenue.

Example of Impact: If a high-value customer spends $1,000 monthly and stops purchasing, the business could lose $12,000 annually per customer.

 - Medium-Value Customers (1427, 47.57% of the total)

These customers are valuable but not as critical as high-value customers. They have potential to become high-value with the right engagement.
Their slightly lower recency suggests they may need nudging to purchase more regularly.
They contribute significantly to revenue but are more price-sensitive or less loyal than high-value customers.

Example Impact: A medium-value customer spending $300 every two months could be nudged to spend $400 monthly with targeted promotions, 
increasing annual revenue per customer from $1,800 to $4,800.

 - Low-Value Customers (438, 14.6 % of the total)
 
These customers contribute the least to revenue and may include one-time or sporadic buyers.
They are at high risk of churn and may not be worth heavy investment unless they show potential to move to a higher-value segment.
Acquiring new low-value customers is often more expensive than retaining or upgrading existing ones, so focus on cost-effective engagement.

Example Impact: A low-value customer spending $50 once a year may cost more to re-engage (e.g., $10 in marketing) than their contribution, so campaigns should be low-cost and scalable.

By segmenting each category into segments, we have:

<img width="1358" height="488" alt="image" src="https://github.com/user-attachments/assets/bc07bee3-5e3b-4779-a743-b15b87df95a0" />


 - VIP/Loyal: The best customers. They often buy and spend the most.
 - Potiential Loyal: These customers exhibit high frequency and monetary value but may have slightly lower recency compared to VIPs, or vice versa, requiring further analysis to identify key areas for targeted engagement.
 - At Risk/Can't Lose: They might have recent purchases but exhibit low frequency or monetary value, or vice versa, necessitating targeted strategies to boost engagement and retention.
 - Lost Customers: Haven’t bought in a long time, don’t buy often, and don’t spend much.

Here’s a breakdown of some key segments and their typical scores:

<img width="1427" height="520" alt="image" src="https://github.com/user-attachments/assets/c284255a-bb2c-47c0-9eaa-e21810dece8e" />


After analysis, for the Potential Loyal, At Risk, and Can't Lose customer categories, we observe that the recency score is relatively good, while frequency and monetary scores are lower, indicating opportunities for improvement. Specifically:
  - Potential Loyal: The recency score is strong (around 2.5), suggesting recent engagement, but the frequency (approximately 2.0) and monetary (around 2.0) scores lag behind, particularly compared to the VIP/Loyal segment. This suggests a need to enhance purchase frequency and spending through targeted incentives or loyalty programs to convert them into VIP/Loyal customers.
  - At Risk: This segment shows a decent recency score (around 2.0), indicating recent purchases, but both frequency (around 1.5) and monetary (around 1.5) scores are notably lower. Efforts should focus on re-engaging these customers with personalized offers to boost their purchase frequency and average spend, preventing potential churn.
  - Can't Lose: The recency score is moderate (around 1.5), but frequency and monetary scores are the lowest among these segments (both around 1.0). This highlights a critical need to investigate why these customers, despite recent activity, are not purchasing frequently or spending more. Strategies could include analyzing their behavior further and implementing retention campaigns to elevate their engagement.



## Concrete Business Implications and Recommendations

 - Resource Allocation:
   
Allocate 60–70% of marketing and retention budgets to VIP/Loyal customers to maximize ROI, given their high recency, frequency, and monetary scores (around 3.0–3.5). Dedicate 20–30% to Potential Loyal customers (recency ~2.5, frequency and monetary ~2.0) to convert them into high-value segments through targeted campaigns. Use low-cost, automated strategies (e.g., email reminders) for At Risk (recency ~2.0, frequency and monetary ~1.5) and Can't Lose (recency ~1.5, frequency and monetary ~1.0) customers to minimize expenses while maintaining engagement.


 - Revenue Growth:

Upsell VIP/Loyal customers with premium products to potentially increase their average spend by 10–20%, leveraging their strong monetary score (~3.5). Converting at least 10% of Potential Loyal customers (e.g., 300 customers) to VIP/Loyal status—by boosting their frequency and monetary scores—could significantly enhance revenue (e.g., $60,000 if each increases spend to $350). For At Risk and Can't Lose segments, focus on re-engagement to gradually elevate their spending potential.


- Customer Lifetime Value (CLV):

VIP/Loyal customers exhibit the highest CLV due to their superior recency, frequency, and monetary scores, making retention efforts here the most lucrative for long-term returns. Potential Loyal customers have a moderate CLV that can be nurtured with strategic interventions to improve frequency and monetary value. At Risk and Can't Lose customers have lower CLV but can be selectively retained based on churn risk assessments.


- Churn Prevention:

Monitor VIP/Loyal customers for declines in recency or frequency (currently ~3.0) and respond promptly with personalized offers to maintain their engagement. For Potential Loyal customers, enhance recency (currently ~2.5) through timely campaigns to prevent slippage. For At Risk and Can't Lose segments, deploy churn prediction models to identify salvageable customers and apply low-cost retention tactics (e.g., discounts) to improve their frequency and monetary scores (currently ~1.0–1.5).













   






