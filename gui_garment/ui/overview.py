import sys
import math
from PyQt5 import QtCore, QtGui, QtWidgets
from FormDH import Ui_DHWindow  # Import form đặt hàng
from FormXK import Ui_XKWindow  # Import form xuất kho vật liệu
from FormNK import Ui_NKTPWindow  # Import form nhập kho thành phẩm
from FormGH import Ui_GHWindow  # Import form giao hàng

class CircularButton(QtWidgets.QPushButton):
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(text, parent)
        self.icon_text = icon_text
        self.setFixedSize(100, 100)
        self.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 50px;
                font-size: 10px;
                font-weight: bold;
                color: #333;
            }
            QPushButton:hover {
                background-color: #f0f8ff;
                border-color: #007acc;
                color: #007acc;
            }
            QPushButton:pressed {
                background-color: #e6f3ff;
            }
        """)
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        rect = self.rect()
        
        # Background circle
        if self.isDown():
            brush = QtGui.QBrush(QtGui.QColor("#e6f3ff"))
            pen = QtGui.QPen(QtGui.QColor("#007acc"), 2)
        elif self.underMouse():
            brush = QtGui.QBrush(QtGui.QColor("#f0f8ff"))
            pen = QtGui.QPen(QtGui.QColor("#007acc"), 2)
        else:
            brush = QtGui.QBrush(QtGui.QColor("white"))
            pen = QtGui.QPen(QtGui.QColor("#ddd"), 2)
            
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.drawEllipse(rect.adjusted(1, 1, -1, -1))
        
        # Draw icon
        if self.icon_text:
            icon_font = QtGui.QFont()
            icon_font.setPointSize(20)
            painter.setFont(icon_font)
            
            color = "#007acc" if (self.isDown() or self.underMouse()) else "#333"
            painter.setPen(QtGui.QColor(color))
                
            icon_rect = QtCore.QRect(rect.x(), rect.y() + 15, rect.width(), 35)
            painter.drawText(icon_rect, QtCore.Qt.AlignCenter, self.icon_text)
        
        # Draw text
        text_font = QtGui.QFont()
        text_font.setPointSize(9)
        text_font.setBold(True)
        painter.setFont(text_font)
        
        color = "#007acc" if (self.isDown() or self.underMouse()) else "#333"
        painter.setPen(QtGui.QColor(color))
            
        text_rect = QtCore.QRect(rect.x(), rect.y() + 55, rect.width(), 30)
        painter.drawText(text_rect, QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap, self.text())

class CenterLogo(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 180)
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Orange gradient circle
        gradient = QtGui.QRadialGradient(80, 80, 80)
        gradient.setColorAt(0, QtGui.QColor("#ff9500"))
        gradient.setColorAt(1, QtGui.QColor("#ff6b00"))
        
        painter.setBrush(QtGui.QBrush(gradient))
        painter.setPen(QtGui.QPen(QtGui.QColor("#e55a00"), 3))
        painter.drawEllipse(5, 5, 150, 150)
        
        # Logo text
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QtGui.QColor("white"))
        
        text_rect = QtCore.QRect(0, 30, 150, 100)
        painter.drawText(text_rect, QtCore.Qt.AlignCenter, "TỔNG\nHỢP")

class OverviewWindow(QtWidgets.QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.dh_window = None  # Lưu reference tới form đặt hàng
        self.xk_window = None  # Lưu reference tới form xuất kho
        self.nk_window = None  # Lưu reference tới form nhập kho
        self.gh_window = None  # Lưu reference tới form giao hàng/trạng thái
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Bàn làm việc - Hệ thống Quản lý May Mặc")
        self.setFixedSize(1000, 800)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f0f4f8, stop:1 #e8f2ff);
            }
        """)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(50, 40, 50, 40)
        main_layout.setSpacing(20)

        # Header
        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QVBoxLayout(header_widget)
        header_layout.setSpacing(5)
        
        # Welcome message
        lbl_welcome = QtWidgets.QLabel(f"Xin chào, {self.current_user['username']}!")
        lbl_welcome.setAlignment(QtCore.Qt.AlignCenter)
        lbl_welcome.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        header_layout.addWidget(lbl_welcome)

        # Subtitle
        lbl_subtitle = QtWidgets.QLabel("Hệ thống Quản lý Công ty May Mặc")
        lbl_subtitle.setAlignment(QtCore.Qt.AlignCenter)
        lbl_subtitle.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #7f8c8d;
                margin-bottom: 10px;
            }
        """)
        header_layout.addWidget(lbl_subtitle)
        
        main_layout.addWidget(header_widget)

        # Circular layout container
        circle_container = QtWidgets.QWidget()
        circle_container.setFixedHeight(600)
        
        # Create center logo
        self.center_logo = CenterLogo()
        
        # Create circular buttons
        self.buttons = [
            CircularButton("Đặt hàng", "📋"),
            CircularButton("Xuất kho\nvật liệu", "📤"),
            CircularButton("Nhập kho\nthành phẩm", "📥"),
            CircularButton("Trạng thái\ngiao hàng", "📊"),  # Cập nhật text cho rõ ràng hơn
            CircularButton("Quản lý\nhóa đơn", "🏪"),
            CircularButton("Báo cáo", "📈"),
            CircularButton("Cài đặt", "⚙️"),
            CircularButton("Hỗ trợ", "❓")
        ]
        
        # Position buttons in circle
        self.position_buttons_in_circle(circle_container)
        
        main_layout.addWidget(circle_container)

        # Footer
        footer_widget = QtWidgets.QWidget()
        footer_layout = QtWidgets.QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(0, 20, 0, 0)
        
        # Logout button
        logout_btn = QtWidgets.QPushButton("Đăng xuất")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        
        footer_layout.addStretch()
        footer_layout.addWidget(logout_btn)
        
        main_layout.addWidget(footer_widget)

        # Connect button events
        self.buttons[0].clicked.connect(self.open_order)     # Đặt hàng
        self.buttons[1].clicked.connect(self.open_dispatch)  # Xuất kho vật liệu
        self.buttons[2].clicked.connect(self.open_receive)   # Nhập kho thành phẩm
        self.buttons[3].clicked.connect(self.open_status)    # Trạng thái giao hàng - FormGH
        self.buttons[4].clicked.connect(self.open_warehouse)
        self.buttons[5].clicked.connect(self.open_reports)
        self.buttons[6].clicked.connect(self.open_settings)
        self.buttons[7].clicked.connect(self.open_help)
        
        self.center_window()

    def position_buttons_in_circle(self, container):
        # Center position
        center_x = 450
        center_y = 300
        radius = 200
        
        # Position center logo
        self.center_logo.setParent(container)
        self.center_logo.move(center_x - 90, center_y - 90)
        
        # Position buttons in circle
        for i, button in enumerate(self.buttons):
            angle = (i * 360 / len(self.buttons)) * (math.pi / 180)
            x = center_x + radius * math.cos(angle) - 50
            y = center_y + radius * math.sin(angle) - 50
            
            button.setParent(container)
            button.move(int(x), int(y))

    def center_window(self):
        frame_geo = self.frameGeometry()
        screen_center = QtWidgets.QDesktopWidget().availableGeometry().center()
        frame_geo.moveCenter(screen_center)
        self.move(frame_geo.topLeft())

    def logout(self):
        reply = QtWidgets.QMessageBox.question(
            self, 'Đăng xuất', 
            'Bạn có chắc chắn muốn đăng xuất?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            # Đóng tất cả các form đang mở
            if self.dh_window:
                self.dh_window.close()
            if self.xk_window:
                self.xk_window.close()
            if self.nk_window:
                self.nk_window.close()
            if self.gh_window:
                self.gh_window.close()
            
            self.close()
            from login import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()

    def open_order(self):
        """Mở form đặt hàng"""
        try:
            # Nếu form đặt hàng đã mở thì đưa lên trước
            if self.dh_window and self.dh_window.isVisible():
                self.dh_window.raise_()
                self.dh_window.activateWindow()
                return
            
            # Tạo form đặt hàng mới
            self.dh_window = QtWidgets.QMainWindow()
            self.dh_ui = Ui_DHWindow()
            self.dh_ui.setupUi(self.dh_window)
            
            # Thiết lập tiêu đề và icon
            self.dh_window.setWindowTitle("Quản lý đặt hàng - Garment Management System")
            
            # Hiển thị form
            self.dh_window.show()
            
            # Kết nối sự kiện đóng form
            self.dh_window.closeEvent = self.on_dh_window_closed
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi", 
                f"Không thể mở form đặt hàng:\n{str(e)}"
            )

    def open_dispatch(self):
        """Mở form xuất kho vật liệu"""
        try:
            # Nếu form xuất kho đã mở thì đưa lên trước
            if self.xk_window and self.xk_window.isVisible():
                self.xk_window.raise_()
                self.xk_window.activateWindow()
                return
            
            # Tạo form xuất kho mới
            self.xk_window = QtWidgets.QMainWindow()
            self.xk_ui = Ui_XKWindow()
            self.xk_ui.setupUi(self.xk_window)
            
            # Thiết lập tiêu đề
            self.xk_window.setWindowTitle("Quản lý xuất kho vật liệu - Garment Management System")
            
            # Hiển thị form
            self.xk_window.show()
            
            # Kết nối sự kiện đóng form
            self.xk_window.closeEvent = self.on_xk_window_closed
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi", 
                f"Không thể mở form xuất kho vật liệu:\n{str(e)}"
            )

    def open_receive(self):
        """Mở form nhập kho thành phẩm"""
        try:
            # Nếu form nhập kho đã mở thì đưa lên trước
            if self.nk_window and self.nk_window.isVisible():
                self.nk_window.raise_()
                self.nk_window.activateWindow()
                return
            
            # Tạo form nhập kho mới
            self.nk_window = QtWidgets.QMainWindow()
            self.nk_ui = Ui_NKTPWindow()
            self.nk_ui.setupUi(self.nk_window)
            
            # Thiết lập tiêu đề
            self.nk_window.setWindowTitle("Nhập kho thành phẩm - Garment Management System")
            
            # Hiển thị form
            self.nk_window.show()
            
            # Kết nối sự kiện đóng form
            self.nk_window.closeEvent = self.on_nk_window_closed
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi", 
                f"Không thể mở form nhập kho thành phẩm:\n{str(e)}"
            )

    def open_status(self):
        """Mở form quản lý giao hàng và trạng thái đơn hàng"""
        try:
            # Nếu form giao hàng đã mở thì đưa lên trước
            if self.gh_window and self.gh_window.isVisible():
                self.gh_window.raise_()
                self.gh_window.activateWindow()
                return
            
            # Tạo form giao hàng mới
            self.gh_window = QtWidgets.QMainWindow()
            self.gh_ui = Ui_GHWindow()
            self.gh_ui.setupUi(self.gh_window)
            
            # Thiết lập tiêu đề
            self.gh_window.setWindowTitle("Quản lý giao hàng & trạng thái đơn hàng - Garment Management System")
            
            # Hiển thị form
            self.gh_window.show()
            
            # Kết nối sự kiện đóng form
            self.gh_window.closeEvent = self.on_gh_window_closed
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi", 
                f"Không thể mở form quản lý giao hàng:\n{str(e)}"
            )

    def on_dh_window_closed(self, event):
        """Xử lý khi form đặt hàng được đóng"""
        self.dh_window = None
        event.accept()

    def on_xk_window_closed(self, event):
        """Xử lý khi form xuất kho được đóng"""
        self.xk_window = None
        event.accept()

    def on_nk_window_closed(self, event):
        """Xử lý khi form nhập kho được đóng"""
        self.nk_window = None
        event.accept()

    def on_gh_window_closed(self, event):
        """Xử lý khi form giao hàng được đóng"""
        self.gh_window = None
        event.accept()

    def open_warehouse(self):
        QtWidgets.QMessageBox.information(self, "Quản lý hóa đơn", "Mở chức năng Quản lý hóa đơn...")

    def open_reports(self):
        QtWidgets.QMessageBox.information(self, "Báo cáo", "Mở chức năng Báo cáo...")

    def open_settings(self):
        QtWidgets.QMessageBox.information(self, "Cài đặt", "Mở chức năng Cài đặt...")

    def open_help(self):
        QtWidgets.QMessageBox.information(self, "Hỗ trợ", "Mở chức năng Hỗ trợ...")

    def closeEvent(self, event):
        """Xử lý khi đóng window overview"""
        # Đóng tất cả các form đang mở
        if self.dh_window:
            self.dh_window.close()
        if self.xk_window:
            self.xk_window.close()
        if self.nk_window:
            self.nk_window.close()
        if self.gh_window:
            self.gh_window.close()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dummy_user = {"username": "Trương Đức Huy", "role": "manager"}
    win = OverviewWindow(dummy_user)
    win.show()
    sys.exit(app.exec_())