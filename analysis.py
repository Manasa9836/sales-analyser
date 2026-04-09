import pandas as pd
import streamlit as st
import os

def load_data():
    try:
        file = os.path.join(os.path.dirname(__file__), "Adidas US Sales Datasets.xlsx")
        df = pd.read_excel(file, sheet_name="Data Sales Adidas", skiprows=3)
        st.write("✅ File loaded successfully")
    except Exception as e:
        st.error(f"❌ ERROR LOADING FILE: {e}")
        return pd.DataFrame()

    # CLEANING
    df["Total Sales"] = pd.to_numeric(df["Total Sales"], errors='coerce')
    df["Operating Profit"] = pd.to_numeric(df["Operating Profit"], errors='coerce')
    df["Units Sold"] = pd.to_numeric(df["Units Sold"], errors='coerce')

    df["Invoice Date"] = pd.to_datetime(df["Invoice Date"], errors='coerce')
    df = df.dropna(subset=["Invoice Date"])

    df[["Total Sales", "Operating Profit", "Units Sold"]] = df[
        ["Total Sales", "Operating Profit", "Units Sold"]
    ].fillna(0)

    df["Year"] = df["Invoice Date"].dt.year
    df["Month"] = df["Invoice Date"].dt.month
    df["Month Name"] = df["Invoice Date"].dt.strftime('%b')

    return df