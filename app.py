"""
Grocery Store Management System - Flask Backend
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from datetime import datetime, date
import mysql.connector
from mysql.connector import Error
import decimal
import json

app = Flask(__name__)
app.secret_key = 'grocery_store_secret_key_2024'

# Enable CORS for all routes
CORS(app)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'monu8212',
    'database': 'grocery_store'
}

def get_db_connection():
    """Create and return database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# JSON encoder for decimal and datetime types
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

# ==================== HOME DASHBOARD ====================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard with summary widgets"""
    return render_template('dashboard.html')

# ==================== API: DASHBOARD ====================

@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    """Get dashboard statistics"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    stats = {}
    
    try:
        # Today's sales total
        cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0) as today_sales 
            FROM sales 
            WHERE DATE(sale_date) = CURDATE()
        """)
        stats['today_sales'] = cursor.fetchone()['today_sales']
        
        # Number of transactions today
        cursor.execute("""
            SELECT COUNT(*) as today_transactions 
            FROM sales 
            WHERE DATE(sale_date) = CURDATE()
        """)
        stats['today_transactions'] = cursor.fetchone()['today_transactions']
        
        # Total products
        cursor.execute("SELECT COUNT(*) as total_products FROM products")
        stats['total_products'] = cursor.fetchone()['total_products']
        
        # Low stock alerts
        cursor.execute("""
            SELECT COUNT(*) as low_stock_count 
            FROM products 
            WHERE quantity <= low_stock_threshold
        """)
        stats['low_stock_count'] = cursor.fetchone()['low_stock_count']
        
        # Low stock products list
        cursor.execute("""
            SELECT product_id, product_name, quantity, low_stock_threshold 
            FROM products 
            WHERE quantity <= low_stock_threshold 
            ORDER BY quantity ASC 
            LIMIT 10
        """)
        stats['low_stock_products'] = cursor.fetchall()
        
        # Monthly sales
        cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0) as monthly_sales 
            FROM sales 
            WHERE MONTH(sale_date) = MONTH(CURDATE()) 
            AND YEAR(sale_date) = YEAR(CURDATE())
        """)
        stats['monthly_sales'] = cursor.fetchone()['monthly_sales']
        
        # Top selling products (last 30 days)
        cursor.execute("""
            SELECT p.product_name, SUM(si.quantity) as total_sold, 
                   SUM(si.total_price) as total_revenue
            FROM sale_items si
            JOIN products p ON si.product_id = p.product_id
            JOIN sales s ON si.sale_id = s.sale_id
            WHERE s.sale_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY p.product_id
            ORDER BY total_sold DESC
            LIMIT 5
        """)
        stats['top_products'] = cursor.fetchall()
        
        return jsonify(stats)
    
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== INVENTORY MANAGEMENT ====================

@app.route('/inventory')
def inventory():
    """Inventory management page"""
    return render_template('inventory.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        search = request.args.get('search', '')
        category_id = request.args.get('category_id', '')
        
        query = """
            SELECT p.*, c.category_name 
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            WHERE 1=1
        """
        params = []
        
        if search:
            query += " AND (p.product_name LIKE %s OR p.barcode LIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        if category_id:
            query += " AND p.category_id = %s"
            params.append(int(category_id))
        
        query += " ORDER BY p.product_name"
        
        cursor.execute(query, params)
        products = cursor.fetchall()
        
        return jsonify(products)
    
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/products', methods=['POST'])
def add_product():
    """Add new product"""
    data = request.get_json()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO products (product_name, category_id, barcode, price, 
                                cost_price, quantity, low_stock_threshold, 
                                expiry_date, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('product_name'),
            data.get('category_id') or None,
            data.get('barcode'),
            data.get('price'),
            data.get('cost_price', 0),
            data.get('quantity', 0),
            data.get('low_stock_threshold', 10),
            data.get('expiry_date') or None,
            data.get('description')
        ))
        
        conn.commit()
        product_id = cursor.lastrowid
        
        return jsonify({'message': 'Product added successfully', 'product_id': product_id})
    
    except Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update product"""
    data = request.get_json()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE products 
            SET product_name = %s, category_id = %s, barcode = %s, 
                price = %s, cost_price = %s, quantity = %s, 
                low_stock_threshold = %s, expiry_date = %s, description = %s
            WHERE product_id = %s
        """, (
            data.get('product_name'),
            data.get('category_id') or None,
            data.get('barcode'),
            data.get('price'),
            data.get('cost_price'),
            data.get('quantity'),
            data.get('low_stock_threshold'),
            data.get('expiry_date') or None,
            data.get('description'),
            product_id
        ))
        
        conn.commit()
        
        return jsonify({'message': 'Product updated successfully'})
    
    except Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete product"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        conn.commit()
        
        return jsonify({'message': 'Product deleted successfully'})
    
    except Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM categories ORDER BY category_name")
        categories = cursor.fetchall()
        return jsonify(categories)
    
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== BILLING / POS SYSTEM ====================

@app.route('/billing')
def billing():
    """Billing/POS page"""
    return render_template('billing.html')

@app.route('/api/products/search')
def search_products():
    """Search products for billing"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = request.args.get('q', '')
        
        cursor.execute("""
            SELECT product_id, product_name, barcode, price, quantity 
            FROM products 
            WHERE (product_name LIKE %s OR barcode LIKE %s) 
            AND quantity > 0
            ORDER BY product_name 
            LIMIT 20
        """, (f'%{query}%', f'%{query}%'))
        
        products = cursor.fetchall()
        return jsonify(products)
    
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/sales', methods=['POST'])
def create_sale():
    """Create new sale"""
    data = request.get_json()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    
    try:
        # Generate invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Insert sale record
        cursor.execute("""
            INSERT INTO sales (customer_id, subtotal, discount_amount, 
                             tax_amount, total_amount, payment_method, 
                             invoice_number, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('customer_id') or None,
            data.get('subtotal'),
            data.get('discount_amount', 0),
            data.get('tax_amount', 0),
            data.get('total_amount'),
            data.get('payment_method'),
            invoice_number,
            data.get('notes')
        ))
        
        sale_id = cursor.lastrowid
        
        # Insert sale items and update stock
        for item in data.get('items', []):
            # Insert sale item
            cursor.execute("""
                INSERT INTO sale_items (sale_id, product_id, quantity, 
                                       unit_price, total_price)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                sale_id,
                item['product_id'],
                item['quantity'],
                item['price'],
                item['total_price']
            ))
            
            # Update product quantity
            cursor.execute("""
                UPDATE products 
                SET quantity = quantity - %s 
                WHERE product_id = %s
            """, (item['quantity'], item['product_id']))
        
        # Insert transaction record
        cursor.execute("""
            INSERT INTO transactions (sale_id, amount, payment_method, status)
            VALUES (%s, %s, %s, 'Completed')
        """, (sale_id, data.get('total_amount'), data.get('payment_method')))
        
        # Update customer total purchases if customer is selected
        if data.get('customer_id'):
            cursor.execute("""
                UPDATE customers 
                SET total_purchases = total_purchases + %s 
                WHERE customer_id = %s
            """, (data.get('total_amount'), data.get('customer_id')))
        
        conn.commit()
        
        return jsonify({
            'message': 'Sale completed successfully',
            'sale_id': sale_id,
            'invoice_number': invoice_number
        })
    
    except Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== CUSTOMER MANAGEMENT ====================

@app.route('/customers')
def customers():
    """Customer management page"""
    return render_template('customers.html')

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """Get all customers"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        search = request.args.get('search', '')
        
        query = "SELECT * FROM customers WHERE 1=1"
        params = []
        
        if search:
            query += " AND (customer_name LIKE %s OR phone LIKE %s)"
            params.extend([f'%{search}%', f'%{search}%'])
        
        query += " ORDER BY customer_name"
        
        cursor.execute(query, params)
        customers = cursor.fetchall()
        
        return jsonify(customers)
    
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/customers', methods=['POST'])
def add_customer():
    """Add new customer"""
    data = request.get_json()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO customers (customer_name, phone, email, address)
            VALUES (%s, %s, %s, %s)
        """, (
            data.get('customer_name'),
            data.get('phone'),
            data.get('email'),
            data.get('address')
        ))
        
        conn.commit()
        customer_id = cursor.lastrowid
        
        return jsonify({'message': 'Customer added successfully', 'customer_id': customer_id})
    
    except Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update customer"""
    data = request.get_json()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE customers 
            SET customer_name = %s, phone = %s, email = %s, address = %s
            WHERE customer_id = %s
        """, (
            data.get('customer_name'),
            data.get('phone'),
            data.get('email'),
            data.get('address'),
            customer_id
        ))
        
        conn.commit()
        
        return jsonify({'message': 'Customer updated successfully'})
    
    except Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """Delete customer"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM customers WHERE customer_id = %s", (customer_id,))
        conn.commit()
        
        return jsonify({'message': 'Customer deleted successfully'})
    
    except Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/customers/<int:customer_id>/history')
def get_customer_history(customer_id):
    """Get customer purchase history"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT s.sale_id, s.invoice_number, s.sale_date, s.total_amount, 
                   s.payment_method, s.status
            FROM sales s
            WHERE s.customer_id = %s
            ORDER BY s.sale_date DESC
            LIMIT 20
        """, (customer_id,))
        
        history = cursor.fetchall()
        
        return jsonify(history)
    
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== TRANSACTION MANAGEMENT ====================

@app.route('/transactions')
def transactions():
    """Transaction management page"""
    return render_template('transactions.html')

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get all transactions"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = """
            SELECT t.*, s.invoice_number, c.customer_name
            FROM transactions t
            LEFT JOIN sales s ON t.sale_id = s.sale_id
            LEFT JOIN customers c ON s.customer_id = c.customer_id
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND DATE(t.transaction_date) >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(t.transaction_date) <= %s"
            params.append(end_date)
        
        query += " ORDER BY t.transaction_date DESC"
        
        cursor.execute(query, params)
        transactions = cursor.fetchall()
        
        return jsonify(transactions)
    
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/sales', methods=['GET'])
def get_sales():
    """Get all sales"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = """
            SELECT s.*, c.customer_name
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.customer_id
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND DATE(s.sale_date) >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(s.sale_date) <= %s"
            params.append(end_date)
        
        query += " ORDER BY s.sale_date DESC"
        
        cursor.execute(query, params)
        sales = cursor.fetchall()
        
        return jsonify(sales)
    
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/sales/<int:sale_id>')
def get_sale_details(sale_id):
    """Get sale details with items"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get sale info
        cursor.execute("""
            SELECT s.*, c.customer_name, c.phone, c.address
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.customer_id
            WHERE s.sale_id = %s
        """, (sale_id,))
        sale = cursor.fetchone()
        
        if not sale:
            return jsonify({'error': 'Sale not found'}), 404
        
        # Get sale items
        cursor.execute("""
            SELECT si.*, p.product_name
            FROM sale_items si
            JOIN products p ON si.product_id = p.product_id
            WHERE si.sale_id = %s
        """, (sale_id,))
        items = cursor.fetchall()
        
        sale['items'] = items
        
        return jsonify(sale)
    
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== SALES DASHBOARD & REPORTS ====================

@app.route('/reports')
def reports():
    """Sales reports page"""
    return render_template('reports.html')

@app.route('/api/reports/sales')
def get_sales_report():
    """Get sales report"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        report_type = request.args.get('type', 'daily')
        
        if report_type == 'daily':
            cursor.execute("""
                SELECT DATE(sale_date) as date, 
                       COUNT(*) as total_transactions,
                       SUM(total_amount) as total_sales
                FROM sales
                WHERE DATE(sale_date) = CURDATE()
                GROUP BY DATE(sale_date)
            """)
        elif report_type == 'monthly':
            cursor.execute("""
                SELECT DATE(sale_date) as date,
                       COUNT(*) as total_transactions,
                       SUM(total_amount) as total_sales
                FROM sales
                WHERE MONTH(sale_date) = MONTH(CURDATE())
                AND YEAR(sale_date) = YEAR(CURDATE())
                GROUP BY DATE(sale_date)
                ORDER BY date
            """)
        elif report_type == 'yearly':
            cursor.execute("""
                SELECT MONTH(sale_date) as month,
                       COUNT(*) as total_transactions,
                       SUM(total_amount) as total_sales
                FROM sales
                WHERE YEAR(sale_date) = YEAR(CURDATE())
                GROUP BY MONTH(sale_date)
                ORDER BY month
            """)
        
        report = cursor.fetchall()
        return jsonify(report)
    
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/reports/chart-data')
def get_chart_data():
    """Get chart data for reports"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Last 7 days sales
        cursor.execute("""
            SELECT DATE(sale_date) as date,
                   SUM(total_amount) as sales
            FROM sales
            WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DATE(sale_date)
            ORDER BY date
        """)
        weekly_data = cursor.fetchall()
        
        # Monthly comparison
        cursor.execute("""
            SELECT MONTH(sale_date) as month,
                   SUM(total_amount) as sales
            FROM sales
            WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
            GROUP BY MONTH(sale_date)
            ORDER BY month
        """)
        monthly_data = cursor.fetchall()
        
        return jsonify({
            'weekly': weekly_data,
            'monthly': monthly_data
        })
    
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
