from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import *
import sys
import pyodbc
from datetime import datetime, timedelta

# Database connection
class DatabaseConnection:
    def __init__(self):
        self.server = '' 
        self.database = 'final_project' 
        self.connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};Trusted_Connection=yes;'

    def get_connection(self):
        try:
            conn = pyodbc.connect(self.connection_string)
            print("Database connection successful")
            return conn
        except Exception as e:
            print(f"Database connection failed: {e}")
            raise

# Base authentication class
class AuthenticationBase:
    def verify_credentials(self, email, password, is_admin=False):
        try:
            db = DatabaseConnection()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Fix the column names in the query to match the database schema
            if is_admin:
                query = """
                    SELECT * FROM Admin 
                    WHERE Admin_email = ? AND password = ?
                """
            else:
                query = """
                    SELECT * FROM Customer 
                    WHERE Customer_email = ? AND password = ?
                """
            
            cursor.execute(query, (email, password))
            result = cursor.fetchone()
            
            # Debug print
            print(f"Query result: {result}")
            
            conn.close()
            return result is not None  # Return True if credentials are valid
        except Exception as e:
            print(f"Database error: {e}")
            return False

# Login screen classes
class CustomerLogin(QtWidgets.QMainWindow, AuthenticationBase):
    def __init__(self):
        super().__init__()
        uic.loadUi('screens/customerlogin.ui', self)
        self.pushButton_2.clicked.connect(self.handle_login)  # Login button
        self.pushButton.clicked.connect(self.open_create_account)  # Create account button

    def handle_login(self):
        email = self.lineEdit.text().strip()
        password = self.lineEdit_2.text().strip()
        
        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter both email and password")
            return
            
        try:
            is_valid = self.verify_credentials(email, password)
            if is_valid:
                self.customer_dashboard = CustomerDashboard(email)
                self.customer_dashboard.show()
                self.close()
            else:
                QMessageBox.warning(self, "Error", "Invalid email or password")
                self.lineEdit_2.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login failed: {str(e)}")

    def open_create_account(self):
        self.create_account = CreateAccount()
        self.create_account.show()
        self.close()

class AdminLogin(QtWidgets.QMainWindow, AuthenticationBase):
    def __init__(self):
        super().__init__()
        uic.loadUi('screens/adminlogin.ui', self)
        self.pushButton.clicked.connect(self.handle_login)

    def handle_login(self):
        email = self.lineEdit.text().strip()
        password = self.lineEdit_2.text().strip()
        
        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter both email and password")
            return
            
        try:
            is_valid = self.verify_credentials(email, password, is_admin=True)
            if is_valid:
                self.admin_dashboard = AdminDashboard(email)
                self.admin_dashboard.show()
                self.close()
            else:
                QMessageBox.warning(self, "Error", "Invalid email or password")
                self.lineEdit_2.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login failed: {str(e)}")

# Customer dashboard and related classes
class CustomerDashboard(QtWidgets.QMainWindow):
    def __init__(self, customer_email):
        super().__init__()
        uic.loadUi('screens/customermain.ui', self)
        self.customer_email = customer_email
        self.setup_ui()
    
    def get_customer_details(self, customer_email):
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()

        # Query to get customer name
        query_name = "SELECT Customer_name FROM Customer WHERE Customer_email = ?"
        cursor.execute(query_name, (customer_email,))
        customer_name = cursor.fetchone()
        if customer_name:
            self.lineEdit.setText(customer_name[0])  # Set customer name
        else:   
            self.lineEdit.setText("Not found")
        
        query_address = "SELECT Address FROM Customer WHERE Customer_email = ?"
        cursor.execute(query_address, (customer_email,))
        customer_address = cursor.fetchone()
        if customer_address:
            self.lineEdit_2.setText(customer_address[0])
        else:
            self.lineEdit_2.setText("Not found")

        cursor.close()
        conn.close()

    def setup_ui(self):

        self.get_customer_details(self.customer_email)

        self.radioButton.toggled.connect(self.on_radio_selected)  # New order
        self.radioButton_2.toggled.connect(self.on_radio_selected)  # Track order
        self.radioButton_3.toggled.connect(self.on_radio_selected)  # Cart
        self.pushButton.clicked.connect(self.handle_selection)

    def handle_selection(self):

        # Update customer details in the database
        new_name = self.lineEdit.text().strip()
        new_address = self.lineEdit_2.text().strip()

        try:
            db = DatabaseConnection()
            conn = db.get_connection()
            cursor = conn.cursor()

            # Add better transaction handling
            try:
                # cursor.execute("BEGIN TRANSACTION")
                # Update query
                update_query = "UPDATE Customer SET Customer_name = ?, Address = ? WHERE Customer_email = ?"
                cursor.execute(update_query, (new_name, new_address, self.customer_email))

                if self.radioButton.isChecked() or self.radioButton_3.isChecked():
                    # Create new order
                    cursor.execute("""
                        INSERT INTO Orders (Order_status, Order_date, Customer_email) 
                        VALUES ('Pending', GETDATE(), ?)
                    """, (self.customer_email,))
                    cursor.execute("SELECT @@IDENTITY")  # Use @@IDENTITY instead of IDENT_CURRENT
                    order_id = cursor.fetchval()
                        
                    # Create shopping cart
                    cursor.execute("INSERT INTO Shopping_cart (OrderID) VALUES (?)", (order_id,))
                    cursor.execute("SELECT @@IDENTITY")
                    cart_id = cursor.fetchval()

                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
                conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update customer details: {str(e)}")
        
        if self.radioButton.isChecked():
            self.order_screen = OrderScreen(self.customer_email, cart_id, order_id)

            self.order_screen.show()
        elif self.radioButton_2.isChecked():
            self.selection_screen = SelectOrderScreen(self.customer_email)
            self.selection_screen.show()
        elif self.radioButton_3.isChecked():
            self.cart_screen = CartScreen(self.customer_email, cart_id, order_id)
            self.cart_screen.show()

    def on_radio_selected(self):
        # Enable selection button when any radio is selected
        self.pushButton.setEnabled(True)

# Admin dashboard and related classes
class AdminDashboard(QtWidgets.QMainWindow):
    def __init__(self, admin_email):
        super().__init__()
        uic.loadUi('screens/admin_main_screen.ui', self)
        self.admin_email = admin_email
        self.setup_ui()

    # Assuming you have a method to get the database connection
    def get_admin_details(self, admin_email):
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()

        # Query to get admin name
        query_name = "SELECT Admin_name FROM Admin WHERE Admin_email = ?"
        cursor.execute(query_name, (admin_email,))
        admin_name = cursor.fetchone()
        if admin_name:
            self.lineEdit.setText(admin_name[0])  # Set admin name
        else:
            self.lineEdit.setText("Not found")
        self.lineEdit.setReadOnly(True)  # Disable editing

        # Query to get admin job title
        query_title = "SELECT Job_title FROM Admin WHERE Admin_email = ?"
        cursor.execute(query_title, (admin_email,))
        admin_title = cursor.fetchone()
        if admin_title:
            self.lineEdit_2.setText(admin_title[0])  # Set admin title
        else:
            self.lineEdit_2.setText("Not found")
        self.lineEdit_2.setReadOnly(True)  # Disable editing

        # Close the cursor and connection
        cursor.close()
        conn.close()

    def setup_ui(self):

        self.get_admin_details(self.admin_email)
        
        self.radioButton.toggled.connect(self.on_radio_selected)  # Update order status
        self.radioButton_2.toggled.connect(self.on_radio_selected)  # Update inventory
        self.pushButton.clicked.connect(self.handle_selection)

    def handle_selection(self):
        if self.radioButton.isChecked():
            self.order_status_screen = UpdateOrderStatusScreen(self.admin_email)
            self.order_status_screen.show()
        elif self.radioButton_2.isChecked():
            self.inventory_screen = UpdateInventoryScreen(self.admin_email)
            self.inventory_screen.show()

    def on_radio_selected(self):
        # Enable selection button when any radio is selected
        self.pushButton.setEnabled(True)

# Inventory management screens
class UpdateInventoryScreen(QtWidgets.QMainWindow):
    def __init__(self, admin_email):
        super().__init__()
        uic.loadUi('screens/update inventory.ui', self)
        self.admin_email = admin_email
        self.setup_ui()
        self.load_inventory()

    def setup_ui(self):
        # Setup table properties
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tableWidget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Connect buttons
        self.pushButton.clicked.connect(self.add_new_product)  # Add new product
        self.pushButton_2.clicked.connect(self.delete_product)  # Delete product
        self.pushButton_3.clicked.connect(self.close)  # OK/Close button

    def load_inventory(self):
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                SELECT Product_id, Product_name, quantity_in_stock, 
                       unit_price, category, description, expiration_date 
                FROM Inventory 
                WHERE quantity_in_stock > 0;
            """)
        
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        
        for row_index, row_data in enumerate(cursor.fetchall()):
            self.tableWidget.insertRow(row_index)
            # Set serial number in first column
            self.tableWidget.setItem(row_index, 0, 
                                     QTableWidgetItem(str(row_index + 1)))
            # Add product data starting from column 1
            for col_index, cell_data in enumerate(row_data):
                self.tableWidget.setItem(row_index, col_index + 1, 
                                         QTableWidgetItem(str(cell_data)))
        conn.close()

    def add_new_product(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Product")
        dialog.setModal(True)
        
        # Create form layout
        layout = QFormLayout(dialog)
        
        # Add input fields
        name_input = QLineEdit()
        qty_input = QSpinBox()
        qty_input.setMaximum(1000)
        price_input = QDoubleSpinBox()
        price_input.setMaximum(10000.00)
        category_input = QLineEdit()
        desc_input = QTextEdit()
        exp_date_input = QDateEdit()
        exp_date_input.setCalendarPopup(True)
        exp_date_input.setDate(QDate.currentDate().addYears(1))
        
        # Add fields to layout
        layout.addRow("Product Name:", name_input)
        layout.addRow("Quantity:", qty_input)
        layout.addRow("Unit Price:", price_input)
        layout.addRow("Category:", category_input)
        layout.addRow("Description:", desc_input)
        layout.addRow("Expiration Date:", exp_date_input)
        
        # Add buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                db = DatabaseConnection()
                conn = db.get_connection()
                cursor = conn.cursor()
                
                # First insert the product
                cursor.execute("""
                    INSERT INTO Inventory (Product_name, quantity_in_stock, description, 
                                        unit_price, category, expiration_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    name_input.text(),
                    qty_input.value(),
                    desc_input.toPlainText(),
                    price_input.value(),
                    category_input.text(),
                    exp_date_input.date().toString("yyyy-MM-dd")
                ))
                
                # Get the ID using a separate SELECT statement
                cursor.execute("SELECT IDENT_CURRENT('Inventory')")
                product_id = cursor.fetchone()[0]
                
                # Then create the management relationship using the obtained ID
                cursor.execute("""
                    INSERT INTO Manages (Admin_email, Product_id)
                    VALUES (?, ?)
                """, (self.admin_email, int(product_id)))
                
                conn.commit()
                conn.close()
                
                self.load_inventory()  # Refresh the table
                QMessageBox.information(self, "Success", "Product added successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add product: {str(e)}")

    def delete_product(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a product to delete")
            return
            
        product_id = self.tableWidget.item(selected_row, 1).text()  # Get product ID from column 1
        product_name = self.tableWidget.item(selected_row, 2).text()  # Get product name from column 2
        
        reply = QMessageBox.question(self, "Confirm Delete",
                                   f"Are you sure you want to delete {product_name}?",
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                db = DatabaseConnection()
                conn = db.get_connection()
                cursor = conn.cursor()
                
                # Start transaction
                # cursor.execute("BEGIN TRANSACTION")
                
                # Delete from Inventory_to_Shopping_Cart first
                cursor.execute("DELETE FROM Inventory_to_Shopping_Cart WHERE product_ID = ?", (product_id,))
                
                # Delete from Manages table
                cursor.execute("DELETE FROM Manages WHERE Product_id = ?", (product_id,))
                
                # Finally delete from Inventory
                cursor.execute("DELETE FROM Inventory WHERE Product_id = ?", (product_id,))
                
                # Commit the transaction
                conn.commit()
                cursor.close()
                conn.close()
                
                self.load_inventory()  # Refresh the table
                QMessageBox.information(self, "Success", "Product deleted successfully")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete product: {str(e)}")
            
# Order management screens
class UpdateOrderStatusScreen(QtWidgets.QMainWindow):
    def __init__(self, admin_email):
        super().__init__()
        uic.loadUi('screens/update order status.ui', self)
        self.admin_email = admin_email
        self.setup_ui()
        self.load_orders()

    def setup_ui(self):
        # Set up status combo box options
        self.comboBox.addItems(['Pending', 'Processing', 'Shipped', 'Delivered'])
        # Connect buttons
        self.pushButton_2.clicked.connect(self.update_order_status)  # OK button
        # Setup date picker
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setDate(QDate.currentDate().addDays(2))  # Default to 2 days from now
        # Setup table widget
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tableWidget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tableWidget.itemSelectionChanged.connect(self.on_order_selected)

    def on_order_selected(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row >= 0:
            # Update fields with selected order details
            order_id = self.tableWidget.item(selected_row, 0).text()
            status = self.tableWidget.item(selected_row, 1).text()
            delivery_date = self.tableWidget.item(selected_row, 3).text()
            
            self.lineEdit.setText(order_id)  # Order number
            self.comboBox.setCurrentText(status)  # Current status
            try:
                # Convert delivery date string to QDate
                date = QDate.fromString(delivery_date, "yyyy-MM-dd")
                self.dateEdit.setDate(date)
            except:
                self.dateEdit.setDate(QDate.currentDate().addDays(2))

    def load_orders(self):
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Simpler query focusing on order details
        cursor.execute("""
            SELECT o.Order_id, o.Order_status, o.Order_date, 
                o.estimated_delivery_date, p.Total_amount
            FROM Orders o
            LEFT JOIN Payment p ON o.Payment_id = p.Payment_id
            ORDER BY o.Order_date DESC
        """)
        
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        
        # Set up table headers
        headers = ["Order ID", "Status", "Order Date", "Delivery Date", "Amount"]
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        
        # Populate table
        for row_index, row_data in enumerate(cursor.fetchall()):
            self.tableWidget.insertRow(row_index)
            for col_index, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                self.tableWidget.setItem(row_index, col_index, item)
        
        cursor.close()
        conn.close()

    def update_order_status(self):
        try:
            # Get values from UI
            order_id = self.lineEdit.text()
            new_status = self.comboBox.currentText()
            new_delivery_date = self.dateEdit.date().toString("yyyy-MM-dd")

            # Validate inputs
            if not order_id or not new_status or not new_delivery_date:
                QMessageBox.warning(self, "Error", "Please fill in all fields")
                return

            # Get current order details to check if there are actual changes
            db = DatabaseConnection()
            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT Order_status, estimated_delivery_date
                FROM Orders 
                WHERE Order_id = ?
            """, (order_id,))
            
            current_order = cursor.fetchone()
            if not current_order:
                QMessageBox.warning(self, "Error", "Order not found")
                return

            current_status, current_delivery_date = current_order

            # Only update if there are actual changes
            if (new_status != current_status or 
                new_delivery_date != str(current_delivery_date)):
                
                # Update order status
                cursor.execute("""
                    UPDATE Orders 
                    SET Order_status = ?, estimated_delivery_date = ?
                    WHERE Order_id = ?
                """, (new_status, new_delivery_date, order_id))
                
                # Check if update record already exists
                cursor.execute("""
                    SELECT 1 FROM Updates 
                    WHERE Admin_email = ? AND Order_id = ?
                """, (self.admin_email, order_id))

                if not cursor.fetchone():
                    # Insert update record only if it doesn't exist
                    cursor.execute("""
                        INSERT INTO Updates (Admin_email, Order_id)
                        VALUES (?, ?)
                    """, (self.admin_email, order_id))
                
                conn.commit()
                QMessageBox.information(self, "Success", "Order status updated successfully")
            else:
                QMessageBox.information(self, "Info", "No changes were made to the order")
            
            cursor.close()
            conn.close()
            self.load_orders()
        
        except Exception as e:
            print(f"Error updating order: {str(e)}")  # Debug print
            if 'conn' in locals():
                conn.rollback()
                cursor.close()
                conn.close()
            QMessageBox.critical(self, "Error", f"Failed to update order: {str(e)}")

# Customer order-related screens
class OrderScreen(QtWidgets.QMainWindow):
    def __init__(self, customer_email, cart_id, order_id):
        super().__init__()
        uic.loadUi('screens/order.ui', self)
        self.customer_email = customer_email
        self.cart_id = cart_id
        self.order_id = order_id
        # Remove this line since productsTable already exists from the UI
        # self.productsTable = self.tableWidget
        
        # Add quantity spinbox
        self.quantitySpinBox = QSpinBox(self)
        self.quantitySpinBox.setMinimum(1)
        self.quantitySpinBox.setMaximum(100)
        self.quantitySpinBox.setGeometry(430, 320, 50, 21)
        
        self.setup_connections()
        self.load_products()  # Move this after setup is complete

    def setup_connections(self):
        self.pushButton.clicked.connect(self.search_products)  # Search button
        self.pushButton_2.clicked.connect(self.add_to_cart)  # Add to cart button
        self.pushButton_3.clicked.connect(self.view_cart)  # View cart button

    def view_cart(self):
        self.cart_screen = CartScreen(self.customer_email, self.cart_id, self.order_id)
        self.cart_screen.show()

    def load_products(self):
        db = DatabaseConnection()
        conn = None
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Add semicolon to end SQL statement
            cursor.execute("""
                SELECT Product_id, Product_name, quantity_in_stock, 
                       unit_price, category, description, expiration_date 
                FROM Inventory 
                WHERE quantity_in_stock > 0;
            """)
            
            results = cursor.fetchall()
            
            self.productsTable.clearContents()
            self.productsTable.setRowCount(0)
            
            for row_index, row_data in enumerate(results):
                self.productsTable.insertRow(row_index)
                # Set serial number in first column
                self.productsTable.setItem(row_index, 0, 
                                         QTableWidgetItem(str(row_index + 1)))
                # Add product data starting from column 1
                for col_index, cell_data in enumerate(row_data):
                    self.productsTable.setItem(row_index, col_index + 1, 
                                             QTableWidgetItem(str(cell_data)))
        except Exception as e:
            print(f"Database error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load products: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def add_to_cart(self):
        selected_row = self.productsTable.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Please select a product")
            return
            
        db = DatabaseConnection()
        conn = None
        cursor = None
        try:
            # Get product details with correct column indices
            product_id = int(self.productsTable.item(selected_row, 1).text())
            requested_quantity = self.quantitySpinBox.value()
            available_quantity = int(self.productsTable.item(selected_row, 3).text())
            unit_price = float(self.productsTable.item(selected_row, 4).text())  # Fix column index
            
            if requested_quantity > available_quantity:
                QMessageBox.warning(self, "Error", f"Only {available_quantity} items available")
                return
                
            conn = db.get_connection()
            cursor = conn.cursor()

            try:
                # cursor.execute("BEGIN TRANSACTION")
                
                # Create new order
                # cursor.execute("""
                #     INSERT INTO Orders (Order_status, Order_date, Customer_email) 
                #     VALUES ('Pending', GETDATE(), ?)
                # """, (self.customer_email,))
                # cursor.execute("SELECT @@IDENTITY")  # Use @@IDENTITY instead of IDENT_CURRENT
                # order_id = cursor.fetchval()
                
                # # Create shopping cart
                # cursor.execute("INSERT INTO Shopping_cart (OrderID) VALUES (?)", (order_id,))
                # cursor.execute("SELECT @@IDENTITY")
                # cart_id = cursor.fetchval()

                # Add item to cart
                cursor.execute("""
                    INSERT INTO Inventory_to_Shopping_Cart 
                    (product_ID, shopping_cart_ID, item_quantity, Price)
                    VALUES (?, ?, ?, ?)
                """, (product_id, self.cart_id, requested_quantity, unit_price * requested_quantity))
                
                # Update inventory
                cursor.execute("""
                    UPDATE Inventory 
                    SET quantity_in_stock = quantity_in_stock - ? 
                    WHERE Product_id = ?
                """, (requested_quantity, product_id))
                
                conn.commit()

                QMessageBox.information(self, "Success", "Item added to cart")

            except Exception as e:
                conn.rollback()
                raise e
            finally:
               
                cursor.close()
                conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add item: {str(e)}")

    def search_products(self):
        search_text = self.lineEdit.text().strip()
        if search_text:
            db = DatabaseConnection()
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM Inventory 
                WHERE quantity_in_stock > 0 
                AND (Product_name LIKE ? OR description LIKE ? OR category LIKE ?)
            """, (f'%{search_text}%', f'%{search_text}%', f'%{search_text}%'))
            
            self.productsTable.clearContents()
            self.productsTable.setRowCount(0)
            
            for row_index, row_data in enumerate(cursor.fetchall()):
                self.productsTable.insertRow(row_index)
                for col_index, cell_data in enumerate(row_data):
                    self.productsTable.setItem(row_index, col_index, 
                                            QTableWidgetItem(str(cell_data)))
            conn.close()

class CartScreen(QtWidgets.QMainWindow):
    def __init__(self, customer_email, cart_id, order_id):
        super().__init__()
        uic.loadUi('screens/cart.ui', self)
        self.customer_email = customer_email
        self.cart_id = cart_id
        self.order_id = order_id
         # Add this line to map the widget
        self.load_cart()
        self.setup_connections()

    def load_cart(self):
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT i.Product_id, i.Product_name, isc.item_quantity, 
               i.description, i.expiration_date, (isc.item_quantity * i.unit_price) as Total
        FROM Inventory_to_Shopping_Cart isc
        JOIN Inventory i ON isc.product_ID = i.Product_id
        WHERE isc.shopping_cart_ID = ?
    """, (self.cart_id,))
        
        self.cartTable.clearContents()
        for row_index, row_data in enumerate(cursor.fetchall()):
            self.cartTable.insertRow(row_index)
            for col_index, cell_data in enumerate(row_data):
                self.cartTable.setItem(row_index, col_index, 
                                    QTableWidgetItem(str(cell_data)))
        conn.close()

    def setup_connections(self):
        self.pushButton.clicked.connect(self.delete_item)  # Delete button
        self.pushButton_2.clicked.connect(self.proceed_to_checkout)  # Proceed to payment button

    def proceed_to_checkout(self):
        self.payment_screen = PaymentScreen(self.customer_email, self.cart_id, self.order_id)
        self.payment_screen.show()

    def delete_item(self):
        selected_row = self.cartTable.currentRow()
        if selected_row >= 0:
            product_id = self.cartTable.item(selected_row, 0).text()
            
            try:
                db = DatabaseConnection()
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM Inventory_to_Shopping_Cart 
                    WHERE product_ID = ? AND shopping_cart_ID = ?
                """, (product_id, self.cart_id))
                
                # Optionally, update inventory to add back the quantity
                # Get the quantity that was removed
                removed_quantity = int(self.cartTable.item(selected_row, 2).text())
                cursor.execute("""
                    UPDATE Inventory 
                    SET quantity_in_stock = quantity_in_stock + ? 
                    WHERE Product_id = ?
                """, (removed_quantity, product_id))

                conn.commit()
                conn.close()

                self.load_cart()  # Refresh cart view
                QMessageBox.information(self, "Success", "Item deleted from cart")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete item: {str(e)}")

class SelectOrderScreen(QtWidgets.QMainWindow):
    def __init__(self, customer_email):
        super().__init__()
        uic.loadUi('screens/select_order_id.ui', self)
        self.customer_email = customer_email
        self.setup_ui()
        self.load_orders()

    def setup_ui(self):
        self.pushButton.clicked.connect(self.proceed_to_tracking)
        self.comboBox.setPlaceholderText("Select Order ID")

    def load_orders(self):
        try:
            db = DatabaseConnection()
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Order_id 
                FROM Orders 
                WHERE Customer_email = ?
                ORDER BY Order_date DESC
            """, (self.customer_email,))
            
            orders = cursor.fetchall()
            if orders:
                self.comboBox.clear()
                for order in orders:
                    self.comboBox.addItem(str(order[0]))
            else:
                QMessageBox.information(self, "Info", "No orders found")
                self.close()
            
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load orders: {str(e)}")

    def proceed_to_tracking(self):
        selected_order = self.comboBox.currentText()
        if selected_order:
            self.tracking_screen = OrderTrackingScreen(self.customer_email, selected_order)
            self.tracking_screen.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Please select an order")

class OrderTrackingScreen(QtWidgets.QMainWindow):
    def __init__(self, customer_email, order_id):
        super().__init__()
        uic.loadUi('screens/orderstatus.ui', self)
        self.customer_email = customer_email
        self.order_id = order_id
        self.setup_ui()
        self.load_order()

    def setup_ui(self):
        self.pushButton.clicked.connect(self.close)
        self.lineEdit.setEnabled(False)
        self.lineEdit_2.setEnabled(False)
        self.comboBox.setEnabled(False)

    def load_order(self):
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.Order_id, o.Order_status, o.Order_date, 
                   o.estimated_delivery_date
            FROM Orders o
            WHERE o.Customer_email = ? AND o.Order_id = ?
        """, (self.customer_email, self.order_id))

        result = cursor.fetchone()
        if result:
            self.lineEdit.setText(str(result[0]))
            self.comboBox.addItem(str(result[1]))
            self.lineEdit_2.setText(str(result[3]))

        conn.close()

# Add this class before the main() function
class RoleSelection(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('screens/select_role.ui', self)
        self.setup_ui()

    def setup_ui(self):
        # Connect radio buttons and proceed button
        self.radioButton.toggled.connect(self.on_role_selected)  # Customer radio
        self.radioButton_2.toggled.connect(self.on_role_selected)  # Admin radio
        self.pushButton.clicked.connect(self.proceed_to_login)  # Proceed button
        self.pushButton.setEnabled(False)

    def on_role_selected(self):
        self.pushButton.setEnabled(True)

    def proceed_to_login(self):
        if self.radioButton.isChecked():  # Customer
            self.login_screen = CustomerLogin()
            self.login_screen.show()
            self.close()
        elif self.radioButton_2.isChecked():  # Admin
            self.login_screen = AdminLogin()
            self.login_screen.show()
            self.close()

# Add CreateAccount class
class CreateAccount(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('screens/create_account.ui', self)
        self.pushButton.clicked.connect(self.handle_create_account)

    def handle_create_account(self):
        email = self.lineEdit.text().strip()
        password = self.lineEdit_2.text().strip()
        confirm_password = self.lineEdit_3.text().strip()
        full_name = self.lineEdit_4.text().strip()
        address = self.lineEdit_5.text().strip()
        contact = self.lineEdit_6.text().strip()

        if not all([email, password, confirm_password, full_name, address, contact]):
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return

        try:
            db = DatabaseConnection()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Check if email already exists
            cursor.execute("SELECT * FROM Customer WHERE Customer_email = ?", (email,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Error", "Email already registered")
                return

            # Add better transaction handling
            try:
                # cursor.execute("BEGIN TRANSACTION")
                # Insert new customer
                cursor.execute("""
                    INSERT INTO Customer (Customer_email, Customer_name, password, Address, Contact_no)
                    VALUES (?, ?, ?, ?, ?)
                """, (email, full_name, password, address, contact))
                conn.commit()
                cursor.close()
                conn.close()

            except Exception as e:
                raise e
            
                
            QMessageBox.information(self, "Success", "Account created successfully")
            self.login_screen = CustomerLogin()
            self.login_screen.show()
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create account: {str(e)}")

# Add PaymentScreen class
class PaymentScreen(QtWidgets.QMainWindow):
    def __init__(self, customer_email, cart_id, order_id):
        super().__init__()
        uic.loadUi('screens/payment.ui', self)
        self.customer_email = customer_email
        self.cart_id = cart_id
        self.order_id = order_id 
        self.setup_ui()

    def setup_ui(self):
        self.pushButton.clicked.connect(self.process_payment)
        self.load_payment_details()

    def load_payment_details(self):
        # Load order total from cart
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT SUM(isc.item_quantity * i.unit_price) as Total
        FROM Inventory_to_Shopping_Cart isc
        JOIN Inventory i ON isc.product_ID = i.Product_id
        WHERE isc.shopping_cart_ID = ?
        """, (self.cart_id,))
        total = cursor.fetchone()[0]
        
         # Get payment ID associated with the order
        cursor.execute("""
        SELECT Payment_id FROM Orders WHERE Order_id = ?
        """, (self.order_id,))
        payment_id = cursor.fetchone()[0]

        self.lineEdit.setText(str(self.order_id))  # Order ID
        self.lineEdit.setEnabled(False)
        
        if  not payment_id:
            self.lineEdit_2.setText(str(self.order_id))  # Payment ID
            self.lineEdit_2.setEnabled(False)
        else:
            self.lineEdit_2.setText(str(payment_id))  # Payment ID
            self.lineEdit_2.setEnabled(False)  # Make read-only
        self.lineEdit_3.setText(str(total))  # Total amount
        self.lineEdit_3.setEnabled(False)  # Make read-only
        conn.close()

    def process_payment(self):
        try:
            db = DatabaseConnection()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Add better transaction handling
            try:
                # cursor.execute("BEGIN TRANSACTION")
                # Create payment record
                total = float(self.lineEdit_3.text())
                cursor.execute("INSERT INTO Payment (Total_amount) VALUES (?)", (total,))
                cursor.execute("SELECT @@IDENTITY")
                payment_id = cursor.fetchval()
                
                # Create order
                cursor.execute("""
                UPDATE Orders
                SET Payment_id = ?, estimated_delivery_date = DATEADD(day, 2, GETDATE())
                WHERE Order_id = ?
                """, (payment_id, self.order_id))
                
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
                conn.close()
            
            QMessageBox.information(self, "Success", "Payment processed successfully")
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Payment failed: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = RoleSelection()  # Start with role selection
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
