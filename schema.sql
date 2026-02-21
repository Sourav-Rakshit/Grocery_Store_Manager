-- Grocery Store Management System Database Schema
-- MySQL Database

-- Create database
CREATE DATABASE IF NOT EXISTS grocery_store;
USE grocery_store;

-- Drop tables if exists (for fresh setup)
DROP TABLE IF EXISTS sale_items;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS categories;

-- Categories table
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Products table
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category_id INT,
    barcode VARCHAR(50) UNIQUE,
    price DECIMAL(10, 2) NOT NULL,
    cost_price DECIMAL(10, 2) DEFAULT 0,
    quantity INT NOT NULL DEFAULT 0,
    low_stock_threshold INT DEFAULT 10,
    expiry_date DATE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Customers table
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100),
    address TEXT,
    total_purchases DECIMAL(12, 2) DEFAULT 0,
    loyalty_points INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Sales table (main sale record)
CREATE TABLE sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('Cash', 'UPI', 'Card') NOT NULL,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    status ENUM('Completed', 'Refunded', 'Cancelled') DEFAULT 'Completed',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Sale items table (individual items in a sale)
CREATE TABLE sale_items (
    sale_item_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Transactions table (payment tracking)
CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('Cash', 'UPI', 'Card') NOT NULL,
    transaction_reference VARCHAR(100),
    status ENUM('Completed', 'Refunded', 'Failed') DEFAULT 'Completed',
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Insert default categories
INSERT INTO categories (category_name, description) VALUES
('Fruits & Vegetables', 'Fresh fruits and vegetables'),
('Dairy Products', 'Milk, cheese, yogurt, and other dairy items'),
('Bakery', 'Bread, pastries, and bakery items'),
('Beverages', 'Drinks, juices, and beverages'),
('Snacks', 'Chips, cookies, and snacks'),
('Household', 'Household essentials'),
('Personal Care', 'Personal hygiene and care products'),
('Other', 'Miscellaneous items');

-- Insert sample products
INSERT INTO products (product_name, category_id, barcode, price, cost_price, quantity, low_stock_threshold) VALUES
('Apple (1kg)', 1, '8901234567890', 120.00, 80.00, 50, 10),
('Banana (1 dozen)', 1, '8901234567891', 60.00, 40.00, 30, 10),
('Milk (1L)', 2, '8901234567892', 45.00, 35.00, 100, 20),
('Curd (500g)', 2, '8901234567893', 35.00, 25.00, 40, 15),
('White Bread', 3, '8901234567894', 30.00, 20.00, 25, 10),
('Cola (1L)', 4, '8901234567895', 40.00, 30.00, 60, 15),
('Potato Chips', 5, '8901234567896', 20.00, 12.00, 80, 20),
('Sugar (1kg)', 6, '8901234567897', 45.00, 38.00, 70, 15),
('Toothpaste', 7, '8901234567898', 50.00, 35.00, 45, 15),
('Shampoo (500ml)', 7, '8901234567899', 150.00, 100.00, 35, 10);

-- Insert sample customers
INSERT INTO customers (customer_name, phone, email, address) VALUES
('John Doe', '9876543210', 'john@example.com', '123 Main Street, City'),
('Jane Smith', '9876543211', 'jane@example.com', '456 Oak Avenue, City'),
('Bob Johnson', '9876543212', 'bob@example.com', '789 Pine Road, City'),
('Alice Brown', '9876543213', 'alice@example.com', '321 Elm Street, City'),
('Charlie Wilson', '9876543214', NULL, '654 Maple Lane, City');

-- Create indexes for better performance
CREATE INDEX idx_products_name ON products(product_name);
CREATE INDEX idx_products_barcode ON products(barcode);
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_sales_invoice ON sales(invoice_number);
