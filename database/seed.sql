-- RetailPulse Seed Fixtures for Local Quick Bootstrapping
-- Sample minimal reference data for sanity checks

USE retailpulse_db;

-- 1. Reference Customers
INSERT INTO customers (customer_id, first_name, last_name, email, phone, city, state, country, registration_date, created_at, updated_at)
VALUES 
  (1, 'Aarav', 'Sharma', 'aarav.sharma@retailpulse.example.in', '+919876543210', 'Bengaluru', 'Karnataka', 'India', '2024-01-15', '2024-01-15 10:00:00', '2024-01-15 10:00:00'),
  (2, 'Aditi', 'Patel', 'aditi.patel@retailpulse.example.in', '+919876543211', 'Mumbai', 'Maharashtra', 'India', '2024-02-20', '2024-02-20 11:30:00', '2024-02-20 11:30:00'),
  (3, 'Kabir', 'Reddy', 'kabir.reddy@retailpulse.example.in', '+919876543212', 'Hyderabad', 'Telangana', 'India', '2024-03-10', '2024-03-10 09:15:00', '2024-03-10 09:15:00')
ON DUPLICATE KEY UPDATE updated_at = VALUES(updated_at);

-- 2. Reference Products
INSERT INTO products (product_id, product_name, category, brand, unit_price, cost_price, stock_quantity, created_at, updated_at)
VALUES
  (1, 'Zephyr Wireless Earbuds Pro', 'Electronics', 'ZephyrStyle', 2999.00, 1800.00, 150, '2024-01-01 00:00:00', '2024-01-01 00:00:00'),
  (2, 'Urban Living Stainless Water Bottle 1L', 'Home & Kitchen', 'UrbanLiving', 799.00, 420.00, 300, '2024-01-01 00:00:00', '2024-01-01 00:00:00'),
  (3, 'TerraCare Vitamin C Radiance Serum', 'Beauty & Wellness', 'TerraCare', 599.00, 260.00, 200, '2024-01-01 00:00:00', '2024-01-01 00:00:00')
ON DUPLICATE KEY UPDATE updated_at = VALUES(updated_at);

-- 3. Reference Orders
INSERT INTO orders (order_id, customer_id, order_date, order_status, payment_method, shipping_city, shipping_state, created_at, updated_at)
VALUES
  (1, 1, '2025-01-10 14:22:00', 'delivered', 'UPI', 'Bengaluru', 'Karnataka', '2025-01-10 14:22:00', '2025-01-10 14:22:00'),
  (2, 2, '2025-01-11 16:45:00', 'delivered', 'CREDIT_CARD', 'Mumbai', 'Maharashtra', '2025-01-11 16:45:00', '2025-01-11 16:45:00')
ON DUPLICATE KEY UPDATE updated_at = VALUES(updated_at);

-- 4. Reference Order Items
INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price, discount_amount, created_at, updated_at)
VALUES
  (1, 1, 1, 1, 2999.00, 150.00, '2025-01-10 14:22:00', '2025-01-10 14:22:00'),
  (2, 2, 2, 2, 799.00, 50.00, '2025-01-11 16:45:00', '2025-01-11 16:45:00')
ON DUPLICATE KEY UPDATE updated_at = VALUES(updated_at);

-- 5. Reference Payments
INSERT INTO payments (payment_id, order_id, payment_method, payment_amount, payment_status, transaction_date, created_at, updated_at)
VALUES
  (1, 1, 'UPI', 2849.00, 'success', '2025-01-10 14:22:00', '2025-01-10 14:22:00'),
  (2, 2, 'CREDIT_CARD', 1548.00, 'success', '2025-01-11 16:45:00', '2025-01-11 16:45:00')
ON DUPLICATE KEY UPDATE updated_at = VALUES(updated_at);

