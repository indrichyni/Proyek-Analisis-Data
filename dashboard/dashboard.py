import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe

def create_bycustomer_city_df(df):
    bycustomer_city_df = df.groupby(by="customer_city").agg({
        "customer_id": "nunique"
    }).sort_values(by="customer_id", ascending=False).reset_index()
    bycustomer_city_df.columns = ["customer_city", "customer_count"]

    return bycustomer_city_df


def create_bycustomer_state_df(df):
    bycustomer_state_df = df.groupby(by="customer_state").agg({
        "customer_id": "nunique"
    }).sort_values(by="customer_id", ascending=False).reset_index()
    bycustomer_state_df.columns = ["customer_state", "customer_count"]

    return bycustomer_state_df


recent_date = pd.to_datetime("today").date() #mengganti dengan tanggal terkini
def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": "max", #mengambil tanggal order terakhir
        "order_id": "nunique",
        "payment_value": "sum"
    })
    rfm_df.columns = ["customer_unique_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    #recent_date = df["order_date"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df


# import data
all_df = pd.read_csv(r"C:\Users\Indri Cahyani\Documents\dashboard\all_data.csv")

# datetime column for filter
all_df.sort_values(by="order_purchase_timestamp", ascending=True, inplace=True)
datetime_columns = [
    "order_purchase_timestamp",
    "order_estimated_delivery_date",
    "shipping_limit_date"]

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()



with st.sidebar:
    # menambahkan logo
    st.image(r"C:/Users/Indri Cahyani/Documents/dashboard/logo.png")

    # mengambil start date and end date dari date_input
    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) &
                 (all_df["order_purchase_timestamp"] <= str(end_date))]

bycustomer_city_df = create_bycustomer_city_df(main_df)
bycustomer_state_df = create_bycustomer_state_df(main_df)
rfm_df = create_rfm_df(main_df)

# Judul Dashboard
st.title("Welcome to Olist Store Dashboard :convenience_store:")
st.subheader("Customer Demographics")

# Membuat tab untuk City dan State
with st.container():
    tab_city, tab_state = st.tabs(["City", "State"])

    # Tab untuk City
    with tab_city:
        st.write("Customer Demographics by City")

        # Plot pertama: Customer by City
        fig_city, ax_city = plt.subplots(figsize=(10, 5))  # Mendefinisikan fig dan ax untuk City
        sns.barplot(
            x="customer_count",
            y="customer_city",
            data=bycustomer_city_df.head(5),
            ax=ax_city,
            orient="h",
            color="#FFC2B7"
        )
        ax_city.patches[0].set_facecolor("#FF6F61")
        ax_city.bar_label(ax_city.containers[0], label_type="edge", fontsize=15)
        ax_city.set_ylabel(None)
        ax_city.set_xlabel(None)
        ax_city.set_title("Number of Customers by City", fontsize=22)
        ax_city.tick_params(axis="y", labelsize=12)
        ax_city.tick_params(axis="x", labelsize=12)
        ax_city.margins(0.1)

        # Menampilkan plot untuk City di Streamlit
        st.pyplot(fig_city)

    # Tab untuk State
    with tab_state:
        st.write("Customer Demographics by State")

        # Plot kedua: Customer by State
        fig_state, ax_state = plt.subplots(figsize=(10, 5))  # Mendefinisikan fig dan ax untuk State
        sns.barplot(
            x="customer_count",
            y="customer_state",
            data=bycustomer_state_df.head(5),
            ax=ax_state,
            orient="h",
            color="#FFC2B7"
        )
        ax_state.patches[0].set_facecolor("#FF6F61")
        ax_state.bar_label(ax_state.containers[0], label_type="edge", fontsize=15, padding=3)
        ax_state.set_ylabel(None)
        ax_state.set_xlabel(None)
        ax_state.set_title("Number of Customers by State", fontsize=22)
        ax_state.invert_xaxis()
        ax_state.tick_params(axis="y", labelsize=12, labelleft=False, labelright=True)
        ax_state.tick_params(axis="x", labelsize=12)
        ax_state.margins(0.1)

        # Menampilkan plot untuk State di Streamlit
        st.pyplot(fig_state)

#Top 10 Penjualan Produk
totalPenjualan_df = all_df.groupby("product_category_name_english")["product_id"].count().reset_index()
totalPenjualan_df = totalPenjualan_df.rename(columns={"product_category_name_english": "Products Name"})
totalPenjualan_df = totalPenjualan_df.rename(columns={"product_id": "Products ID"})
totalPenjualan_df = totalPenjualan_df.sort_values(by="Products ID", ascending=False)
totalPenjualan_df = totalPenjualan_df.head(10)

st.header('Top 10 Product Categories by Number of Sales')
col1, col2 = st.columns(2)


with col1:
    st.dataframe(totalPenjualan_df)

with col2:
    st.write("Top 10 Product Categories by Number of Sales")

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(x='Products ID', y='Products Name', data=totalPenjualan_df, color='#FF6F61')


    plt.title('Top 10 Product Categories by Number of Sales', fontsize=16)
    plt.xlabel('Number of Products Sales', fontsize=14)
    plt.ylabel('Product Categories', fontsize=14)

    st.pyplot(fig)

# Rating Overview
ratingScores = all_df['review_score'].value_counts().sort_values(ascending=False)
most_common_score = ratingScores.idxmax()

st.header("Customer Satisfaction Ratings Overview")
colors = ["#FF6F61" if score == most_common_score else "grey" for score in ratingScores.index]

# Membuat plot untuk rating
fig_rating, ax_rating = plt.subplots(figsize=(10, 5))
sns.barplot(x=ratingScores.index,
            y=ratingScores.values,
            order=ratingScores.index,
            palette=colors)

plt.title("Customer Satisfaction Ratings Overview", fontsize=15)
plt.xlabel("Rating", fontsize=14)
plt.ylabel("Total Rate", fontsize=14)
plt.xticks(fontsize=12)
plt.tight_layout()

# Menampilkan plot rating di Streamlit
st.pyplot(fig_rating)

# Payment Types
payment_labels = {
    'credit_card': 'Credit Card',
    'boleto': 'Boleto',
    'voucher': 'Voucher',
    'debit_card': 'Debit',
    'not_defined': 'Other'  # Shortened label for 'not_defined'
}

# Replace the payment_type values with the new labels
all_df['payment_type'] = all_df['payment_type'].replace(payment_labels)


payment_counts = all_df['payment_type'].value_counts()
filtered_payment_counts = payment_counts[payment_counts.index != 'Other']
colors = ['#FF6F61', '#6A5ACD', '#FFD700', '#32CD32']

st.header('Distribution of Payment Types')

# Create the pie chart
fig, ax = plt.subplots(figsize=(4, 4))
ax.pie(filtered_payment_counts, 
       labels=filtered_payment_counts.index, 
       autopct='%1.1f%%', 
       startangle=140, 
       colors=colors, 
       explode=[0.1] * len(filtered_payment_counts))  # Add explosion effect for each slice

ax.set_title('Distribution of Payment Types', fontsize=12)
ax.axis('equal')

st.pyplot(fig)

# Monthly Sales Overview 
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])

# Extract month and year
all_df['bulan'] = all_df['order_purchase_timestamp'].dt.to_period('M')

# Group by bulan dan melakukan kalkulasi
penjualan_per_bulan = all_df.groupby('bulan')['price'].agg(['sum', 'mean']).reset_index()

penjualan_per_bulan['bulan'] = penjualan_per_bulan['bulan'].astype(str) + '-01'
penjualan_per_bulan['bulan'] = pd.to_datetime(penjualan_per_bulan['bulan'])

st.header("Sales Performance")
st.write(penjualan_per_bulan)

# Plot
st.subheader("Monthly Sales Overview")
plt.figure(figsize=(10, 6))
plt.plot(penjualan_per_bulan['bulan'], penjualan_per_bulan['sum'], marker='o', color='#FF6F61', linestyle='-')
plt.xlabel('Month')
plt.ylabel('Total Sales (Juta $)')
plt.title('Monthly Sales Overview')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()

st.pyplot(plt)

# RFM Analysis
st.header('Best Customer Based on RFM Parameters')
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(20, 8))

# Plot Recency
sns.barplot(
    y="recency",
    x="customer_unique_id",
    data=rfm_df.sort_values(by="recency", ascending=True).head(5),
    color="#72BCD4",
    ax=ax[0]
)
ax[0].set_ylabel("Days")
ax[0].set_xlabel("Customer Unique ID")
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis='x', labelsize=15, rotation=75)

# Plot Frequency
sns.barplot(
    x="customer_unique_id",
    y="frequency",
    data=rfm_df.sort_values(by="frequency", ascending=False).head(5),
    color="#72BCD4",
    ax=ax[1]
)
ax[1].set_xlabel("Customer Unique ID")
ax[1].set_ylabel("Frequency")
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15, rotation=75)

# Plot Monetary
sns.barplot(
    x="customer_unique_id",
    y="monetary",
    data=rfm_df.sort_values(by="monetary", ascending=False).head(5),
    color="#72BCD4",
    ax=ax[2]
)
ax[2].set_xlabel("Customer Unique ID")
ax[2].set_ylabel("Monetary")
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15, rotation=75)
ax[2].bar_label(ax[2].containers[0], label_type="edge", fontsize=15)

plt.suptitle("Best Customer Based on RFM Parameters (customer_unique_id)", fontsize=20)

# Display the plot in Streamlit
st.pyplot(fig)

st.caption('Copyright (C) Indri Cahyani - Project Dicoding - Bangkit. 2024')
