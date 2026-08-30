-- ci-seed.sql: Idempotent schema + seed data for all DB2 test repos.
-- Run once after PostgreSQL starts. Safe to re-run (IF NOT EXISTS + ON CONFLICT).
-- Database: modernization_db  User: modernize

-- Core tables
CREATE TABLE IF NOT EXISTS customer (
    cust_id   INT PRIMARY KEY,
    cust_name VARCHAR(100),
    dept_id   INT
);
CREATE TABLE IF NOT EXISTS orders (
    order_id    INT PRIMARY KEY,
    customer_id INT,
    order_date  DATE
);
CREATE TABLE IF NOT EXISTS dept (
    dept_id   INT PRIMARY KEY,
    dept_name VARCHAR(100)
);
-- DB2E2E01
CREATE TABLE IF NOT EXISTS db2_test_e2e (
    id   INT PRIMARY KEY,
    name VARCHAR(20)
);

-- Seed data
INSERT INTO customer (cust_id, cust_name, dept_id) VALUES (101, 'TEST CUSTOMER', 10) ON CONFLICT (cust_id) DO NOTHING;
INSERT INTO customer (cust_id, cust_name, dept_id) VALUES (102, 'ANOTHER CUST', 10) ON CONFLICT (cust_id) DO NOTHING;
INSERT INTO customer (cust_id, cust_name, dept_id) VALUES (103, 'NULL TEST CUST', NULL) ON CONFLICT (cust_id) DO NOTHING;
INSERT INTO orders (order_id, customer_id, order_date) VALUES (1, 101, '2024-01-15') ON CONFLICT (order_id) DO NOTHING;
INSERT INTO dept (dept_id, dept_name) VALUES (10, 'ENGINEERING') ON CONFLICT (dept_id) DO NOTHING;
INSERT INTO db2_test_e2e (id, name) VALUES (1, 'INIT') ON CONFLICT (id) DO NOTHING;
