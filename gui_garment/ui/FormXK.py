from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtPrintSupport  # Thêm import này cho chức năng in
import pymysql as mysql
from pymysql import MySQLError  # Thay đổi từ Error thành MySQLError
import uuid
from datetime import datetime, date

class Ui_XKWindow(object):
    def __init__(self):
        self.db_connection = None
        self.selected_material_id = None
        self.selected_export_id = None
        self.current_materials = []  # Danh sách vật liệu xuất
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
        except MySQLError as e:  # Thay đổi từ Error thành MySQLError
            print(f"Error connecting to database: {e}")
            QtWidgets.QMessageBox.critical(None, "Lỗi kết nối", 
                f"Không thể kết nối đến cơ sở dữ liệu:\n{e}")

    def setupUi(self, XKWindow):
        XKWindow.setObjectName("XKWindow")
        XKWindow.resize(1600, 900)
        XKWindow.setMinimumSize(1400, 800)
        
        # Apply modern styling
        self.setup_styles(XKWindow)
        
        self.centralwidget = QtWidgets.QWidget(XKWindow)
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
        main_layout.addWidget(content_splitter, 3) # Tăng stretch factor
        
        # Left panel - Material selection and details
        left_panel = self.setup_material_selection_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Export list and operations
        right_panel = self.setup_export_panel()
        content_splitter.addWidget(right_panel)
        
        # Bottom panel - giảm kích thước
        bottom_panel = self.setup_export_summary_panel_compact()
        main_layout.addWidget(bottom_panel)
        
        content_splitter.setSizes([600, 800])

        XKWindow.setCentralWidget(self.centralwidget)
        
        # Setup menubar and statusbar
        self.setup_menubar(XKWindow)
        self.setup_statusbar(XKWindow)

        self.retranslateUi(XKWindow)
        self.setup_models()
        QtCore.QMetaObject.connectSlotsByName(XKWindow)

    def setup_styles(self, XKWindow):
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
        XKWindow.setStyleSheet(style)

    def setup_header_compact(self):
        """Thiết lập header nhỏ gọn"""
        header_widget = QtWidgets.QWidget()
        header_widget.setMaximumHeight(80)  # Giới hạn chiều cao
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(5, 5, 5, 5)
        
        # Title - thu gọn
        title_label = QtWidgets.QLabel("QUẢN LÝ XUẤT KHO VẬT LIỆU")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_font = QtGui.QFont()
        title_font.setPointSize(16)  # Giảm từ 20 xuống 16
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #007bff; margin: 5px;")
        
        # Export info - thu gọn
        export_info_widget = QtWidgets.QWidget()
        export_info_layout = QtWidgets.QHBoxLayout(export_info_widget)  # Đổi từ Grid sang HBox
        
        export_info_layout.addWidget(QtWidgets.QLabel("Mã phiếu:"))
        self.label_export_code = QtWidgets.QLabel(f"PXKVL-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}")
        self.label_export_code.setStyleSheet("font-weight: bold; color: #007bff; font-size: 12px;")
        export_info_layout.addWidget(self.label_export_code)
        
        export_info_layout.addWidget(QtWidgets.QLabel("Ngày:"))
        self.label_create_date = QtWidgets.QLabel(datetime.now().strftime("%d/%m/%Y %H:%M"))
        self.label_create_date.setStyleSheet("font-size: 12px;")
        export_info_layout.addWidget(self.label_create_date)
        
        header_layout.addWidget(title_label, 2)
        header_layout.addWidget(export_info_widget, 1)
        
        return header_widget

    def setup_export_summary_panel_compact(self):
        """Thiết lập panel tổng kết nhỏ gọn"""
        summary_group = QtWidgets.QGroupBox("Thông tin phiếu xuất")
        summary_group.setMaximumHeight(200)  # Tăng chiều cao để chứa label trạng thái
        summary_layout = QtWidgets.QHBoxLayout(summary_group)
        
        # Export details - thu gọn
        details_widget = QtWidgets.QWidget()
        details_layout = QtWidgets.QGridLayout(details_widget)
        details_layout.setSpacing(5)  # Giảm spacing
        
        # Mã đơn hàng với label trạng thái ở trên
        details_layout.addWidget(QtWidgets.QLabel("Mã đơn hàng:"), 0, 0)
        
        # Container cho input và trạng thái
        order_container = QtWidgets.QWidget()
        order_layout = QtWidgets.QVBoxLayout(order_container)
        order_layout.setSpacing(2)
        order_layout.setContentsMargins(0, 0, 0, 0)
        
        # Label trạng thái ở trên
        self.label_order_status = QtWidgets.QLabel("Chưa kiểm tra")
        self.label_order_status.setStyleSheet("color: #6c757d; font-size: 10px; margin: 0px; padding: 2px;")
        self.label_order_status.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        order_layout.addWidget(self.label_order_status)
        
        # Input mã đơn hàng ở dưới
        self.line_order_code_XK = QtWidgets.QLineEdit()
        self.line_order_code_XK.setPlaceholderText("Nhập mã đơn hàng (VD: DH001)")
        self.line_order_code_XK.setMaximumHeight(30)
        # Thêm sự kiện kiểm tra khi nhập
        self.line_order_code_XK.textChanged.connect(self.validate_order_code)
        order_layout.addWidget(self.line_order_code_XK)
        
        details_layout.addWidget(order_container, 0, 1)
        
        details_layout.addWidget(QtWidgets.QLabel("Lý do xuất:"), 1, 0)
        self.line_reason_XK = QtWidgets.QLineEdit()
        self.line_reason_XK.setPlaceholderText("Nhập lý do xuất kho...")
        self.line_reason_XK.setMaximumHeight(30)
        details_layout.addWidget(self.line_reason_XK, 1, 1)
        
        details_layout.addWidget(QtWidgets.QLabel("Ngày xuất:"), 0, 2)
        self.edit_date_materials = QtWidgets.QDateEdit()
        self.edit_date_materials.setDate(QtCore.QDate.currentDate())
        self.edit_date_materials.setCalendarPopup(True)
        self.edit_date_materials.setMaximumHeight(30)
        details_layout.addWidget(self.edit_date_materials, 0, 3)
        
        details_layout.addWidget(QtWidgets.QLabel("Tổng giá trị:"), 1, 2)
        self.line_total_value = QtWidgets.QLineEdit()
        self.line_total_value.setReadOnly(True)
        self.line_total_value.setMaximumHeight(30)
        self.line_total_value.setStyleSheet("font-weight: bold; font-size: 12px; background-color: #f8f9fa;")
        details_layout.addWidget(self.line_total_value, 1, 3)
        
        # Ẩn ghi chú để tiết kiệm không gian
        self.text_notes_XK = QtWidgets.QTextEdit()
        self.text_notes_XK.setVisible(False)  # Ẩn đi
        
        # Action buttons - thu gọn thành 2 hàng
        action_widget = QtWidgets.QWidget()
        action_layout = QtWidgets.QGridLayout(action_widget)
        action_layout.setSpacing(5)
        
        # Hàng 1
        self.btn_export_orders_XK = QtWidgets.QPushButton("Tạo phiếu xuất")
        self.btn_export_orders_XK.setProperty("class", "save-btn")
        self.btn_export_orders_XK.setMaximumHeight(30)
        
        # Thêm button xem danh sách phiếu xuất
        self.btn_view_export_list = QtWidgets.QPushButton("Xem DS phiếu xuất")
        self.btn_view_export_list.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        self.btn_view_export_list.setMaximumHeight(30)

        action_layout.addWidget(self.btn_export_orders_XK, 0, 0)
        action_layout.addWidget(self.btn_view_export_list, 0, 1)
        
        # Hàng 2
        self.btn_new_export = QtWidgets.QPushButton("Phiếu mới")
        self.btn_new_export.setMaximumHeight(30)
        
        self.btn_cancel = QtWidgets.QPushButton("Hủy")
        self.btn_cancel.setMaximumHeight(30)
        
        action_layout.addWidget(self.btn_new_export, 2, 0)
        action_layout.addWidget(self.btn_cancel, 2, 1)
        
        # Connect signals
        self.btn_export_orders_XK.clicked.connect(self.create_export)
        self.btn_new_export.clicked.connect(self.new_export)
        self.btn_cancel.clicked.connect(self.cancel_export)
        
        # Ẩn bảng lịch sử xuất
        self.table_orderListMaterials_XK = QtWidgets.QTableView()
        self.table_orderListMaterials_XK.setVisible(False)  # Ẩn đi
        self.table_orderListMaterials_XK.clicked.connect(self.on_export_selected)
        
        summary_layout.addWidget(details_widget, 2)
        summary_layout.addWidget(action_widget, 1)
        
        return summary_group

    def validate_order_code(self):
        """Kiểm tra mã đơn hàng khi nhập"""
        order_code = self.line_order_code_XK.text().strip()
        
        if not order_code:
            self.label_order_status.setText("Chưa kiểm tra")
            self.label_order_status.setStyleSheet("color: #6c757d; font-size: 11px;")
            self.current_order_id = None
            return
        
        if not self.db_connection:
            self.label_order_status.setText("Lỗi kết nối DB")
            self.label_order_status.setStyleSheet("color: #dc3545; font-size: 11px;")
            return
        
        try:
            cursor = self.db_connection.cursor()
            # Sửa SQL query - bỏ cột trangThai vì không tồn tại trong bảng DonDatHang
            cursor.execute("""
                SELECT id, maDonHang, ngayDatHang, tongTien, tienDatCoc
                FROM DonDatHang 
                WHERE maDonHang = %s
            """, (order_code,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                order_id, ma_don_hang, ngay_dat_hang, tong_tien, tien_dat_coc = result
                self.current_order_id = order_id
                
                # Hiển thị thông tin đơn hàng hợp lệ
                status_text = f"✓ Hợp lệ "
                
                # # Thêm thông tin tổng tiền nếu có
                # if tong_tien and tong_tien > 0:
                #     status_text += f" - {tong_tien:,.0f} VNĐ"
                
                self.label_order_status.setText(status_text)
                self.label_order_status.setStyleSheet("color: #28a745; font-size: 11px; font-weight: bold;")
                
            else:
                self.current_order_id = None
                self.label_order_status.setText("✗ Không tồn tại")
                self.label_order_status.setStyleSheet("color: #dc3545; font-size: 11px; font-weight: bold;")
                
        except MySQLError as e:
            # Xử lý lỗi MySQL cụ thể
            self.current_order_id = None
            self.label_order_status.setText("Lỗi DB")
            self.label_order_status.setStyleSheet("color: #dc3545; font-size: 11px;")
            print(f"MySQL Error validating order: {e}")
            QtWidgets.QMessageBox.critical(None, "Lỗi Database", 
                f"Lỗi khi kiểm tra đơn hàng:\n{e}")
        
        except Exception as e:
            # Xử lý lỗi khác
            self.current_order_id = None
            self.label_order_status.setText("Lỗi kiểm tra")
            self.label_order_status.setStyleSheet("color: #dc3545; font-size: 11px;")
            print(f"Error validating order: {e}")



    def setup_material_selection_panel(self):
        """Thiết lập panel chọn vật liệu với kích thước tối ưu"""
        material_group = QtWidgets.QGroupBox("Chọn vật liệu xuất kho")
        material_layout = QtWidgets.QVBoxLayout(material_group)
        
        # Material search - thu gọn
        search_widget = QtWidgets.QWidget()
        search_widget.setMaximumHeight(60)
        search_layout = QtWidgets.QHBoxLayout(search_widget)
        
        search_layout.addWidget(QtWidgets.QLabel("Tìm vật liệu:"))
        self.line_materials_XK = QtWidgets.QLineEdit()
        self.line_materials_XK.setPlaceholderText("Nhập tên vật liệu...")
        self.line_materials_XK.setMaximumHeight(50)
        search_layout.addWidget(self.line_materials_XK)
        
        self.btn_search_materials_XK = QtWidgets.QPushButton("Tìm")
        self.btn_search_materials_XK.setMaximumHeight(50)
        self.btn_search_materials_XK.clicked.connect(self.search_materials)
        search_layout.addWidget(self.btn_search_materials_XK)
        
        material_layout.addWidget(search_widget)
        
        # Available materials table - tăng kích thước
        material_layout.addWidget(QtWidgets.QLabel("Danh sách vật liệu có sẵn:"))
        self.table_listMaterials_XK = QtWidgets.QTableView()
        self.table_listMaterials_XK.setMinimumHeight(100)  
        self.table_listMaterials_XK.setMaximumHeight(300) 
        self.table_listMaterials_XK.clicked.connect(self.on_material_selected)
        material_layout.addWidget(self.table_listMaterials_XK)
        
        # Material input form - thu gọn
        input_group = QtWidgets.QGroupBox("Thông tin xuất vật liệu")
        input_group.setMaximumHeight(190)  # Giới hạn chiều cao
        input_layout = QtWidgets.QGridLayout(input_group)
        input_layout.setSpacing(5)
        
        input_layout.addWidget(QtWidgets.QLabel("Tên vật liệu:"), 0, 0)
        self.line_add_materials_XK = QtWidgets.QLineEdit()
        self.line_add_materials_XK.setReadOnly(True)
        self.line_add_materials_XK.setMaximumHeight(70)
        input_layout.addWidget(self.line_add_materials_XK, 0, 1, 1, 2)
        
        input_layout.addWidget(QtWidgets.QLabel("Số lượng:"), 1, 0)
        self.spin_quantity_XK = QtWidgets.QSpinBox()
        self.spin_quantity_XK.setMinimum(1)
        self.spin_quantity_XK.setMaximum(999999)
        self.spin_quantity_XK.setMaximumHeight(30)
        self.spin_quantity_XK.setStyleSheet("""
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
        input_layout.addWidget(self.spin_quantity_XK, 1, 1)
        
        self.combobox_unitOfMaterials_XK = QtWidgets.QComboBox()
        self.combobox_unitOfMaterials_XK.addItems(["m", "kg", "lô", "hộp", "thùng", "cái"])
        self.combobox_unitOfMaterials_XK.setMaximumHeight(30)
        input_layout.addWidget(self.combobox_unitOfMaterials_XK, 1, 2)
        
        input_layout.addWidget(QtWidgets.QLabel("Đơn giá:"), 2, 0)
        self.line_unit_price_XK = QtWidgets.QLineEdit()
        self.line_unit_price_XK.setPlaceholderText("VNĐ")
        self.line_unit_price_XK.setMaximumHeight(30)
        input_layout.addWidget(self.line_unit_price_XK, 2, 1)
        
        self.label_current_stock = QtWidgets.QLabel("0")
        self.label_current_stock.setStyleSheet("font-weight: bold; color: #28a745; font-size: 12px;")
        # input_layout.addWidget(self.label_current_stock, 2, 3)
        
        # Add button
        self.btn_add_materials_XK = QtWidgets.QPushButton("Thêm vào phiếu xuất")
        self.btn_add_materials_XK.setProperty("class", "save-btn")
        self.btn_add_materials_XK.setMaximumHeight(35)
        self.btn_add_materials_XK.clicked.connect(self.add_material)
        input_layout.addWidget(self.btn_add_materials_XK, 3, 0, 1, 3)
        
        material_layout.addWidget(input_group)
        
        return material_group

    def setup_export_panel(self):
        """Thiết lập panel danh sách xuất với kích thước tối ưu"""
        export_group = QtWidgets.QGroupBox("Danh sách vật liệu xuất kho")
        export_layout = QtWidgets.QVBoxLayout(export_group)
        
        # Selected materials table 
        self.table_materials_XK = QtWidgets.QTableView()
        self.table_materials_XK.setMinimumHeight(250)  
        export_layout.addWidget(self.table_materials_XK)
        
        # Material management buttons - thu gọn
        btn_widget = QtWidgets.QWidget()
        btn_widget.setMaximumHeight(40)
        btn_layout = QtWidgets.QHBoxLayout(btn_widget)
        
        self.btn_edit_listMaterials_XK = QtWidgets.QPushButton("Sửa")
        self.btn_edit_listMaterials_XK.setProperty("class", "warning-btn")
        self.btn_edit_listMaterials_XK.setMaximumHeight(30)
        
        self.btn_del_listMaterials_XK = QtWidgets.QPushButton("Xóa")
        self.btn_del_listMaterials_XK.setProperty("class", "delete-btn")
        self.btn_del_listMaterials_XK.setMaximumHeight(30)
        
        self.btn_edit_listMaterials_XK.clicked.connect(self.edit_material)
        self.btn_del_listMaterials_XK.clicked.connect(self.delete_material)
        
        btn_layout.addWidget(self.btn_edit_listMaterials_XK)
        btn_layout.addWidget(self.btn_del_listMaterials_XK)
        btn_layout.addStretch()
        
        export_layout.addWidget(btn_widget)
        
        return export_group

    def setup_menubar(self, XKWindow):
        """Thiết lập menu bar"""
        self.menubar = QtWidgets.QMenuBar(XKWindow)
        XKWindow.setMenuBar(self.menubar)

    def setup_statusbar(self, XKWindow):
        """Thiết lập status bar"""
        self.statusbar = QtWidgets.QStatusBar(XKWindow)
        self.statusbar.showMessage("Sẵn sàng")
        XKWindow.setStatusBar(self.statusbar)

    def on_material_selected(self):
        """Xử lý khi chọn vật liệu"""
        selected = self.table_listMaterials_XK.currentIndex()
        if selected.isValid():
            # Lấy thông tin từ các cột theo thứ tự: ID(0), Mã VL(1), Tên(2), Loại(3), ĐVT(4), Đơn giá(5), Tồn kho(6)
            self.selected_material_id = self.available_materials_model.item(selected.row(), 0).text()
            material_name = self.available_materials_model.item(selected.row(), 2).text()
            unit = self.available_materials_model.item(selected.row(), 4).text()
            unit_price = self.available_materials_model.item(selected.row(), 5).text()  # Đơn giá từ cột 5
            stock = self.available_materials_model.item(selected.row(), 6).text()       # Tồn kho từ cột 6
            
            # Tự động điền thông tin vào form
            self.line_add_materials_XK.setText(material_name)
            self.combobox_unitOfMaterials_XK.setCurrentText(unit)
            
            # Tự động điền đơn giá (loại bỏ dấu phẩy nếu có)
            clean_price = unit_price.replace(',', '') if unit_price else "0"
            self.line_unit_price_XK.setText(clean_price)
            
            # Hiển thị tồn kho
            self.label_current_stock.setText(f"{stock} {unit}")
            
            # Set maximum quantity based on stock
            try:
                max_stock = int(float(stock.replace(',', '')))
                self.spin_quantity_XK.setMaximum(max_stock)
                # Reset số lượng về 1
                self.spin_quantity_XK.setValue(1)
            except (ValueError, AttributeError):
                self.spin_quantity_XK.setMaximum(999999)
                self.spin_quantity_XK.setValue(1)
            
            # Hiển thị thông tin trên status bar
            self.statusbar.showMessage(f"Đã chọn: {material_name} - Đơn giá: {unit_price} VNĐ", 3000)

    def on_export_selected(self):
        """Xử lý khi chọn phiếu xuất từ danh sách"""
        selected = self.table_orderListMaterials_XK.currentIndex()
        if selected.isValid():
            ma_phieu = self.export_model.item(selected.row(), 0).text()
            self.load_export_details(ma_phieu)

    def calculate_total_value(self):
        """Tính tổng giá trị phiếu xuất"""
        total = 0
        for row in range(self.material_model.rowCount()):
            try:
                thanh_tien = float(self.material_model.item(row, 5).text().replace(',', ''))
                total += thanh_tien
            except (ValueError, AttributeError):
                continue
        self.line_total_value.setText(f"{total:,.0f} VNĐ")

    def new_export(self):
        """Tạo phiếu xuất mới"""
        self.current_materials.clear()
        self.selected_material_id = None
        self.selected_export_id = None
        self.current_order_id = None  # Reset order ID
        
        # Reset form
        self.line_add_materials_XK.clear()
        self.spin_quantity_XK.setValue(1)
        self.line_unit_price_XK.clear()
        self.label_current_stock.setText("0")
        self.line_order_code_XK.clear()  # Reset order code input
        self.label_order_status.setText("Chưa kiểm tra")  # Reset status
        self.edit_date_materials.setDate(QtCore.QDate.currentDate())
        self.line_reason_XK.clear()
        self.text_notes_XK.clear()
        self.line_total_value.clear()
        
        # Generate new export code
        new_code = f"PXKVL-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        self.label_export_code.setText(new_code)
        
        # Clear table
        self.material_model.clear()
        self.material_model.setHorizontalHeaderLabels(["ID", "Tên VL", "Số lượng", "ĐVT", "Đơn giá", "Thành tiền"])
        
        self.statusbar.showMessage("Đã tạo phiếu xuất mới", 2000)

    def cancel_export(self):
        """Hủy phiếu xuất hiện tại"""
        reply = QtWidgets.QMessageBox.question(None, "Xác nhận", 
            "Bạn có chắc chắn muốn hủy phiếu xuất hiện tại?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.new_export()

    def validate_export(self):
        """Kiểm tra tính hợp lệ của phiếu xuất"""
        if self.material_model.rowCount() == 0:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng thêm ít nhất một vật liệu")
            return False
        
        # Kiểm tra mã đơn hàng
        order_code = self.line_order_code_XK.text().strip()
        if not order_code:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng nhập mã đơn hàng")
            return False
        
        # Kiểm tra đơn hàng có tồn tại không
        if not hasattr(self, 'current_order_id') or self.current_order_id is None:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", 
                "Mã đơn hàng không hợp lệ hoặc không tồn tại. Vui lòng kiểm tra lại.")
            return False
            
        if not self.line_reason_XK.text().strip():
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng nhập lý do xuất kho")
            return False
            
        return True

    # Keep all existing methods but improved
    def retranslateUi(self, XKWindow):
        _translate = QtCore.QCoreApplication.translate
        XKWindow.setWindowTitle(_translate("XKWindow", "Quản lý xuất kho vật liệu - Garment Management System"))

    def setup_models(self):
        self.material_model = QtGui.QStandardItemModel()
        self.material_model.setHorizontalHeaderLabels(["ID", "Tên VL", "Số lượng", "ĐVT", "Đơn giá", "Thành tiền"])
        self.table_materials_XK.setModel(self.material_model)
        
        self.available_materials_model = QtGui.QStandardItemModel()
        self.table_listMaterials_XK.setModel(self.available_materials_model)
        
        self.export_model = QtGui.QStandardItemModel()
        self.table_orderListMaterials_XK.setModel(self.export_model)
        
        # Set table properties và row height
        for table in [self.table_materials_XK, self.table_listMaterials_XK, self.table_orderListMaterials_XK]:
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
        
        # Đặt chiều cao tối thiểu cho bảng vật liệu để hiển thị ít nhất 4 dòng
        header_height = self.table_listMaterials_XK.horizontalHeader().height()
        row_height = 30  # Chiều cao mỗi dòng
        min_rows = 4
        min_height = header_height + (row_height * min_rows) + 10  # +10 cho margin
        self.table_listMaterials_XK.setMinimumHeight(min_height)
        
        self.load_materials()
        self.load_exports()

    def load_materials(self):
        self.available_materials_model.clear()
        self.available_materials_model.setHorizontalHeaderLabels(["ID", "Mã VL", "Tên", "Loại", "ĐVT", "Đơn giá", "Tồn kho"])
        if self.db_connection:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM VatLieu WHERE tonKho > 0")
            for row in cursor.fetchall():
                items = [QtGui.QStandardItem(str(field) if field is not None else "") for field in row]
                self.available_materials_model.appendRow(items)
            cursor.close()

    def load_exports(self):
        self.export_model.clear()
        self.export_model.setHorizontalHeaderLabels(["Mã Phiếu", "Đơn hàng", "Nhân viên", "Ngày xuất", "Lý do", "Tổng giá trị"])
        if self.db_connection:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT p.maPhieu, d.maDonHang, n.tenNhanVien, p.ngayXuat, p.lyDoXuat,
                       SUM(ct.thanhTien) as tongGiaTri
                FROM PhieuXuatKhoVL p
                LEFT JOIN DonDatHang d ON p.donDatHangId = d.id
                LEFT JOIN NhanVien n ON p.nhanVienXuatId = n.id
                LEFT JOIN ChiTietXuatKhoVL ct ON p.id = ct.phieuXuatId
                GROUP BY p.id
                ORDER BY p.ngayXuat DESC
            """)
            for row in cursor.fetchall():
                items = [QtGui.QStandardItem(str(field) if field is not None else "") for field in row]
                if len(items) > 5 and items[5].text():
                    items[5].setText(f"{float(items[5].text()):,.0f} VNĐ")
                self.export_model.appendRow(items)
            cursor.close()

    def search_materials(self):
        search_text = self.line_materials_XK.text()
        self.available_materials_model.clear()
        self.available_materials_model.setHorizontalHeaderLabels(["ID", "Mã VL", "Tên", "Loại", "ĐVT","Đơn giá", "Tồn kho"])
        if self.db_connection:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM VatLieu WHERE tenVatLieu LIKE %s AND tonKho > 0", (f"%{search_text}%",))
            for row in cursor.fetchall():
                items = [QtGui.QStandardItem(str(field) if field is not None else "") for field in row]
                self.available_materials_model.appendRow(items)
            cursor.close()

    def add_material(self):
        if not self.selected_material_id:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn vật liệu từ danh sách")
            return
            
        material_name = self.line_add_materials_XK.text()
        quantity = self.spin_quantity_XK.value()
        unit = self.combobox_unitOfMaterials_XK.currentText()
        unit_price_text = self.line_unit_price_XK.text()
        
        if not unit_price_text:
            QtWidgets.QMessageBox.warning(None, "Cảnh báo", "Vui lòng nhập đơn giá")
            return
        
        try:
            unit_price = float(unit_price_text.replace(',', ''))
            total_price = quantity * unit_price
            
            # Check if material already exists in the list
            for row in range(self.material_model.rowCount()):
                if self.material_model.item(row, 0).text() == self.selected_material_id:
                    # Update existing material
                    current_qty = int(self.material_model.item(row, 2).text())
                    new_qty = current_qty + quantity
                    new_total = new_qty * unit_price
                    
                    self.material_model.item(row, 2).setText(str(new_qty))
                    self.material_model.item(row, 5).setText(f"{new_total:,.0f}")
                    self.calculate_total_value()
                    self.clear_material_inputs()
                    return
            
            # Add new material
            items = [
                QtGui.QStandardItem(self.selected_material_id),
                QtGui.QStandardItem(material_name),
                QtGui.QStandardItem(str(quantity)),
                QtGui.QStandardItem(unit),
                QtGui.QStandardItem(f"{unit_price:,.0f}"),
                QtGui.QStandardItem(f"{total_price:,.0f}")
            ]
            self.material_model.appendRow(items)
            self.calculate_total_value()
            self.clear_material_inputs()
            self.statusbar.showMessage(f"Đã thêm {material_name}", 2000)
            
        except ValueError:
            QtWidgets.QMessageBox.critical(None, "Lỗi", "Vui lòng nhập đơn giá hợp lệ")

    def delete_material(self):
        selected = self.table_materials_XK.currentIndex()
        if selected.isValid():
            material_name = self.material_model.item(selected.row(), 1).text()
            reply = QtWidgets.QMessageBox.question(None, "Xác nhận xóa", 
                f"Bạn có chắc chắn muốn xóa vật liệu '{material_name}' khỏi danh sách?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            
            if reply == QtWidgets.QMessageBox.Yes:
                self.material_model.removeRow(selected.row())
                self.calculate_total_value()
                self.statusbar.showMessage(f"Đã xóa {material_name}", 2000)

    def edit_material(self):
        selected = self.table_materials_XK.currentIndex()
        if selected.isValid():
            material_id = self.material_model.item(selected.row(), 0).text()
            material_name = self.material_model.item(selected.row(), 1).text()
            current_qty = int(self.material_model.item(selected.row(), 2).text())
            unit = self.material_model.item(selected.row(), 3).text()
            unit_price = float(self.material_model.item(selected.row(), 4).text().replace(',', ''))
            
            # Create edit dialog
            dialog = QtWidgets.QDialog()
            dialog.setWindowTitle(f"Sửa số lượng - {material_name}")
            dialog.resize(300, 150)
            
            layout = QtWidgets.QFormLayout()
            
            qty_spin = QtWidgets.QSpinBox()
            qty_spin.setMinimum(1)
            qty_spin.setMaximum(999999)
            qty_spin.setValue(current_qty)
            layout.addRow("Số lượng mới:", qty_spin)
            
            price_line = QtWidgets.QLineEdit()
            price_line.setText(f"{unit_price:,.0f}")
            layout.addRow("Đơn giá:", price_line)
            
            btn_layout = QtWidgets.QHBoxLayout()
            btn_ok = QtWidgets.QPushButton("OK")
            btn_cancel = QtWidgets.QPushButton("Hủy")
            
            btn_ok.clicked.connect(lambda: self.confirm_edit_material(
                dialog, selected.row(), qty_spin.value(), 
                float(price_line.text().replace(',', ''))))
            btn_cancel.clicked.connect(dialog.reject)
            
            btn_layout.addWidget(btn_ok)
            btn_layout.addWidget(btn_cancel)
            
            layout.addRow(btn_layout)
            dialog.setLayout(layout)
            dialog.exec_()

    def confirm_edit_material(self, dialog, row, new_qty, new_price):
        """Xác nhận sửa vật liệu"""
        try:
            new_total = new_qty * new_price
            self.material_model.item(row, 2).setText(str(new_qty))
            self.material_model.item(row, 4).setText(f"{new_price:,.0f}")
            self.material_model.item(row, 5).setText(f"{new_total:,.0f}")
            self.calculate_total_value()
            dialog.accept()
            self.statusbar.showMessage("Đã cập nhật thông tin vật liệu", 2000)
        except ValueError:
            QtWidgets.QMessageBox.critical(None, "Lỗi", "Vui lòng nhập số hợp lệ")

    def clear_material_inputs(self):
        self.line_add_materials_XK.clear()
        self.spin_quantity_XK.setValue(1)
        self.line_unit_price_XK.clear()
        self.label_current_stock.setText("0")
        self.selected_material_id = None

    def save_materials(self):
        """Lưu danh sách vật liệu hiện tại"""
        if self.material_model.rowCount() == 0:
            QtWidgets.QMessageBox.information(None, "Thông báo", "Không có vật liệu nào để lưu")
            return
        
        self.statusbar.showMessage("Đã lưu danh sách vật liệu", 2000)
        QtWidgets.QMessageBox.information(None, "Thành công", "Đã lưu danh sách vật liệu")

    def create_export(self):
        """Hiển thị form xác nhận phiếu xuất trước khi tạo"""
        if not self.validate_export():
            return

        # Hiển thị form xác nhận
        self.show_export_confirmation()

    def show_export_confirmation(self):
        """Hiển thị form xác nhận phiếu xuất"""
        # Tạo dialog xác nhận
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Xác nhận phiếu xuất kho vật liệu")
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
        header_label = QtWidgets.QLabel("XÁC NHẬN PHIẾU XUẤT KHO VẬT LIỆU")
        header_label.setAlignment(QtCore.Qt.AlignCenter)
        header_font = QtGui.QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setStyleSheet("color: #007bff; margin: 10px; padding: 10px;")
        layout.addWidget(header_label)
        
        # Thông tin phiếu xuất
        export_info_group = QtWidgets.QGroupBox("Thông tin phiếu xuất")
        export_info_layout = QtWidgets.QGridLayout(export_info_group)
        
        export_info_layout.addWidget(QtWidgets.QLabel("Mã phiếu xuất:"), 0, 0)
        export_code_label = QtWidgets.QLabel(self.label_export_code.text())
        export_code_label.setStyleSheet("font-weight: bold; color: #007bff;")
        export_info_layout.addWidget(export_code_label, 0, 1)
        
        export_info_layout.addWidget(QtWidgets.QLabel("Ngày xuất:"), 0, 2)
        export_date = self.edit_date_materials.date().toString("dd/MM/yyyy")
        export_info_layout.addWidget(QtWidgets.QLabel(export_date), 0, 3)
        
        export_info_layout.addWidget(QtWidgets.QLabel("Đơn hàng:"), 1, 0)
        order_text = self.line_order_code_XK.text() if self.line_order_code_XK.text().strip() else "Không có"
        export_info_layout.addWidget(QtWidgets.QLabel(order_text), 1, 1)
        
        export_info_layout.addWidget(QtWidgets.QLabel("Lý do xuất:"), 1, 2)
        reason_label = QtWidgets.QLabel(self.line_reason_XK.text())
        reason_label.setWordWrap(True)
        export_info_layout.addWidget(reason_label, 1, 3)
        
        layout.addWidget(export_info_group)
        
        # Danh sách vật liệu xuất
        materials_group = QtWidgets.QGroupBox("Danh sách vật liệu xuất kho")
        materials_layout = QtWidgets.QVBoxLayout(materials_group)
        
        # Tạo bảng hiển thị vật liệu
        materials_table = QtWidgets.QTableWidget()
        materials_table.setColumnCount(5)
        materials_table.setHorizontalHeaderLabels(["Tên vật liệu", "Số lượng", "Đơn vị", "Đơn giá", "Thành tiền"])
        materials_table.setRowCount(self.material_model.rowCount())
        
        # Điền dữ liệu vào bảng
        for row in range(self.material_model.rowCount()):
            # Tên vật liệu
            name_item = QtWidgets.QTableWidgetItem(self.material_model.item(row, 1).text())
            name_item.setFlags(name_item.flags() & ~QtCore.Qt.ItemIsEditable)
            materials_table.setItem(row, 0, name_item)
            
            # Số lượng
            qty_item = QtWidgets.QTableWidgetItem(self.material_model.item(row, 2).text())
            qty_item.setFlags(qty_item.flags() & ~QtCore.Qt.ItemIsEditable)
            materials_table.setItem(row, 1, qty_item)
            
            # Đơn vị
            unit_item = QtWidgets.QTableWidgetItem(self.material_model.item(row, 3).text())
            unit_item.setFlags(unit_item.flags() & ~QtCore.Qt.ItemIsEditable)
            materials_table.setItem(row, 2, unit_item)
            
            # Đơn giá
            price_text = f"{float(self.material_model.item(row, 4).text().replace(',', '')):,.0f} VNĐ"
            price_item = QtWidgets.QTableWidgetItem(price_text)
            price_item.setFlags(price_item.flags() & ~QtCore.Qt.ItemIsEditable)
            materials_table.setItem(row, 3, price_item)
            
            # Thành tiền
            total_text = f"{float(self.material_model.item(row, 5).text().replace(',', '')):,.0f} VNĐ"
            total_item = QtWidgets.QTableWidgetItem(total_text)
            total_item.setFlags(total_item.flags() & ~QtCore.Qt.ItemIsEditable)
            materials_table.setItem(row, 4, total_item)
        
        # Tự động điều chỉnh kích thước cột
        materials_table.resizeColumnsToContents()
        materials_table.horizontalHeader().setStretchLastSection(True)
        materials_table.setMaximumHeight(200)
        
        materials_layout.addWidget(materials_table)
        layout.addWidget(materials_group)
        
        # Thông tin tổng kết
        summary_group = QtWidgets.QGroupBox("Tổng kết")
        summary_layout = QtWidgets.QGridLayout(summary_group)
        
        summary_layout.addWidget(QtWidgets.QLabel("Tổng số loại vật liệu:"), 0, 0)
        total_types_label = QtWidgets.QLabel(str(self.material_model.rowCount()))
        total_types_label.setStyleSheet("font-weight: bold; color: #007bff;")
        summary_layout.addWidget(total_types_label, 0, 1)
        
        summary_layout.addWidget(QtWidgets.QLabel("Tổng giá trị:"), 0, 2)
        total_value_label = QtWidgets.QLabel(self.line_total_value.text())
        total_value_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #dc3545;")
        summary_layout.addWidget(total_value_label, 0, 3)
        
        layout.addWidget(summary_group)
        
        # Ghi chú (nếu có)
        if self.text_notes_XK.toPlainText().strip():
            notes_group = QtWidgets.QGroupBox("Ghi chú")
            notes_layout = QtWidgets.QVBoxLayout(notes_group)
            notes_label = QtWidgets.QLabel(self.text_notes_XK.toPlainText())
            notes_label.setWordWrap(True)
            notes_layout.addWidget(notes_label)
            layout.addWidget(notes_group)
    
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        # btn_confirm = QtWidgets.QPushButton("Tạo phiếu xuất")
        # btn_confirm.setProperty("class", "confirm-btn")
        
        btn_print = QtWidgets.QPushButton("In và lưu phiếu")
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
        
        btn_save_pdf = QtWidgets.QPushButton("Xuất phiếu PDF")
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
        
        # button_layout.addWidget(btn_confirm)
        button_layout.addWidget(btn_print)
        button_layout.addWidget(btn_save_pdf)
        button_layout.addWidget(btn_cancel)
        
        layout.addLayout(button_layout)
        
        # Kết nối sự kiện
        # btn_confirm.clicked.connect(lambda: self.confirm_and_save_export(dialog))
        btn_print.clicked.connect(lambda: self.print_export_directly(dialog))
        btn_save_pdf.clicked.connect(lambda: self.save_export_pdf_directly(dialog))
        btn_cancel.clicked.connect(dialog.reject)
        
        # Hiển thị dialog
        dialog.exec_()

    def print_export_directly(self, dialog):
        """In phiếu xuất trực tiếp"""
        try:
            # Tạo nội dung in
            print_content = self.generate_export_print_content()
            
            # Tạo document để in
            document = QtGui.QTextDocument()
            document.setHtml(print_content)
            
            # In ngay lập tức
            printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
            print_dialog = QtPrintSupport.QPrintDialog(printer)
            
            if print_dialog.exec_() == QtWidgets.QDialog.Accepted:
                document.print_(printer)
                QtWidgets.QMessageBox.information(None, "Thành công", "Đã gửi lệnh in phiếu xuất thành công!")
                
                # Lưu vào database và reset form
                if self.save_export_to_database():
                    dialog.accept()
                    QtWidgets.QMessageBox.information(None, "Hoàn tất", 
                        f"Phiếu xuất {self.label_export_code.text()} đã được tạo và in thành công!")
                    self.new_export()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi", f"Lỗi khi in phiếu: {e}")

    def save_export_pdf_directly(self, dialog):
        """Lưu phiếu xuất thành PDF trực tiếp"""
        try:
            # Chọn nơi lưu file
            file_name = f"PhieuXuat_{self.label_export_code.text()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                None, "Lưu phiếu xuất PDF", 
                file_name,
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                # Tạo nội dung PDF
                print_content = self.generate_export_print_content()
                
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
                    f"Đã lưu phiếu xuất thành file PDF:\n{file_path}")
                
                # Lưu vào database và reset form
                if self.save_export_to_database():
                    dialog.accept()
                    QtWidgets.QMessageBox.information(None, "Hoàn tất", 
                        f"Phiếu xuất {self.label_export_code.text()} đã được tạo và lưu PDF thành công!")
                    self.new_export()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi", f"Lỗi khi lưu PDF: {e}")

    def confirm_and_save_export(self, dialog):
        """Chỉ tạo phiếu xuất không in và không lưu PDF"""
        # Đóng dialog xác nhận
        dialog.accept()
        
        # Thực hiện lưu phiếu xuất
        if self.save_export_to_database():
            QtWidgets.QMessageBox.information(None, "Thành công", 
                f"Phiếu xuất {self.label_export_code.text()} đã được tạo thành công!")
            self.new_export()

    def generate_export_print_content(self):
        """Tạo nội dung HTML cho phiếu xuất kho"""
        order_text = self.line_order_code_XK.text() if self.line_order_code_XK.text().strip() else "Không có"
        
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
                <div class="document-title">PHIẾU XUẤT KHO VẬT LIỆU</div>
            </div>
            
            <div class="info-section">
                <div class="info-row">
                    <span class="label">Mã phiếu xuất:</span>
                    <span style="font-weight: bold; color: #007bff;">{self.label_export_code.text()}</span>
                </div>
                <div class="info-row">
                    <span class="label">Ngày xuất:</span>
                    <span>{self.edit_date_materials.date().toString("dd/MM/yyyy")}</span>
                </div>
                <div class="info-row">
                    <span class="label">Đơn hàng liên quan:</span>
                    <span>{order_text}</span>
                </div>
                <div class="info-row">
                    <span class="label">Lý do xuất:</span>
                    <span>{self.line_reason_XK.text()}</span>
                </div>
            </div>
            
            <div class="info-section">
                <h3>DANH SÁCH VẬT LIỆU XUẤT KHO</h3>
                <table>
                    <thead>
                        <tr>
                            <th>STT</th>
                            <th>Tên vật liệu</th>
                            <th>Số lượng</th>
                            <th>Đơn vị</th>
                            <th>Đơn giá (VNĐ)</th>
                            <th>Thành tiền (VNĐ)</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Thêm danh sách vật liệu
        total_amount = 0
        for row in range(self.material_model.rowCount()):
            ten_vl = self.material_model.item(row, 1).text()
            so_luong = self.material_model.item(row, 2).text()
            don_vi = self.material_model.item(row, 3).text()
            don_gia = float(self.material_model.item(row, 4).text().replace(',', ''))
            thanh_tien = float(self.material_model.item(row, 5).text().replace(',', ''))
            total_amount += thanh_tien
            
            html_content += f"""
                        <tr>
                            <td class="text-center">{row + 1}</td>
                            <td>{ten_vl}</td>
                            <td class="text-center">{so_luong}</td>
                            <td class="text-center">{don_vi}</td>
                            <td class="text-right">{don_gia:,.0f}</td>
                            <td class="text-right">{thanh_tien:,.0f}</td>
                        </tr>
            """
        
        # Thêm dòng tổng cộng
        html_content += f"""
                        <tr style="font-weight: bold; background-color: #f8f9fa;">
                            <td colspan="5" class="text-right">TỔNG CỘNG:</td>
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
                    <span class="label">Tổng số loại vật liệu:</span>
                    <span style="font-weight: bold;">{self.material_model.rowCount()} loại</span>
                </div>
                <div class="total-row">
                    <span class="label">Tổng giá trị xuất kho:</span>
                    <span style="font-weight: bold; font-size: 16px; color: #dc3545;">{total_amount:,.0f} VNĐ</span>
                </div>
            </div>
        """
        
        # Ghi chú nếu có
        if self.text_notes_XK.toPlainText().strip():
            html_content += f"""
            <div class="info-section">
                <h3>GHI CHÚ</h3>
                <p>{self.text_notes_XK.toPlainText()}</p>
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
                    <div>Người nhận</div>
                    <div style="margin-top: 60px;">(Ký tên)</div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 30px; font-style: italic;">
                Phiếu xuất kho được tạo tự động bởi hệ thống quản lý kho
            </div>
        </body>
        </html>
        """
        
        return html_content

    def save_export_to_database(self):
        """Lưu phiếu xuất vào database"""
        if not self.db_connection:
            QtWidgets.QMessageBox.critical(None, "Lỗi", "Không có kết nối cơ sở dữ liệu")
            return False
        
        try:
            cursor = self.db_connection.cursor()
            
            # Sử dụng current_order_id đã được validate
            don_dat_hang_id = self.current_order_id
            
            # Lưu phiếu xuất chính
            cursor.execute("""
                INSERT INTO PhieuXuatKhoVL (maPhieu, donDatHangId, nhanVienXuatId, ngayXuat, lyDoXuat)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                self.label_export_code.text(),
                don_dat_hang_id,
                1,  # ID nhân viên mặc định
                self.edit_date_materials.date().toString("yyyy-MM-dd"),
                self.line_reason_XK.text()
            ))
            
            phieu_xuat_id = cursor.lastrowid
            
            # Lưu chi tiết và cập nhật tồn kho
            for row in range(self.material_model.rowCount()):
                vat_lieu_id = self.material_model.item(row, 0).text()
                so_luong = int(self.material_model.item(row, 2).text())
                don_gia = float(self.material_model.item(row, 4).text().replace(',', ''))
                thanh_tien = float(self.material_model.item(row, 5).text().replace(',', ''))
                
                # Lưu chi tiết vào bảng ChiTietXuatKhoVL
                cursor.execute("""
                    INSERT INTO ChiTietXuatKhoVL (phieuXuatId, vatLieuId, soLuongXuat, donGia, thanhTien)
                    VALUES (%s, %s, %s, %s, %s)
                """, (phieu_xuat_id, vat_lieu_id, so_luong, don_gia, thanh_tien))
                
                # Cập nhật tồn kho
                cursor.execute("""
                    UPDATE VatLieu 
                    SET tonKho = tonKho - %s 
                    WHERE id = %s AND tonKho >= %s
                """, (so_luong, vat_lieu_id, so_luong))
                
                if cursor.rowcount == 0:
                    raise Exception(f"Không đủ tồn kho cho vật liệu ID: {vat_lieu_id}")

            self.db_connection.commit()
            return True
        except Exception as e:
            self.db_connection.rollback()
            QtWidgets.QMessageBox.critical(None, "Lỗi", str(e))
            return False