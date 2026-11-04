CREATE DATABASE IF NOT EXISTS retailpulse_db;
USE retailpulse_db;

CREATE TABLE IF NOT EXISTS customers (
  customer_id BIGINT PRIMARY KEY,
  first_name VARCHAR(80) NOT NULL,
  last_name VARCHAR(80) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  phone VARCHAR(30),
  city VARCHAR(80) NOT NULL,
  state VARCHAR(80) NOT NULL,
  country VARCHAR(80) NOT NULL DEFAULT 'India',
  registration_date DATE NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_customers_updated_at (updated_at)
);

CREATE TABLE IF NOT EXISTS products (
  product_id BIGINT PRIMARY KEY,
  product_name VARCHAR(200) NOT NULL,
  category VARCHAR(80) NOT NULL,
  brand VARCHAR(100) NOT NULL,
  unit_price DECIMAL(12,2) NOT NULL CHECK (unit_price >= 0),
  cost_price DECIMAL(12,2) NOT NULL CHECK (cost_price >= 0),
  stock_quantity INT NOT NULL CHECK (stock_quantity >= 0),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_products_updated_at (updated_at)
);

CREATE TABLE IF NOT EXISTS orders (
  order_id BIGINT PRIMARY KEY,
  customer_id BIGINT NOT NULL,
  order_date DATETIME NOT NULL,
  order_status VARCHAR(30) NOT NULL,
  payment_method VARCHAR(30) NOT NULL,
  shipping_city VARCHAR(80) NOT NULL,
  shipping_state VARCHAR(80) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  INDEX idx_orders_updated_at (updated_at),
  INDEX idx_orders_customer (customer_id),
  INDEX idx_orders_order_date (order_date)
);

CREATE TABLE IF NOT EXISTS order_items (
  order_item_id BIGINT PRIMARY KEY,
  order_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  quantity INT NOT NULL CHECK (quantity > 0),
  unit_price DECIMAL(12,2) NOT NULL CHECK (unit_price >= 0),
  discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0 CHECK (discount_amount >= 0),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_items_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
  CONSTRAINT fk_items_product FOREIGN KEY (product_id) REFERENCES products(product_id),
  INDEX idx_items_updated_at (updated_at),
  INDEX idx_items_order (order_id)
);

CREATE TABLE IF NOT EXISTS payments (
  payment_id BIGINT PRIMARY KEY,
  order_id BIGINT NOT NULL,
  payment_method VARCHAR(30) NOT NULL,
  payment_amount DECIMAL(12,2) NOT NULL CHECK (payment_amount >= 0),
  payment_status VARCHAR(30) NOT NULL,
  transaction_date DATETIME NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_payments_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
  INDEX idx_payments_updated_at (updated_at),
  INDEX idx_payments_transaction_date (transaction_date)
);

CREATE TABLE IF NOT EXISTS pipeline_metadata (
  execution_id VARCHAR(64) NOT NULL,
  source_table VARCHAR(80) NOT NULL,
  last_successful_extraction_timestamp TIMESTAMP NULL,
  records_extracted BIGINT NOT NULL DEFAULT 0,
  records_loaded BIGINT NOT NULL DEFAULT 0,
  execution_status VARCHAR(20) NOT NULL,
  started_at TIMESTAMP NOT NULL,
  completed_at TIMESTAMP NULL,
  error_message TEXT,
  PRIMARY KEY (execution_id, source_table)
);
