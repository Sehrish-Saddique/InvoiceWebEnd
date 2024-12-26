
# Web Development Invoice Management System

## Overview

This is a simple **Invoice Management System** built using **Flask**, **MySQL** (for the database), and basic HTML templates. The system allows users to query invoices based on dates and supplier/buyer names/NTNs, calculate the total sales, sales tax, and display detailed invoice records.

### Features
- Query invoices by date range and supplier/buyer name or NTN.
- Calculate total sales and total sales tax.
- View detailed records of invoices, including item details.
- Upload and store invoice data in the MySQL database.

---

## Prerequisites

Before running the application, ensure you have the following installed:
- **Python 3.x** (preferably Python 3.7 or higher)
- **MySQL** (for database storage)
- **pip** (for installing dependencies)

---

## Installation

### 1. Clone or Download the Repository
Download or clone this project to your local machine.

```bash
git clone <your_repository_url>
```

### 2. Install Python Dependencies
Navigate to the project directory and install the necessary Python packages:

```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, you can manually install the following packages:

```bash
pip install flask mysql-connector
```

### 3. Set up the Database

- Open `invoicedb.sql` and run the SQL script to create the necessary tables in your MySQL database.

```sql
CREATE DATABASE IF NOT EXISTS InvoiceDB;

USE InvoiceDB;

CREATE TABLE IF NOT EXISTS Invoices (
    Invoice_ID INT AUTO_INCREMENT PRIMARY KEY,
    Receipt_NO VARCHAR(50) NOT NULL UNIQUE,
    Supplier_ID INT,
    Buyer_ID INT,
    Date DATE,
    Total_Amount DECIMAL(10, 2)
);

CREATE TABLE IF NOT EXISTS Invoice_Items (
    Item_ID INT AUTO_INCREMENT PRIMARY KEY,
    Invoice_ID INT,
    Item_Name VARCHAR(100),
    Quantity INT,
    Rate DECIMAL(10, 2),
    Amount DECIMAL(10, 2),
    FOREIGN KEY (Invoice_ID) REFERENCES Invoices(Invoice_ID)
);

CREATE TABLE IF NOT EXISTS Suppliers (
    Supplier_ID INT AUTO_INCREMENT PRIMARY KEY,
    NAME VARCHAR(100),
    NTN VARCHAR(50) UNIQUE
);

CREATE TABLE IF NOT EXISTS Buyers (
    Buyer_ID INT AUTO_INCREMENT PRIMARY KEY,
    NAME VARCHAR(100),
    NTN VARCHAR(50) UNIQUE
);
```

- Ensure your MySQL server is running and that the database is accessible.

### 4. Configure Database Connection
In `app.py`, ensure that the `get_db_connection()` function connects to your MySQL database using the correct credentials. Example:

```python
import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',  # Change to your MySQL username
        password='password',  # Change to your MySQL password
        database='InvoiceDB'  # Change to your database name
    )
    return conn
```

---

## Running the Application

1. **Start the Flask Application**:
   
   Navigate to the directory containing `app.py` and run:

   ```bash
   python app.py
   ```

2. **Access the Application**:
   
   Open your web browser and go to:

   ```
   http://127.0.0.1:5000/
   ```

---

## Usage

### Home Page:
- The home page will allow you to input a **company name or NTN**, along with a **start date** and **end date** to query the invoices.

### Query Results Page:
- Once the query is executed, you will see:
  - **Total Sales**: The sum of the invoice amounts within the given date range.
  - **Total Sales Tax Paid**: The sales tax calculated as 18% of the total sales.
  - **Detailed Records**: A table with detailed records of each invoice and its items, including invoice ID, receipt number, supplier, buyer, date, item name, quantity, rate, and amount.

---

## Folder Structure

The project is organized into the following structure:

```
Web_development/
│
├── app.py              # Main application script
├── invoicedb.sql       # SQL script to create the database
├── uploads/            # Folder for uploading files (e.g., invoices)
├── static/             # Folder for static assets (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── img/
├── templates/          # Folder for HTML templates (Flask uses Jinja templating)
│   ├── index.html      # Homepage template
│   └── query_results.html  # Query results template
└── requirements.txt    # List of Python dependencies (if applicable)
```

---

## Code Explanation

### `app.py`
- **Functions**:
  - `get_db_connection()`: Establishes a connection to the MySQL database.
  - `query_invoices()`: Handles the form submission to query invoices based on the provided dates and supplier/buyer information. It calculates total sales, sales tax, and retrieves detailed records.
  
  The main function in `app.py` runs a Flask application that listens for requests on the `/` and `/query_invoices` routes.

### `invoicedb.sql`
This file contains the SQL script to create the required tables in the MySQL database for invoices, suppliers, buyers, and invoice items.

### `templates/`
- **`index.html`**: The main page where users enter the date range and company or NTN information.
- **`query_results.html`**: Displays the query results, including total sales, sales tax, and detailed invoice records.

---

## Troubleshooting

### Common Issues:
- **Database Connection Errors**: Ensure that MySQL is running, and your database credentials in `app.py` are correct.
- **No Data Found**: If no records are returned, ensure the date range and supplier/buyer information are correctly inputted.
- **Duplicate `Receipt_NO` Error**: Ensure that the `Receipt_NO` is unique for each invoice and not empty.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

If you have any questions, feel free to reach out to the project maintainer at sehr.sehr@gmail.com.
