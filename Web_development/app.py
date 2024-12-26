
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from werkzeug.utils import secure_filename
import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import json
import re
from decimal import Decimal

app = Flask(__name__)

# Set Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Configure the database connection
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'jpg', 'jpeg', 'png'}

# Function to connect to the MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='InvoiceDB'
    )

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route to display data from all tables
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch Suppliers
    cursor.execute('SELECT * FROM Suppliers')
    suppliers = cursor.fetchall()

    # Fetch Buyers
    cursor.execute('SELECT * FROM Buyers')
    buyers = cursor.fetchall()

    # Fetch Invoices
    cursor.execute('SELECT * FROM Invoices')
    invoices = cursor.fetchall()

    # Fetch Invoice Items
    cursor.execute('SELECT * FROM Invoice_Items')
    invoice_items = cursor.fetchall()

    conn.close()

    return render_template('index.html', suppliers=suppliers, buyers=buyers, invoices=invoices, invoice_items=invoice_items)

# Route to handle file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process the file (PDF/Image) to extract text using Tesseract
        extracted_text = ''
        if file.filename.endswith('.pdf'):
            images = convert_from_path(file_path)
            for image in images:
                extracted_text += pytesseract.image_to_string(image)
        else:
            image = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(image)
        
        # Parse the extracted text to extract structured data
        extracted_json = parse_extracted_text(extracted_text)
        print("Hey here is json: \n",extracted_json)
        # Insert parsed data into the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert Supplier if not exists
        cursor.execute("SELECT Supplier_ID FROM Suppliers WHERE NTN = %s", (extracted_json['supplier']['NTN'],))
        supplier = cursor.fetchone()
        if not supplier:
            cursor.execute('''
                INSERT INTO Suppliers (NTN, NAME, BUSINESS_NAME, S_T_REG_NO, Phone_Number, Address)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (extracted_json['supplier']['NTN'], extracted_json['supplier']['name'], 
                  extracted_json['supplier']['business_name'], extracted_json['supplier']['st_reg_no'], 
                  extracted_json['supplier']['phone_number'], extracted_json['supplier']['address']))
            conn.commit()

        # Insert Buyer if not exists
        cursor.execute("SELECT Buyer_ID FROM Buyers WHERE NTN = %s", (extracted_json['buyer']['NTN'],))
        buyer = cursor.fetchone()
        if not buyer:
            cursor.execute('''
                INSERT INTO Buyers (NTN, NAME, S_T_REG_NO, Address)
                VALUES (%s, %s, %s, %s)
            ''', (extracted_json['buyer']['NTN'], extracted_json['buyer']['name'], 
                  extracted_json['buyer']['st_reg_no'], extracted_json['buyer']['address']))
            conn.commit()

        # Insert Invoice data
        cursor.execute('''
            INSERT INTO Invoices (Receipt_NO, Supplier_ID, Buyer_ID, Date, Total_Amount)
            VALUES (%s, %s, %s, %s, %s)
        ''', (extracted_json['invoice']['receipt_no'], extracted_json['invoice']['supplier_id'], 
              extracted_json['invoice']['buyer_id'], extracted_json['invoice']['date'], 
              extracted_json['invoice']['total_amount']))
        conn.commit()

        invoice_id = cursor.lastrowid

        # Insert Invoice Items
        for item in extracted_json['items']:
            cursor.execute('''
                INSERT INTO Invoice_Items (Invoice_ID, Item_Name, Quantity, Rate, Amount)
                VALUES (%s, %s, %s, %s, %s)
            ''', (invoice_id, item['name'], item['quantity'], item['rate'], item['amount']))
        conn.commit()

        conn.close()

        return f"Data inserted successfully from the extracted text: {json.dumps(extracted_json)}"

    return redirect(request.url)

# Function to parse extracted text (basic example, you may need to refine this)
def parse_extracted_text(extracted_text):
    # Example regex patterns to extract data from the text (adjust as needed)
    
    # Extract supplier details
    supplier = {
        'NTN': re.search(r'NTN: (\S+)', extracted_text).group(1) if re.search(r'NTN: (\S+)', extracted_text) else '',
        'name': re.search(r'Supplier Name: ([\w\s]+)', extracted_text).group(1) if re.search(r'Supplier Name: ([\w\s]+)', extracted_text) else '',
        'business_name': re.search(r'Business Name: ([\w\s]+)', extracted_text).group(1) if re.search(r'Business Name: ([\w\s]+)', extracted_text) else '',
        'st_reg_no': re.search(r'ST Reg No: (\S+)', extracted_text).group(1) if re.search(r'ST Reg No: (\S+)', extracted_text) else '',
        'phone_number': re.search(r'Phone: (\S+)', extracted_text).group(1) if re.search(r'Phone: (\S+)', extracted_text) else '',
        'address': re.search(r'Supplier Address: (.+)', extracted_text).group(1) if re.search(r'Supplier Address: (.+)', extracted_text) else '',
    }

    # Extract buyer details
    buyer = {
        'NTN': re.search(r'Buyer NTN: (\S+)', extracted_text).group(1) if re.search(r'Buyer NTN: (\S+)', extracted_text) else '',
        'name': re.search(r'Buyer Name: ([\w\s]+)', extracted_text).group(1) if re.search(r'Buyer Name: ([\w\s]+)', extracted_text) else '',
        'st_reg_no': re.search(r'Buyer ST Reg No: (\S+)', extracted_text).group(1) if re.search(r'Buyer ST Reg No: (\S+)', extracted_text) else '',
        'address': re.search(r'Buyer Address: (.+)', extracted_text).group(1) if re.search(r'Buyer Address: (.+)', extracted_text) else '',
    }

    # Extract invoice details
    invoice = {
        'receipt_no': re.search(r'Receipt No: (\S+)', extracted_text).group(1) if re.search(r'Receipt No: (\S+)', extracted_text) else '',
        'supplier_id': 1,  # Placeholder, will be updated after inserting supplier data
        'buyer_id': 1,     # Placeholder, will be updated after inserting buyer data
        'date': re.search(r'Date: (\d{4}-\d{2}-\d{2})', extracted_text).group(1) if re.search(r'Date: (\d{4}-\d{2}-\d{2})', extracted_text) else '2024-12-26',
        'total_amount': float(re.search(r'Total Amount: (\d+(\.\d{1,2})?)', extracted_text).group(1)) if re.search(r'Total Amount: (\d+(\.\d{1,2})?)', extracted_text) else 0.0
    }

    # Extract invoice items
    items = []
    item_matches = re.findall(r'Item Name: (\S+), Quantity: (\d+), Rate: (\d+(\.\d{1,2})?), Amount: (\d+(\.\d{1,2})?)', extracted_text)
    for match in item_matches:
        items.append({
            'name': match[0],
            'quantity': int(match[1]),
            'rate': float(match[2]),
            'amount': float(match[4])
        })

    # Return the structured JSON
    return {
        'supplier': supplier,
        'buyer': buyer,
        'invoice': invoice,
        'items': items
    }
@app.route('/query', methods=['POST'])
def query_invoices():
    company_or_ntn = request.form['company_or_ntn']
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch total sales
    cursor.execute('''
        SELECT SUM(Total_Amount) AS total_sales 
        FROM Invoices 
        WHERE Date BETWEEN %s AND %s 
        AND (Supplier_ID IN (
            SELECT Supplier_ID FROM Suppliers WHERE NAME = %s OR NTN = %s
        ) OR Buyer_ID IN (
            SELECT Buyer_ID FROM Buyers WHERE NAME = %s OR NTN = %s
        ))
    ''', (start_date, end_date, company_or_ntn, company_or_ntn, company_or_ntn, company_or_ntn))
    total_sales = cursor.fetchone()['total_sales']

  # Query to calculate total sales from Invoice_Items
    cursor.execute('''
        SELECT SUM(ii.Quantity * ii.Rate) AS total_sales
        FROM Invoice_Items ii
        JOIN Invoices i ON ii.Invoice_ID = i.Invoice_ID
        WHERE i.Date BETWEEN %s AND %s
    ''', (start_date, end_date))

    # Fetch total sales
    total_sales = cursor.fetchone()['total_sales']
    
    # Check if total_sales is None (in case no results are found)
    if total_sales is None:
        total_sales = 0  # Default to 0 if no sales are found

    # Calculate sales tax (18% of total sales)
    total_tax = total_sales * Decimal('0.18')
    total_sales=total_sales + total_tax

    # Calculate the total amount including sales tax
    
    
# You can now return these values in your template or further processing


        # Calculate total sales tax (18% of total sales)
    
      
    # Fetch detailed invoice records
    cursor.execute('''
    SELECT 
        i.Invoice_ID, 
        i.Receipt_NO, 
        s.NAME AS Supplier_Name, 
        b.NAME AS Buyer_Name, 
        i.Date, 
        i.Total_Amount,
        ii.Item_Name, 
        ii.Quantity, 
        ii.Rate, 
        ii.Amount
    FROM Invoices i
    LEFT JOIN Suppliers s ON i.Supplier_ID = s.Supplier_ID
    LEFT JOIN Buyers b ON i.Buyer_ID = b.Buyer_ID
    LEFT JOIN Invoice_Items ii ON i.Invoice_ID = ii.Invoice_ID
    WHERE i.Date BETWEEN %s AND %s 
    AND (s.NAME = %s OR s.NTN = %s OR b.NAME = %s OR b.NTN = %s)
''', (start_date, end_date, company_or_ntn, company_or_ntn, company_or_ntn, company_or_ntn))

    detailed_records = cursor.fetchall()
    no_records_found = len(detailed_records) == 0
    conn.close()

    return render_template('query_results.html', total_sales=total_sales,total_tax=total_sales* Decimal('0.18'), detailed_records=detailed_records, no_records_found=no_records_found)

if __name__ == '__main__':
    app.run(debug=True)