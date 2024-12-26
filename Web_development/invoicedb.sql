-- DROP DATABASE IF EXISTS InvoiceDB;
-- Step 1: Create the new Database
CREATE DATABASE InvoiceDB;

-- Step 2: Use the new Database
USE InvoiceDB;

-- Step 3: Create Table for Suppliers
CREATE TABLE suppliers (
    Supplier_ID INT AUTO_INCREMENT PRIMARY KEY,  -- Make Supplier_ID auto-increment and primary key
    NTN VARCHAR(20) UNIQUE NOT NULL,
    NAME VARCHAR(100),
    BUSINESS_NAME VARCHAR(100),
    S_T_REG_NO VARCHAR(50),
    Phone_Number VARCHAR(50),
    Address TEXT
);

-- Step 4: Create Table for Buyers
CREATE TABLE Buyers (
    Buyer_ID INT AUTO_INCREMENT PRIMARY KEY,  -- Make Buyer_ID auto-increment and primary key
    NTN VARCHAR(20) UNIQUE NOT NULL,
    NAME VARCHAR(100),
    S_T_REG_NO VARCHAR(50),
    Address TEXT
);

-- Step 5: Create Table for Invoices
CREATE TABLE Invoices (
    Invoice_ID INT AUTO_INCREMENT PRIMARY KEY,
    Receipt_NO VARCHAR(20) UNIQUE NOT NULL,
    Supplier_ID INT,
    Buyer_ID INT,
    Date DATE,
    Total_Amount DECIMAL(10, 2),
    FOREIGN KEY (Supplier_ID) REFERENCES Suppliers(Supplier_ID),
    FOREIGN KEY (Buyer_ID) REFERENCES Buyers(Buyer_ID)
);

-- Step 6: Create Table for Invoice Items
CREATE TABLE Invoice_Items (
    Item_ID INT AUTO_INCREMENT PRIMARY KEY,
    Invoice_ID INT,
    Item_Name VARCHAR(100),
    Quantity INT,
    Rate DECIMAL(10, 2),
    Amount DECIMAL(10, 2),
    FOREIGN KEY (Invoice_ID) REFERENCES Invoices(Invoice_ID)
);

-- Step 7: Optional - Create Indexes (If needed for performance)
CREATE INDEX idx_supplier_ntn ON Suppliers (NTN);
CREATE INDEX idx_buyer_ntn ON Buyers (NTN);
CREATE INDEX idx_invoice_receipt_no ON Invoices (Receipt_NO);

INSERT INTO Buyers (NTN, NAME, S_T_REG_NO, Address)
VALUES 
('1122334455', 'John Doe', 'ST678', '123 Buyer St, City, Country'),
('2233445566', 'Jane Smith', 'ST789', '234 Buyer Ave, City, Country'),
('3344556677', 'Michael Johnson', 'ST890', '345 Buyer Rd, City, Country'),
('4455667788', 'Emily Davis', 'ST901', '456 Buyer Blvd, City, Country'),
('5566778899', 'David Wilson', 'ST012', '567 Buyer Lane, City, Country');

INSERT INTO Suppliers (NTN, NAME, BUSINESS_NAME, S_T_REG_NO, Phone_Number, Address)
VALUES 
('1234567890', 'ABC Suppliers', 'ABC Trading Co.', 'ST123', '123-456-7890', '123 Supplier St, City, Country'),
('2345678901', 'XYZ Supplies', 'XYZ Distributors', 'ST234', '234-567-8901', '234 Supplier Ave, City, Country'),
('3456789012', 'PQR Manufacturers', 'PQR Corp.', 'ST345', '345-678-9012', '345 Supplier Rd, City, Country'),
('4567890123', 'MNO Enterprises', 'MNO International', 'ST456', '456-789-0123', '456 Supplier Blvd, City, Country'),
('5678901234', 'DEF Products', 'DEF Trading Ltd.', 'ST567', '567-890-1234', '567 Supplier Lane, City, Country');

INSERT INTO Invoices (Receipt_NO, Supplier_ID, Buyer_ID, Date, Total_Amount)
VALUES 
('REC001', 1, 1, '2024-12-01', 1500.00),
('REC002', 2, 2, '2024-12-02', 2000.00),
('REC003', 3, 3, '2024-12-03', 2500.00),
('REC004', 4, 4, '2024-12-04', 1800.00),
('REC005', 5, 5, '2024-12-05', 2200.00);

INSERT INTO Invoice_Items (Invoice_ID, Item_Name, Quantity, Rate, Amount)
VALUES 
(1, 'Laptop', 5, 300.00, 1500.00),
(1, 'Mouse', 10, 10.00, 100.00),
(2, 'Printer', 8, 250.00, 2000.00),
(2, 'Scanner', 5, 100.00, 500.00),
(3, 'Smartphone', 4, 625.00, 2500.00),
(3, 'Charger', 6, 20.00, 120.00),
(4, 'Tablet', 6, 300.00, 1800.00),
(4, 'Headphones', 4, 50.00, 200.00),
(5, 'Camera', 5, 400.00, 2000.00),
(5, 'Tripod', 3, 66.67, 200.00);

