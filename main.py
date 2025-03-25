import sys
import sqlite3
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QComboBox, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QFileDialog)

class BannerStock(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Estoque Banner")
        self.setGeometry(100, 100, 800, 600)
        
        self.db_connection = sqlite3.connect('stock.db')
        self.create_table()

        self.products = self.get_products()
        self.initUI()
        
    def create_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product TEXT NOT NULL,
                current_stock INTEGER DEFAULT 0 NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.db_connection.commit()
        
    def get_products(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT product FROM stock')
        products = [row[0] for row in cursor.fetchall()]
        products_list = ['11 10.5-19', '11 10.5-21', '11 10.5K-25', '11 10.5E-16', '11 10.5E-18', '5S 8-16.5',
                         '5S 8A -19', '5S 8A-16.5', '5S 8E-18', '5S 8K-17.5', '5S 8M -16', '5S 8N-13', '6174 N (LTS)',
                         '9 10-16', '9 10-18-5', '9 10-19', '9 10-21', '9 95SP-14-4', '9 9KS-17.5', '9 9LS-13.5', '9 9S - 12'
                        ]
        return products if products else products_list
    
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        self.product_dropdown = QComboBox()
        self.product_dropdown.addItems(self.products)
        layout.addWidget(QLabel("Selecione a referência: "))
        layout.addWidget(self.product_dropdown)
        
        self.stock_input = QLineEdit()
        layout.addWidget(QLabel('Estoque: '))
        layout.addWidget(self.stock_input)
        
        self.add_stock_button = QPushButton('Adicionar material ao estoque')
        self.add_stock_button.clicked.connect(self.save)
        layout.addWidget(self.add_stock_button)
        
        self.reduce_stock_button = QPushButton('Retirar material do estoque')
        # self.reduce_stock_button.clicked.connect(self.reduce_stock)
        layout.addWidget(self.reduce_stock_button)
        
        self.stock_preview = QTableWidget()
        self.stock_preview.setColumnCount(4)
        self.stock_preview.setHorizontalHeaderLabels(['ID', 'Produto', 'Estoque atual', 'Última atualização'])
        layout.addWidget(self.stock_preview)
        
        central_widget.setLayout(layout)
        
    def load_db(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT * FROM stock')
        rows = cursor.fetchall()
        self.stock_preview.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            self.stock_preview.setItem(row_index, 0, QTableWidgetItem(row[0]))
            self.stock_preview.setItem(row_index, 1, QTableWidgetItem(str(row[1])))
            self.stock_preview.setItem(row_index, 2, QTableWidgetItem(str(row[2])))
            self.stock_preview.setItem(row_index, 3, QTableWidgetItem(str(row[3])))
            
    def save(self):
        product = self.product_dropdown.currentText()
        current_stock = self.stock_input.text()
        
        if not current_stock.isdigit():
            QMessageBox.warning(self, "Erro", "Insira apenas números")
            return
        
        current_stock = int(current_stock)
        cursor = self.db_connection.cursor()
        cursor.execute('''
                       INSERT OR REPLACE INTO stock (product, current_stock)
                       VALUES (?, COALESCE((SELECT current_stock FROM stock WHERE product = ?), 0) + ?)
                       ''', (product, product, current_stock))
        self.db_connection.commit()
        
        self.load_db()
        self.stock_input.clear()
        
    def closeEvent(self, event):
        self.db_connection.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BannerStock()
    window.show()
    sys.exit(app.exec_())