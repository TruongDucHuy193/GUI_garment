from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtPrintSupport  # Thêm import này cho chức năng in
import pymysql as mysql
from pymysql import Error
import uuid
from datetime import datetime, date

class Ui_NKTPWindow(object):
    def __init__(self):
        self.db_connection = None
        self.selected_product_id = None
        self.selected_receipt_id = None
        self.current_products = []  # Danh sách sản phẩm nhập
        self.connect_to_database()
        
    def connect_to_database(self):
        try:
            self.db_connection = mysql.connect(
                host="localhost",
                user="root",
                password="2310",
                database="gar_db",
                charset='utf8mb4'
            )
            if self.db_connection.open:
                print("Database connected successfully")
        except Error as e:
            print(f"Error connecting to database: {e}")
            QtWidgets.QMessageBox.critical(None, "Lỗi kết nối", 
                f"Không thể kết nối đến cơ sở dữ liệu:\n{e}")

    def setupUi(self, NKTPWindow):
        NKTPWindow.setObjectName("NKTPWindow")
        NKTPWindow.resize(1600, 900)
        NKTPWindow.setMinimumSize(1400, 800)
        
        # Apply modern styling
        self.setup_styles(NKTPWindow)
        
        self.centralwidget = QtWidgets.QWidget(NKTPWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Create main layout
        main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header - giảm kích thước
        header_widget = self.setup_header_compact()
        main_layout.addWidget(header_widget)
        
        # Content area with splitter - tăng kích thước
        content_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        main_layout.addWidget(content_splitter, 3)
        
        # Left panel - Product selection and details
        left_panel = self.setup_product_selection_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Import list and operations
        right_panel = self.setup_import_panel()
        content_splitter.addWidget(right_panel)
        
        # Bottom panel - giảm kích thước
        bottom_panel = self.setup_import_summary_panel_compact()
        main_layout.addWidget(bottom_panel)
        
        content_splitter.setSizes([600, 800])

        NKTPWindow.setCentralWidget(self.centralwidget)
        
        # Setup menubar and statusbar
        self.setup_menubar(NKTPWindow)
        self.setup_statusbar(NKTPWindow)

        self.retranslateUi(NKTPWindow)
        self.setup_models()
        QtCore.QMetaObject.connectSlotsByName(NKTPWindow)

    def setup_styles(self, NKTPWindow):
        """Thiết lập style hiện đại cho form"""
        style = """
        QMainWindow {
            background-color: #f8f9fa;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            margin: 8px 0px;
            padding-top: 15px;
            background-color: white;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 8px 0 8px;
            color: #495057;
        }
        
        QPushButton {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 500;
            min-height: 25px;
        }
        
        QPushButton:hover {
            background-color: #0056b3;
        }
        
        QPushButton:pressed {
            background-color: #004085;
        }
        
        QPushButton:disabled {
            background-color: #6c757d;
        }
        
        QPushButton.save-btn {
            background-color: #28a745;
        }
        
        QPushButton.save-btn:hover {
            background-color: #218838;
        }
        
        QPushButton.delete-btn {
            background-color: #dc3545;
        }
        
        QPushButton.delete-btn:hover {
            background-color: #c82333;
        }
        
        QPushButton.warning-btn {
            background-color: #ffc107;
            color: #212529;
        }
        
        QPushButton.warning-btn:hover {
            background-color: #e0a800;
        }
        
        QTableView {
            gridline-color: #dee2e6;
            selection-background-color: #007bff;
            alternate-background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
        }
        
        QLineEdit, QComboBox, QDateEdit, QSpinBox {
            padding: 8px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            background-color: white;
        }
        
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {
            border: 2px solid #007bff;
            outline: none;
        }
        
        QLineEdit:read-only {
            background-color: #e9ecef;
        }
        
        QLabel {
            color: #495057;
        }
        """
        NKTPWindow.setStyleSheet(style)

    def setup_header_compact(self):
        """Thiết lập header nhỏ gọn"""
        header_widget = QtWidgets.QWidget()
        header_widget.setMaximumHeight(80)
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(5, 5, 5, 5)
        
        # Title - thu gọn
        title_label = QtWidgets.QLabel("QUẢN LÝ NHẬP KHO THÀNH PHẨM")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_font = QtGui.QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #007bff; margin: 5px;")
        
        # Receipt info - thu gọn
        receipt_info_widget = QtWidgets.QWidget()
        receipt_info_layout = QtWidgets.QHBoxLayout(receipt_info_widget)
        
        receipt_info_layout.addWidget(QtWidgets.QLabel("Mã phiếu:"))
        self.label_receipt_code = QtWidgets.QLabel(f"PNKTP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}")
        self.label_receipt_code.setStyleSheet("font-weight: bold; color: #007bff; font-size: 12px;")
        receipt_info_layout.addWidget(self.label_receipt_code)
        
        receipt_info_layout.addWidget(QtWidgets.QLabel("Ngày:"))
        self.label_create_date = QtWidgets.QLabel(datetime.now().strftime("%d/%m/%Y %H:%M"))
        self.label_create_date.setStyleSheet("font-size: 12px;")
        receipt_info_layout.addWidget(self.label_create_date)
        
        header_layout.addWidget(title_label, 2)
        header_layout.addWidget(receipt_info_widget, 1)
        
        return header_widget

    def setup_product_selection_panel(self):
        """Thiết lập panel chọn sản phẩm với kích thước tối ưu"""
        product_group = QtWidgets.QGroupBox("Chọn sản phẩm nhập kho")
        product_layout = QtWidgets.QVBoxLayout(product_group)
        
        # Product search - thu gọn
        search_widget = QtWidgets.QWidget()
        search_widget.setMaximumHeight(60)
        search_layout = QtWidgets.QHBoxLayout(search_widget)
        
        search_layout.addWidget(QtWidgets.QLabel("Tìm sản phẩm:"))
        self.line_search_products_NKTP = QtWidgets.QLineEdit()
        self.line_search_products_NKTP.setPlaceholderText("Nhập tên sản phẩm...")
        self.line_search_products_NKTP.setMaximumHeight(30)
        search_layout.addWidget(self.line_search_products_NKTP)
        
        self.btn_search_products_NKTP = QtWidgets.QPushButton("Tìm")
        self.btn_search_products_NKTP.setMaximumHeight(30)
        self.btn_search_products_NKTP.clicked.connect(self.search_products)
        search_layout.addWidget(self.btn_search_products_NKTP)
        
        product_layout.addWidget(search_widget)
        
        # Available products table - tăng kích thước
        product_layout.addWidget(QtWidgets.QLabel("Danh sách sản phẩm có sẵn:"))
        self.table_listProducts_NKTP = QtWidgets.QTableView()
        self.table_listProducts_NKTP.setMinimumHeight(100)
        self.table_listProducts_NKTP.setMaximumHeight(300)
        self.table_listProducts_NKTP.clicked.connect(self.on_product_selected)
        product_layout.addWidget(self.table_listProducts_NKTP)
        
        # Product input form - thu gọn
        input_group = QtWidgets.QGroupBox("Thông tin nhập sản phẩm")
        input_group.setMaximumHeight(190)
        input_layout = QtWidgets.QGridLayout(input_group)
        input_layout.setSpacing(5)
        
        input_layout.addWidget(QtWidgets.QLabel("Tên sản phẩm:"), 0, 0)
        self.line_product_name_NKTP = QtWidgets.QLineEdit()
        self.line_product_name_NKTP.setReadOnly(True)
        self.line_product_name_NKTP.setMaximumHeight(30)
        input_layout.addWidget(self.line_product_name_NKTP, 0, 1, 1, 2)
        
        input_layout.addWidget(QtWidgets.QLabel("SL nhập:"), 1, 0)
        self.spin_quantity_total_NKTP = QtWidgets.QSpinBox()
        self.spin_quantity_total_NKTP.setMinimum(1)
        self.spin_quantity_total_NKTP.setMaximum(999999)
        self.spin_quantity_total_NKTP.setMaximumHeight(30)
        self.spin_quantity_total_NKTP.setStyleSheet("""
            QSpinBox {
                font-size: 12px;
                padding: 5px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
            }
            QSpinBox:focus {
                border: 2px solid #007bff;
            }
        """)
        input_layout.addWidget(self.spin_quantity_total_NKTP, 1, 1)
        
        input_layout.addWidget(QtWidgets.QLabel("SL đạt:"), 1, 2)
        self.spin_quantity_standard_NKTP = QtWidgets.QSpinBox()
        self.spin_quantity_standard_NKTP.setMinimum(0)
        self.spin_quantity_standard_NKTP.setMaximum(999999)
        self.spin_quantity_standard_NKTP.setMaximumHeight(30)
        self.spin_quantity_standard_NKTP.setStyleSheet("""
            QSpinBox {
                font-size: 12px;
                padding: 5px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
            }
            QSpinBox:focus {
                border: 2px solid #007bff;
            }
        """)
        input_layout.addWidget(self.spin_quantity_standard_NKTP, 1, 3)
        
        input_layout.addWidget(QtWidgets.QLabel("SL lỗi:"), 2, 0)
        self.spin_quantity_defective_NKTP = QtWidgets.QSpinBox()
        self.spin_quantity_defective_NKTP.setMinimum(0)
        self.spin_quantity_defective_NKTP.setMaximum(999999)
        self.spin_quantity_defective_NKTP.setMaximumHeight(30)
        self.spin_quantity_defective_NKTP.setStyleSheet("""
            QSpinBox {
                font-size: 12px;
                padding: 5px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
            }
            QSpinBox:focus {
                border: 2px solid #007bff;
            }
        """)
        input_layout.addWidget(self.spin_quantity_defective_NKTP, 2, 1)
        
        input_layout.addWidget(QtWidgets.QLabel("Giá thành:"), 2, 2)
        self.line_cost_price_NKTP = QtWidgets.QLineEdit()
        self.line_cost_price_NKTP.setPlaceholderText("VNĐ")
        self.line_cost_price_NKTP.setMaximumHeight(30)
        input_layout.addWidget(self.line_cost_price_NKTP, 2, 3)
        
        # Add button
        self.btn_add_product_NKTP = QtWidgets.QPushButton("Thêm vào phiếu nhập")
        self.btn_add_product_NKTP.setProperty("class", "save-btn")
        self.btn_add_product_NKTP.setMaximumHeight(35)
        self.btn_add_product_NKTP.clicked.connect(self.add_product)
        input_layout.addWidget(self.btn_add_product_NKTP, 3, 0, 1, 4)
        
        product_layout.addWidget(input_group)
        
        return product_group

    def setup_import_panel(self):
        """Thiết lập panel danh sách nhập với kích thước tối ưu"""
        import_group = QtWidgets.QGroupBox("Danh sách sản phẩm nhập kho")
        import_layout = QtWidgets.QVBoxLayout(import_group)
        
        # Selected products table
        self.table_products_NKTP = QtWidgets.QTableView()
        self.table_products_NKTP.setMinimumHeight(250)
        import_layout.addWidget(self.table_products_NKTP)
        
        # Product management buttons - thu gọn
        btn_widget = QtWidgets.QWidget()
        btn_widget.setMaximumHeight(40)
        btn_layout = QtWidgets.QHBoxLayout(btn_widget)
        
        self.btn_edit_product_NKTP = QtWidgets.QPushButton("Sửa")
        self.btn_edit_product_NKTP.setProperty("class", "warning-btn")
        self.btn_edit_product_NKTP.setMaximumHeight(30)
        
        self.btn_del_product_NKTP = QtWidgets.QPushButton("Xóa")
        self.btn_del_product_NKTP.setProperty("class", "delete-btn")
        self.btn_del_product_NKTP.setMaximumHeight(30)
        
        self.btn_edit_product_NKTP.clicked.connect(self.edit_product)
        self.btn_del_product_NKTP.clicked.connect(self.delete_product)
        
        btn_layout.addWidget(self.btn_edit_product_NKTP)
        btn_layout.addWidget(self.btn_del_product_NKTP)
        btn_layout.addStretch()
        
        import_layout.addWidget(btn_widget)
        
        return import_group

    def setup_import_summary_panel_compact(self):
        """Thiết lập panel tổng kết nhỏ gọn"""
        summary_group = QtWidgets.QGroupBox("Thông tin phiếu nhập")
        summary_group.setMaximumHeight(180)
        summary_layout = QtWidgets.QHBoxLayout(summary_group)
        
        # Import details - thu gọn
        details_widget = QtWidgets.QWidget()
        details_layout = QtWidgets.QGridLayout(details_widget)
        details_layout.setSpacing(5)
        
        details_layout.addWidget(QtWidgets.QLabel("Ngày nhập:"), 0, 0)
        self.edit_date_entry = QtWidgets.QDateEdit()
        self.edit_date_entry.setDate(QtCore.QDate.currentDate())
        self.edit_date_entry.setCalendarPopup(True)
        self.edit_date_entry.setMaximumHeight(30)
        details_layout.addWidget(self.edit_date_entry, 0, 1)
        
        details_layout.addWidget(QtWidgets.QLabel("Ghi chú:"), 1, 0)
        self.line_notes_NKTP = QtWidgets.QLineEdit()
        self.line_notes_NKTP.setPlaceholderText("Ghi chú phiếu nhập...")
        self.line_notes_NKTP.setMaximumHeight(30)
        details_layout.addWidget(self.line_notes_NKTP, 1, 1)
        
        details_layout.addWidget(QtWidgets.QLabel("Đơn hàng:"), 0, 2)
        self.combobox_order_NKTP = QtWidgets.QComboBox()
        self.combobox_order_NKTP.setMaximumHeight(30)
        details_layout.addWidget(self.combobox_order_NKTP, 0, 3)
        
        details_layout.addWidget(QtWidgets.QLabel("Tổng giá trị:"), 1, 2)
        self.line_total_value_NKTP = QtWidgets.QLineEdit()
        self.line_total_value_NKTP.setReadOnly(True)
        self.line_total_value_NKTP.setMaximumHeight(30)
        self.line_total_value_NKTP.setStyleSheet("font-weight: bold; font-size: 12px; background-color: #f8f9fa;")
        details_layout.addWidget(self.line_total_value_NKTP, 1, 3)
        
        # Action buttons - thu gọn thành 2 hàng
        action_widget = QtWidgets.QWidget()
        action_layout = QtWidgets.QGridLayout(action_widget)
        action_layout.setSpacing(5)
        
        # Hàng 1
        self.btn_create_receipt_NKTP = QtWidgets.QPushButton("Tạo phiếu nhập")
        self.btn_create_receipt_NKTP.setProperty("class", "save-btn")
        self.btn_create_receipt_NKTP.setMaximumHeight(30)
        
        action_layout.addWidget(self.btn_create_receipt_NKTP, 0, 0)
        
        # Hàng 2
        self.btn_new_receipt = QtWidgets.QPushButton("Phiếu mới")
        self.btn_new_receipt.setMaximumHeight(30)
        
        self.btn_del_receipt_NKTP = QtWidgets.QPushButton("Xóa phiếu")
        self.btn_del_receipt_NKTP.setProperty("class", "delete-btn")
        self.btn_del_receipt_NKTP.setMaximumHeight(30)
        
        action_layout.addWidget(self.btn_new_receipt, 1, 0)
        action_layout.addWidget(self.btn_del_receipt_NKTP, 1, 1)
        
        # Hàng 3
        self.btn_cancel_NKTP = QtWidgets.QPushButton("Hủy")
        self.btn_cancel_NKTP.setMaximumHeight(30)
        
        action_layout.addWidget(self.btn_cancel_NKTP, 2, 0)
        
        # Connect signals
        self.btn_create_receipt_NKTP.clicked.connect(self.create_receipt)
        self.btn_new_receipt.clicked.connect(self.new_receipt)
        self.btn_del_receipt_NKTP.clicked.connect(self.delete_receipt)
        self.btn_cancel_NKTP.clicked.connect(self.cancel_receipt)
        
        # Ẩn bảng lịch sử nhập để tiết kiệm không gian
        self.table_receipt_list_NKTP = QtWidgets.QTableView()
        self.table_receipt_list_NKTP.setVisible(False)
        
        summary_layout.addWidget(details_widget, 2)
        summary_layout.addWidget(action_widget, 1)
        
        return summary_group

    def setup_menubar(self, NKTPWindow):
        """Thiết lập menu bar"""
        self.menubar = QtWidgets.QMenuBar(NKTPWindow)
        NKTPWindow.setMenuBar(self.menubar)

    def setup_statusbar(self, NKTPWindow):
        """Thiết lập status bar"""
        self.statusbar = QtWidgets.QStatusBar(NKTPWindow)
        self.statusbar.showMessage("Sẵn sàng")
        NKTPWindow.setStatusBar(self.statusbar)

    def on_product_selected(self):
        """Xử lý khi chọn sản phẩm"""
        selected = self.table_listProducts_NKTP.currentIndex()
        if selected.isValid():
            self.selected_product_id = self.available_products_model.item(selected.row(), 0).text()
            product_name = self.available_products_model.item(selected.row(), 2).text()
            product_price = self.available_products_model.item(selected.row(), 6).text()
            
            # Tự động điền thông tin vào form
            self.line_product_name_NKTP.setText(product_name)
            self.line_cost_price_NKTP.setText(product_price.replace(',', '') if product_price else "0")
            
            # Reset quantity
            self.spin_quantity_total_NKTP.setValue(1)
            self.spin_quantity_standard_NKTP.setValue(0)
            self.spin_quantity_defective_NKTP.setValue(0)
            
            self.statusbar.showMessage(f"Đã chọn: {product_name}", 3000)

    def new_receipt(self):
        """Tạo phiếu nhập mới"""
        self.current_products.clear()
        self.selected_product_id = None
        self.selected_receipt_id = None
        
        # Reset form
        self.line_product_name_NKTP.clear()
        self.spin_quantity_total_NKTP.setValue(1)
        self.spin_quantity_standard_NKTP.setValue(0)
        self.spin_quantity_defective_NKTP.setValue(0)
        self.line_cost_price_NKTP.clear()
        self.edit_date_entry.setDate(QtCore.QDate.currentDate())
        self.line_notes_NKTP.clear()
        
        # Generate new receipt code
        new_code = f"PNKTP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        self.label_receipt_code.setText(new_code)
        
        # Clear table
        self.product_model.clear()
        self.product_model.setHorizontalHeaderLabels(["ID", "Tên SP", "SL Nhập", "SL Đạt", "SL Lỗi", "Giá thành"])
        
        self.statusbar.showMessage("Đã tạo phiếu nhập mới", 2000)

    # Keep all existing methods from the original code
    def retranslateUi(self, NKTPWindow):
        _translate = QtCore.QCoreApplication.translate
        NKTPWindow.setWindowTitle(_translate("NKTPWindow", "Quản lý nhập kho thành phẩm - Garment Management System"))

    def setup_models(self):
        self.product_model = QtGui.QStandardItemModel()
        self.product_model.setHorizontalHeaderLabels(["ID", "Tên SP", "SL Nhập", "SL Đạt", "SL Lỗi", "Giá thành"])
        self.table_products_NKTP.setModel(self.product_model)
        
        self.available_products_model = QtGui.QStandardItemModel()
        self.table_listProducts_NKTP.setModel(self.available_products_model)
        
        self.receipt_model = QtGui.QStandardItemModel()
        self.table_receipt_list_NKTP.setModel(self.receipt_model)
        
        # Set table properties
        for table in [self.table_products_NKTP, self.table_listProducts_NKTP, self.table_receipt_list_NKTP]:
            table.setAlternatingRowColors(True)
            table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            table.verticalHeader().setDefaultSectionSize(30)
            table.setStyleSheet("""
                QTableView {
                    gridline-color: #dee2e6;
                    selection-background-color: #007bff;
                    alternate-background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    font-size: 13px;
                }
                QTableView::item {
                    padding: 5px;
                    border-bottom: 1px solid #dee2e6;
                }
                QTableView::item:selected {
                    background-color: #007bff;
                    color: white;
                }
                QHeaderView::section {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    padding: 8px;
                    font-weight: bold;
                    font-size: 13px;
                }
            """)
        
        self.load_products()
        self.load_orders_for_receipt()
        self.load_receipts()

    def load_orders_for_receipt(self):
        """Load orders for receipt combobox"""
        self.combobox_order_NKTP.clear()
        if self.db_connection:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT id, maDonHang FROM DonDatHang ORDER BY ngayDatHang DESC")
            self.order_map_receipt = {}
            for row in cursor.fetchall():
                order_id, ma_don_hang = row
                self.combobox_order_NKTP.addItem(ma_don_hang)
                self.order_map_receipt[ma_don_hang] = order_id
            cursor.close()

    def load_products(self):
        """Load products from database"""
        self.available_products_model.clear()
        self.available_products_model.setHorizontalHeaderLabels(["ID", "Mã SP", "Tên", "Loại", "Size", "Màu", "Giá", "Hình", "SL Tồn", "GT Tồn"])
        if self.db_connection:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM SanPham")
            for row in cursor.fetchall():
                items = [QtGui.QStandardItem(str(field) if field is not None else "") for field in row]
                self.available_products_model.appendRow(items)
            cursor.close()

    def load_receipts(self):
        """Load receipts from database (placeholder)"""
        # Implement loading receipts from database
        pass

    def search_products(self):
        """Search products"""
        search_text = self.line_search_products_NKTP.text()
        self.available_products_model.clear()
        self.available_products_model.setHorizontalHeaderLabels(["ID", "Mã SP", "Tên", "Loại", "Size", "Màu", "Giá", "Hình", "SL Tồn", "GT Tồn"])
        if self.db_connection:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM SanPham WHERE tenSanPham LIKE %s", (f"%{search_text}%",))
            for row in cursor.fetchall():
                items = [QtGui.QStandardItem(str(field) if field is not None else "") for field in row]
                self.available_products_model.appendRow(items)
            cursor.close()

    def edit_product(self):
        """Edit selected product in receipt"""
        selected = self.table_products_NKTP.currentIndex()
        if selected.isValid():
            # Implement edit logic similar to edit_material in FormXK
            pass

    def delete_product(self):
        """Delete selected product from receipt"""
        selected = self.table_products_NKTP.currentIndex()
        if selected.isValid():
            product_name = self.product_model.item(selected.row(), 1).text()
            reply = QtWidgets.QMessageBox.question(None, "Xác nhận xóa", 
                f"Bạn có chắc chắn muốn xóa sản phẩm '{product_name}' khỏi danh sách?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            
            if reply == QtWidgets.QMessageBox.Yes:
                self.product_model.removeRow(selected.row())
                self.calculate_total_value_receipt()
                self.statusbar.showMessage(f"Đã xóa {product_name}", 2000)

    def delete_receipt(self):
        """Delete receipt (placeholder)"""
        # Implement delete receipt logic
        pass

    def print_receipt(self):
        """Print receipt (placeholder - now handled by create_receipt)"""
        QtWidgets.QMessageBox.information(None, "Thông báo", 
            "Vui lòng sử dụng chức năng 'Tạo phiếu nhập' để in phiếu")

    def cancel_receipt(self):
        """Hủy phiếu nhập hiện tại"""
        reply = QtWidgets.QMessageBox.question(None, "Xác nhận", 
            "Bạn có chắc chắn muốn hủy phiếu nhập hiện tại?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.new_receipt()

    def calculate_total_value_receipt(self):
        """Tính tổng giá trị phiếu nhập"""
        total = 0
        for row in range(self.product_model.rowCount()):
            try:
                # Giá thành từ cột 5
                gia_thanh = float(self.product_model.item(row, 5).text().replace(',', ''))
                # Số lượng nhập từ cột 2
                so_luong = int(self.product_model.item(row, 2).text())
                total += gia_thanh * so_luong
            except (ValueError, AttributeError):
                continue
        self.line_total_value_NKTP.setText(f"{total:,.0f} VNĐ")

    def add_product(self):
        """Thêm sản phẩm vào phiếu nhập với validation"""
        if not self.selected_product_id:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn sản phẩm từ danh sách")
            return
            
        product_name = self.line_product_name_NKTP.text()
        quantity_total = self.spin_quantity_total_NKTP.value()
        quantity_standard = self.spin_quantity_standard_NKTP.value()
        quantity_defective = self.spin_quantity_defective_NKTP.value()
        cost_price_text = self.line_cost_price_NKTP.text()
        
        # Validation
        if quantity_standard + quantity_defective != quantity_total:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", 
                "Tổng số lượng đạt + số lượng lỗi phải bằng số lượng nhập")
            return
        
        if not cost_price_text:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng nhập giá thành")
            return
        
        try:
            cost_price = float(cost_price_text.replace(',', ''))
            
            # Check if product already exists in the list
            for row in range(self.product_model.rowCount()):
                if self.product_model.item(row, 0).text() == self.selected_product_id:
                    # Update existing product
                    current_qty = int(self.product_model.item(row, 2).text())
                    current_std = int(self.product_model.item(row, 3).text())
                    current_def = int(self.product_model.item(row, 4).text())
                    
                    new_qty = current_qty + quantity_total
                    new_std = current_std + quantity_standard
                    new_def = current_def + quantity_defective
                    
                    self.product_model.item(row, 2).setText(str(new_qty))
                    self.product_model.item(row, 3).setText(str(new_std))
                    self.product_model.item(row, 4).setText(str(new_def))
                    self.product_model.item(row, 5).setText(f"{cost_price:,.0f}")
                    
                    self.calculate_total_value_receipt()
                    self.clear_product_inputs()
                    return
            
            # Add new product
            items = [
                QtGui.QStandardItem(self.selected_product_id),
                QtGui.QStandardItem(product_name),
                QtGui.QStandardItem(str(quantity_total)),
                QtGui.QStandardItem(str(quantity_standard)),
                QtGui.QStandardItem(str(quantity_defective)),
                QtGui.QStandardItem(f"{cost_price:,.0f}")
            ]
            self.product_model.appendRow(items)
            self.calculate_total_value_receipt()
            self.clear_product_inputs()
            self.statusbar.showMessage(f"Đã thêm {product_name}", 2000)
            
        except ValueError:
            QtWidgets.QMessageBox.critical(None, "Lỗi", "Vui lòng nhập giá thành hợp lệ")

    def clear_product_inputs(self):
        """Xóa thông tin nhập sản phẩm"""
        self.line_product_name_NKTP.clear()
        self.spin_quantity_total_NKTP.setValue(1)
        self.spin_quantity_standard_NKTP.setValue(0)
        self.spin_quantity_defective_NKTP.setValue(0)
        self.line_cost_price_NKTP.clear()
        self.selected_product_id = None

    def validate_receipt(self):
        """Kiểm tra tính hợp lệ của phiếu nhập"""
        if self.product_model.rowCount() == 0:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng thêm ít nhất một sản phẩm")
            return False
            
        return True

    def create_receipt(self):
        """Tạo phiếu nhập với form xác nhận"""
        if not self.validate_receipt():
            return

        # Hiển thị form xác nhận
        self.show_receipt_confirmation()

    def show_receipt_confirmation(self):
        """Hiển thị form xác nhận phiếu nhập"""
        # Tạo dialog xác nhận
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Xác nhận phiếu nhập kho thành phẩm")
        dialog.resize(800, 700)
        dialog.setModal(True)
        
        # Áp dụng style cho dialog
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin: 8px 0px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #495057;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton.confirm-btn {
                background-color: #28a745;
            }
            QPushButton.confirm-btn:hover {
                background-color: #218838;
            }
            QPushButton.cancel-btn {
                background-color: #6c757d;
            }
            QPushButton.cancel-btn:hover {
                background-color: #545b62;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_label = QtWidgets.QLabel("XÁC NHẬN PHIẾU NHẬP KHO THÀNH PHẨM")
        header_label.setAlignment(QtCore.Qt.AlignCenter)
        header_font = QtGui.QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setStyleSheet("color: #007bff; margin: 10px; padding: 10px;")
        layout.addWidget(header_label)
        
        # Thông tin phiếu nhập
        receipt_info_group = QtWidgets.QGroupBox("Thông tin phiếu nhập")
        receipt_info_layout = QtWidgets.QGridLayout(receipt_info_group)
        
        receipt_info_layout.addWidget(QtWidgets.QLabel("Mã phiếu nhập:"), 0, 0)
        receipt_code_label = QtWidgets.QLabel(self.label_receipt_code.text())
        receipt_code_label.setStyleSheet("font-weight: bold; color: #007bff;")
        receipt_info_layout.addWidget(receipt_code_label, 0, 1)
        
        receipt_info_layout.addWidget(QtWidgets.QLabel("Ngày nhập:"), 0, 2)
        receipt_date = self.edit_date_entry.date().toString("dd/MM/yyyy")
        receipt_info_layout.addWidget(QtWidgets.QLabel(receipt_date), 0, 3)
        
        receipt_info_layout.addWidget(QtWidgets.QLabel("Đơn hàng:"), 1, 0)
        order_text = self.combobox_order_NKTP.currentText() if self.combobox_order_NKTP.currentIndex() >= 0 else "Không có"
        receipt_info_layout.addWidget(QtWidgets.QLabel(order_text), 1, 1)
        
        receipt_info_layout.addWidget(QtWidgets.QLabel("Ghi chú:"), 1, 2)
        notes_label = QtWidgets.QLabel(self.line_notes_NKTP.text())
        notes_label.setWordWrap(True)
        receipt_info_layout.addWidget(notes_label, 1, 3)
        
        layout.addWidget(receipt_info_group)
        
        # Danh sách sản phẩm nhập
        products_group = QtWidgets.QGroupBox("Danh sách sản phẩm nhập kho")
        products_layout = QtWidgets.QVBoxLayout(products_group)
        
        # Tạo bảng hiển thị sản phẩm
        products_table = QtWidgets.QTableWidget()
        products_table.setColumnCount(6)
        products_table.setHorizontalHeaderLabels(["Tên sản phẩm", "SL Nhập", "SL Đạt", "SL Lỗi", "Giá thành", "Thành tiền"])
        products_table.setRowCount(self.product_model.rowCount())
        
        # Điền dữ liệu vào bảng
        for row in range(self.product_model.rowCount()):
            # Tên sản phẩm
            name_item = QtWidgets.QTableWidgetItem(self.product_model.item(row, 1).text())
            name_item.setFlags(name_item.flags() & ~QtCore.Qt.ItemIsEditable)
            products_table.setItem(row, 0, name_item)
            
            # SL Nhập
            qty_total_item = QtWidgets.QTableWidgetItem(self.product_model.item(row, 2).text())
            qty_total_item.setFlags(qty_total_item.flags() & ~QtCore.Qt.ItemIsEditable)
            products_table.setItem(row, 1, qty_total_item)
            
            # SL Đạt
            qty_std_item = QtWidgets.QTableWidgetItem(self.product_model.item(row, 3).text())
            qty_std_item.setFlags(qty_std_item.flags() & ~QtCore.Qt.ItemIsEditable)
            products_table.setItem(row, 2, qty_std_item)
            
            # SL Lỗi
            qty_def_item = QtWidgets.QTableWidgetItem(self.product_model.item(row, 4).text())
            qty_def_item.setFlags(qty_def_item.flags() & ~QtCore.Qt.ItemIsEditable)
            products_table.setItem(row, 3, qty_def_item)
            
            # Giá thành
            cost_text = f"{float(self.product_model.item(row, 5).text().replace(',', '')):,.0f} VNĐ"
            cost_item = QtWidgets.QTableWidgetItem(cost_text)
            cost_item.setFlags(cost_item.flags() & ~QtCore.Qt.ItemIsEditable)
            products_table.setItem(row, 4, cost_item)
            
            # Thành tiền
            cost_price = float(self.product_model.item(row, 5).text().replace(',', ''))
            quantity = int(self.product_model.item(row, 2).text())
            total_amount = cost_price * quantity
            total_item = QtWidgets.QTableWidgetItem(f"{total_amount:,.0f} VNĐ")
            total_item.setFlags(total_item.flags() & ~QtCore.Qt.ItemIsEditable)
            products_table.setItem(row, 5, total_item)
        
        # Tự động điều chỉnh kích thước cột
        products_table.resizeColumnsToContents()
        products_table.horizontalHeader().setStretchLastSection(True)
        products_table.setMaximumHeight(200)
        
        products_layout.addWidget(products_table)
        layout.addWidget(products_group)
        
        # Thông tin tổng kết
        summary_group = QtWidgets.QGroupBox("Tổng kết")
        summary_layout = QtWidgets.QGridLayout(summary_group)
        
        summary_layout.addWidget(QtWidgets.QLabel("Tổng số loại sản phẩm:"), 0, 0)
        total_types_label = QtWidgets.QLabel(str(self.product_model.rowCount()))
        total_types_label.setStyleSheet("font-weight: bold; color: #007bff;")
        summary_layout.addWidget(total_types_label, 0, 1)
        
        summary_layout.addWidget(QtWidgets.QLabel("Tổng giá trị:"), 0, 2)
        total_value_label = QtWidgets.QLabel(self.line_total_value_NKTP.text())
        total_value_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #28a745;")
        summary_layout.addWidget(total_value_label, 0, 3)
        
        layout.addWidget(summary_group)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        btn_print = QtWidgets.QPushButton("In phiếu")
        btn_print.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        
        btn_save_pdf = QtWidgets.QPushButton("Lưu PDF")
        btn_save_pdf.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #5a32a3;
            }
        """)
        
        btn_cancel = QtWidgets.QPushButton("Hủy")
        btn_cancel.setProperty("class", "cancel-btn")
        
        button_layout.addWidget(btn_print)
        button_layout.addWidget(btn_save_pdf)
        button_layout.addWidget(btn_cancel)
        
        layout.addLayout(button_layout)
        
        # Kết nối sự kiện
        btn_print.clicked.connect(lambda: self.print_receipt_directly(dialog))
        btn_save_pdf.clicked.connect(lambda: self.save_receipt_pdf_directly(dialog))
        btn_cancel.clicked.connect(dialog.reject)
        
        # Hiển thị dialog
        dialog.exec_()

    def print_receipt_directly(self, dialog):
        """In phiếu nhập trực tiếp"""
        try:
            # Tạo nội dung in
            print_content = self.generate_receipt_print_content()
            
            # Tạo document để in
            document = QtGui.QTextDocument()
            document.setHtml(print_content)
            
            # In ngay lập tức
            printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
            print_dialog = QtPrintSupport.QPrintDialog(printer)
            
            if print_dialog.exec_() == QtWidgets.QDialog.Accepted:
                document.print_(printer)
                QtWidgets.QMessageBox.information(None, "Thành công", "Đã gửi lệnh in phiếu nhập thành công!")
                
                # Lưu vào database và reset form
                if self.save_receipt_to_database():
                    dialog.accept()
                    QtWidgets.QMessageBox.information(None, "Hoàn tất", 
                        f"Phiếu nhập {self.label_receipt_code.text()} đã được tạo và in thành công!")
                    self.new_receipt()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi", f"Lỗi khi in phiếu: {e}")

    def save_receipt_pdf_directly(self, dialog):
        """Lưu phiếu nhập thành PDF trực tiếp"""
        try:
            # Chọn nơi lưu file
            file_name = f"PhieuNhap_{self.label_receipt_code.text()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                None, "Lưu phiếu nhập PDF", 
                file_name,
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                # Tạo nội dung PDF
                print_content = self.generate_receipt_print_content()
                
                # Tạo document
                document = QtGui.QTextDocument()
                document.setHtml(print_content)
                
                # Lưu thành PDF
                printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
                printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
                printer.setOutputFileName(file_path)
                printer.setPageSize(QtPrintSupport.QPrinter.A4)
                printer.setPageMargins(15, 15, 15, 15, QtPrintSupport.QPrinter.Millimeter)
                
                document.print_(printer)
                
                QtWidgets.QMessageBox.information(None, "Thành công", 
                    f"Đã lưu phiếu nhập thành file PDF:\n{file_path}")
                
                # Lưu vào database và reset form
                if self.save_receipt_to_database():
                    dialog.accept()
                    QtWidgets.QMessageBox.information(None, "Hoàn tất", 
                        f"Phiếu nhập {self.label_receipt_code.text()} đã được tạo và lưu PDF thành công!")
                    self.new_receipt()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi", f"Lỗi khi lưu PDF: {e}")

    def generate_receipt_print_content(self):
        """Tạo nội dung HTML cho phiếu nhập kho"""
        order_text = self.combobox_order_NKTP.currentText() if self.combobox_order_NKTP.currentIndex() >= 0 else "Không có"
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .company-name {{ font-size: 24px; font-weight: bold; color: #007bff; }}
                .document-title {{ font-size: 20px; font-weight: bold; margin: 20px 0; }}
                .info-section {{ margin: 15px 0; }}
                .info-row {{ margin: 5px 0; }}
                .label {{ font-weight: bold; display: inline-block; width: 150px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; font-weight: bold; }}
                .total-section {{ margin-top: 20px; text-align: right; }}
                .total-row {{ margin: 5px 0; }}
                .signature-section {{ margin-top: 40px; }}
                .signature {{ display: inline-block; width: 200px; text-align: center; margin: 0 50px; }}
                .text-center {{ text-align: center; }}
                .text-right {{ text-align: right; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="company-name">CÔNG TY MAY MẶC ABC</div>
                <div>Địa chỉ: 123 Đường ABC, Quận XYZ, TP.HCM</div>
                <div>Điện thoại: (028) 1234-5678 | Email: info@maymac.com</div>
                <div class="document-title">PHIẾU NHẬP KHO THÀNH PHẨM</div>
            </div>
            
            <div class="info-section">
                <div class="info-row">
                    <span class="label">Mã phiếu nhập:</span>
                    <span style="font-weight: bold; color: #007bff;">{self.label_receipt_code.text()}</span>
                </div>
                <div class="info-row">
                    <span class="label">Ngày nhập:</span>
                    <span>{self.edit_date_entry.date().toString("dd/MM/yyyy")}</span>
                </div>
                <div class="info-row">
                    <span class="label">Đơn hàng liên quan:</span>
                    <span>{order_text}</span>
                </div>
                <div class="info-row">
                    <span class="label">Ghi chú:</span>
                    <span>{self.line_notes_NKTP.text()}</span>
                </div>
            </div>
            
            <div class="info-section">
                <h3>DANH SÁCH SẢN PHẨM NHẬP KHO</h3>
                <table>
                    <thead>
                        <tr>
                            <th>STT</th>
                            <th>Tên sản phẩm</th>
                            <th>SL Nhập</th>
                            <th>SL Đạt</th>
                            <th>SL Lỗi</th>
                            <th>Giá thành (VNĐ)</th>
                            <th>Thành tiền (VNĐ)</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Thêm danh sách sản phẩm
        total_amount = 0
        for row in range(self.product_model.rowCount()):
            ten_sp = self.product_model.item(row, 1).text()
            sl_nhap = self.product_model.item(row, 2).text()
            sl_dat = self.product_model.item(row, 3).text()
            sl_loi = self.product_model.item(row, 4).text()
            gia_thanh = float(self.product_model.item(row, 5).text().replace(',', ''))
            thanh_tien = gia_thanh * int(sl_nhap)
            total_amount += thanh_tien
            
            html_content += f"""
                        <tr>
                            <td class="text-center">{row + 1}</td>
                            <td>{ten_sp}</td>
                            <td class="text-center">{sl_nhap}</td>
                            <td class="text-center">{sl_dat}</td>
                            <td class="text-center">{sl_loi}</td>
                            <td class="text-right">{gia_thanh:,.0f}</td>
                            <td class="text-right">{thanh_tien:,.0f}</td>
                        </tr>
            """
        
        # Thêm dòng tổng cộng
        html_content += f"""
                        <tr style="font-weight: bold; background-color: #f8f9fa;">
                            <td colspan="6" class="text-right">TỔNG CỘNG:</td>
                            <td class="text-right">{total_amount:,.0f}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        """
        
        # Thêm tổng kết
        html_content += f"""
            <div class="total-section">
                <div class="total-row">
                    <span class="label">Tổng số loại sản phẩm:</span>
                    <span style="font-weight: bold;">{self.product_model.rowCount()} loại</span>
                </div>
                <div class="total-row">
                    <span class="label">Tổng giá trị nhập kho:</span>
                    <span style="font-weight: bold; font-size: 16px; color: #28a745;">{total_amount:,.0f} VNĐ</span>
                </div>
            </div>
        """
        
        html_content += f"""
            <div class="signature-section">
                <div class="signature">
                    <div>Người lập phiếu</div>
                    <div style="margin-top: 60px;">(Ký tên)</div>
                </div>
                <div class="signature">
                    <div>Thủ kho</div>
                    <div style="margin-top: 60px;">(Ký tên)</div>
                </div>
                <div class="signature">
                    <div>Người giao</div>
                    <div style="margin-top: 60px;">(Ký tên)</div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 30px; font-style: italic;">
                Phiếu nhập kho được tạo tự động bởi hệ thống quản lý kho
            </div>
        </body>
        </html>
        """
        
        return html_content

    def save_receipt_to_database(self):
        """Lưu phiếu nhập vào database (placeholder method)"""
        # Implement database saving logic here
        return True