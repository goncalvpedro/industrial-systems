import sys
import sqlite3
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QComboBox, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QFileDialog)

class InventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Production and Inventory Control")
        self.setGeometry(100, 100, 800, 600)

        self.db_connection = sqlite3.connect('inventory.db')
        self.create_table()

        self.products = self.get_products()
        self.initUI()

    def create_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                product TEXT PRIMARY KEY,
                produced INTEGER,
                stock INTEGER
            )
        ''')
        self.db_connection.commit()

    def get_products(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT product FROM inventory')
        products = [row[0] for row in cursor.fetchall()]
        return products if products else ["Product A", "Product B", "Product C"]

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Dropdown for product selection
        self.product_dropdown = QComboBox()
        self.product_dropdown.addItems(self.products)
        layout.addWidget(QLabel("Select Product:"))
        layout.addWidget(self.product_dropdown)

        # Input fields for production and stock
        self.production_input = QLineEdit()
        self.stock_input = QLineEdit()
        layout.addWidget(QLabel("Produced Quantity:"))
        layout.addWidget(self.production_input)
        layout.addWidget(QLabel("Stock Quantity:"))
        layout.addWidget(self.stock_input)

        # Buttons for actions
        self.record_button = QPushButton("Record Production")
        self.record_button.clicked.connect(self.record_production)
        layout.addWidget(self.record_button)

        # Dropdown for reducing stock
        self.reduce_product_dropdown = QComboBox()
        self.reduce_product_dropdown.addItems(self.products)
        layout.addWidget(QLabel("Select Product to Reduce Stock:"))
        layout.addWidget(self.reduce_product_dropdown)

        self.reduce_stock_input = QLineEdit()
        layout.addWidget(QLabel("Reduce Stock Amount:"))
        layout.addWidget(self.reduce_stock_input)

        self.reduce_stock_button = QPushButton("Reduce Stock")
        self.reduce_stock_button.clicked.connect(self.reduce_stock)
        layout.addWidget(self.reduce_stock_button)

        self.export_button = QPushButton("Export Data")
        self.export_button.clicked.connect(self.export_data)
        layout.addWidget(self.export_button)

        # Table to display inventory
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(3)
        self.inventory_table.setHorizontalHeaderLabels(["Product", "Produced", "Stock"])
        layout.addWidget(self.inventory_table)

        self.load_inventory()
        central_widget.setLayout(layout)

    def load_inventory(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT * FROM inventory')
        rows = cursor.fetchall()
        self.inventory_table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            self.inventory_table.setItem(row_index, 0, QTableWidgetItem(row[0]))
            self.inventory_table.setItem(row_index, 1, QTableWidgetItem(str(row[1])))
            self.inventory_table.setItem(row_index, 2, QTableWidgetItem(str(row[2])))

    def record_production(self):
        product = self.product_dropdown.currentText()
        produced = self.production_input.text()
        stock = self.stock_input.text()

        if not produced.isdigit() or not stock.isdigit():
            QMessageBox.warning(self, "Input Error", "Please enter valid numbers for production and stock.")
            return

        produced = int(produced)
        stock = int(stock)

        cursor = self.db_connection.cursor()
        cursor.execute('INSERT OR REPLACE INTO inventory (product, produced, stock) VALUES (?, ?, COALESCE((SELECT stock FROM inventory WHERE product = ?), 0) + ?)', 
                       (product, produced, product, stock))
        self.db_connection.commit()

        self.load_inventory()
        self.production_input.clear()
        self.stock_input.clear()

    def reduce_stock(self):
        product = self.reduce_product_dropdown.currentText()
        reduce_amount = self.reduce_stock_input.text()

        if not reduce_amount.isdigit():
            QMessageBox.warning(self, "Input Error", "Please enter a valid number to reduce stock.")
            return

        reduce_amount = int(reduce_amount)

        cursor = self.db_connection.cursor()
        cursor.execute('SELECT stock FROM inventory WHERE product = ?', (product,))
        current_stock = cursor.fetchone()

        if current_stock is None or reduce_amount > current_stock[0]:
            QMessageBox.warning(self, "Stock Error", "Cannot reduce stock below zero.")
            return

        new_stock = current_stock[0] - reduce_amount
        cursor.execute('UPDATE inventory SET stock = ? WHERE product = ?', (new_stock, product))
        self.db_connection.commit()

        self.load_inventory()
        self.reduce_stock_input.clear()

    def export_data(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT * FROM inventory')
        rows = cursor.fetchall()

        if not rows:
            QMessageBox.warning(self, "Export Error", "No data to export.")
            return

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv);;Excel Files (*.xlsx)", options=options)
        if file_name:
            df = pd.DataFrame(rows, columns=["Product", "Produced", "Stock"])
            if file_name.endswith('.csv'):
                df.to_csv(file_name, index=False)
            elif file_name.endswith('.xlsx'):
                df.to_excel(file_name, index=False)

            QMessageBox.information(self, "Export Successful", "Data exported successfully.")

    def closeEvent(self, event):
        self.db_connection.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InventoryApp()
    window.show()
    sys.exit(app.exec_())