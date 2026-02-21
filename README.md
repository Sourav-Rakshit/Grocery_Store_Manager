# Grocery Store Management System

A complete web-based Grocery Store Management System built with Python Flask, MySQL, and Bootstrap 5. This application handles inventory management, billing (POS), customer management, transaction tracking, and sales dashboard reporting.

## Features

### 1. Home Dashboard
- Card-based navigation menu with quick access to all modules
- Summary widgets showing:
  - Today's sales total
  - Number of transactions today
  - Total products
  - Low stock alerts

### 2. Inventory Management
- Add, edit, and delete products
- Track stock quantity with low stock warnings
- Product categories support
- Barcode support
- Expiry date tracking (optional)
- Search and filter products

### 3. Billing / POS System
- Search products by name or barcode
- Add items to cart with quantity modification
- Auto price calculation
- Optional discount and tax
- Select customer or walk-in customer
- Generate invoice
- Automatic stock reduction after sale
- Multiple payment modes (Cash, UPI, Card)

### 4. Customer Management
- Add and update customer details
- Search by name or phone number
- Store name, phone, email, and address
- View purchase history
- Show total purchases and last purchase date

### 5. Transaction Management
- Store payment records
- Track payment method
- Filter by date range
- View transaction history
- Export to Excel/CSV

### 6. Sales Dashboard & Reports
- Today's sales summary
- Monthly sales total
- Top selling products
- Low stock products list
- Interactive charts using Chart.js

## Technology Stack

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- Vanilla JavaScript
- Chart.js for data visualization
- Font Awesome for icons

### Backend
- Python 3.x
- Flask Framework
- Flask-CORS

### Database
- MySQL
- Proper normalization and foreign key relationships

## Project Structure

```
grocery_store/
├── app.py                 # Main Flask application
├── schema.sql             # Database schema
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── inventory.html
│   ├── billing.html
│   ├── customers.html
│   ├── transactions.html
│   ├── reports.html
│   ├── 404.html
│   └── 500.html
└── static/              # Static files
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## Installation Instructions

### Prerequisites

1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/

2. **MySQL Server**
   - Download from: https://dev.mysql.com/downloads/mysql/
   - Or use XAMPP/WAMP for easier setup

### Step 1: Database Setup

1. Start MySQL server
2. Open MySQL command line or any MySQL GUI tool (MySQL Workbench, phpMyAdmin)
3. Run the schema.sql file:

```bash
mysql -u root -p < schema.sql
```

Or in MySQL Workbench:
- File → Open SQL Script → Select schema.sql → Execute

### Step 2: Configure Database Connection

1. Open `app.py` in a text editor
2. Find the `DB_CONFIG` dictionary around line 20
3. Update with your MySQL credentials:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',          # Your MySQL username
    'password': 'your_password',  # Your MySQL password
    'database': 'grocery_store'
}
```

### Step 3: Install Python Dependencies

1. Open terminal/command prompt
2. Navigate to the project folder:
   ```bash
   cd grocery_store
   ```

3. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   ```

4. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Step 4: Run the Application

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. You should see output like:
   ```
   * Running on http://127.0.0.1:5000
   ```

3. Open your web browser and go to:
   ```
   http://127.0.0.1:5000
   ```

## Default Login

The application doesn't require login by default. You can access all features directly from the dashboard.

## Sample Data

The schema.sql file includes sample data:
- 8 product categories
- 10 sample products
- 5 sample customers

## Customization

### Changing Database Configuration

Edit the `DB_CONFIG` in `app.py`:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',
    'database': 'grocery_store'
}
```

### Adding New Categories

You can add categories through the MySQL database:

```sql
INSERT INTO categories (category_name, description) 
VALUES ('Your Category', 'Description');
```

### Changing Application Port

In `app.py`, find the last line:

```python
if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

Change `port=5000` to your desired port number.

## Troubleshooting

### MySQL Connection Error

1. Make sure MySQL server is running
2. Verify username and password in DB_CONFIG
3. Ensure the database 'grocery_store' exists

### Port Already in Use

If port 5000 is already in use:
```bash
python app.py --port 5001
```

### Module Not Found Error

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Database Table Error

If you get table-related errors, try recreating the database:
```sql
DROP DATABASE IF EXISTS grocery_store;
CREATE DATABASE grocery_store;
-- Then run schema.sql again
```

## API Endpoints

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

### Products
- `GET /api/products` - Get all products
- `POST /api/products` - Add new product
- `PUT /api/products/<id>` - Update product
- `DELETE /api/products/<id>` - Delete product

### Categories
- `GET /api/categories` - Get all categories

### Customers
- `GET /api/customers` - Get all customers
- `POST /api/customers` - Add new customer
- `PUT /api/customers/<id>` - Update customer
- `DELETE /api/customers/<id>` - Delete customer
- `GET /api/customers/<id>/history` - Get customer purchase history

### Billing
- `GET /api/products/search?q=<query>` - Search products
- `POST /api/sales` - Create new sale

### Reports
- `GET /api/sales` - Get all sales
- `GET /api/sales/<id>` - Get sale details
- `GET /api/reports/sales?type=<type>` - Get sales report
- `GET /api/reports/chart-data` - Get chart data

## License

This project is open source and available for educational and commercial use.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the console output for error messages
3. Ensure all prerequisites are properly installed

## Screenshots

The application features:
- Clean, modern Bootstrap-based UI
- Responsive design for mobile and desktop
- Interactive charts for sales analytics
- Real-time stock management
- Professional invoice generation
