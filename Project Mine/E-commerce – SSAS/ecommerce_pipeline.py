"""Reproducible cleaning + star schema + exploratory charts.
Run: python ecommerce_pipeline.py --input ecommerce_orders_dataset.csv --output output
Dependencies: pandas, numpy, matplotlib
"""
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", default="output")
    args=ap.parse_args()
    out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
    raw=pd.read_csv(args.input); df=raw.copy()
    df.columns=[c.strip() for c in df.columns]
    for c in df.select_dtypes(include="object").columns:
        df[c]=df[c].astype("string").str.strip().replace({"":pd.NA,"NULL":pd.NA,"null":pd.NA,"N/A":pd.NA,"NA":pd.NA})
    df["Order_Date"]=pd.to_datetime(df["Order_Date"],errors="coerce")
    for c in ["Year","Month","Day","Quarter","Customer_Age","Unit_Price","Quantity","Discount_Percent","Discount_Amount","Shipping_Cost","Tax_Amount","Order_Amount","Delivery_Days","Review_Rating","Customer_Lifetime_Value","Profit_Margin_Percent","Profit_Amount"]:
        df[c]=pd.to_numeric(df[c],errors="coerce")
    report=[("rows_input",len(raw)),("exact_duplicate_rows",int(df.duplicated().sum())),("duplicate_order_id_rows",int(df["Order_ID"].duplicated().sum())),("missing_cells_before_cleaning",int(df.isna().sum().sum())),("invalid_dates",int(df["Order_Date"].isna().sum()))]
    df=df.drop_duplicates().sort_values("Order_Date").drop_duplicates("Order_ID",keep="first").dropna(subset=["Order_Date"])
    for c in df.select_dtypes(include="object").columns: df[c]=df[c].fillna("Unknown")
    for c in df.select_dtypes(include="number").columns:
        if df[c].isna().any(): df[c]=df[c].fillna(df[c].median())
    df["Year"]=df.Order_Date.dt.year; df["Month"]=df.Order_Date.dt.month; df["Day"]=df.Order_Date.dt.day; df["Quarter"]=df.Order_Date.dt.quarter; df["Day_Of_Week"]=df.Order_Date.dt.day_name()
    report.append(("rows_after_cleaning",len(df)))
    pd.DataFrame(report,columns=["check","value"]).to_csv(out/"data_quality_report.csv",index=False)
    date=pd.DataFrame({"Date":pd.date_range(df.Order_Date.min().normalize(),df.Order_Date.max().normalize())})
    date["DateKey"]=date.Date.dt.strftime("%Y%m%d").astype(int); date["Year"]=date.Date.dt.year; date["Quarter"]=date.Date.dt.quarter; date["Month"]=date.Date.dt.month; date["MonthName"]=date.Date.dt.month_name(); date["Day"]=date.Date.dt.day; date["DayOfWeek"]=date.Date.dt.day_name(); date["WeekdayNumber"]=date.Date.dt.dayofweek+1; date["IsWeekend"]=date.WeekdayNumber.isin([6,7]).astype(int); date["Date"]=date.Date.dt.strftime("%Y-%m-%d")
    date=date[["DateKey","Date","Year","Quarter","Month","MonthName","Day","DayOfWeek","WeekdayNumber","IsWeekend"]]
    specs={
      "DimCustomer":(["Customer_ID","Customer_Age","Customer_Gender","Customer_Segment","Membership_Status","Customer_Lifetime_Value"],"Customer_ID","CustomerKey"),
      "DimProduct":(["Product_ID","Product_Category","Product_Subcategory","Brand"],"Product_ID","ProductKey"),
      "DimGeography":(["Country","City","Warehouse_Region"],["Country","City","Warehouse_Region"],"GeographyKey"),
      "DimOrderContext":(["Payment_Method","Device_Type","Traffic_Source","Shipping_Method","Order_Status","Returned","Coupon_Used","Season","Holiday_Season","High_Value_Order"],["Payment_Method","Device_Type","Traffic_Source","Shipping_Method","Order_Status","Returned","Coupon_Used","Season","Holiday_Season","High_Value_Order"],"OrderContextKey")
    }
    dims={}
    for name,(cols,uniq,key) in specs.items():
        dim=df[cols].drop_duplicates(uniq).sort_values(cols).reset_index(drop=True)
        dim.insert(0,key,range(1,len(dim)+1)); dims[name]=dim; dim.to_csv(out/f"{name}.csv",index=False,encoding="utf-8-sig")
    date.to_csv(out/"DimDate.csv",index=False,encoding="utf-8-sig")
    df["DateKey"]=df.Order_Date.dt.strftime("%Y%m%d").astype(int)
    for name,cols,key,src in [("CustomerKey",["Customer_ID"],"CustomerKey","DimCustomer"),("ProductKey",["Product_ID"],"ProductKey","DimProduct"),("GeographyKey",["Country","City","Warehouse_Region"],"GeographyKey","DimGeography"),("OrderContextKey",specs["DimOrderContext"][0],"OrderContextKey","DimOrderContext")]:
        df=df.merge(dims[src][[key]+cols],on=cols,how="left")
    fact=df[["Order_ID","DateKey","CustomerKey","ProductKey","GeographyKey","OrderContextKey","Unit_Price","Quantity","Discount_Percent","Discount_Amount","Shipping_Cost","Tax_Amount","Order_Amount","Delivery_Days","Review_Rating","Profit_Margin_Percent","Profit_Amount"]]
    fact.to_csv(out/"FactOrders.csv",index=False,encoding="utf-8-sig")
    df.to_csv(out/"cleaned_orders.csv",index=False,encoding="utf-8-sig")
    monthly=df.groupby(df.Order_Date.dt.to_period("M")).Order_Amount.sum()
    category=df.groupby("Product_Category").Order_Amount.sum().sort_values(ascending=False)
    fig,ax=plt.subplots(1,2,figsize=(13,5)); monthly.plot(ax=ax[0],marker="o",title="Order Amount by Month"); ax[0].tick_params(axis="x",rotation=60); category.plot(kind="bar",ax=ax[1],title="Order Amount by Category"); fig.tight_layout(); fig.savefig(out/"dashboard_preview.png",dpi=150)
    print(f"Done. Clean rows: {len(df)}. Output folder: {out.resolve()}")
if __name__=="__main__": main()
