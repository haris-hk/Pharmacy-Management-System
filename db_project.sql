-- Create Tables

CREATE TABLE Admin (
    Admin_email VARCHAR(255) PRIMARY KEY,
    Admin_name VARCHAR(255),
    Job_title VARCHAR(255),
    password VARCHAR(255)
);

CREATE TABLE Customer (
    Customer_email VARCHAR(255) PRIMARY KEY,
    Customer_name VARCHAR(255),
    password VARCHAR(255),
    Address TEXT,
    Contact_no VARCHAR(255)
);

CREATE TABLE Inventory (
    Product_id INT IDENTITY(1,1) PRIMARY KEY,
    Product_name VARCHAR(255),
    quantity_in_stock INT,
    description TEXT,
    unit_price DECIMAL(10,2),
    category VARCHAR(255),
    expiration_date DATETIME
);

CREATE TABLE Payment (
    Payment_id INT IDENTITY(1,1) PRIMARY KEY,
    Total_amount DECIMAL(10,2)
);

CREATE TABLE Orders (
    Order_id INT IDENTITY(1,1) PRIMARY KEY,
    Order_status VARCHAR(255),
    Order_date DATE,
    estimated_delivery_date DATETIME,
    Payment_id INT,
    Customer_email VARCHAR(255),
    FOREIGN KEY (Customer_email) REFERENCES Customer(Customer_email),
    FOREIGN KEY (Payment_id) REFERENCES Payment(Payment_id)
);

-- Modified Shopping_cart table with foreign key to Orders
CREATE TABLE Shopping_cart (
    shopping_cart_ID INT IDENTITY(1,1) PRIMARY KEY,
    OrderID INT,
    FOREIGN KEY (OrderID) REFERENCES Orders(Order_id)
);

CREATE TABLE Inventory_to_Shopping_Cart (
    product_ID INT,
    shopping_cart_ID INT,
    item_quantity INT,
    Price DECIMAL(10,2),
    PRIMARY KEY (product_ID, shopping_cart_ID),
    FOREIGN KEY (product_ID) REFERENCES Inventory(Product_id),
    FOREIGN KEY (shopping_cart_ID) REFERENCES Shopping_cart(shopping_cart_ID)
);

CREATE TABLE Updates (
    Admin_email VARCHAR(255),
    Order_id INT,
    PRIMARY KEY (Admin_email, Order_id),
    FOREIGN KEY (Admin_email) REFERENCES Admin(Admin_email),
    FOREIGN KEY (Order_id) REFERENCES Orders(Order_id)
);

CREATE TABLE Manages (
    Admin_email VARCHAR(255),
    Product_id INT,
    PRIMARY KEY (Admin_email, Product_id),
    FOREIGN KEY (Admin_email) REFERENCES Admin(Admin_email),
    FOREIGN KEY (Product_id) REFERENCES Inventory(Product_id)
);

-- Insert sample data
-- Admin data
INSERT INTO Admin VALUES
('admin1@pharmacy.com', 'John Smith', 'Head Pharmacist', 'pass123'),
('admin2@pharmacy.com', 'Sarah Johnson', 'Pharmacy Manager', 'pass456'),
('admin3@pharmacy.com', 'Michael Brown', 'Inventory Manager', 'pass789'),
('admin4@pharmacy.com', 'Emma Thompson', 'Assistant Pharmacist', 'pass321'),
('admin5@pharmacy.com', 'David Chen', 'Sales Manager', 'pass654'),
('admin6@pharmacy.com', 'Lisa Rodriguez', 'Customer Service Manager', 'pass987'),
('admin7@pharmacy.com', 'James Wilson', 'Pharmacy Technician', 'passabc'),
('admin8@pharmacy.com', 'Maria Garcia', 'Inventory Assistant', 'passdef'),
('admin9@pharmacy.com', 'Robert Taylor', 'Quality Control Manager', 'passghi'),
('admin10@pharmacy.com', 'Sophie Martin', 'Operations Manager', 'passjkl');

-- Customer data
INSERT INTO Customer VALUES
('john@email.com', 'John Doe', 'pass123', '123 Main St, City', '123-456-7890'),
('sarah@email.com', 'Sarah Smith', 'pass456', '456 Oak St, Town', '234-567-8901'),
('mike@email.com', 'Mike Johnson', 'pass789', '789 Pine St, Village', '345-678-9012'),
('david@email.com', 'David Miller', 'pass321', '321 Elm St, Metro', '456-789-0123'),
('emma@email.com', 'Emma Wilson', 'pass654', '654 Maple Dr, County', '567-890-1234'),
('frank@email.com', 'Frank Johnson', 'pass987', '987 Cedar Ln, District', '678-901-2345'),
('grace@email.com', 'Grace Lee', 'passabc', '246 Birch Rd, Borough', '789-012-3456'),
('henry@email.com', 'Henry Zhang', 'passdef', '135 Spruce Ave, Heights', '890-123-4567'),
('isabel@email.com', 'Isabel Garcia', 'passghi', '864 Pine St, Gardens', '901-234-5678'),
('jack@email.com', 'Jack Thompson', 'passjkl', '753 Oak Ct, Springs', '012-345-6789');

-- Inventory data
INSERT INTO Inventory (Product_name, quantity_in_stock, description, unit_price, category, expiration_date) VALUES
('Paracetamol', 100, 'Pain relief tablets', 5.99, 'Pain Relief', '2025-12-31 00:00:00'),
('Ibuprofen', 150, 'Anti-inflammatory medication', 6.99, 'Pain Relief', '2025-10-31 00:00:00'),
('Amoxicillin', 80, 'Antibiotic capsules', 12.99, 'Antibiotics', '2025-09-30 00:00:00'),
('Vitamin C', 200, 'Immune support supplement', 8.99, 'Vitamins', '2026-01-31 00:00:00'),
('Calcium', 120, 'Bone health supplement', 9.99, 'Minerals', '2026-03-31 00:00:00'),
('Aspirin', 120, 'Blood thinner medication', 7.99, 'Pain Relief', '2025-06-30 00:00:00'),
('Cetirizine', 90, 'Antihistamine tablets', 15.99, 'Allergy', '2025-08-31 00:00:00'),
('Omeprazole', 60, 'Acid reflux medication', 19.99, 'Digestive Health', '2025-07-31 00:00:00'),
('Vitamin D3', 200, 'Bone health supplement', 11.99, 'Vitamins', '2026-06-30 00:00:00'),
('Zinc tablets', 180, 'Immune support mineral', 13.99, 'Minerals', '2026-09-30 00:00:00');

-- Payment data (must be inserted before Orders due to FK constraint)
INSERT INTO Payment (Total_amount) VALUES
(11.98),
(20.97),
(12.99),
(17.98),
(39.96),
(23.97),
(31.98),
(19.99),
(23.98),
(41.97);

-- Orders data (must be inserted before Shopping_cart due to FK constraint)
INSERT INTO Orders (Order_status, Order_date, estimated_delivery_date, Payment_id, Customer_email) VALUES
('Delivered', '2024-09-23', '2024-09-25 12:00:00', 1, 'john@email.com'),
('Shipped', '2024-09-24', '2024-09-26 12:00:00', 2, 'sarah@email.com'),
('Processing', '2024-09-25', '2024-09-27 12:00:00', 3, 'mike@email.com'),
('Delivered', '2024-09-26', '2024-09-28 12:00:00', 4, 'david@email.com'),
('Pending', '2024-09-27', '2024-09-29 12:00:00', 5, 'emma@email.com'),
('Shipped', '2024-09-28', '2024-09-30 12:00:00', 6, 'frank@email.com'),
('Processing', '2024-09-29', '2024-10-01 12:00:00', 7, 'grace@email.com'),
('Delivered', '2024-09-30', '2024-10-02 12:00:00', 8, 'henry@email.com'),
('Pending', '2024-10-01', '2024-10-03 12:00:00', 9, 'isabel@email.com'),
('Shipped', '2024-10-02', '2024-10-04 12:00:00', 10, 'jack@email.com');

-- Shopping cart data (now with foreign key constraint to Orders)
INSERT INTO Shopping_cart (OrderID) VALUES
(1),
(2),
(3),
(4),
(5),
(6),
(7),
(8),
(9),
(10);

-- Inventory to Shopping Cart relationships with quantity and price
INSERT INTO Inventory_to_Shopping_Cart VALUES
(1, 1, 2, 11.98),
(2, 2, 3, 20.97),
(3, 3, 1, 12.99),
(4, 4, 2, 17.98),
(5, 5, 4, 39.96),
(6, 6, 3, 23.97),
(7, 7, 2, 31.98),
(8, 8, 1, 19.99),
(9, 9, 2, 23.98),
(10, 10, 3, 41.97);

-- Updates relationships
INSERT INTO Updates VALUES
('admin1@pharmacy.com', 1),
('admin2@pharmacy.com', 2),
('admin3@pharmacy.com', 3),
('admin4@pharmacy.com', 4),
('admin5@pharmacy.com', 5),
('admin6@pharmacy.com', 6),
('admin7@pharmacy.com', 7),
('admin8@pharmacy.com', 8),
('admin9@pharmacy.com', 9),
('admin10@pharmacy.com', 10);

-- Manages relationships
INSERT INTO Manages VALUES
('admin1@pharmacy.com', 1),
('admin2@pharmacy.com', 2),
('admin3@pharmacy.com', 3),
('admin4@pharmacy.com', 4),
('admin5@pharmacy.com', 5),
('admin6@pharmacy.com', 6),
('admin7@pharmacy.com', 7),
('admin8@pharmacy.com', 8),
('admin9@pharmacy.com', 9),
('admin10@pharmacy.com', 10);

