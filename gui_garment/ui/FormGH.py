from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtPrintSupport
import pymysql as mysql
from pymysql import Error
from datetime import datetime, date
import uuid

class Ui_GHWindow(object):
    def __init__(self):
        self.db_connection = None
        self.selected_order_id = None
        self.selected_delivery_id = None
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

    def setupUi(self, GHWindow):
        GHWindow.setObjectName("GHWindow")
        GHWindow.resize(1600, 900)
        GHWindow.setMinimumSize(1400, 800)
        
        # Set modern style
        self.setup_styles(GHWindow)
        
        self.centralwidget = QtWidgets.QWidget(GHWindow)
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
        
        # Left panel - Order search and list
        left_panel = self.setup_order_search_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Order details and status
        right_panel = self.setup_order_details_panel()
        content_splitter.addWidget(right_panel)
        
        # Bottom panel - Delivery management
        bottom_panel = self.setup_delivery_management_panel()
        main_layout.addWidget(bottom_panel)
        
        # Set splitter proportions
        content_splitter.setSizes([600, 1000])

        GHWindow.setCentralWidget(self.centralwidget)
        
        # Setup menubar and statusbar
        self.setup_menubar(GHWindow)
        self.setup_statusbar(GHWindow)

        self.retranslateUi(GHWindow)
        self.setup_models()
        QtCore.QMetaObject.connectSlotsByName(GHWindow)

    def setup_styles(self, GHWindow):
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
        
        QPushButton.warning-btn {
            background-color: #ffc107;
            color: #212529;
        }
        
        QPushButton.warning-btn:hover {
            background-color: #e0a800;
        }
        
        QPushButton.info-btn {
            background-color: #17a2b8;
        }
        
        QPushButton.info-btn:hover {
            background-color: #138496;
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
        
        QLineEdit, QComboBox, QDateEdit, QTextEdit {
            padding: 8px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            background-color: white;
        }
        
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
            border: 2px solid #007bff;
            outline: none;
        }
        
        QLineEdit:read-only, QTextEdit:read-only {
            background-color: #f8f9fa;
        }
        
        QLabel {
            color: #495057;
        }
        """
        GHWindow.setStyleSheet(style)

    def setup_header(self, layout):
        """Thiết lập header"""
        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        
        # Title
        title_label = QtWidgets.QLabel("QUẢN LÝ GIAO HÀNG & TRẠNG THÁI ĐƠN HÀNG")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_font = QtGui.QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #007bff; margin: 10px;")
        
        # Statistics
        stats_widget = QtWidgets.QWidget()
        stats_layout = QtWidgets.QGridLayout(stats_widget)
        
        # Tổng phiếu giao hàng
        stats_layout.addWidget(QtWidgets.QLabel("Tổng phiếu GH:"), 0, 0)
        self.label_total_deliveries = QtWidgets.QLabel("0")
        self.label_total_deliveries.setStyleSheet("font-weight: bold; color: #007bff; font-size: 14px;")
        stats_layout.addWidget(self.label_total_deliveries, 0, 1)
        
        # Đang giao
        stats_layout.addWidget(QtWidgets.QLabel("Đang giao:"), 0, 2)
        self.label_shipping_orders = QtWidgets.QLabel("0")
        self.label_shipping_orders.setStyleSheet("font-weight: bold; color: #fd7e14; font-size: 14px;")
        stats_layout.addWidget(self.label_shipping_orders, 0, 3)
        
        # Đã giao thành công
        stats_layout.addWidget(QtWidgets.QLabel("Đã giao:"), 1, 0)
        self.label_completed_orders = QtWidgets.QLabel("0")
        self.label_completed_orders.setStyleSheet("font-weight: bold; color: #28a745; font-size: 14px;")
        stats_layout.addWidget(self.label_completed_orders, 1, 1)
        
        # Giao không thành công
        stats_layout.addWidget(QtWidgets.QLabel("Giao thất bại:"), 1, 2)
        self.label_failed_orders = QtWidgets.QLabel("0")
        self.label_failed_orders.setStyleSheet("font-weight: bold; color: #dc3545; font-size: 14px;")
        stats_layout.addWidget(self.label_failed_orders, 1, 3)
        
        header_layout.addWidget(title_label, 2)
        header_layout.addWidget(stats_widget, 1)
        
        layout.addWidget(header_widget)

    def setup_order_search_panel(self):
        """Thiết lập panel tìm kiếm phiếu giao hàng"""
        search_group = QtWidgets.QGroupBox("Tìm kiếm & Danh sách phiếu giao hàng")
        search_layout = QtWidgets.QVBoxLayout(search_group)
        
        # Search section
        search_widget = QtWidgets.QWidget()
        search_form_layout = QtWidgets.QGridLayout(search_widget)
        
        # Tìm kiếm theo mã phiếu
        search_form_layout.addWidget(QtWidgets.QLabel("Mã phiếu GH:"), 0, 0)
        self.line_search_delivery_code = QtWidgets.QLineEdit()
        self.line_search_delivery_code.setPlaceholderText("Nhập mã phiếu giao hàng...")
        search_form_layout.addWidget(self.line_search_delivery_code, 0, 1)
        
        # Tìm kiếm theo khách hàng
        search_form_layout.addWidget(QtWidgets.QLabel("Khách hàng:"), 0, 2)
        self.line_search_customer = QtWidgets.QLineEdit()
        self.line_search_customer.setPlaceholderText("Nhập tên khách hàng...")
        search_form_layout.addWidget(self.line_search_customer, 0, 3)
        
        # Lọc theo trạng thái giao hàng
        search_form_layout.addWidget(QtWidgets.QLabel("Trạng thái GH:"), 1, 0)
        self.combobox_status_filter = QtWidgets.QComboBox()
        self.combobox_status_filter.addItems([
            "Tất cả", "Chờ giao", "Đang giao", "Đã giao", "Giao không thành công"
        ])
        search_form_layout.addWidget(self.combobox_status_filter, 1, 1)
        
        # Lọc theo thời gian
        search_form_layout.addWidget(QtWidgets.QLabel("Từ ngày:"), 1, 2)
        self.date_from = QtWidgets.QDateEdit()
        self.date_from.setDate(QtCore.QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        search_form_layout.addWidget(self.date_from, 1, 3)
        
        search_form_layout.addWidget(QtWidgets.QLabel("Đến ngày:"), 2, 0)
        self.date_to = QtWidgets.QDateEdit()
        self.date_to.setDate(QtCore.QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        search_form_layout.addWidget(self.date_to, 2, 1)
        
        # Search buttons
        btn_search = QtWidgets.QPushButton("Tìm kiếm")
        btn_search.clicked.connect(self.search_deliveries)
        search_form_layout.addWidget(btn_search, 2, 2)
        
        btn_refresh = QtWidgets.QPushButton("Làm mới")
        btn_refresh.clicked.connect(self.refresh_deliveries)
        search_form_layout.addWidget(btn_refresh, 2, 3)
        
        search_layout.addWidget(search_widget)
        
        # Deliveries table
        search_layout.addWidget(QtWidgets.QLabel("Danh sách phiếu giao hàng:"))
        self.table_deliveries = QtWidgets.QTableView()
        self.table_deliveries.setMinimumHeight(300)
        self.table_deliveries.clicked.connect(self.on_delivery_selected)
        self.table_deliveries.doubleClicked.connect(self.view_delivery_details)
        search_layout.addWidget(self.table_deliveries)
        
        # Quick action buttons
        quick_actions_widget = QtWidgets.QWidget()
        quick_actions_layout = QtWidgets.QHBoxLayout(quick_actions_widget)
        
        self.btn_view_details = QtWidgets.QPushButton("Xem chi tiết")
        self.btn_view_details.setProperty("class", "info-btn")
        self.btn_view_details.clicked.connect(self.view_delivery_details)
        
        self.btn_update_status = QtWidgets.QPushButton("Cập nhật trạng thái")
        self.btn_update_status.setProperty("class", "warning-btn")
        self.btn_update_status.clicked.connect(self.update_delivery_status)
        
        self.btn_print_delivery = QtWidgets.QPushButton("In phiếu giao hàng")
        self.btn_print_delivery.clicked.connect(self.print_delivery_note)
        
        quick_actions_layout.addWidget(self.btn_view_details)
        quick_actions_layout.addWidget(self.btn_update_status)
        quick_actions_layout.addWidget(self.btn_print_delivery)
        quick_actions_layout.addStretch()
        
        search_layout.addWidget(quick_actions_widget)
        
        return search_group

    def setup_order_details_panel(self):
        """Thiết lập panel chi tiết phiếu giao hàng"""
        details_group = QtWidgets.QGroupBox("Chi tiết phiếu giao hàng")
        details_layout = QtWidgets.QVBoxLayout(details_group)
        
        # Delivery info section
        delivery_info_widget = QtWidgets.QWidget()
        delivery_info_layout = QtWidgets.QGridLayout(delivery_info_widget)
        
        # Basic delivery info
        delivery_info_layout.addWidget(QtWidgets.QLabel("Mã phiếu GH:"), 0, 0)
        self.label_delivery_code = QtWidgets.QLabel("-")
        self.label_delivery_code.setStyleSheet("font-weight: bold; color: #007bff;")
        delivery_info_layout.addWidget(self.label_delivery_code, 0, 1)
        
        delivery_info_layout.addWidget(QtWidgets.QLabel("Mã đơn hàng:"), 0, 2)
        self.label_order_code = QtWidgets.QLabel("-")
        delivery_info_layout.addWidget(self.label_order_code, 0, 3)
        
        delivery_info_layout.addWidget(QtWidgets.QLabel("Ngày giao:"), 1, 0)
        self.label_delivery_date = QtWidgets.QLabel("-")
        delivery_info_layout.addWidget(self.label_delivery_date, 1, 1)
        
        delivery_info_layout.addWidget(QtWidgets.QLabel("Người nhận:"), 1, 2)
        self.label_receiver_name = QtWidgets.QLabel("-")
        delivery_info_layout.addWidget(self.label_receiver_name, 1, 3)
        
        delivery_info_layout.addWidget(QtWidgets.QLabel("Trạng thái GH:"), 2, 0)
        self.label_delivery_status = QtWidgets.QLabel("-")
        delivery_info_layout.addWidget(self.label_delivery_status, 2, 1)
        
        delivery_info_layout.addWidget(QtWidgets.QLabel("SĐT người nhận:"), 2, 2)
        self.label_receiver_phone = QtWidgets.QLabel("-")
        delivery_info_layout.addWidget(self.label_receiver_phone, 2, 3)
        
        details_layout.addWidget(delivery_info_widget)
        
        # Delivery address info
        address_group = QtWidgets.QGroupBox("Thông tin giao hàng")
        address_layout = QtWidgets.QGridLayout(address_group)
        
        address_layout.addWidget(QtWidgets.QLabel("Địa chỉ giao hàng:"), 0, 0)
        self.text_delivery_address = QtWidgets.QTextEdit()
        self.text_delivery_address.setMaximumHeight(60)
        self.text_delivery_address.setReadOnly(True)
        address_layout.addWidget(self.text_delivery_address, 0, 1, 1, 3)
        
        address_layout.addWidget(QtWidgets.QLabel("Ghi chú:"), 1, 0)
        self.text_delivery_note = QtWidgets.QTextEdit()
        self.text_delivery_note.setMaximumHeight(60)
        self.text_delivery_note.setReadOnly(True)
        address_layout.addWidget(self.text_delivery_note, 1, 1, 1, 3)
        
        details_layout.addWidget(address_group)
        
        # Products in delivery
        products_group = QtWidgets.QGroupBox("Sản phẩm giao hàng")
        products_layout = QtWidgets.QVBoxLayout(products_group)
        
        self.table_delivery_products = QtWidgets.QTableView()
        self.table_delivery_products.setMaximumHeight(200)
        products_layout.addWidget(self.table_delivery_products)
        
        details_layout.addWidget(products_group)
        
        return details_group

    def setup_delivery_management_panel(self):
        """Thiết lập panel quản lý giao hàng"""
        delivery_group = QtWidgets.QGroupBox("Quản lý giao hàng")
        delivery_layout = QtWidgets.QHBoxLayout(delivery_group)
        
        # Status update section
        status_widget = QtWidgets.QWidget()
        status_layout = QtWidgets.QVBoxLayout(status_widget)
        
        status_form_widget = QtWidgets.QWidget()
        status_form_layout = QtWidgets.QGridLayout(status_form_widget)
        
        status_form_layout.addWidget(QtWidgets.QLabel("Cập nhật trạng thái:"), 0, 0)
        self.combobox_new_status = QtWidgets.QComboBox()
        self.combobox_new_status.addItems([
            "Chờ giao", "Đang giao", "Đã giao", "Giao không thành công"
        ])
        status_form_layout.addWidget(self.combobox_new_status, 0, 1)
        
        status_form_layout.addWidget(QtWidgets.QLabel("Ngày cập nhật:"), 1, 0)
        self.date_status_update = QtWidgets.QDateEdit()
        self.date_status_update.setDate(QtCore.QDate.currentDate())
        self.date_status_update.setCalendarPopup(True)
        status_form_layout.addWidget(self.date_status_update, 1, 1)
        
        status_form_layout.addWidget(QtWidgets.QLabel("Ghi chú:"), 2, 0)
        self.text_status_note = QtWidgets.QTextEdit()
        self.text_status_note.setMaximumHeight(80)
        self.text_status_note.setPlaceholderText("Nhập ghi chú về trạng thái...")
        status_form_layout.addWidget(self.text_status_note, 2, 1)
        
        # Update button
        self.btn_confirm_status_update = QtWidgets.QPushButton("Xác nhận cập nhật")
        self.btn_confirm_status_update.setProperty("class", "save-btn")
        self.btn_confirm_status_update.clicked.connect(self.confirm_status_update)
        status_form_layout.addWidget(self.btn_confirm_status_update, 3, 0, 1, 2)
        
        status_layout.addWidget(status_form_widget)
        
        # Action buttons
        actions_widget = QtWidgets.QWidget()
        actions_layout = QtWidgets.QVBoxLayout(actions_widget)
        
        self.btn_create_delivery = QtWidgets.QPushButton("Tạo phiếu giao hàng")
        self.btn_create_delivery.setProperty("class", "save-btn")
        self.btn_create_delivery.clicked.connect(self.create_delivery_note)
        
        self.btn_assign_delivery = QtWidgets.QPushButton("Phân công giao hàng")
        self.btn_assign_delivery.setProperty("class", "info-btn")
        self.btn_assign_delivery.clicked.connect(self.assign_delivery_staff)
        
        self.btn_complete_delivery = QtWidgets.QPushButton("Hoàn thành giao hàng")
        self.btn_complete_delivery.setProperty("class", "save-btn")
        self.btn_complete_delivery.clicked.connect(self.complete_delivery)
        
        self.btn_fail_delivery = QtWidgets.QPushButton("Giao hàng thất bại")
        self.btn_fail_delivery.setProperty("class", "delete-btn")
        self.btn_fail_delivery.clicked.connect(self.fail_delivery)
        
        actions_layout.addWidget(self.btn_create_delivery)
        actions_layout.addWidget(self.btn_assign_delivery)
        actions_layout.addWidget(self.btn_complete_delivery)
        actions_layout.addWidget(self.btn_fail_delivery)
        actions_layout.addStretch()
        
        delivery_layout.addWidget(status_widget, 2)
        delivery_layout.addWidget(actions_widget, 1)
        
        return delivery_group

    def setup_menubar(self, GHWindow):
        """Thiết lập menu bar"""
        self.menubar = QtWidgets.QMenuBar(GHWindow)
        GHWindow.setMenuBar(self.menubar)

    def setup_statusbar(self, GHWindow):
        """Thiết lập status bar"""
        self.statusbar = QtWidgets.QStatusBar(GHWindow)
        self.statusbar.showMessage("Sẵn sàng")
        GHWindow.setStatusBar(self.statusbar)

    def setup_models(self):
        """Thiết lập các model cho table views"""
        # Deliveries model
        self.deliveries_model = QtGui.QStandardItemModel()
        self.deliveries_model.setHorizontalHeaderLabels([
            "ID", "Mã phiếu GH", "Mã đơn hàng", "Khách hàng", "Ngày giao", 
            "Trạng thái GH", "Người nhận", "SĐT", "Địa chỉ"
        ])
        self.table_deliveries.setModel(self.deliveries_model)
        # Hide ID column
        self.table_deliveries.setColumnHidden(0, True)
        
        # Delivery products model
        self.delivery_products_model = QtGui.QStandardItemModel()
        self.delivery_products_model.setHorizontalHeaderLabels([
            "Tên sản phẩm", "Loại", "Size", "Màu", "Số lượng giao"
        ])
        self.table_delivery_products.setModel(self.delivery_products_model)
        
        # Set table properties
        for table in [self.table_deliveries, self.table_delivery_products]:
            table.setAlternatingRowColors(True)
            table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            table.verticalHeader().setDefaultSectionSize(30)
            table.horizontalHeader().setStretchLastSection(True)
        
        # Load initial data
        self.load_deliveries()
        self.update_statistics()

    def load_deliveries(self):
        """Load deliveries from database"""
        self.deliveries_model.clear()
        self.deliveries_model.setHorizontalHeaderLabels([
            "ID", "Mã phiếu GH", "Mã đơn hàng", "Khách hàng", "Ngày giao", 
            "Trạng thái GH", "Người nhận", "SĐT", "Địa chỉ"
        ])
        
        if not self.db_connection:
            return
            
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT p.id, p.maPhieu, d.maDonHang, k.tenKhachHang, p.ngayGiao,
                       p.trangThai, p.nguoiNhan, p.sdtNguoiNhan, p.diaChiGiao
                FROM PhieuGiaoHang p
                JOIN DonDatHang d ON p.donDatHangId = d.id
                JOIN KhachHang k ON d.khachHangId = k.id
                ORDER BY p.ngayGiao DESC
            """)
            
            for row in cursor.fetchall():
                items = []
                for i, field in enumerate(row):
                    if i == 5:  # Status column
                        item = QtGui.QStandardItem(str(field))
                        item.setData(self.get_delivery_status_style(str(field)), QtCore.Qt.BackgroundColorRole)
                    else:
                        item = QtGui.QStandardItem(str(field) if field else "")
                    items.append(item)
                self.deliveries_model.appendRow(items)
            
            cursor.close()
            
        except Error as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi", f"Lỗi khi tải danh sách phiếu giao hàng: {e}")

    def get_delivery_status_style(self, status):
        """Get background color for delivery status"""
        status_colors = {
            "Chờ giao": QtGui.QColor("#ffc107"),
            "Đang giao": QtGui.QColor("#fd7e14"),
            "Đã giao": QtGui.QColor("#28a745"),
            "Giao không thành công": QtGui.QColor("#dc3545")
        }
        return status_colors.get(status, QtGui.QColor("#6c757d"))

    def search_deliveries(self):
        """Search deliveries based on criteria"""
        delivery_code = self.line_search_delivery_code.text().strip()
        customer_name = self.line_search_customer.text().strip()
        status_filter = self.combobox_status_filter.currentText()
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        
        if not self.db_connection:
            return
            
        try:
            cursor = self.db_connection.cursor()
            query = """
                SELECT p.id, p.maPhieu, d.maDonHang, k.tenKhachHang, p.ngayGiao,
                       p.trangThai, p.nguoiNhan, p.sdtNguoiNhan, p.diaChiGiao
                FROM PhieuGiaoHang p
                JOIN DonDatHang d ON p.donDatHangId = d.id
                JOIN KhachHang k ON d.khachHangId = k.id
                WHERE 1=1
            """
            params = []
            
            if delivery_code:
                query += " AND p.maPhieu LIKE %s"
                params.append(f"%{delivery_code}%")
            
            if customer_name:
                query += " AND k.tenKhachHang LIKE %s"
                params.append(f"%{customer_name}%")
            
            if status_filter != "Tất cả":
                query += " AND p.trangThai = %s"
                params.append(status_filter)
            
            query += " AND DATE(p.ngayGiao) BETWEEN %s AND %s"
            params.extend([date_from, date_to])
            
            query += " ORDER BY p.ngayGiao DESC"
            
            cursor.execute(query, params)
            
            self.deliveries_model.clear()
            self.deliveries_model.setHorizontalHeaderLabels([
                "ID", "Mã phiếu GH", "Mã đơn hàng", "Khách hàng", "Ngày giao", 
                "Trạng thái GH", "Người nhận", "SĐT", "Địa chỉ"
            ])
            
            for row in cursor.fetchall():
                items = []
                for i, field in enumerate(row):
                    if i == 5:  # Status column
                        item = QtGui.QStandardItem(str(field))
                        item.setData(self.get_delivery_status_style(str(field)), QtCore.Qt.BackgroundColorRole)
                    else:
                        item = QtGui.QStandardItem(str(field) if field else "")
                    items.append(item)
                self.deliveries_model.appendRow(items)
            
            cursor.close()
            self.statusbar.showMessage(f"Tìm thấy {self.deliveries_model.rowCount()} phiếu giao hàng", 3000)
            
        except Error as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi", f"Lỗi khi tìm kiếm: {e}")

    def refresh_deliveries(self):
        """Refresh deliveries list"""
        self.line_search_delivery_code.clear()
        self.line_search_customer.clear()
        self.combobox_status_filter.setCurrentIndex(0)
        self.load_deliveries()
        self.update_statistics()
        self.statusbar.showMessage("Đã làm mới danh sách phiếu giao hàng", 2000)

    def on_delivery_selected(self):
        """Handle delivery selection"""
        selected = self.table_deliveries.currentIndex()
        if not selected.isValid():
            return
            
        self.selected_delivery_id = self.deliveries_model.item(selected.row(), 0).text()
        self.load_delivery_details(self.selected_delivery_id)

    def load_delivery_details(self, delivery_id):
        """Load detailed information of selected delivery"""
        if not self.db_connection or not delivery_id:
            return
            
        try:
            cursor = self.db_connection.cursor()
            
            # Load delivery info
            cursor.execute("""
                SELECT p.maPhieu, d.maDonHang, p.ngayGiao, p.nguoiNhan,
                       p.trangThai, p.sdtNguoiNhan, p.diaChiGiao, p.ghiChu
                FROM PhieuGiaoHang p
                JOIN DonDatHang d ON p.donDatHangId = d.id
                WHERE p.id = %s
            """, (delivery_id,))
            
            delivery_info = cursor.fetchone()
            if delivery_info:
                self.label_delivery_code.setText(delivery_info[0])
                self.label_order_code.setText(delivery_info[1])
                self.label_delivery_date.setText(str(delivery_info[2]))
                self.label_receiver_name.setText(delivery_info[3] or "")
                self.label_delivery_status.setText(delivery_info[4])
                self.label_delivery_status.setStyleSheet(f"color: white; padding: 4px 8px; border-radius: 4px; background-color: {self.get_delivery_status_style(delivery_info[4]).name()};")
                self.label_receiver_phone.setText(delivery_info[5] or "")
                self.text_delivery_address.setText(delivery_info[6] or "")
                self.text_delivery_note.setText(delivery_info[7] or "")
            
            # Load delivery products
            cursor.execute("""
                SELECT sp.tenSanPham, sp.loaiSanPham, sp.mauSac, ct.soLuongGiao
                FROM ChiTietGiaoHang ct
                JOIN SanPham sp ON ct.sanPhamId = sp.id
                WHERE ct.phieuGiaoHangId = %s
            """, (delivery_id,))
            
            self.delivery_products_model.clear()
            self.delivery_products_model.setHorizontalHeaderLabels([
                "Tên sản phẩm", "Loại", "Size", "Màu", "Số lượng giao"
            ])
            
            for row in cursor.fetchall():
                items = [QtGui.QStandardItem(str(field) if field else "") for field in row]
                self.delivery_products_model.appendRow(items)
            
            cursor.close()
            
        except Error as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi", f"Lỗi khi tải chi tiết phiếu giao hàng: {e}")

    def update_statistics(self):
        """Update delivery statistics"""
        if not self.db_connection:
            return
            
        try:
            cursor = self.db_connection.cursor()
            
            # Total deliveries
            cursor.execute("SELECT COUNT(*) FROM PhieuGiaoHang")
            total = cursor.fetchone()[0]
            self.label_total_deliveries.setText(str(total))
            
            # Shipping deliveries
            cursor.execute("SELECT COUNT(*) FROM PhieuGiaoHang WHERE trangThai = 'Đang giao'")
            shipping = cursor.fetchone()[0]
            self.label_shipping_orders.setText(str(shipping))
            
            # Completed deliveries
            cursor.execute("SELECT COUNT(*) FROM PhieuGiaoHang WHERE trangThai = 'Đã giao'")
            completed = cursor.fetchone()[0]
            self.label_completed_orders.setText(str(completed))
            
            # Failed deliveries
            cursor.execute("SELECT COUNT(*) FROM PhieuGiaoHang WHERE trangThai = 'Giao không thành công'")
            failed = cursor.fetchone()[0]
            self.label_failed_orders.setText(str(failed))
            
            cursor.close()
            
        except Error as e:
            print(f"Error updating statistics: {e}")

    def view_delivery_details(self):
        """View detailed delivery information in dialog"""
        if not self.selected_delivery_id:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn một phiếu giao hàng")
            return
            
        # Create detailed view dialog
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle(f"Chi tiết phiếu giao hàng - {self.label_delivery_code.text()}")
        dialog.resize(900, 700)
        dialog.setModal(True)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Delivery information
        info_group = QtWidgets.QGroupBox("Thông tin phiếu giao hàng")
        info_layout = QtWidgets.QGridLayout(info_group)
        
        info_layout.addWidget(QtWidgets.QLabel("Mã phiếu GH:"), 0, 0)
        info_layout.addWidget(QtWidgets.QLabel(self.label_delivery_code.text()), 0, 1)
        
        info_layout.addWidget(QtWidgets.QLabel("Mã đơn hàng:"), 0, 2)
        info_layout.addWidget(QtWidgets.QLabel(self.label_order_code.text()), 0, 3)
        
        info_layout.addWidget(QtWidgets.QLabel("Trạng thái:"), 1, 0)
        info_layout.addWidget(QtWidgets.QLabel(self.label_delivery_status.text()), 1, 1)
        
        info_layout.addWidget(QtWidgets.QLabel("Người nhận:"), 1, 2)
        info_layout.addWidget(QtWidgets.QLabel(self.label_receiver_name.text()), 1, 3)
        
        layout.addWidget(info_group)
        
        # Products table
        products_group = QtWidgets.QGroupBox("Sản phẩm giao hàng")
        products_layout = QtWidgets.QVBoxLayout(products_group)
        
        products_table = QtWidgets.QTableView()
        products_table.setModel(self.delivery_products_model)
        products_layout.addWidget(products_table)
        
        layout.addWidget(products_group)
        
        # Close button
        btn_close = QtWidgets.QPushButton("Đóng")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close)
        
        dialog.exec_()

    def update_delivery_status(self):
        """Update delivery status"""
        if not self.selected_delivery_id:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn một phiếu giao hàng")
            return
            
        # Enable status update controls
        self.combobox_new_status.setEnabled(True)
        self.date_status_update.setEnabled(True)
        self.text_status_note.setEnabled(True)
        self.btn_confirm_status_update.setEnabled(True)
        
        self.statusbar.showMessage("Chọn trạng thái mới và nhấn 'Xác nhận cập nhật'")

    def confirm_status_update(self):
        """Confirm and save status update"""
        if not self.selected_delivery_id:
            return
            
        new_status = self.combobox_new_status.currentText()
        note = self.text_status_note.toPlainText().strip()
        
        if not self.db_connection:
            return
            
        try:
            cursor = self.db_connection.cursor()
            
            # Update delivery status
            cursor.execute("""
                UPDATE PhieuGiaoHang 
                SET trangThai = %s, ghiChu = %s
                WHERE id = %s
            """, (new_status, note, self.selected_delivery_id))
            
            self.db_connection.commit()
            cursor.close()
            
            # Refresh data
            self.load_deliveries()
            self.load_delivery_details(self.selected_delivery_id)
            self.update_statistics()
            
            # Clear form
            self.text_status_note.clear()
            
            QtWidgets.QMessageBox.information(None, "Thành công", 
                f"Đã cập nhật trạng thái phiếu giao hàng thành '{new_status}'")
            self.statusbar.showMessage(f"Đã cập nhật trạng thái: {new_status}", 3000)
            
        except Error as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi", f"Lỗi khi cập nhật trạng thái: {e}")

    def create_delivery_note(self):
        """Create new delivery note"""
        QtWidgets.QMessageBox.information(None, "Thông báo", 
            "Chức năng tạo phiếu giao hàng mới đang được phát triển")

    def assign_delivery_staff(self):
        """Assign delivery staff"""
        if not self.selected_delivery_id:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn một phiếu giao hàng")
            return
            
        QtWidgets.QMessageBox.information(None, "Thông báo", 
            "Chức năng phân công giao hàng đang được phát triển")

    def complete_delivery(self):
        """Mark delivery as completed"""
        if not self.selected_delivery_id:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn một phiếu giao hàng")
            return
            
        reply = QtWidgets.QMessageBox.question(None, "Xác nhận", 
            "Bạn có chắc chắn muốn đánh dấu phiếu giao hàng này là đã giao thành công?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.combobox_new_status.setCurrentText("Đã giao")
            self.text_status_note.setText("Giao hàng thành công")
            self.confirm_status_update()

    def fail_delivery(self):
        """Mark delivery as failed"""
        if not self.selected_delivery_id:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn một phiếu giao hàng")
            return
            
        reply = QtWidgets.QMessageBox.question(None, "Xác nhận", 
            "Bạn có chắc chắn muốn đánh dấu phiếu giao hàng này là giao không thành công?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        
        if reply == QtWidgets.QMessageBox.Yes:
            reason, ok = QtWidgets.QInputDialog.getText(None, "Lý do thất bại", 
                "Nhập lý do giao hàng không thành công:")
            if ok and reason.strip():
                self.combobox_new_status.setCurrentText("Giao không thành công")
                self.text_status_note.setText(f"Giao thất bại: {reason}")
                self.confirm_status_update()

    def print_delivery_note(self):
        """Print delivery note"""
        if not self.selected_delivery_id:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn một phiếu giao hàng")
            return
            
        try:
            # Generate delivery note content
            print_content = self.generate_delivery_note_content()
            
            # Create preview dialog
            preview_dialog = QtWidgets.QDialog()
            preview_dialog.setWindowTitle("Xem trước - Phiếu giao hàng")
            preview_dialog.resize(700, 800)
            preview_dialog.setModal(True)
            
            layout = QtWidgets.QVBoxLayout(preview_dialog)
            
            # Text area
            text_area = QtWidgets.QTextEdit()
            text_area.setHtml(print_content)
            text_area.setReadOnly(True)
            layout.addWidget(text_area)
            
            # Buttons
            button_layout = QtWidgets.QHBoxLayout()
            btn_print = QtWidgets.QPushButton("In ngay")
            btn_save_pdf = QtWidgets.QPushButton("Lưu PDF")
            btn_close = QtWidgets.QPushButton("Đóng")
            
            btn_print.clicked.connect(lambda: self.print_document(text_area.document()))
            btn_save_pdf.clicked.connect(lambda: self.save_delivery_pdf(text_area.document()))
            btn_close.clicked.connect(preview_dialog.accept)
            
            button_layout.addWidget(btn_print)
            button_layout.addWidget(btn_save_pdf)
            button_layout.addWidget(btn_close)
            
            layout.addLayout(button_layout)
            preview_dialog.exec_()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi", f"Lỗi khi tạo phiếu giao hàng: {e}")

    def generate_delivery_note_content(self):
        """Generate HTML content for delivery note"""
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
                .signature-section {{ margin-top: 40px; }}
                .signature {{ display: inline-block; width: 200px; text-align: center; margin: 0 50px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="company-name">CÔNG TY MAY MẶC ABC</div>
                <div>Địa chỉ: 123 Đường ABC, Quận XYZ, TP.HCM</div>
                <div>Điện thoại: (028) 1234-5678 | Email: info@maymac.com</div>
                <div class="document-title">PHIẾU GIAO HÀNG</div>
            </div>
            
            <div class="info-section">
                <div class="info-row">
                    <span class="label">Mã phiếu GH:</span>
                    <span style="font-weight: bold; color: #007bff;">{self.label_delivery_code.text()}</span>
                </div>
                <div class="info-row">
                    <span class="label">Mã đơn hàng:</span>
                    <span>{self.label_order_code.text()}</span>
                </div>
                <div class="info-row">
                    <span class="label">Ngày giao:</span>
                    <span>{self.label_delivery_date.text()}</span>
                </div>
                <div class="info-row">
                    <span class="label">Người nhận:</span>
                    <span>{self.label_receiver_name.text()}</span>
                </div>
                <div class="info-row">
                    <span class="label">Số điện thoại:</span>
                    <span>{self.label_receiver_phone.text()}</span>
                </div>
                <div class="info-row">
                    <span class="label">Địa chỉ giao hàng:</span>
                    <span>{self.text_delivery_address.toPlainText()}</span>
                </div>
            </div>
            
            <div class="info-section">
                <h3>DANH SÁCH SẢN PHẨM GIAO</h3>
                <table>
                    <thead>
                        <tr>
                            <th>STT</th>
                            <th>Tên sản phẩm</th>
                            <th>Loại</th>
                            <th>Size</th>
                            <th>Màu</th>
                            <th>Số lượng giao</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Add products
        for row in range(self.delivery_products_model.rowCount()):
            html_content += f"""
                        <tr>
                            <td>{row + 1}</td>
                            <td>{self.delivery_products_model.item(row, 0).text()}</td>
                            <td>{self.delivery_products_model.item(row, 1).text()}</td>
                            <td>{self.delivery_products_model.item(row, 2).text()}</td>
                            <td>{self.delivery_products_model.item(row, 3).text()}</td>
                            <td>{self.delivery_products_model.item(row, 4).text()}</td>
                        </tr>
            """
        
        html_content += f"""
                    </tbody>
                </table>
            </div>
            
            <div class="info-section">
                <div class="info-row">
                    <span class="label">Ghi chú:</span>
                    <span>{self.text_delivery_note.toPlainText()}</span>
                </div>
            </div>
            
            <div class="signature-section">
                <div class="signature">
                    <div>Người giao hàng</div>
                    <div style="margin-top: 60px;">(Ký tên)</div>
                </div>
                <div class="signature">
                    <div>Người nhận hàng</div>
                    <div style="margin-top: 60px;">(Ký tên)</div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 30px; font-style: italic;">
                Cảm ơn quý khách đã sử dụng dịch vụ của chúng tôi!
            </div>
        </body>
        </html>
        """
        
        return html_content

    def print_document(self, document):
        """Print document"""
        try:
            printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
            print_dialog = QtPrintSupport.QPrintDialog(printer)
            
            if print_dialog.exec_() == QtWidgets.QDialog.Accepted:
                document.print_(printer)
                QtWidgets.QMessageBox.information(None, "Thành công", "Đã gửi lệnh in thành công!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi", f"Lỗi khi in: {e}")

    def save_delivery_pdf(self, document):
        """Save delivery note as PDF"""
        try:
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                None, "Lưu phiếu giao hàng PDF", 
                f"PhieuGiaoHang_{self.label_delivery_code.text()}_{datetime.now().strftime('%Y%m%d')}.pdf",
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

    def retranslateUi(self, GHWindow):
        _translate = QtCore.QCoreApplication.translate
        GHWindow.setWindowTitle(_translate("GHWindow", "Quản lý giao hàng - Garment Management System"))

    def __del__(self):
        if self.db_connection and self.db_connection.open:
            self.db_connection.close()