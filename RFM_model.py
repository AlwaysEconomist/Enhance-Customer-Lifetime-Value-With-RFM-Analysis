# RFM Customer Segmentation Analysis (Recency, Frequency and Monetary)

## Dataset Description
                      Online Retail Dataset, Transactions of a UK-based non-store online retail  

 - InvoiceNo   : Unique 8-digit invoice number for each transaction. 
              Invoices starting with 'C' indicate cancellations.
 - StockCode   : Unique 8-digit code for each product.
 - Description : Name of the product.
 - Quantity    : Number of units of the product in the transaction.
 - InvoiceDate : Date and time of the transaction.
 - UnitPrice   : Price per unit (in GBP).
 - CustomerID  : Unique 9-digit customer identifier.
 - Country     : Country where the customer resides.

Notes:
- Contains transactions from 01/12/2022 and 30/06/2023 for a UK-based online retailer.
- The company sells unique, all-occasion gifts.
- Many customers are wholesalers.


# Import the necessary libraries
import pandas as pd
from datetime import datetime as dt, timedelta
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors

# Load and inspect the dataset

data = pd.read_csv(r"C:\Users\phabr\Downloads\dataset_rfm.csv")

print(" Dataset Loaded")
print(data.head())       # Display first 5 rows

print(data.tail())       # Display last 5 rows

print(data.info())       # Data types + missing values

print(data.describe())   # Numerical statistics


# Data Cleaning and Preparation

# Remove rows with missing CustomerID
data.dropna(subset=['CustomerID'], inplace=True)

# Ensure InvoiceDate is in datetime format
data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'], format='mixed', errors='coerce')

# Remove duplicate InvoiceNo entries (if any)
data.drop_duplicates(subset=['InvoiceNo'], inplace=True)

# Calculate total amount per transaction
data['TotalAmount'] = data['Quantity'] * data['UnitPrice']

print("\n After cleaning:")
print(data.info())


# Reference Date for Recency Calculation
# If data were live, reference date = today; here, we take the day after last transaction
reference_date = data['InvoiceDate'].max() + timedelta(days=1)


# Create RFM Table
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

print(rfm)


# Calculate Quantiles
quantiles = rfm.quantile(q=[0.25, 0.50, 0.75])

# Define R, F, M scoring functions

def RScore(x, p, d):
    """Assign R, F, or M score based on quantiles"""
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


# Assign segment labels (High, Mid, Low value customers)

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


# Number of customers by Segment and Visualization - Bar Chart

segment_counts = rfm['RFM_Segment_Labels'].value_counts().reset_index()
segment_counts.columns = ['RFM_Segment', 'Count']
segment_counts = segment_counts.sort_values('RFM_Segment')

fig_bar = px.bar(
    segment_counts,
    x='RFM_Segment',
    y='Count',
    title="Over 85% of our customers deliver real value—led by Mid-Value (47.6%) and High-Value (37.8%) segments.",
    labels={'RFM_Segment': 'RFM Segment', 'Count': 'Number of Customers'},
    color='RFM_Segment',
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig_bar.show()


# Assign descriptive customer segments

rfm['RFM_Customer_Segment'] = ''  # Initialize
rfm.loc[rfm['RFM_Score'] >= 9, 'RFM_Customer_Segment'] = 'VIP/Loyal'
rfm.loc[(rfm['RFM_Score'] >= 6) & (rfm['RFM_Score'] < 9), 'RFM_Customer_Segment'] = 'Potential Loyal'
rfm.loc[(rfm['RFM_Score'] >= 5) & (rfm['RFM_Score'] < 6), 'RFM_Customer_Segment'] = 'At Risk'
rfm.loc[(rfm['RFM_Score'] >= 4) & (rfm['RFM_Score'] < 5), 'RFM_Customer_Segment'] = "Can't Lose"
rfm.loc[(rfm['RFM_Score'] >= 3) & (rfm['RFM_Score'] < 4), 'RFM_Customer_Segment'] = 'Lost'

segment_counts = rfm['RFM_Segment_Labels'].value_counts().sort_index()

print("\n Descriptive Segments Assigned:")
print(rfm[['RFM_Score', 'RFM_Customer_Segment']].head(10))


# Group the rfm DataFrame by RFM_Segment_Labels and RFM_Customer_Segment, and count the number of occurrences in each group
segment_product_counts = rfm.groupby(['RFM_Segment_Labels', 'RFM_Customer_Segment']).size().reset_index(name='Count')

# Sort the grouped data by Count in descending order to prioritize segments with higher counts
segment_product_counts = segment_product_counts.sort_values('Count', ascending=False)

# Visualization - Treemap
  
segment_product_counts = (
    rfm.groupby(['RFM_Segment_Labels', 'RFM_Customer_Segment'])
       .size()
       .reset_index(name='Count')
       .sort_values('Count', ascending=False)
)

fig_treemap = px.treemap(
    segment_product_counts,
    path=['RFM_Segment_Labels', 'RFM_Customer_Segment'],
    values='Count',
    color='RFM_Segment_Labels',
    color_discrete_sequence=px.colors.qualitative.Pastel,
    title='Positive retention dynamics: 78% of Mid-Value customers are on track to become loyal High-Value'
)
fig_treemap.show()

# Calculate mean R, F, M scores for each RFM segment

segment_scores = rfm.groupby('RFM_Customer_Segment')[['R', 'F', 'M']].mean().reset_index()

# Create the figure
fig = go.Figure()

# Add bar for Recency score
fig.add_trace(go.Bar(
    x=segment_scores['RFM_Customer_Segment'],
    y=segment_scores['R'],
    name='Recency Score',
    marker_color='rgb(158,202,225)'
))

# Add bar for Frequency score
fig.add_trace(go.Bar(
    x=segment_scores['RFM_Customer_Segment'],
    y=segment_scores['F'],
    name='Frequency Score',
    marker_color='rgb(94,158,217)'
))

# Add bar for Monetary score
fig.add_trace(go.Bar(
    x=segment_scores['RFM_Customer_Segment'],
    y=segment_scores['M'],
    name='Monetary Score',
    marker_color='rgb(32,102,148)'
))

# Update the layout 
fig.update_layout(
    title='Comparison of RFM Segments by Recency, Frequency, and Monetary Scores',
    xaxis_title='RFM Segments',
    yaxis_title='Average Score',
    barmode='group',
    legend_title='RFM Metrics',
    showlegend=True,
    annotations=[
        dict(
            text='Recency Score shines across the board—delivering strong positive dynamics in all segments except VIP/Loyal, where Frequency needs a boost.',
            xref='paper', yref='paper',
            x=0.02, y=1.08,
            showarrow=False,
            font=dict(size=12),
            align='left'
        )
    ]
)

# Show the plot
fig.show()

rfm.to_csv('final_analysis.csv')












