"""
CS 230 – Final Project
Michelle Catano 
New York Housing Data App

This Streamlit app allows users to explore the New York housing dataset using
filters, graphs, maps, and summary insights.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# LOAD DATA

@st.cache_data
def load_data():
    return pd.read_excel("NY-House-Dataset.xlsx")

df = load_data()

# Drop rows missing essential numeric info
df_clean = df.dropna(subset=["PRICE", "BEDS", "BATH", "PROPERTYSQFT"])

# SIDEBAR & APP HEADER

st.sidebar.title("New York Housing Dashboard")
st.sidebar.markdown(
    "Explore New York housing data through maps, charts, and interactive filters."
)

st.title("New York Housing Market Analysis")

# MAP OF ALL LISTINGS

st.header("Map of All Listings")

map_df = df_clean.dropna(subset=["LATITUDE", "LONGITUDE"])
st.map(map_df[["LATITUDE", "LONGITUDE"]])

# QUERY 1: Average price for selected location & show bar chart

st.header("Query 1: Average Price by Location")

locations = sorted(df_clean["LOCALITY"].dropna().unique())

selected_location = st.selectbox("Select a location:", locations)

# Filter by LOCALITY
q1_df = df_clean[df_clean["LOCALITY"] == selected_location]

if len(q1_df) > 0:
    avg_price = q1_df["PRICE"].mean()
    min_price = q1_df["PRICE"].min()
    max_price = q1_df["PRICE"].max()

    st.write(f"**Average Price:** ${avg_price:,.0f}")
    st.write(f"Lowest Price: ${min_price:,.0f}")
    st.write(f"Highest Price: ${max_price:,.0f}")
else:
    st.write("No listings in this location.")

# ---------- Bar Chart: Average Price for ALL Locations ----------

st.subheader("Average Price Across All Locations")

avg_prices = df_clean.groupby("LOCALITY")["PRICE"].mean().sort_values(ascending=False)

fig1, ax1 = plt.subplots(figsize=(12, 4))
avg_prices.plot(kind="bar", ax=ax1, color="steelblue")
ax1.set_xlabel("Location")
ax1.set_ylabel("Average Price ($)")
ax1.set_title("Average Home Price by Location")
plt.xticks(rotation=45)
st.pyplot(fig1)

# QUERY 2:  Average Price by Bedrooms ($K)

st.header("Query 2: Average Price Based on Number of Bedrooms")

st.write("""
Use the slider to choose a maximum number of bedrooms and see how 
the **average home price (in thousands of dollars)** changes.
""")

min_beds = int(df_clean["BEDS"].min())
max_beds = int(df_clean["BEDS"].max())

selected_beds = st.slider(
    "Select maximum number of bedrooms:",
    min_beds, max_beds, max_beds
)

# Filter dataset
q2_df = df_clean[df_clean["BEDS"] <= selected_beds].copy()

# Convert price to thousands
q2_df["PRICE_K"] = q2_df["PRICE"] / 1000

# Group by bedroom count
avg_price_by_bed = q2_df.groupby("BEDS")["PRICE_K"].mean().sort_index()

st.subheader(f"Average Price (in $1,000s) for Homes With ≤ {selected_beds} Bedrooms")

# ---- Bar Chart ----
fig2, ax2 = plt.subplots(figsize=(8, 4))
ax2.bar(avg_price_by_bed.index, avg_price_by_bed.values, color="royalblue")

ax2.set_xlabel("Number of Bedrooms")
ax2.set_ylabel("Average Price ($K)")
ax2.set_title("Average Home Price by Bedrooms")
ax2.ticklabel_format(style='plain', axis='y')

st.pyplot(fig2)

# QUERY 3: Find Homes Under a Selected Price (with outlier fix)

st.header("Query 3: Find Homes Under a Selected Price")

# Remove extreme outliers
price_cap = df_clean["PRICE"].quantile(0.99)
df_no_outliers = df_clean[df_clean["PRICE"] <= price_cap]

min_price = float(df_no_outliers["PRICE"].min())
max_price = float(df_no_outliers["PRICE"].max())

selected_price = st.slider(
    "Maximum Price (in dollars):",
    min_price,
    max_price,
    min_price
)

st.write(f"Showing homes under **${selected_price:,.0f}**")

# Use LOCALITY column (correct name)
selected_locations = st.multiselect("Select locations:", locations)

q3_df = df_no_outliers[df_no_outliers["PRICE"] <= selected_price]

if selected_locations:
    q3_df = q3_df[q3_df["LOCALITY"].isin(selected_locations)]

# ---- MAP ----
st.subheader("Map of Filtered Homes")

map_q3 = q3_df.dropna(subset=["LATITUDE", "LONGITUDE"])
st.map(map_q3[["LATITUDE", "LONGITUDE"]])

# ---- TABLE ----
st.subheader("Matching Listings")
st.write(f"Number of properties: **{len(q3_df)}**")

table_df = q3_df.copy()
table_df["PRICE"] = table_df["PRICE"].apply(lambda x: f"${x:,.0f}")

st.dataframe(table_df[[
    "PRICE",
    "BEDS",
    "BATH",
    "PROPERTYSQFT",
    "LOCALITY",
    "ADDRESS"
]])

# SUMMARY & INSIGHTS

st.header("Summary & Insights")

st.markdown("""
The analysis shows that New York home prices are heavily skewed with most homes 
priced on the lower end of the market and a small number of extremely expensive 
properties raising the overall averages.

Square footage, beds, and baths relate strongly to each other, but they do not
strongly correlate with price. This suggests that price is driven more by 
neighborhood, desirability, and other non-numerical factors.

Overall, New York housing values are shaped primarily by location rather than 
property size alone.
""")

