import pandas as pd

# 1. Đọc file dữ liệu (Đã sửa lỗi thiếu dấu \ và thêm r trước chuỗi đường dẫn)
df = pd.read_csv(r'E:\FPT Polytechnic\DATN1\Data\ecommerce_orders_dataset (1).csv')

# 2. Xây dựng bảng Dim_Customer
dim_customer = df[[
    'Customer_ID', 'Customer_Age', 'Customer_Gender', 
    'Country', 'City', 'Customer_Segment', 
    'Membership_Status', 'Customer_Lifetime_Value'
]].drop_duplicates(subset=['Customer_ID']).reset_index(drop=True)

# 3. Xây dựng bảng Dim_Product
dim_product = df[[
    'Product_ID', 'Product_Category', 'Product_Subcategory', 
    'Brand', 'Unit_Price'
]].drop_duplicates(subset=['Product_ID']).reset_index(drop=True)

# 4. Xây dựng bảng Dim_Date
df['Order_Date'] = pd.to_datetime(df['Order_Date'])
dim_date = df[[
    'Order_Date', 'Year', 'Month', 'Day', 
    'Day_Of_Week', 'Quarter', 'Season', 'Holiday_Season'
]].drop_duplicates(subset=['Order_Date']).reset_index(drop=True)

# 5. Xây dựng bảng Fact_Orders
fact_orders = df[[
    'Order_ID', 'Customer_ID', 'Product_ID', 'Order_Date', 
    'Quantity', 'Discount_Percent', 'Discount_Amount', 'Coupon_Used', 
    'Shipping_Cost', 'Tax_Amount', 'Order_Amount', 'Payment_Method', 
    'Device_Type', 'Traffic_Source', 'Shipping_Method', 'Warehouse_Region', 
    'Delivery_Days', 'Order_Status', 'Returned', 'Review_Rating', 
    'Profit_Margin_Percent', 'Profit_Amount', 'High_Value_Order'
]].copy()

print("Đã tạo thành công các bảng Dim và Fact!")
print(f"Dim_Customer: {dim_customer.shape}")
print(f"Dim_Product: {dim_product.shape}")
print(f"Dim_Date: {dim_date.shape}")
print(f"Fact_Orders: {fact_orders.shape}")