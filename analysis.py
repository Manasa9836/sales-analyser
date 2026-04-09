import pandas as pd

# ================= LOAD & CLEAN DATA ================= #
def load_data():
    file = "Adidas US Sales Datasets.xlsx"

    # Load dataset
    df = pd.read_excel(file, sheet_name="Data Sales Adidas", skiprows=3)

    # Fix header
    df.columns = df.iloc[0]
    df = df[1:]

    # Clean column names
    df.columns = df.columns.astype(str).str.strip()

    # Remove unwanted column
    df = df.drop(columns=['nan'], errors='ignore')

    # Remove empty rows
    df.dropna(how='all', inplace=True)

    # Reset index
    df.reset_index(drop=True, inplace=True)

    # ================= DATA TYPE FIX ================= #
    df["Total Sales"] = pd.to_numeric(df["Total Sales"], errors='coerce')
    df["Operating Profit"] = pd.to_numeric(df["Operating Profit"], errors='coerce')
    df["Units Sold"] = pd.to_numeric(df["Units Sold"], errors='coerce')

    df["Invoice Date"] = pd.to_datetime(df["Invoice Date"], errors='coerce')

    # Fill numeric nulls
    df[["Total Sales", "Operating Profit", "Units Sold"]] = df[
        ["Total Sales", "Operating Profit", "Units Sold"]
    ].fillna(0)

    # ================= FEATURE ENGINEERING ================= #

    # Time features
    df["Year"] = df["Invoice Date"].dt.year
    df["Month"] = df["Invoice Date"].dt.month
    df["Month Name"] = df["Invoice Date"].dt.strftime('%b')

    # Sort months properly
    month_order = ['Jan','Feb','Mar','Apr','May','Jun',
                   'Jul','Aug','Sep','Oct','Nov','Dec']
    df["Month Name"] = pd.Categorical(df["Month Name"],
                                      categories=month_order,
                                      ordered=True)

    # Business metrics
    df["Revenue per Unit"] = df["Total Sales"] / df["Units Sold"]
    df["Profit per Unit"] = df["Operating Profit"] / df["Units Sold"]
    df["Profit Ratio"] = df["Operating Profit"] / df["Total Sales"]

    return df


# ================= KPI CALCULATIONS ================= #
def get_kpis(df):
    total_sales = df["Total Sales"].sum()
    total_profit = df["Operating Profit"].sum()
    total_units = df["Units Sold"].sum()

    profit_margin = (total_profit / total_sales) * 100 if total_sales != 0 else 0

    return {
        "Total Sales": total_sales,
        "Total Profit": total_profit,
        "Total Units": total_units,
        "Profit Margin (%)": profit_margin,
        "Max Sale": df["Total Sales"].max(),
        "Min Sale": df["Total Sales"].min(),
        "Average Sale": df["Total Sales"].mean()
    }


# ================= CHART DATA ================= #
def get_chart_data(df):

    sales_by_region = df.groupby("Region")["Total Sales"].sum().reset_index()

    sales_by_product = (
        df.groupby("Product")["Total Sales"]
        .sum()
        .reset_index()
        .sort_values(by="Total Sales", ascending=False)
    )

    sales_by_method = (
        df.groupby("Sales Method")["Total Sales"]
        .sum()
        .reset_index()
    )

    monthly_sales = (
        df.groupby("Month Name")["Total Sales"]
        .sum()
        .reset_index()
        .sort_values("Month Name")
    )

    sales_trend = (
        df.groupby("Invoice Date")["Total Sales"]
        .sum()
        .reset_index()
    )

    top_cities = (
        df.groupby("City")["Total Sales"]
        .sum()
        .reset_index()
        .sort_values(by="Total Sales", ascending=False)
    )

    profit_by_region = (
        df.groupby("Region")["Operating Profit"]
        .sum()
        .reset_index()
    )

    return {
        "sales_by_region": sales_by_region,
        "sales_by_product": sales_by_product,
        "sales_by_method": sales_by_method,
        "monthly_sales": monthly_sales,
        "sales_trend": sales_trend,
        "top_cities": top_cities,
        "profit_by_region": profit_by_region
    }


# ================= INSIGHTS ================= #
def get_insights(df):
    best_region = df.groupby("Region")["Total Sales"].sum().idxmax()
    best_product = df.groupby("Product")["Total Sales"].sum().idxmax()
    best_method = df.groupby("Sales Method")["Total Sales"].sum().idxmax()
    best_city = df.groupby("City")["Total Sales"].sum().idxmax()

    return {
        "Best Region": best_region,
        "Best Product": best_product,
        "Best Sales Method": best_method,
        "Best City": best_city
    }


# ================= MAIN (FOR TESTING) ================= #