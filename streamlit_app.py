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

# ============================================================
#                       LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    return pd.read_excel("NY-House-Dataset.xlsx")

df = load_data()

# Drop rows missing essential numeric info
df_clean = df.dropna(subset=["PRICE", "BEDS", "BATH", "PROPERTYSQFT"])

# ============================================================
#                  SIDEBAR & APP HEADER
# ============================================================

st.sidebar.title("New York Housing Dashboard")
st.sidebar.markdown(
    "Explore New York housing data through maps, charts, and interactive filters."
)

st.title("New York Housing Market Analysis")

# ============================================================
#                   MAP OF ALL LISTINGS
# ============================================================

st.header("Map of All Listings")

map_df = df_clean.dropna(subset=["LATITUDE", "LONGITUDE"])
st.map(map_df[["LATITUDE", "LONGITUDE"]])

# ============================================================
#                      QUERY 1
#   Average price for selected locality & show bar chart
# ============================================================

st.header("Query 1: Average Price by Locality")

localities = sorted(df_clean["LOCALITY"].dropna().unique())

selected_locality = st.selectbox("Select a locality:", localities)

# Filter for locality
q1_df = df_clean[df_clean["LOCALITY"] == selected_locality]

if len(q1_df) > 0:
    avg_price = q1_df["PRICE"].mean()
    min_price = q1_df["PRICE"].min()
    max_price = q1_df["PRICE"].max()

    st.write(f"**Average Price:** ${avg_price:,.0f}")
    st.write(f"Lowest Price: ${min_price:,.0f}")
    st.write(f"Highest Price: ${max_price:,.0f}")
else:
    st.write("No listings in this locality.")

# ---------- Bar Chart: Average Price for ALL Localities ----------

st.subheader("Average Price Across All Localities")

avg_prices = df_clean.groupby("LOCALITY")["PRICE"].mean().sort_values(ascending=False)

fig1, ax1 = plt.subplots(figsize=(12, 4))
avg_prices.plot(kind="bar", ax=ax1, color="steelblue")
ax1.set_xlabel("Locality")
ax1.set_ylabel("Average Price ($)")
ax1.set_title("Average Home Price by Locality")
plt.xticks(rotation=45)
st.pyplot(fig1)

# ============================================================
#                      QUERY 2
#    Bedrooms, Bathrooms, and Price (Improved Visualizations)
# ============================================================

st.header("Query 2: How Do Bedrooms & Bathrooms Relate to Price?")

st.write("""
This section explores whether the number of bedrooms and bathrooms meaningfully 
affects home prices in New York.  
To avoid misleading bubble scaling and overlapping points, clearer visualizations 
(heatmap + boxplot) are used instead of a scatterplot.
""")

# --- Filter options ---

bed_options = sorted(df_clean["BEDS"].unique())
bath_options = sorted(df_clean["BATH"].unique())

selected_beds = st.multiselect("Select bedroom counts:", bed_options, default=bed_options)
selected_baths = st.multiselect("Select bathroom counts:", bath_options, default=bath_options)

q2_df = df_clean[
    df_clean["BEDS"].isin(selected_beds) &
    df_clean["BATH"].isin(selected_baths)
]

# ============================================================
#           Visualization 1: Average Price Heatmap
# ============================================================

st.subheader("Average Price Heatmap (Beds × Baths)")

heatmap_data = q2_df.pivot_table(
    values="PRICE",
    index="BATH",
    columns="BEDS",
    aggfunc="mean"
)

fig_hm, ax_hm = plt.subplots(figsize=(8, 5))
sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="Blues", ax=ax_hm)
ax_hm.set_title("Average Price ($) by Bedrooms and Bathrooms")
ax_hm.set_xlabel("Bedrooms")
ax_hm.set_ylabel("Bathrooms")
st.pyplot(fig_hm)

# ============================================================
#           Visualization 2: Price Distribution Boxplot
# ============================================================

st.subheader("Price Distribution by Number of Bedrooms")

fig_box, ax_box = plt.subplots(figsize=(8, 5))
sns.boxplot(data=q2_df, x="BEDS", y="PRICE", ax=ax_box, palette="Blues")
ax_box.set_title("Price Distribution Across Bedroom Counts")
ax_box.set_xlabel("Bedrooms")
ax_box.set_ylabel("Price ($)")
st.pyplot(fig_box)

# ============================================================
#                      QUERY 3
#    Filter by maximum price + locality → map + table
# ============================================================

st.header("Query 3: Find Homes Under a Selected Price")

min_price = float(df_clean["PRICE"].min())
max_price = float(df_clean["PRICE"].max())

selected_price = st.slider(
    "Maximum Price (in dollars):",
    min_price,
    max_price,
    min_price
)

st.write(f"Showing homes under **${selected_price:,.0f}**")

query3_localities = st.multiselect("Select localities:", localities)

q3_df = df_clean[df_clean["PRICE"] <= selected_price]

if query3_localities:
    q3_df = q3_df[q3_df["LOCALITY"].isin(query3_localities)]

# ---------- Show Map ----------

st.subheader("Map of Filtered Homes")

map_q3 = q3_df.dropna(subset=["LATITUDE", "LONGITUDE"])
st.map(map_q3[["LATITUDE", "LONGITUDE"]])

# ---------- Show Table ----------

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

# ============================================================
#                 SUMMARY & INSIGHTS
# ============================================================

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
