from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtPrintSupport
import pymysql as mysql
from pymysql import Error
import uuid
from datetime import datetime, date

class Ui_DHWindow(object):
    def __init__(self):
        self.db_connection = None
        self.selected_customer_id = None
        self.current_order_id = None
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

    def setupUi(self, DHWindow):
        DHWindow.setObjectName("DHWindow")
        DHWindow.resize(1600, 900)
        DHWindow.setMinimumSize(1400, 800)
        
        # Set modern style
        self.setup_styles(DHWindow)
        
        self.centralwidget = QtWidgets.QWidget(DHWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Create main layout
        main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header
        self.setup_header(main_layout)
        
        # Content area using QSplitter
        content_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        main_layout.addWidget(content_splitter)
        
        # Left panel - Customer info
        left_panel = self.setup_customer_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Products only (removed materials)
        right_panel = self.setup_product_panel()
        content_splitter.addWidget(right_panel)
        
        # Bottom panel - Order summary
        bottom_panel = self.setup_order_summary_panel()
        main_layout.addWidget(bottom_panel)
        
        # Set splitter proportions
        content_splitter.setSizes([500, 800])

        DHWindow.setCentralWidget(self.centralwidget)
        
        # Setup menubar and statusbar
        self.setup_menubar(DHWindow)
        self.setup_statusbar(DHWindow)

        self.retranslateUi(DHWindow)
        self.setup_models()
        QtCore.QMetaObject.connectSlotsByName(DHWindow)

    def setup_styles(self, DHWindow):
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
        
        QLabel {
            color: #495057;
        }
        """
        DHWindow.setStyleSheet(style)

    def setup_header(self, layout):
        """Thiết lập header với thông tin đơn hàng"""
        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        
        # Title
        title_label = QtWidgets.QLabel("QUẢN LÝ ĐẶT HÀNG")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_font = QtGui.QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #007bff; margin: 10px;")
        
        # Order info
        order_info_widget = QtWidgets.QWidget()
        order_info_layout = QtWidgets.QGridLayout(order_info_widget)
        
        order_info_layout.addWidget(QtWidgets.QLabel("Mã đơn hàng:"), 0, 0)
        self.label_order_code = QtWidgets.QLabel(f"DH-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}")
        self.label_order_code.setStyleSheet("font-weight: bold; color: #007bff;")
        order_info_layout.addWidget(self.label_order_code, 0, 1)
        
        order_info_layout.addWidget(QtWidgets.QLabel("Ngày tạo:"), 1, 0)
        self.label_create_date = QtWidgets.QLabel(datetime.now().strftime("%d/%m/%Y %H:%M"))
        order_info_layout.addWidget(self.label_create_date, 1, 1)
        
        header_layout.addWidget(title_label, 2)
        header_layout.addWidget(order_info_widget, 1)
        
        layout.addWidget(header_widget)

    def setup_customer_panel(self):
        """Thiết lập panel thông tin khách hàng"""
        customer_group = QtWidgets.QGroupBox("Thông tin khách hàng")
        customer_layout = QtWidgets.QVBoxLayout(customer_group)
        
        # Customer search section
        search_widget = QtWidgets.QWidget()
        search_layout = QtWidgets.QGridLayout(search_widget)
        
        search_layout.addWidget(QtWidgets.QLabel("Tìm kiếm:"), 0, 0)
        self.line_search_customer_DH = QtWidgets.QLineEdit()
        self.line_search_customer_DH.setPlaceholderText("Nhập tên, SĐT hoặc CMND...")
        self.line_search_customer_DH.textChanged.connect(self.auto_search_customer)
        search_layout.addWidget(self.line_search_customer_DH, 0, 1)
        
        self.combobox_search_type_DH = QtWidgets.QComboBox()
        self.combobox_search_type_DH.addItems(["Tên", "Số điện thoại", "CMND"])
        search_layout.addWidget(self.combobox_search_type_DH, 0, 2)
        
        self.btn_search_customer_DH = QtWidgets.QPushButton("Tìm kiếm")
        self.btn_search_customer_DH.clicked.connect(self.search_customer)
        search_layout.addWidget(self.btn_search_customer_DH, 0, 3)
        
        # Customer selection
        search_layout.addWidget(QtWidgets.QLabel("Chọn khách hàng:"), 1, 0)
        self.combobox_customer_DH = QtWidgets.QComboBox()
        self.combobox_customer_DH.currentIndexChanged.connect(self.on_customer_selected)
        search_layout.addWidget(self.combobox_customer_DH, 1, 1, 1, 2)
        
        customer_layout.addWidget(search_widget)
        
        # Customer management buttons
        btn_widget = QtWidgets.QWidget()
        btn_layout = QtWidgets.QHBoxLayout(btn_widget)
        
        self.btn_add_customer_DH = QtWidgets.QPushButton("Thêm KH")
        self.btn_edit_customer_DH = QtWidgets.QPushButton("Sửa KH")
        
        self.btn_add_customer_DH.clicked.connect(self.add_customer)
        self.btn_edit_customer_DH.clicked.connect(self.edit_customer)
        
        btn_layout.addWidget(self.btn_add_customer_DH)
        btn_layout.addWidget(self.btn_edit_customer_DH)
        btn_layout.addStretch()
        
        customer_layout.addWidget(btn_widget)
        
        # Customer details table
        self.table_ttkh_DH = QtWidgets.QTableView()
        self.table_ttkh_DH.setMaximumHeight(200)
        self.table_ttkh_DH.clicked.connect(self.select_customer_from_table)
        customer_layout.addWidget(self.table_ttkh_DH)
        
        # Order details
        order_details_widget = QtWidgets.QWidget()
        order_details_layout = QtWidgets.QGridLayout(order_details_widget)
        
        order_details_layout.addWidget(QtWidgets.QLabel("Ngày giao hàng:"), 0, 0)
        self.edit_date_finish_DH = QtWidgets.QDateEdit()
        self.edit_date_finish_DH.setDate(QtCore.QDate.currentDate().addDays(7))
        self.edit_date_finish_DH.setCalendarPopup(True)
        order_details_layout.addWidget(self.edit_date_finish_DH, 0, 1)
        
        order_details_layout.addWidget(QtWidgets.QLabel("Ghi chú:"), 1, 0)
        self.text_notes = QtWidgets.QTextEdit()
        self.text_notes.setMaximumHeight(60)
        self.text_notes.setPlaceholderText("Ghi chú cho đơn hàng...")
        order_details_layout.addWidget(self.text_notes, 1, 1)
        
        customer_layout.addWidget(order_details_widget)
        
        return customer_group

    def setup_product_panel(self):
        """Thiết lập panel sản phẩm (đã loại bỏ vật liệu)"""
        products_group = QtWidgets.QGroupBox("Quản lý sản phẩm")
        products_layout = QtWidgets.QVBoxLayout(products_group)
        
        # Product search
        search_widget = QtWidgets.QWidget()
        search_layout = QtWidgets.QHBoxLayout(search_widget)
        
        search_layout.addWidget(QtWidgets.QLabel("Tìm sản phẩm:"))
        self.line_search_products_DH = QtWidgets.QLineEdit()
        self.line_search_products_DH.setPlaceholderText("Nhập tên sản phẩm...")
        self.line_search_products_DH.textChanged.connect(self.auto_search_products)
        search_layout.addWidget(self.line_search_products_DH)
        
        self.btn_search_products_DH = QtWidgets.QPushButton("Tìm")
        self.btn_search_products_DH.clicked.connect(self.search_products)
        search_layout.addWidget(self.btn_search_products_DH)
        
        products_layout.addWidget(search_widget)
        
        # Available products for custom manufacturing
        products_layout.addWidget(QtWidgets.QLabel("Danh sách mẫu sản phẩm có thể đặt may:"))
        self.table_listProducts_DH = QtWidgets.QTableView()
        self.table_listProducts_DH.setMaximumHeight(250)
        self.table_listProducts_DH.doubleClicked.connect(self.add_product_with_quantity)
        products_layout.addWidget(self.table_listProducts_DH)
        
        # Selected products
        products_layout.addWidget(QtWidgets.QLabel("Sản phẩm đã chọn đặt may:"))
        self.table_products_DH = QtWidgets.QTableView()
        products_layout.addWidget(self.table_products_DH)
        
        # Product buttons
        product_btn_widget = QtWidgets.QWidget()
        product_btn_layout = QtWidgets.QHBoxLayout(product_btn_widget)
        
        self.btn_add_product_DH = QtWidgets.QPushButton("Thêm sản phẩm")
        self.btn_edit_quantity_DH = QtWidgets.QPushButton("Sửa số lượng")
        self.btn_del_product_DH = QtWidgets.QPushButton("Xóa")
        self.btn_del_product_DH.setProperty("class", "delete-btn")
        
        self.btn_add_product_DH.clicked.connect(self.add_product_with_quantity)
        self.btn_edit_quantity_DH.clicked.connect(self.edit_product_quantity)
        self.btn_del_product_DH.clicked.connect(self.delete_product)
        
        product_btn_layout.addWidget(self.btn_add_product_DH)
        product_btn_layout.addWidget(self.btn_edit_quantity_DH)
        product_btn_layout.addWidget(self.btn_del_product_DH)
        product_btn_layout.addStretch()
        
        products_layout.addWidget(product_btn_widget)
        
        return products_group

    def setup_order_summary_panel(self):
        """Thiết lập panel tổng kết đơn hàng"""
        summary_group = QtWidgets.QGroupBox("Tổng kết đơn hàng")
        summary_layout = QtWidgets.QHBoxLayout(summary_group)
        
        # Order summary info
        info_widget = QtWidgets.QWidget()
        info_layout = QtWidgets.QGridLayout(info_widget)
        
        info_layout.addWidget(QtWidgets.QLabel("Tổng tiền:"), 0, 0)
        self.line_total_price = QtWidgets.QLineEdit()
        self.line_total_price.setReadOnly(True)
        self.line_total_price.setStyleSheet("font-weight: bold; font-size: 14px; background-color: #f8f9fa;")
        info_layout.addWidget(self.line_total_price, 0, 1)
        
        info_layout.addWidget(QtWidgets.QLabel("Tiền đặt cọc:"), 1, 0)
        self.line_deposit = QtWidgets.QLineEdit()
        self.line_deposit.setPlaceholderText("Nhập số tiền đặt cọc...")
        self.line_deposit.textChanged.connect(self.calculate_remaining)
        info_layout.addWidget(self.line_deposit, 1, 1)
        
        info_layout.addWidget(QtWidgets.QLabel("Còn lại:"), 2, 0)
        self.line_remaining = QtWidgets.QLineEdit()
        self.line_remaining.setReadOnly(True)
        self.line_remaining.setStyleSheet("background-color: #f8f9fa; font-weight: bold;")
        info_layout.addWidget(self.line_remaining, 2, 1)
        
        # Action buttons
        action_widget = QtWidgets.QWidget()
        action_layout = QtWidgets.QVBoxLayout(action_widget)
        
        btn_row1 = QtWidgets.QHBoxLayout()
        self.btn_save_Orders_DH = QtWidgets.QPushButton("Lưu đơn hàng")
        self.btn_save_Orders_DH.setProperty("class", "save-btn")
        self.btn_update_Orders_DH = QtWidgets.QPushButton("Cập nhật")
        
        self.btn_save_Orders_DH.clicked.connect(self.save_order)
        self.btn_update_Orders_DH.clicked.connect(self.update_order)
        
        btn_row1.addWidget(self.btn_save_Orders_DH)
        btn_row1.addWidget(self.btn_update_Orders_DH)
        
        btn_row2 = QtWidgets.QHBoxLayout()
        self.btn_print_Orders_DH = QtWidgets.QPushButton("In đơn hàng")
        self.btn_del_Orders = QtWidgets.QPushButton("Xóa đơn hàng")
        self.btn_del_Orders.setProperty("class", "delete-btn")
        
        self.btn_print_Orders_DH.clicked.connect(self.print_order_confirmation)
        self.btn_del_Orders.clicked.connect(self.delete_order)
        
        btn_row2.addWidget(self.btn_print_Orders_DH)
        btn_row2.addWidget(self.btn_del_Orders)
        
        btn_row3 = QtWidgets.QHBoxLayout()
        self.btn_new_order = QtWidgets.QPushButton("Đơn hàng mới")
        self.btn_cancel = QtWidgets.QPushButton("Hủy")
        self.btn_new_order.clicked.connect(self.new_order)
        self.btn_cancel.clicked.connect(self.cancel_order)
        
        btn_row3.addWidget(self.btn_new_order)
        btn_row3.addWidget(self.btn_cancel)
        
        action_layout.addLayout(btn_row1)
        action_layout.addLayout(btn_row2)
        action_layout.addLayout(btn_row3)
        
        # Orders list
        orders_widget = QtWidgets.QWidget()
        orders_layout = QtWidgets.QVBoxLayout(orders_widget)
        orders_layout.addWidget(QtWidgets.QLabel("Danh sách đơn hàng:"))
        
        self.table_listOrder_DH = QtWidgets.QTableView()
        self.table_listOrder_DH.setMaximumHeight(150)
        self.table_listOrder_DH.clicked.connect(self.on_order_selected)
        orders_layout.addWidget(self.table_listOrder_DH)
        
        summary_layout.addWidget(info_widget, 1)
        summary_layout.addWidget(action_widget, 1)
        summary_layout.addWidget(orders_widget, 2)
        
        return summary_group

    def setup_menubar(self, DHWindow):
        """Thiết lập menu bar"""
        self.menubar = QtWidgets.QMenuBar(DHWindow)
        DHWindow.setMenuBar(self.menubar)

    def setup_statusbar(self, DHWindow):
        """Thiết lập status bar"""
        self.statusbar = QtWidgets.QStatusBar(DHWindow)
        self.statusbar.showMessage("Sẵn sàng")
        DHWindow.setStatusBar(self.statusbar)

    def setup_models(self):
        """Thiết lập các model cho tables"""
        # Customer model
        self.customer_model = QtGui.QStandardItemModel()
        self.table_ttkh_DH.setModel(self.customer_model)
        
        # Product models
        self.product_model = QtGui.QStandardItemModel()
        self.table_products_DH.setModel(self.product_model)
        
        self.available_products_model = QtGui.QStandardItemModel()
        self.table_listProducts_DH.setModel(self.available_products_model)
        
        # Order model
        self.order_model = QtGui.QStandardItemModel()
        self.table_listOrder_DH.setModel(self.order_model)
        
        # Set table properties
        for table in [self.table_ttkh_DH, self.table_products_DH, 
                     self.table_listOrder_DH, self.table_listProducts_DH]:
            table.setAlternatingRowColors(True)
            table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        
        self.load_customers()
        self.load_products()
        self.load_orders()

    def auto_search_customer(self):
        """Tự động tìm kiếm khách hàng khi nhập"""
        if len(self.line_search_customer_DH.text()) >= 2:
            self.search_customer()

    def auto_search_products(self):
        """Tự động tìm kiếm sản phẩm khi nhập"""
        if len(self.line_search_products_DH.text()) >= 2:
            self.search_products()

    def select_customer_from_table(self):
        """Chọn khách hàng từ bảng"""
        selected = self.table_ttkh_DH.currentIndex()
        if selected.isValid():
            customer_id = self.customer_model.item(selected.row(), 0).text()
            customer_name = self.customer_model.item(selected.row(), 2).text()
            
            # Tìm và chọn khách hàng trong combobox
            for i in range(self.combobox_customer_DH.count()):
                if self.combobox_customer_DH.itemText(i) == customer_name:
                    self.combobox_customer_DH.setCurrentIndex(i)
                    break

    def calculate_remaining(self):
        """Tính toán số tiền còn lại với validation"""
        try:
            total_text = self.line_total_price.text().replace(',', '').replace(' VNĐ', '')
            deposit_text = self.line_deposit.text().replace(',', '')
            
            total = float(total_text) if total_text else 0
            deposit = float(deposit_text) if deposit_text else 0
            
            if deposit > total:
                QtWidgets.QMessageBox.warning(None, "Cảnh báo", 
                    "Tiền đặt cọc không được vượt quá tổng tiền đơn hàng!")
                self.line_deposit.setText(str(int(total)))
                deposit = total
            
            remaining = total - deposit
            self.line_remaining.setText(f"{remaining:,.0f} VNĐ")
            
        except ValueError:
            self.line_remaining.setText("0 VNĐ")

    def on_customer_selected(self):
        """Xử lý khi chọn khách hàng với validation"""
        index = self.combobox_customer_DH.currentIndex()
        if index >= 0 and self.customer_model.rowCount() > 0:
            # Lấy ID khách hàng từ model
            if index < self.customer_model.rowCount():
                self.selected_customer_id = self.customer_model.item(index, 0).text()
                customer_name = self.customer_model.item(index, 2).text()
                self.statusbar.showMessage(f"Đã chọn khách hàng: {customer_name}", 3000)

    def add_product_with_quantity(self):
        """Thêm sản phẩm với dialog nhập số lượng"""
        selected = self.table_listProducts_DH.currentIndex()
        if not selected.isValid():
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn mẫu sản phẩm để đặt may!")
            return
        
        # Lấy thông tin sản phẩm
        product_id = self.available_products_model.item(selected.row(), 0).text()
        product_name = self.available_products_model.item(selected.row(), 2).text()
        product_price = float(self.available_products_model.item(selected.row(), 5).text().replace(',', ''))
        
        # Kiểm tra sản phẩm đã có trong đơn hàng chưa
        for row in range(self.product_model.rowCount()):
            if self.product_model.item(row, 0).text() == product_id:
                QtWidgets.QMessageBox.warning(None, "Cảnh báo", 
                    "Sản phẩm đã có trong đơn đặt may! Vui lòng sử dụng chức năng 'Sửa số lượng'")
                return
        
        # Dialog nhập số lượng
        quantity, ok = QtWidgets.QInputDialog.getInt(
            None, "Nhập số lượng đặt may", 
            f"Số lượng đặt may cho {product_name}:",
            value=1, min=1, max=9999
        )
        
        if ok and quantity > 0:
            # Thêm vào bảng sản phẩm đã chọn
            items = []
            for col in range(self.available_products_model.columnCount()):
                items.append(QtGui.QStandardItem(self.available_products_model.item(selected.row(), col).text()))
            
            # Thêm cột số lượng và thành tiền
            items.append(QtGui.QStandardItem(str(quantity)))  # Số lượng
            total_price = quantity * product_price
            items.append(QtGui.QStandardItem(f"{total_price:,.0f}"))  # Thành tiền
            
            self.product_model.appendRow(items)
            self.update_total_price()
            self.statusbar.showMessage(f"Đã thêm {quantity} {product_name} vào đơn đặt may", 2000)

    def edit_product_quantity(self):
        """Sửa số lượng sản phẩm đã chọn"""
        selected = self.table_products_DH.currentIndex()
        if not selected.isValid():
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn sản phẩm để sửa số lượng đặt may!")
            return
        
        current_quantity = int(self.product_model.item(selected.row(), 7).text())  # Cột số lượng
        product_name = self.product_model.item(selected.row(), 2).text()
        product_price = float(self.product_model.item(selected.row(), 5).text().replace(',', ''))
        
        new_quantity, ok = QtWidgets.QInputDialog.getInt(
            None, "Sửa số lượng đặt may", 
            f"Số lượng đặt may mới cho {product_name}:",
            value=current_quantity, min=1, max=9999
        )
        
        if ok and new_quantity > 0:
            # Cập nhật số lượng và thành tiền
            self.product_model.item(selected.row(), 7).setText(str(new_quantity))
            new_total = new_quantity * product_price
            self.product_model.item(selected.row(), 8).setText(f"{new_total:,.0f}")
            self.update_total_price()
            self.statusbar.showMessage(f"Đã cập nhật số lượng đặt may {product_name}", 2000)

    def update_total_price(self):
        """Cập nhật tổng tiền đơn hàng"""
        total = 0
        for row in range(self.product_model.rowCount()):
            try:
                # Lấy thành tiền từ cột 8
                amount_text = self.product_model.item(row, 8).text().replace(',', '')
                amount = float(amount_text)
                total += amount
            except (ValueError, AttributeError):
                continue
        
        self.line_total_price.setText(f"{total:,.0f} VNĐ")
        self.calculate_remaining()

    def save_order(self):
        """Lưu đơn hàng với validation đầy đủ"""
        # Validation
        if not self.validate_order_data():
            return
        
        if not self.db_connection:
            QtWidgets.QMessageBox.critical(None, "Lỗi", "Không có kết nối cơ sở dữ liệu")
            return
        
        # Kiểm tra đơn hàng đã tồn tại
        if self.order_exists():
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", 
                "Đơn hàng đã tồn tại! Vui lòng sử dụng chức năng 'Cập nhật' hoặc tạo đơn hàng mới.")
            return
        
        try:
            ma_don_hang = self.label_order_code.text()
            ngay_giao = self.edit_date_finish_DH.date().toString("yyyy-MM-dd")
            total_text = self.line_total_price.text().replace(',', '').replace(' VNĐ', '')
            tong_tien = float(total_text) if total_text else 0
            deposit_text = self.line_deposit.text().replace(',', '')
            tien_dat_coc = float(deposit_text) if deposit_text else 0
            nhan_vien_id = 1  # Default employee ID
            
            cursor = self.db_connection.cursor()
            
            # Insert order
            cursor.execute("""
                INSERT INTO DonDatHang (maDonHang, khachHangId, nhanVienId, ngayGiaoHangDuKien, tongTien, tienDatCoc, loaiDonHang)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (ma_don_hang, self.selected_customer_id, nhan_vien_id, ngay_giao, tong_tien, tien_dat_coc, 'Đặt may'))
            
            order_id = cursor.lastrowid
            self.current_order_id = order_id
            
            # Insert order details
            for row in range(self.product_model.rowCount()):
                san_pham_id = self.product_model.item(row, 0).text()
                so_luong = int(self.product_model.item(row, 7).text())  # Cột số lượng
                gia_ban = float(self.product_model.item(row, 5).text().replace(',', ''))  # Giá may
                thanh_tien_text = self.product_model.item(row, 8).text().replace(',', '')
                thanh_tien = float(thanh_tien_text)
                
                cursor.execute("""
                    INSERT INTO ChiTietDonHang (donDatHangId, sanPhamId, soLuong, giaBan, thanhTien)
                    VALUES (%s, %s, %s, %s, %s)
                """, (order_id, san_pham_id, so_luong, gia_ban, thanh_tien))
            
            self.db_connection.commit()
            cursor.close()
            
            self.load_orders()
            self.statusbar.showMessage("Đã lưu đơn đặt may thành công", 3000)
            QtWidgets.QMessageBox.information(None, "Thành công", 
                f"Đơn đặt may {ma_don_hang} đã được lưu thành công!\nTổng tiền: {tong_tien:,.0f} VNĐ")
            
        except Error as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi", f"Lỗi khi lưu đơn đặt may:\n{e}")

    def validate_order_data(self):
        """Validate dữ liệu đơn hàng"""
        if not self.selected_customer_id:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn khách hàng")
            return False
        
        if self.product_model.rowCount() == 0:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng thêm ít nhất một sản phẩm")
            return False
        
        # Kiểm tra ngày giao hàng
        delivery_date = self.edit_date_finish_DH.date().toPyDate()
        if delivery_date <= date.today():
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", 
                "Ngày giao hàng phải sau ngày hiện tại")
            return False
        
        # Kiểm tra tiền đặt cọc
        try:
            total_text = self.line_total_price.text().replace(',', '').replace(' VNĐ', '')
            deposit_text = self.line_deposit.text().replace(',', '')
            
            total = float(total_text) if total_text else 0
            deposit = float(deposit_text) if deposit_text else 0
            
            if deposit > total:
                QtWidgets.QMessageBox.warning(None, "Cảnh báo", 
                    "Tiền đặt cọc không được vượt quá tổng tiền")
                return False
        except ValueError:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", 
                "Vui lòng nhập số tiền hợp lệ")
            return False
        
        return True

    def order_exists(self):
        """Kiểm tra đơn hàng đã tồn tại"""
        if not self.db_connection:
            return False
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT id FROM DonDatHang WHERE maDonHang = %s", (self.label_order_code.text(),))
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        except Error:
            return False

    def update_order(self):
        """Cập nhật đơn hàng hiện tại"""
        if not self.current_order_id:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", 
                "Không có đơn hàng nào để cập nhật. Vui lòng lưu đơn hàng mới hoặc chọn đơn hàng từ danh sách.")
            return
        
        if not self.validate_order_data():
            return
        
        reply = QtWidgets.QMessageBox.question(None, "Xác nhận cập nhật",
            "Bạn có chắc chắn muốn cập nhật đơn hàng này?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        
        if reply != QtWidgets.QMessageBox.Yes:
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # Update order
            ngay_giao = self.edit_date_finish_DH.date().toString("yyyy-MM-dd")
            total_text = self.line_total_price.text().replace(',', '').replace(' VNĐ', '')
            tong_tien = float(total_text) if total_text else 0
            deposit_text = self.line_deposit.text().replace(',', '')
            tien_dat_coc = float(deposit_text) if deposit_text else 0
            
            cursor.execute("""
                UPDATE DonDatHang 
                SET khachHangId = %s, ngayGiaoHangDuKien = %s, tongTien = %s, tienDatCoc = %s
                WHERE id = %s
            """, (self.selected_customer_id, ngay_giao, tong_tien, tien_dat_coc, self.current_order_id))
            
            # Delete old order details
            cursor.execute("DELETE FROM ChiTietDonHang WHERE donDatHangId = %s", (self.current_order_id,))
            
            # Insert new order details
            for row in range(self.product_model.rowCount()):
                san_pham_id = self.product_model.item(row, 0).text()
                so_luong = int(self.product_model.item(row, 7).text())  # Cột số lượng
                gia_ban = float(self.product_model.item(row, 5).text().replace(',', ''))  # Giá may
                thanh_tien_text = self.product_model.item(row, 8).text().replace(',', '')
                thanh_tien = float(thanh_tien_text)
                
                cursor.execute("""
                    INSERT INTO ChiTietDonHang (donDatHangId, sanPhamId, soLuong, giaBan, thanhTien)
                    VALUES (%s, %s, %s, %s, %s)
                """, (self.current_order_id, san_pham_id, so_luong, gia_ban, thanh_tien))
            
            self.db_connection.commit()
            cursor.close()
            
            self.load_orders()
            self.statusbar.showMessage("Đã cập nhật đơn hàng thành công", 3000)
            QtWidgets.QMessageBox.information(None, "Thành công", "Đơn hàng đã được cập nhật thành công!")
            
        except Error as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi", f"Lỗi khi cập nhật đơn hàng:\n{e}")

    def new_order(self):
        """Tạo đơn hàng mới"""
        if self.product_model.rowCount() > 0 or self.selected_customer_id:
            reply = QtWidgets.QMessageBox.question(None, "Xác nhận",
                "Bạn có chắc chắn muốn tạo đơn hàng mới? Dữ liệu hiện tại sẽ bị xóa.",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            
            if reply != QtWidgets.QMessageBox.Yes:
                return
        
        # Reset form
        self.combobox_customer_DH.setCurrentIndex(0)  # Chọn "-- Chọn khách hàng --"
        self.selected_customer_id = None
        self.current_order_id = None
        self.edit_date_finish_DH.setDate(QtCore.QDate.currentDate().addDays(7))
        self.line_total_price.clear()
        self.line_deposit.clear()
        self.line_remaining.clear()
        self.text_notes.clear()
        self.line_search_customer_DH.clear()
        self.line_search_products_DH.clear()
        
        # Generate new order code
        new_code = f"DH-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        self.label_order_code.setText(new_code)
        self.label_create_date.setText(datetime.now().strftime("%d/%m/%Y %H:%M"))
        
        # Clear tables
        self.product_model.clear()
        self.setup_product_model_headers()
        
        self.statusbar.showMessage("Đã tạo đơn hàng mới", 2000)

    def cancel_order(self):
        """Hủy thao tác hiện tại"""
        if self.product_model.rowCount() > 0 or self.selected_customer_id:
            reply = QtWidgets.QMessageBox.question(None, "Xác nhận hủy",
                "Bạn có chắc chắn muốn hủy? Dữ liệu hiện tại sẽ bị mất.",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            
            if reply == QtWidgets.QMessageBox.Yes:
                self.new_order()
                self.statusbar.showMessage("Đã hủy thao tác", 2000)

    def print_order_confirmation(self):
        """Hiển thị form xác nhận in đơn hàng"""
        if not self.selected_customer_id:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn khách hàng trước khi in đơn hàng")
            return
        
        if self.product_model.rowCount() == 0:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng thêm sản phẩm trước khi in đơn hàng")
            return
        
        try:
            # Tạo nội dung in
            print_content = self.generate_print_content()
            
            # Tạo dialog hiển thị preview
            preview_dialog = QtWidgets.QDialog()
            preview_dialog.setWindowTitle("Xem trước - Phiếu đặt may")
            preview_dialog.resize(700, 800)
            preview_dialog.setModal(True)
            
            layout = QtWidgets.QVBoxLayout(preview_dialog)
            
            # Text area hiển thị nội dung
            text_area = QtWidgets.QTextEdit()
            text_area.setHtml(print_content)
            text_area.setReadOnly(True)
            layout.addWidget(text_area)
            
            # Buttons
            button_layout = QtWidgets.QHBoxLayout()
            btn_print = QtWidgets.QPushButton("In ngay")
            btn_save_pdf = QtWidgets.QPushButton("Lưu PDF")
            btn_close = QtWidgets.QPushButton("Đóng")
            
            btn_print.setStyleSheet("background-color: #28a745; color: white; padding: 10px;")
            btn_save_pdf.setStyleSheet("background-color: #17a2b8; color: white; padding: 10px;")
            btn_close.setStyleSheet("background-color: #6c757d; color: white; padding: 10px;")
            
            button_layout.addStretch()
            button_layout.addWidget(btn_print)
            button_layout.addWidget(btn_save_pdf)
            button_layout.addWidget(btn_close)
            
            layout.addLayout(button_layout)
            
            # Kết nối events
            btn_print.clicked.connect(lambda: self.print_document(text_area.document()))
            btn_save_pdf.clicked.connect(lambda: self.save_as_pdf(text_area.document()))
            btn_close.clicked.connect(preview_dialog.accept)
            
            preview_dialog.exec_()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi", f"Lỗi khi tạo phiếu in: {e}")

    def print_document(self, document):
        """In tài liệu"""
        try:
            printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
            print_dialog = QtPrintSupport.QPrintDialog(printer)
            
            if print_dialog.exec_() == QtWidgets.QDialog.Accepted:
                document.print_(printer)
                QtWidgets.QMessageBox.information(None, "Thành công", "Đã gửi lệnh in thành công!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi", f"Lỗi khi in: {e}")

    def save_as_pdf(self, document):
        """Lưu thành file PDF"""
        try:
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                None, "Lưu PDF", 
                f"DonDatMay_{self.label_order_code.text()}_{datetime.now().strftime('%Y%m%d')}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
                printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
                printer.setOutputFileName(file_path)
                document.print_(printer)
                QtWidgets.QMessageBox.information(None, "Thành công", f"Đã lưu file PDF: {file_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi", f"Lỗi khi lưu PDF: {e}")

    def delete_order(self):
        """Xóa đơn hàng với xác nhận"""
        if not self.current_order_id:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", 
                "Không có đơn hàng nào để xóa. Vui lòng chọn đơn hàng từ danh sách.")
            return
        
        # Xác nhận xóa
        reply = QtWidgets.QMessageBox.question(None, "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa đơn hàng {self.label_order_code.text()}?\n"
            "Hành động này không thể hoàn tác!",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        
        if reply != QtWidgets.QMessageBox.Yes:
            return
        
        if not self.db_connection:
            QtWidgets.QMessageBox.critical(None, "Lỗi", "Không có kết nối cơ sở dữ liệu")
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # Xóa chi tiết đơn hàng trước (do khóa ngoại)
            cursor.execute("DELETE FROM ChiTietDonHang WHERE donDatHangId = %s", (self.current_order_id,))
            
            # Xóa đơn hàng
            cursor.execute("DELETE FROM DonDatHang WHERE id = %s", (self.current_order_id,))
            
            self.db_connection.commit()
            cursor.close()
            
            # Reset form
            self.new_order()
            self.load_orders()
            
            QtWidgets.QMessageBox.information(None, "Thành công", "Đã xóa đơn hàng thành công!")
            self.statusbar.showMessage("Đã xóa đơn hàng", 3000)
            
        except Error as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi", f"Lỗi khi xóa đơn hàng:\n{e}")

    def closeEvent(self, event):
        """Xử lý khi đóng form"""
        if hasattr(self, 'db_connection') and self.db_connection:
            try:
                self.db_connection.close()
                print("Database connection closed")
            except:
                pass
        event.accept()

    def search_customer(self):
        """Tìm kiếm khách hàng theo loại được chọn"""
        search_text = self.line_search_customer_DH.text().strip()
        search_type = self.combobox_search_type_DH.currentText()
        
        if not search_text:
            self.load_customers()
            return
        
        self.customer_model.clear()
        self.customer_model.setHorizontalHeaderLabels([
            "ID", "Mã KH", "Tên khách hàng", "Số điện thoại", "Email", "Địa chỉ", "CMND", "Ghi chú"
        ])
        
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # Xác định cột tìm kiếm
            if search_type == "Tên":
                column = "tenKhachHang"
            elif search_type == "Số điện thoại":
                column = "soDienThoai"
            elif search_type == "CMND":
                column = "soCMND"
            else:
                column = "tenKhachHang"
            
            query = f"SELECT id, maKhachHang, tenKhachHang, soDienThoai, email, diaChi, soCMND, ghiChu FROM KhachHang WHERE {column} LIKE %s ORDER BY tenKhachHang"
            cursor.execute(query, (f"%{search_text}%",))
            
            # Thêm dòng đầu tiên để chọn
            empty_row = [QtGui.QStandardItem("") for _ in range(8)]
            empty_row[2] = QtGui.QStandardItem("-- Chọn khách hàng --")
            self.customer_model.appendRow(empty_row)
            
            # Xóa và thêm lại combobox
            self.combobox_customer_DH.clear()
            self.combobox_customer_DH.addItem("-- Chọn khách hàng --")
            
            for row in cursor.fetchall():
                items = []
                for field in row:
                    items.append(QtGui.QStandardItem(str(field) if field is not None else ""))
                self.customer_model.appendRow(items)
                
                # Thêm vào combobox
                self.combobox_customer_DH.addItem(row[2])  # tenKhachHang
            
            cursor.close()
            self.statusbar.showMessage(f"Tìm thấy {self.customer_model.rowCount()-1} khách hàng", 2000)
            
        except Error as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi", f"Lỗi khi tìm kiếm khách hàng:\n{e}")
            print(f"Error searching customers: {e}")

    def load_customers(self):
        """Load danh sách khách hàng"""
        self.customer_model.clear()
        self.customer_model.setHorizontalHeaderLabels([
            "ID", "Mã KH", "Tên khách hàng", "Số điện thoại", "Email", "Địa chỉ", "CMND", "Ghi chú"
        ])
        
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT id, maKhachHang, tenKhachHang, soDienThoai, email, diaChi, soCMND, ghiChu FROM KhachHang ORDER BY tenKhachHang")
            
            # Thêm dòng đầu tiên để chọn
            empty_row = [QtGui.QStandardItem("") for _ in range(8)]
            empty_row[2] = QtGui.QStandardItem("-- Chọn khách hàng --")
            self.customer_model.appendRow(empty_row)
            
            # Xóa và thêm lại combobox
            self.combobox_customer_DH.clear()
            self.combobox_customer_DH.addItem("-- Chọn khách hàng --")
            
            for row in cursor.fetchall():
                items = []
                for field in row:
                    items.append(QtGui.QStandardItem(str(field) if field is not None else ""))
                self.customer_model.appendRow(items)
                
                # Thêm vào combobox
                self.combobox_customer_DH.addItem(row[2])  # tenKhachHang
            
            cursor.close()
        except Error as e:
            print(f"Error loading customers: {e}")

    def add_customer(self):
        """Thêm khách hàng mới"""
        dialog = CustomerDialog(self.db_connection)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.load_customers()
            self.statusbar.showMessage("Đã thêm khách hàng mới", 2000)

    def edit_customer(self):
        """Sửa thông tin khách hàng"""
        if not self.selected_customer_id:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn khách hàng để sửa")
            return
        
        dialog = CustomerDialog(self.db_connection, self.selected_customer_id)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.load_customers()
            self.statusbar.showMessage("Đã cập nhật thông tin khách hàng", 2000)

    def delete_product(self):
        """Xóa sản phẩm khỏi đơn đặt may"""
        selected = self.table_products_DH.currentIndex()
        if not selected.isValid():
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn sản phẩm để xóa!")
            return
        
        product_name = self.product_model.item(selected.row(), 2).text()
        
        # Xác nhận xóa
        reply = QtWidgets.QMessageBox.question(None, "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa {product_name} khỏi đơn đặt may?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.product_model.removeRow(selected.row())
            self.update_total_price()
            self.statusbar.showMessage(f"Đã xóa {product_name} khỏi đơn đặt may", 2000)

    def load_products(self):
        """Load danh sách mẫu sản phẩm có thể đặt may"""
        self.available_products_model.clear()
        self.available_products_model.setHorizontalHeaderLabels([
            "ID", "Mã SP", "Tên sản phẩm", "Loại", "Mô tả", "Giá may", "Hình ảnh"
        ])
        
        if not self.db_connection:
            return
            
        try:
            cursor = self.db_connection.cursor()
            # Chỉ lấy các thông tin cần thiết cho đặt may
            cursor.execute("""
                SELECT id, maSanPham, tenSanPham, loaiSanPham, moTa, giaMay, hinhAnh
                FROM SanPham 
                WHERE giaMay IS NOT NULL AND giaMay > 0
                ORDER BY tenSanPham
            """)
            
            for row in cursor.fetchall():
                items = []
                for i, field in enumerate(row):
                    if i == 5 and field:  # Cột giá may
                        items.append(QtGui.QStandardItem(f"{field:,.0f}"))
                    else:
                        items.append(QtGui.QStandardItem(str(field) if field is not None else ""))
                self.available_products_model.appendRow(items)
            cursor.close()
        except Error as e:
            print(f"Error loading products: {e}")
        
        # Setup selected products model
        self.setup_product_model_headers()

    def search_products(self):
        """Tìm kiếm sản phẩm"""
        search_text = self.line_search_products_DH.text().strip()
        
        if not search_text:
            self.load_products()
            return
        
        self.available_products_model.clear()
        self.available_products_model.setHorizontalHeaderLabels([
            "ID", "Mã SP", "Tên sản phẩm", "Loại", "Mô tả", "Giá may", "Hình ảnh"
        ])
        
        if not self.db_connection:
            return
            
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT id, maSanPham, tenSanPham, loaiSanPham, moTa, giaMay, hinhAnh
                FROM SanPham 
                WHERE (tenSanPham LIKE %s OR maSanPham LIKE %s OR loaiSanPham LIKE %s)
                AND giaMay IS NOT NULL AND giaMay > 0
                ORDER BY tenSanPham
            """, (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"))
            
            for row in cursor.fetchall():
                items = []
                for i, field in enumerate(row):
                    if i == 5 and field:  # Cột giá may
                        items.append(QtGui.QStandardItem(f"{field:,.0f}"))
                    else:
                        items.append(QtGui.QStandardItem(str(field) if field is not None else ""))
                self.available_products_model.appendRow(items)
            cursor.close()
            
            self.statusbar.showMessage(f"Tìm thấy {self.available_products_model.rowCount()} mẫu sản phẩm", 2000)
        except Error as e:
            print(f"Error searching products: {e}")

    def load_orders(self):
        """Load danh sách đơn hàng"""
        self.order_model.clear()
        self.order_model.setHorizontalHeaderLabels([
            "ID", "Mã ĐH", "Khách hàng", "Ngày đặt", "Ngày giao", "Tổng tiền", "Đặt cọc", "Còn lại", "Trạng thái"
        ])
        
        if not self.db_connection:
            return
            
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT d.id, d.maDonHang, k.tenKhachHang, d.ngayDatHang, 
                       d.ngayGiaoHangDuKien, d.tongTien, d.tienDatCoc,
                       (d.tongTien - d.tienDatCoc) as conLai, d.trangThai
                FROM DonDatHang d
                JOIN KhachHang k ON d.khachHangId = k.id
                ORDER BY d.ngayDatHang DESC
            """)
            for row in cursor.fetchall():
                items = []
                for i, field in enumerate(row):
                    if i in [5, 6, 7] and field:  # Các cột tiền
                        items.append(QtGui.QStandardItem(f"{field:,.0f}"))
                    elif field is not None:
                        items.append(QtGui.QStandardItem(str(field)))
                    else:
                        items.append(QtGui.QStandardItem(""))
                self.order_model.appendRow(items)
            cursor.close()
        except Error as e:
            print(f"Error loading orders: {e}")

    def on_order_selected(self):
        """Xử lý khi chọn đơn hàng từ danh sách"""
        selected = self.table_listOrder_DH.currentIndex()
        if not selected.isValid():
            return
        
        order_id = self.order_model.item(selected.row(), 0).text()
        order_code = self.order_model.item(selected.row(), 1).text()
        self.load_order_details(order_id, order_code)

    def load_order_details(self, order_id, order_code):
        """Load chi tiết đơn hàng"""
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # Load order info
            cursor.execute("""
                SELECT d.*, k.tenKhachHang
                FROM DonDatHang d
                JOIN KhachHang k ON d.khachHangId = k.id
                WHERE d.id = %s
            """, (order_id,))
            
            order_info = cursor.fetchone()
            if not order_info:
                return
            
            # Update form with order info
            self.current_order_id = int(order_id)
            self.label_order_code.setText(order_info[1])
            self.selected_customer_id = order_info[2]
            
            # Set customer in combobox
            customer_name = order_info[-1]
            for i in range(self.combobox_customer_DH.count()):
                if self.combobox_customer_DH.itemText(i) == customer_name:
                    self.combobox_customer_DH.setCurrentIndex(i)
                    break
            
            # Set dates and amounts
            if order_info[4]:  # ngayDatHang
                self.label_create_date.setText(order_info[4].strftime("%d/%m/%Y %H:%M"))
            if order_info[5]:  # ngayGiaoHangDuKien
                self.edit_date_finish_DH.setDate(QtCore.QDate.fromString(
                    order_info[5].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            self.line_total_price.setText(f"{order_info[6]:,.0f}")
            self.line_deposit.setText(str(int(order_info[7])) if order_info[7] else "0")
            
            # Load order details
            cursor.execute("""
                SELECT ct.*, sp.maSanPham, sp.tenSanPham, sp.loaiSanPham, 
                       sp.moTa, sp.hinhAnh
                FROM ChiTietDonHang ct
                JOIN SanPham sp ON ct.sanPhamId = sp.id
                WHERE ct.donDatHangId = %s
            """, (order_id,))
            
            # Clear and populate product model
            self.product_model.clear()
            self.setup_product_model_headers()
            
            for detail in cursor.fetchall():
                items = [
                    QtGui.QStandardItem(str(detail[2])),      # sanPhamId
                    QtGui.QStandardItem(detail[6] or ""),     # maSanPham
                    QtGui.QStandardItem(detail[7] or ""),     # tenSanPham
                    QtGui.QStandardItem(detail[8] or ""),     # loaiSanPham
                    QtGui.QStandardItem(detail[9] or ""),     # moTa
                    QtGui.QStandardItem(f"{detail[4]:,.0f}"), # giaBan
                    QtGui.QStandardItem(detail[10] or ""),    # hinhAnh
                    QtGui.QStandardItem(str(detail[3])),      # soLuong
                    QtGui.QStandardItem(f"{detail[5]:,.0f}")  # thanhTien
                ]
                self.product_model.appendRow(items)
            
            cursor.close()
            self.calculate_remaining()
            self.statusbar.showMessage(f"Đã load đơn hàng {order_code}", 2000)
            
        except Error as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi", f"Lỗi khi load chi tiết đơn hàng:\n{e}")
            print(f"Error loading order details: {e}")

    def setup_product_model_headers(self):
        """Thiết lập header cho bảng sản phẩm đã chọn"""
        self.product_model.setHorizontalHeaderLabels([
            "ID", "Mã SP", "Tên sản phẩm", "Loại", "Mô tả", "Giá may", "Hình ảnh", "Số lượng", "Thành tiền"
        ])

    def get_customer_info(self, customer_id):
        """Lấy thông tin khách hàng"""
        if not self.db_connection or not customer_id:
            return None
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT tenKhachHang, soDienThoai, diaChi, email, soCMND
                FROM KhachHang WHERE id = %s
            """, (customer_id,))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    'ten': result[0],
                    'sdt': result[1],
                    'dia_chi': result[2],
                    'email': result[3],
                    'cmnd': result[4]
                }
            return None
        except Error as e:
            print(f"Error getting customer info: {e}")
            return None

    def generate_print_content(self):
        """Tạo nội dung HTML cho phiếu đặt may"""
        customer_info = self.get_customer_info(self.selected_customer_id)
        
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
            </style>
        </head>
        <body>
            <div class="header">
                <div class="company-name">XƯỞNG MAY ABC</div>
                <div>Địa chỉ: 123 Đường ABC, Quận XYZ, TP.HCM</div>
                <div>Điện thoại: (028) 1234-5678 | Email: info@xuongmay.com</div>
                <div class="document-title">PHIẾU ĐẶT MAY</div>
            </div>
            
            <div class="info-section">
                <div class="info-row">
                    <span class="label">Mã đơn đặt may:</span>
                    <span style="font-weight: bold; color: #007bff;">{self.label_order_code.text()}</span>
                </div>
                <div class="info-row">
                    <span class="label">Ngày đặt:</span>
                    <span>{self.label_create_date.text()}</span>
                </div>
                <div class="info-row">
                    <span class="label">Ngày giao dự kiến:</span>
                    <span>{self.edit_date_finish_DH.date().toString("dd/MM/yyyy")}</span>
                </div>
            </div>
            
            <div class="info-section">
                <h3>THÔNG TIN KHÁCH HÀNG</h3>
                <div class="info-row">
                    <span class="label">Tên khách hàng:</span>
                    <span>{customer_info['ten'] if customer_info else ''}</span>
                </div>
                <div class="info-row">
                    <span class="label">Số điện thoại:</span>
                    <span>{customer_info['sdt'] if customer_info else ''}</span>
                </div>
                <div class="info-row">
                    <span class="label">Địa chỉ:</span>
                    <span>{customer_info['dia_chi'] if customer_info else ''}</span>
                </div>
            </div>
            
            <div class="info-section">
                <h3>DANH SÁCH SẢN PHẨM ĐẶT MAY</h3>
                <table>
                    <thead>
                        <tr>
                            <th>STT</th>
                            <th>Mã SP</th>
                            <th>Tên sản phẩm</th>
                            <th>Loại</th>
                            <th>Số lượng</th>
                            <th>Giá may (VNĐ)</th>
                            <th>Thành tiền (VNĐ)</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Thêm danh sách sản phẩm
        for row in range(self.product_model.rowCount()):
            ma_sp = self.product_model.item(row, 1).text()
            ten_sp = self.product_model.item(row, 2).text()
            loai = self.product_model.item(row, 3).text()
            so_luong = self.product_model.item(row, 7).text()
            gia_may = float(self.product_model.item(row, 5).text().replace(',', ''))
            thanh_tien = float(self.product_model.item(row, 8).text().replace(',', ''))
            
            html_content += f"""
                        <tr>
                            <td>{row + 1}</td>
                            <td>{ma_sp}</td>
                            <td>{ten_sp}</td>
                            <td>{loai}</td>
                            <td>{so_luong}</td>
                            <td>{gia_may:,.0f}</td>
                            <td>{thanh_tien:,.0f}</td>
                        </tr>
            """
        
        total_amount = self.line_total_price.text()
        deposit_amount = self.line_deposit.text() or "0"
        remaining_amount = self.line_remaining.text()
        
        html_content += f"""
                    </tbody>
                </table>
            </div>
            
            <div class="total-section">
                <div class="total-row">
                    <span class="label">Tổng tiền:</span>
                    <span style="font-weight: bold; font-size: 16px;">{total_amount}</span>
                </div>
                <div class="total-row">
                    <span class="label">Tiền đặt cọc:</span>
                    <span>{deposit_amount} VNĐ</span>
                </div>
                <div class="total-row">
                    <span class="label">Còn lại:</span>
                    <span style="font-weight: bold;">{remaining_amount}</span>
                </div>
            </div>
            
            <div class="signature-section">
                <div class="signature">
                    <div style="font-weight: bold;">KHÁCH HÀNG</div>
                    <div style="margin-top: 50px;">(Ký và ghi rõ họ tên)</div>
                </div>
                <div class="signature">
                    <div style="font-weight: bold;">NHÂN VIÊN</div>
                    <div style="margin-top: 50px;">(Ký và ghi rõ họ tên)</div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content

    def retranslateUi(self, DHWindow):
        """Thiết lập text cho các widget"""
        _translate = QtCore.QCoreApplication.translate
        DHWindow.setWindowTitle(_translate("DHWindow", "Quản lý đặt hàng"))

# Dialog class cho quản lý khách hàng
class CustomerDialog(QtWidgets.QDialog):
    def __init__(self, db_connection, customer_id=None):
        super().__init__
        self.db_connection = db_connection
        self.customer_id = customer_id
        self.setupUi()
        
        if customer_id:
            self.load_customer_data()
    
    def setupUi(self):
        self.setWindowTitle("Thông tin khách hàng")
        self.resize(400, 300)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Form fields
        form_layout = QtWidgets.QFormLayout()
        
        self.line_ten = QtWidgets.QLineEdit()
        self.line_sdt = QtWidgets.QLineEdit()
        self.line_email = QtWidgets.QLineEdit()
        self.line_diachi = QtWidgets.QLineEdit()
        self.line_cmnd = QtWidgets.QLineEdit()
        self.text_ghichu = QtWidgets.QTextEdit()
        self.text_ghichu.setMaximumHeight(60)
        
        form_layout.addRow("Tên khách hàng:", self.line_ten)
        form_layout.addRow("Số điện thoại:", self.line_sdt)
        form_layout.addRow("Email:", self.line_email)
        form_layout.addRow("Địa chỉ:", self.line_diachi)
        form_layout.addRow("CMND:", self.line_cmnd)
        form_layout.addRow("Ghi chú:", self.text_ghichu)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.btn_save = QtWidgets.QPushButton("Lưu")
        self.btn_cancel = QtWidgets.QPushButton("Hủy")
        
        self.btn_save.clicked.connect(self.save_customer)
        self.btn_cancel.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_cancel)
        layout.addLayout(button_layout)
    
    def load_customer_data(self):
        """Load dữ liệu khách hàng để sửa"""
        if not self.db_connection or not self.customer_id:
            return
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT tenKhachHang, soDienThoai, email, diaChi, soCMND, ghiChu
                FROM KhachHang WHERE id = %s
            """, (self.customer_id,))
            
            result = cursor.fetchone()
            if result:
                self.line_ten.setText(result[0] or "")
                self.line_sdt.setText(result[1] or "")
                self.line_email.setText(result[2] or "")
                self.line_diachi.setText(result[3] or "")
                self.line_cmnd.setText(result[4] or "")
                self.text_ghichu.setText(result[5] or "")
            cursor.close()
        except Error as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi", f"Lỗi khi load dữ liệu khách hàng:\n{e}")
    
    def save_customer(self):
        """Lưu thông tin khách hàng"""
        if not self.line_ten.text().strip():
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập tên khách hàng")
            return
        
        if not self.line_sdt.text().strip():
            QtWidgets.QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập số điện thoại")
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            if self.customer_id:  # Update
                cursor.execute("""
                    UPDATE KhachHang 
                    SET tenKhachHang = %s, soDienThoai = %s, email = %s, 
                        diaChi = %s, soCMND = %s, ghiChu = %s
                    WHERE id = %s
                """, (
                    self.line_ten.text().strip(),
                    self.line_sdt.text().strip(),
                    self.line_email.text().strip(),
                    self.line_diachi.text().strip(),
                    self.line_cmnd.text().strip(),
                    self.text_ghichu.toPlainText().strip(),
                    self.customer_id
                ))
            else:  # Insert
                # Generate customer code
                ma_kh = f"KH{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:4].upper()}"
                cursor.execute("""
                    INSERT INTO KhachHang (maKhachHang, tenKhachHang, soDienThoai, email, diaChi, soCMND, ghiChu)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    ma_kh,
                    self.line_ten.text().strip(),
                    self.line_sdt.text().strip(),
                    self.line_email.text().strip(),
                    self.line_diachi.text().strip(),
                    self.line_cmnd.text().strip(),
                    self.text_ghichu.toPlainText().strip()
                ))
            
            self.db_connection.commit()
            cursor.close()
            
            QtWidgets.QMessageBox.information(self, "Thành công", 
                "Đã lưu thông tin khách hàng thành công!")
            self.accept()
            
        except Error as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi", f"Lỗi khi lưu khách hàng:\n{e}")