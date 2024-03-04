import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency



def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_sum_spend_df(df):
    sum_spend_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "payment_value": "sum"
    })
    sum_spend_df = sum_spend_df.reset_index()
    sum_spend_df.rename(columns={
        "payment_value": "total_spend"
    }, inplace=True)

    return sum_spend_df

def create_sum_category(df):
    sum_category = df.groupby("product_category_name")["product_id"].count().reset_index()
    sum_category.rename(columns={
        "product_id": "product_count"
    }, inplace=True)
    sum_category = sum_category.sort_values(by='product_count', ascending=False)

    return sum_category

def create_payment_sum_category(df):
    sum_category = df.groupby("product_category_name").payment_value.sum().sort_values(ascending=False).reset_index()
    sum_category.rename(columns={
        "order_id": "nunique",
        "payment_value": "payment_sum"
    }, inplace=True)
    sum_category = sum_category.sort_values(by='payment_sum', ascending=False)
    print(sum_category)
    return sum_category

def create_bystate_city_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    return bystate_df, bycity_df



all_df = pd.read_csv("https://raw.githubusercontent.com/Azzoekroef/data-analyst-dicoding/master/dashboard/main_data.csv")
datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date", "order_approved_at", "order_delivered_carrier_date", "order_estimated_delivery_date", "shipping_limit_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Pilih Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]


daily_orders_df = create_daily_orders_df(main_df)
sum_category = create_sum_category(main_df)
payment_sum_category = create_payment_sum_category(main_df)
state, city = create_bystate_city_df(main_df)


st.subheader('customer spend')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL") 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
sns.lineplot(
    x=daily_orders_df["order_purchase_timestamp"],
    y=daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#9290C3"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.subheader("Category items trend")
col1,= st.columns(1)

with col1:
    total_items = sum_category["product_count"].sum()
    st.metric("Total items", value=total_items)


fig1, ax = plt.subplots(nrows=1, ncols=2, figsize=(30, 15))

colors = ["#1B1A55", "#9290C3", "#9290C3", "#9290C3", "#9290C3", "#9290C3", "#9290C3", "#9290C3", "#9290C3", "#9290C3", "#9290C3", "#9290C3"]

sns.barplot(x="product_count", y="product_category_name", data=sum_category.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("\nBest Performing category Product", loc="center", fontsize=45)
ax[0].tick_params(axis ='y', labelsize=40)
ax[0].tick_params(axis ='x', labelsize=50)

sns.barplot(x="product_count", y="product_category_name", data=sum_category.sort_values(by="product_count", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("\nWorst Performing category Product", loc="center", fontsize=45)
ax[1].tick_params(axis='y', labelsize=40)
ax[1].tick_params(axis ='x', labelsize=50)

plt.suptitle("Best and Worst category", fontsize=60)

st.pyplot(fig1)


st.subheader("Category items revenue")


fig2, ax = plt.subplots(nrows=1, ncols=2, figsize=(30, 15))

sns.barplot(x="payment_sum", y="product_category_name", data=payment_sum_category.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing category Product", loc="center", fontsize=45)
ax[0].tick_params(axis='y', labelsize=40)
ax[0].tick_params(axis ='x', labelsize=50)
ax[0].xaxis.get_offset_text().set_fontsize(40)

sns.barplot(x="payment_sum", y="product_category_name", data=payment_sum_category.sort_values(by="payment_sum", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing category Product", loc="center", fontsize=45)
ax[1].tick_params(axis='y', labelsize=40)
ax[1].tick_params(axis ='x', labelsize=50)

st.pyplot(fig2)

st.subheader("Customer Demographics")

fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(
    y="customer_count", 
    x=state.customer_state.value_counts().index,
    data=state.sort_values(by="customer_count", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title("Number of Customer by States", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=15)
st.pyplot(fig)

fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(
    x="customer_count", 
    y="customer_city",
    data=city.sort_values(by="customer_count", ascending=False).head(10),
    palette=colors,
    ax=ax
)
ax.set_title("Number of Customer in Top 10 City", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=20, rotation= 35)
ax.tick_params(axis='y', labelsize=15)
st.pyplot(fig)
