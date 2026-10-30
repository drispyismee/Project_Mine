-- ==========================================
-- BƯỚC 0: XÓA CÁC BẢNG CŨ NẾU ĐÃ TỒN TẠI
-- ==========================================
DROP TABLE IF EXISTS Fact_Orders;
DROP TABLE IF EXISTS Dim_Customer;
DROP TABLE IF EXISTS Dim_Product;
DROP TABLE IF EXISTS Dim_Location;
DROP TABLE IF EXISTS Dim_Date;
DROP TABLE IF EXISTS Dim_Logistics;
DROP TABLE IF EXISTS Dim_Marketing;


-- ==========================================
-- BƯỚC 1: TẠO CÁC BẢNG DIM
-- ==========================================

-- 1. Dim Khách hàng
CREATE TABLE Dim_Customer (
    DimCustomerID INT NOT NULL PRIMARY KEY,
    Customer_ID NVARCHAR(50),
    Customer_Age TINYINT,
    Customer_Gender NVARCHAR(50),
    Customer_Segment NVARCHAR(50),
    Membership_Status NVARCHAR(50),
    Customer_Lifetime_Value FLOAT
);

INSERT INTO Dim_Customer (DimCustomerID, Customer_ID, Customer_Age, Customer_Gender, Customer_Segment, Membership_Status, Customer_Lifetime_Value)
SELECT ROW_NUMBER() OVER (ORDER BY Customer_ID), Customer_ID, Customer_Age, Customer_Gender, Customer_Segment, Membership_Status, Customer_Lifetime_Value
FROM (SELECT DISTINCT Customer_ID, Customer_Age, Customer_Gender, Customer_Segment, Membership_Status, Customer_Lifetime_Value FROM dbo.ecommerce_orders_dataset) t;


-- 2. Dim Sản phẩm
CREATE TABLE Dim_Product (
    DimProductID INT NOT NULL PRIMARY KEY,
    Product_ID NVARCHAR(50),
    Product_Category NVARCHAR(50),
    Product_Subcategory NVARCHAR(50),
    Brand NVARCHAR(50)
);

INSERT INTO Dim_Product (DimProductID, Product_ID, Product_Category, Product_Subcategory, Brand)
SELECT ROW_NUMBER() OVER (ORDER BY Product_ID), Product_ID, Product_Category, Product_Subcategory, Brand
FROM (SELECT DISTINCT Product_ID, Product_Category, Product_Subcategory, Brand FROM dbo.ecommerce_orders_dataset) t;


-- 3. Dim Địa lý
CREATE TABLE Dim_Location (
    DimLocationID INT NOT NULL PRIMARY KEY,
    Country NVARCHAR(50),
    City NVARCHAR(50),
    Warehouse_Region NVARCHAR(50)
);

INSERT INTO Dim_Location (DimLocationID, Country, City, Warehouse_Region)
SELECT ROW_NUMBER() OVER (ORDER BY Country, City, Warehouse_Region), Country, City, Warehouse_Region
FROM (SELECT DISTINCT Country, City, Warehouse_Region FROM dbo.ecommerce_orders_dataset) t;


-- 4. Dim Thời gian
CREATE TABLE Dim_Date (
    DimDateID INT NOT NULL PRIMARY KEY,
    Order_Date DATE,
    [Year] SMALLINT,
    [Month] TINYINT,
    [Day] TINYINT,
    Day_Of_Week NVARCHAR(50),
    [Quarter] TINYINT,
    Season NVARCHAR(50),
    Holiday_Season NVARCHAR(50)
);

INSERT INTO Dim_Date (DimDateID, Order_Date, [Year], [Month], [Day], Day_Of_Week, [Quarter], Season, Holiday_Season)
SELECT ROW_NUMBER() OVER (ORDER BY Order_Date), Order_Date, [Year], [Month], [Day], Day_Of_Week, [Quarter], Season, Holiday_Season
FROM (SELECT DISTINCT Order_Date, [Year], [Month], [Day], Day_Of_Week, [Quarter], Season, Holiday_Season FROM dbo.ecommerce_orders_dataset) t;


-- 5. Dim Vận chuyển & Thanh toán
CREATE TABLE Dim_Logistics (
    DimLogisticsID INT NOT NULL PRIMARY KEY,
    Shipping_Method NVARCHAR(50),
    Payment_Method NVARCHAR(50),
    Device_Type NVARCHAR(50)
);

INSERT INTO Dim_Logistics (DimLogisticsID, Shipping_Method, Payment_Method, Device_Type)
SELECT ROW_NUMBER() OVER (ORDER BY Shipping_Method, Payment_Method, Device_Type), Shipping_Method, Payment_Method, Device_Type
FROM (SELECT DISTINCT Shipping_Method, Payment_Method, Device_Type FROM dbo.ecommerce_orders_dataset) t;


-- 6. Dim Marketing
CREATE TABLE Dim_Marketing (
    DimMarketingID INT NOT NULL PRIMARY KEY,
    Traffic_Source NVARCHAR(50)
);

INSERT INTO Dim_Marketing (DimMarketingID, Traffic_Source)
SELECT ROW_NUMBER() OVER (ORDER BY Traffic_Source), Traffic_Source
FROM (SELECT DISTINCT Traffic_Source FROM dbo.ecommerce_orders_dataset) t;


-- ==========================================
-- BƯỚC 2: TẠO BẢNG FACT (DÙNG ID TỰ TĂNG LÀM KHÓA CHÍNH)
-- ==========================================
SELECT 
    ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS FactOrder_ID, -- Khóa chính tự sinh tránh lỗi trùng Order_ID
    o.Order_ID,
    d.DimCustomerID,
    p.DimProductID,
    l.DimLocationID,
    dt.DimDateID,
    log.DimLogisticsID,
    m.DimMarketingID,
    o.Unit_Price, o.Quantity, o.Discount_Percent, o.Discount_Amount,
    o.Coupon_Used, o.Shipping_Cost, o.Tax_Amount, o.Order_Amount,
    o.Delivery_Days, o.Order_Status, o.Returned, o.Review_Rating,
    o.Profit_Margin_Percent, o.Profit_Amount, o.High_Value_Order
INTO Fact_Orders
FROM dbo.ecommerce_orders_dataset o
LEFT JOIN Dim_Customer d ON o.Customer_ID = d.Customer_ID
LEFT JOIN Dim_Product p ON o.Product_ID = p.Product_ID
LEFT JOIN Dim_Location l ON o.Country = l.Country AND o.City = l.City AND o.Warehouse_Region = l.Warehouse_Region
LEFT JOIN Dim_Date dt ON o.Order_Date = dt.Order_Date
LEFT JOIN Dim_Logistics log ON o.Shipping_Method = log.Shipping_Method AND o.Payment_Method = log.Payment_Method AND o.Device_Type = log.Device_Type
LEFT JOIN Dim_Marketing m ON o.Traffic_Source = m.Traffic_Source;

-- Đặt khóa chính trên cột FactOrder_ID vừa tạo
ALTER TABLE Fact_Orders ALTER COLUMN FactOrder_ID INT NOT NULL;
ALTER TABLE Fact_Orders ADD PRIMARY KEY (FactOrder_ID);


-- ==========================================
-- BƯỚC 3: THIẾT LẬP RÀNG BUỘC KHÓA NGOẠI (FK)
-- ==========================================
ALTER TABLE Fact_Orders ADD CONSTRAINT FK_Fact_Customer FOREIGN KEY (DimCustomerID) REFERENCES Dim_Customer(DimCustomerID);
ALTER TABLE Fact_Orders ADD CONSTRAINT FK_Fact_Product FOREIGN KEY (DimProductID) REFERENCES Dim_Product(DimProductID);
ALTER TABLE Fact_Orders ADD CONSTRAINT FK_Fact_Location FOREIGN KEY (DimLocationID) REFERENCES Dim_Location(DimLocationID);
ALTER TABLE Fact_Orders ADD CONSTRAINT FK_Fact_Date FOREIGN KEY (DimDateID) REFERENCES Dim_Date(DimDateID);
ALTER TABLE Fact_Orders ADD CONSTRAINT FK_Fact_Logistics FOREIGN KEY (DimLogisticsID) REFERENCES Dim_Logistics(DimLogisticsID);
ALTER TABLE Fact_Orders ADD CONSTRAINT FK_Fact_Marketing FOREIGN KEY (DimMarketingID) REFERENCES Dim_Marketing(DimMarketingID);