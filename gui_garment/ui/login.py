import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import pymysql as mysql
from pymysql import Error
from overview import OverviewWindow

class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_connection = None
        self.current_user = None
        self.init_ui()
        self.connect_to_database()

    def init_ui(self):
        self.setWindowTitle("Đăng nhập")
        self.setFixedSize(450, 600)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)
        
        # Set window icon (optional)
        # self.setWindowIcon(QtGui.QIcon('icon.png'))
        
        # Central widget với background gradient
        central = QtWidgets.QWidget()
        central.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d4a574, stop:1 #a67c52);
            }
        """)
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header section
        header_widget = QtWidgets.QWidget()
        header_widget.setFixedHeight(120)
        header_widget.setStyleSheet("background: transparent;")
        header_layout = QtWidgets.QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 30, 0, 0)
        
        # Logo/Icon (you can add an actual logo here)
        logo_label = QtWidgets.QLabel("🏭")
        logo_label.setAlignment(QtCore.Qt.AlignCenter)
        logo_label.setStyleSheet("""
            font-size: 48px;
            color: white;
            margin-bottom: 10px;
        """)
        header_layout.addWidget(logo_label)
        
        main_layout.addWidget(header_widget)
        
        # Login form container
        form_container = QtWidgets.QWidget()
        form_container.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 20px;
            }
        """)
        
        form_layout = QtWidgets.QVBoxLayout(form_container)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(25)
        
        # Title
        title = QtWidgets.QLabel("Đăng nhập")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        form_layout.addWidget(title)
        

        
        # Username field
        username_container = QtWidgets.QWidget()
        username_layout = QtWidgets.QVBoxLayout(username_container)
        username_layout.setContentsMargins(0, 0, 0, 0)
        username_layout.setSpacing(5)
        
        username_label = QtWidgets.QLabel("Tên đăng nhập")
        username_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #34495e;
            }
        """)
        username_layout.addWidget(username_label)
        
        self.line_username = QtWidgets.QLineEdit()
        self.line_username.setPlaceholderText("Nhập tên đăng nhập")
        self.line_username.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid #ecf0f1;
                border-radius: 10px;
                font-size: 14px;
                background: #f8f9fa;
            }
            QLineEdit:focus {
                border-color: #667eea;
                background: white;
            }
            QLineEdit:hover {
                border-color: #bdc3c7;
            }
        """)
        username_layout.addWidget(self.line_username)
        form_layout.addWidget(username_container)
        
        # Password field
        password_container = QtWidgets.QWidget()
        password_layout = QtWidgets.QVBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(5)
        
        password_label = QtWidgets.QLabel("Mật khẩu")
        password_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #34495e;
            }
        """)
        password_layout.addWidget(password_label)
        
        self.line_password = QtWidgets.QLineEdit()
        self.line_password.setPlaceholderText("Nhập mật khẩu")
        self.line_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.line_password.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid #ecf0f1;
                border-radius: 10px;
                font-size: 14px;
                background: #f8f9fa;
            }
            QLineEdit:focus {
                border-color: #667eea;
                background: white;
            }
            QLineEdit:hover {
                border-color: #bdc3c7;
            }
        """)
        password_layout.addWidget(self.line_password)
        form_layout.addWidget(password_container)
    
        
        # Login button
        self.btn_login = QtWidgets.QPushButton("Đăng nhập")
        self.btn_login.setFixedHeight(45)
        self.btn_login.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_login.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a6fd8, stop:1 #6a4190);
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4e5bc6, stop:1 #5e387e);
            }
        """)
        self.btn_login.clicked.connect(self.attempt_login)
        form_layout.addWidget(self.btn_login)
        
        # Status label for error messages
        self.lbl_status = QtWidgets.QLabel("")
        self.lbl_status.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_status.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 12px;
                padding: 8px;
                border-radius: 6px;
                background: rgba(231, 76, 60, 0.1);
            }
        """)
        self.lbl_status.hide()  # Hide initially
        form_layout.addWidget(self.lbl_status)
        
        # Add some stretch at the bottom
        form_layout.addStretch()
        
        # Add form container to main layout with margins
        container_wrapper = QtWidgets.QWidget()
        container_wrapper.setStyleSheet("background: transparent;")
        wrapper_layout = QtWidgets.QHBoxLayout(container_wrapper)
        wrapper_layout.setContentsMargins(25, 0, 25, 25)
        wrapper_layout.addWidget(form_container)
        
        main_layout.addWidget(container_wrapper)
        

        # Connect Enter key to login
        self.line_username.returnPressed.connect(self.line_password.setFocus)
        self.line_password.returnPressed.connect(self.attempt_login)
        
        # Center window on screen
        self.center_window()

    def center_window(self):
        screen = QtWidgets.QApplication.desktop().screenGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

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
            QtWidgets.QMessageBox.critical(
                self, "Lỗi kết nối",
                f"Không thể kết nối đến cơ sở dữ liệu:\n{e}"
            )
            sys.exit(1)

    def show_error(self, message):
        self.lbl_status.setText(message)
        self.lbl_status.show()
        # Auto hide after 5 seconds
        QtCore.QTimer.singleShot(5000, self.lbl_status.hide)

    def attempt_login(self):
        username = self.line_username.text().strip()
        password = self.line_password.text().strip()
        
        # Hide previous error messages
        self.lbl_status.hide()
        
        if not username or not password:
            self.show_error("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
            return

        # Show loading state
        self.btn_login.setText("Đang đăng nhập...")
        self.btn_login.setEnabled(False)

        try:
            cursor = self.db_connection.cursor()
            sql = """
            SELECT id, role, fullname
            FROM Users
            WHERE username = %s AND password = %s
            LIMIT 1
            """
            cursor.execute(sql, (username, password))
            result = cursor.fetchone()
            
            if result:
                user_id, role, fullname = result
                self.current_user = {
                    "id": user_id,
                    "username": username,
                    "role": role,
                    "fullname": fullname if fullname else username
                }
                self.overview = OverviewWindow(self.current_user)
                self.overview.show()
                self.close()
            else:
                self.lbl_status.setText("Sai tên đăng nhập hoặc mật khẩu.")
                
        except Error as e:
            QtWidgets.QMessageBox.critical(
                self, "Lỗi truy vấn",
                f"Đã xảy ra lỗi khi kiểm tra đăng nhập:\n{e}"
            )
        finally:
            # Reset button state
            self.btn_login.setText("Đăng nhập")
            self.btn_login.setEnabled(True)

    def fade_out_effect(self):
        """Create a smooth fade out effect when logging in successfully"""
        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        self.animation = QtCore.QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.open_overview)
        self.animation.start()

    def open_overview(self):
        """Open overview window after fade out"""
        self.overview = OverviewWindow(self.current_user)
        self.overview.show()
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Optional: Set application font
    font = QtGui.QFont("Segoe UI", 9)
    app.setFont(font)
    
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())