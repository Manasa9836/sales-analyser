import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import hashlib
from analysis import load_data, get_kpis, get_chart_data, get_insights
from PIL import Image

# ================= DATABASE ================= #
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT,
    password TEXT
)
""")
conn.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    c.execute("INSERT INTO users VALUES (?,?)", (username, hash_password(password)))
    conn.commit()

def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    return c.fetchone()

# ================= SESSION ================= #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ================= LOGIN ================= #
if not st.session_state.logged_in:

    st.set_page_config(page_title="Login", layout="centered")

    st.markdown("""
    <style>
    .stApp { background: black; }

    .title {
        font-size: 28px;
        font-weight: bold;
        text-align: center;
        color: white;
    }

    .subtitle {
        text-align: center;
        color: #aaa;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='title'>Business Sales Analyser</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        img = Image.open("logo.png")
        img = img.resize((300, 220))
        st.image(img)

    st.markdown("<div class='subtitle'>🔐 Login / Signup</div>", unsafe_allow_html=True)

    menu = st.radio("Select Option", ["Login", "Signup"], horizontal=True, label_visibility="collapsed")

    if menu == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid Credentials")

    else:
        new_user = st.text_input("Create Username")
        new_pass = st.text_input("Create Password", type="password")

        if st.button("Signup"):
            create_user(new_user, new_pass)
            st.success("Account created! Please login.")

# ================= MAIN APP ================= #
else:

    st.set_page_config(page_title="Sales Dashboard", layout="wide")

    # 🌙 GLOBAL DARK THEME
    st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: white;
    }

    section[data-testid="stSidebar"] {
        background-color: #111827;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1f2937, #374151);
        border-radius: 12px;
        padding: 15px;
        border-left: 5px solid #3b82f6;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center;'>📊 Business Sales Analyser</h1>", unsafe_allow_html=True)

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    @st.cache_data
    def load_data_cached():
        return load_data()

    df = load_data_cached()

    # ================= SIDEBAR ================= #
    st.sidebar.header("🔍 Filters")

    region = st.sidebar.multiselect("🌍 Region", df["Region"].unique())
    product = st.sidebar.multiselect("🛍 Product", df["Product"].unique())

    date_range = st.sidebar.date_input(
        "📅 Date Range",
        (df["Invoice Date"].min(), df["Invoice Date"].max())
    )

    if len(date_range) != 2:
        st.stop()

    start_date, end_date = date_range

    region = region if region else df["Region"].dropna().unique()
    product = product if product else df["Product"].dropna().unique()

    filtered_df = df.copy()

    if filtered_df.empty:
        st.warning("No data")
        st.stop()

    kpis = get_kpis(filtered_df)
    charts = get_chart_data(filtered_df)
    insights = get_insights(filtered_df)

    page = st.sidebar.radio("📂 Navigate", [
        "Overview",
        "Sales Analysis",
        "Business Forecasting & Strategy",
        "Raw Data"
    ])

    # ================= OVERVIEW ================= #
    if page == "Overview":

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Sales", f"{kpis['Total Sales']:,.0f}")
        c2.metric("Total Profit", f"{kpis['Total Profit']:,.0f}")
        c3.metric("Total Units", f"{kpis['Total Units']:,.0f}")
        c4.metric("Profit Margin", f"{kpis['Profit Margin (%)']:.2f}%")

        st.success(f"🏆 Best Region: {insights['Best Region']}") 
        st.success(f"🛍 Best Product: {insights['Best Product']}") 
        st.success(f"📊 Best Method: {insights['Best Sales Method']}") 
        st.success(f"🏙 Best City: {insights['Best City']}")
    # ================= SALES ================= #
    elif page == "Sales Analysis":

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(
                px.bar(charts["sales_by_region"], x="Region", y="Total Sales", template="plotly_dark"),
                use_container_width="stretch"
            )

        with col2:
            st.plotly_chart(
                px.bar(charts["profit_by_region"], x="Region", y="Operating Profit", template="plotly_dark"),
                use_container_width="stretch"
            )

        col3, col4 = st.columns(2)

        with col3:
            st.plotly_chart(
                px.line(charts["monthly_sales"], x="Month Name", y="Total Sales", template="plotly_dark"),
                use_container_width="stretch"
            )

        with col4:
            st.plotly_chart(
                px.pie(charts["sales_by_product"], names="Product", values="Total Sales", template="plotly_dark"),
                use_container_width="stretch"
            )

        st.plotly_chart(
            px.scatter(filtered_df, x="Units Sold", y="Total Sales", color="Region", template="plotly_dark"),
            use_container_width="stretch"
        )

        corr = filtered_df[["Total Sales","Operating Profit","Units Sold","Price per Unit"]].corr()
        st.plotly_chart(
            px.imshow(corr, text_auto=True, template="plotly_dark"),
            use_container_width="stretch"
        )

    # ================= FORECAST ================= #
    elif page == "Business Forecasting & Strategy":

        profit = filtered_df.groupby(filtered_df["Invoice Date"].dt.to_period("M"))["Operating Profit"].sum().reset_index()
        profit["Invoice Date"] = profit["Invoice Date"].astype(str)

        if len(profit) > 1:
            growth = profit["Operating Profit"].iloc[-1] - profit["Operating Profit"].iloc[-2]
            pred = profit["Operating Profit"].iloc[-1] + growth
            st.metric("Predicted Profit", f"{pred:,.0f}")

        st.plotly_chart(
            px.line(profit, x="Invoice Date", y="Operating Profit", template="plotly_dark"),
            use_container_width=True
        )

        change = st.slider("Price Change %", -50, 50, 0)
        st.metric("Simulated Sales", f"{filtered_df['Total Sales'].sum()*(1+change/100):,.0f}")

    # ================= RAW ================= #
    elif page == "Raw Data":

        st.subheader("📄 Raw Dataset")

        # 🔍 DEBUG (VERY IMPORTANT)
        st.write("Original DF shape:", df.shape)
        st.write("Filtered DF shape:", filtered_df.shape)
        st.write("Columns:", list(filtered_df.columns))

        if filtered_df.empty:
            st.error("❌ Filter removed all data!")

            st.write("Selected Region:", region)
            st.write("Selected Product:", product)
            st.write("Date Range:", start_date, end_date)

        else:
            st.success("✅ Data is present")

            st.dataframe(filtered_df, width="stretch")

            csv = filtered_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "📥 Download Data",
                csv,
                "sales_data.csv",
                "text/csv"
            )