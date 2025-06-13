CREATE DATABASE IF NOT EXISTS gar_db;
USE gar_db;

-- Bảng users
CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname NVARCHAR(50) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,       
    password VARCHAR(255) NOT NULL,       
    role ENUM('order','warehouse','delivery','admin') NOT NULL
);

-- Bảng nhân viên
CREATE TABLE NhanVien (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maNhanVien VARCHAR(20) UNIQUE NOT NULL,
    tenNhanVien VARCHAR(100) NOT NULL,
    chucVu VARCHAR(50),
    boPhan VARCHAR(50),
    soDienThoai VARCHAR(15),
    email VARCHAR(100),
    diaChi TEXT
);
-- Bảng khách hàng
CREATE TABLE KhachHang (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maKhachHang VARCHAR(20) UNIQUE NOT NULL,
    tenKhachHang VARCHAR(100) NOT NULL,
    diaChi TEXT,
    soDienThoai VARCHAR(15),
    CMND VARCHAR(20),
    email VARCHAR(100)
);

-- Bảng vật liệu
CREATE TABLE VatLieu (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maVatLieu VARCHAR(20) UNIQUE NOT NULL,
    tenVatLieu VARCHAR(100) NOT NULL,
    loaiVatLieuId INT,
    donViTinh VARCHAR(20) NOT NULL,
    donGia INT NOT NULL,
    tonKho INT DEFAULT 0
);

-- Bảng sản phẩm (thành phẩm)
CREATE TABLE SanPham (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maSanPham VARCHAR(20) UNIQUE NOT NULL,
    tenSanPham VARCHAR(100) NOT NULL,
    loaiSanPham VARCHAR(50),
    size VARCHAR(20),
    mauSac VARCHAR(30),
    giaBan DECIMAL(15,2) NOT NULL,
    hinhAnh VARCHAR(255),
    soLuongTon INT DEFAULT 0,
    giaTriTon DECIMAL(15,2) DEFAULT 0
);



-- Bảng đơn đặt hàng
CREATE TABLE DonDatHang (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maDonHang VARCHAR(20) UNIQUE NOT NULL,
    khachHangId INT,
    nhanVienId INT, -- nhân viên tiếp nhận đơn hàng
    ngayDatHang TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ngayGiaoHangDuKien DATE,
    tongTien DECIMAL(15,2) DEFAULT 0,
    tienDatCoc DECIMAL(15,2) DEFAULT 0,
    FOREIGN KEY (khachHangId) REFERENCES KhachHang(id),
    FOREIGN KEY (nhanVienId) REFERENCES NhanVien(id)
);

-- Bảng chi tiết đơn đặt hàng
CREATE TABLE ChiTietDonHang (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donDatHangId INT,
    sanPhamId INT,
    soLuong INT NOT NULL,
    giaBan DECIMAL(15,2) NOT NULL,
    thanhTien DECIMAL(15,2) NOT NULL,
    FOREIGN KEY (donDatHangId) REFERENCES DonDatHang(id) ON DELETE CASCADE,
    FOREIGN KEY (sanPhamId) REFERENCES SanPham(id)
);

-- Bảng phiếu xuất kho vật liệu
CREATE TABLE PhieuXuatKhoVL (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maPhieu VARCHAR(50) UNIQUE NOT NULL,
    donDatHangId INT,
    nhanVienXuatId INT,
    ngayXuat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lyDoXuat VARCHAR(100),
    FOREIGN KEY (donDatHangId) REFERENCES DonDatHang(id),
    FOREIGN KEY (nhanVienXuatId) REFERENCES NhanVien(id)
);

-- Bảng chi tiết phiếu xuất kho vật liệu
CREATE TABLE ChiTietXuatKhoVL (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phieuXuatId INT,
    vatLieuId INT,
    soLuongXuat DECIMAL(10,3) NOT NULL,
    donGia DECIMAL(15,2),
    thanhTien DECIMAL(15,2),
    FOREIGN KEY (phieuXuatId) REFERENCES PhieuXuatKhoVL(id) ON DELETE CASCADE,
    FOREIGN KEY (vatLieuId) REFERENCES VatLieu(id)
);

-- Bảng phiếu nhập kho thành phẩm
CREATE TABLE PhieuNhapKhoTP (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maPhieu VARCHAR(20) UNIQUE NOT NULL,
    nhanVienNhapId INT,
    ngayNhap TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ghiChu TEXT,
    FOREIGN KEY (nhanVienNhapId) REFERENCES NhanVien(id)
);

-- Bảng chi tiết phiếu nhập kho thành phẩm
CREATE TABLE ChiTietNhapKhoTP (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phieuNhapId INT,
    sanPhamId INT,
    soLuongNhap INT NOT NULL,
    soLuongDatChuan INT DEFAULT 0,
    soLuongLoi INT DEFAULT 0,
    giaThanh DECIMAL(15,2),
    FOREIGN KEY (phieuNhapId) REFERENCES PhieuNhapKhoTP(id) ON DELETE CASCADE,
    FOREIGN KEY (sanPhamId) REFERENCES SanPham(id)
);


-- Bảng phiếu giao hàng
CREATE TABLE PhieuGiaoHang (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maPhieu VARCHAR(20) UNIQUE NOT NULL,
    donDatHangId INT,
    nhanVienGiaoId INT,
    ngayGiao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    diaChiGiao TEXT,
    nguoiNhan VARCHAR(100),
    sdtNguoiNhan VARCHAR(15),
    trangThai ENUM('Chờ giao', 'Đang giao', 'Đã giao', 'Giao không thành công') DEFAULT 'Chờ giao',
    ghiChu TEXT,
    FOREIGN KEY (donDatHangId) REFERENCES DonDatHang(id),
    FOREIGN KEY (nhanVienGiaoId) REFERENCES NhanVien(id)
);

-- Bảng chi tiết phiếu giao hàng
CREATE TABLE ChiTietGiaoHang (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phieuGiaoHangId INT,
    sanPhamId INT,
    soLuongGiao INT NOT NULL,
    FOREIGN KEY (phieuGiaoHangId) REFERENCES PhieuGiaoHang(id) ON DELETE CASCADE,
    FOREIGN KEY (sanPhamId) REFERENCES SanPham(id)
);

-- Insert dữ liệu mẫu cho hệ thống quản lý công ty may mặc

INSERT INTO Users (fullname,username, password, role) VALUES
    ('Nguyễn Phương Ngân','nvtiepnhan1',     '123',     'order'),
    ('Trương Đức Huy','nvkho1', '123', 'warehouse'),
    ('Vũ Khánh Nam','nvgh1',  '123',  'delivery'),
    ('Admin','admin',          'admin',     'admin');
-- Thêm nhân viên
INSERT INTO NhanVien (maNhanVien, tenNhanVien, chucVu, boPhan, soDienThoai, email, diaChi) VALUES
('NV001', 'Nguyễn Văn A', 'Tiếp nhận đơn hàng', 'Sales', '0901111222', 'a.nguyen@garment.com', 'Hà Nội'),
('NV002', 'Trần Thị B', 'Quản lý kho', 'Kho', '0903333444', 'b.tran@garment.com', 'Hồ Chí Minh'),
('NV003', 'Lê Văn C', 'Giao hàng', 'Logistics', '0905555666', 'c.le@garment.com', 'Đà Nẵng');

-- Thêm khách hàng
INSERT INTO KhachHang (maKhachHang, tenKhachHang, diaChi, soDienThoai, CMND, email) VALUES
('KH001', 'Nguyễn Văn An', '123 Lê Lợi, Q1, TP.HCM', '0901234567', '123456789', 'nguyenvanan@email.com'),
('KH002', 'Trần Thị Bình', '456 Nguyễn Huệ, Q1, TP.HCM', '0907654321', '987654321', 'tranthibibh@email.com'),
('KH003', 'Lê Minh Cường', '789 Điện Biên Phủ, Q3, TP.HCM', '0912345678', '456789123', 'leminhcuong@email.com'),
('KH004', 'Phạm Thị Dung', '321 Lý Tự Trọng, Q1, TP.HCM', '0923456789', '789123456', 'phamthidung@email.com'),
('KH005', 'Hoàng Văn Em', '654 Pasteur, Q3, TP.HCM', '0934567890', '321654987', 'hoangvanem@email.com');

-- Thêm vật liệu
INSERT INTO VatLieu (maVatLieu, tenVatLieu, loaiVatLieuId, donViTinh,donGia, tonKho) VALUES
('VL001', 'Vải cotton 100%', 1, 'mét', 75000, 5000),
('VL002', 'Vải polyester', 1, 'mét', 60000, 4000),
('VL003', 'Vải jean', 1, 'mét', 85000, 3000),
('VL004', 'Chỉ may màu trắng', 2, 'cuộn', 12000, 2000),
('VL005', 'Chỉ may màu đen', 2, 'cuộn', 12000, 1800),
('VL006', 'Khuy áo nhựa', 3, 'cái', 500, 10000),
('VL007', 'Khuy áo kim loại', 3, 'cái', 1500, 6000),
('VL008', 'Dây kéo', 4, 'cái', 4000, 3000),
('VL009', 'Nhãn mác thương hiệu', 5, 'cái', 2000, 15000),
('VL010', 'Vải lining', 1, 'mét', 40000, 3500),
('VL011', 'Vải thun 4 chiều', 1, 'mét', 70000, 4000),
('VL012', 'Vải kaki', 1, 'mét', 80000, 3000),
('VL013', 'Vải dệt kim', 1, 'mét', 65000, 2500),
('VL014', 'Chỉ may màu xanh dương', 2, 'cuộn', 12000, 1000),
('VL015', 'Chỉ thêu', 2, 'cuộn', 18000, 800),
('VL016', 'Khuy bấm nhựa', 3, 'cái', 1000, 5000),
('VL017', 'Khóa bấm kim loại', 3, 'cái', 2000, 3000),
('VL018', 'Dây thun bản nhỏ', 4, 'mét', 3000, 2000),
('VL019', 'Dây thun bản to', 4, 'mét', 5000, 2000),
('VL020', 'Mếch vải', 6, 'mét', 10000, 1500);
-- Thêm sản phẩm
INSERT INTO SanPham (maSanPham, tenSanPham, loaiSanPham, size, mauSac, giaBan, hinhAnh, soLuongTon, giaTriTon) VALUES
('SP001', 'Áo sơ mi nam trắng', 'Áo sơ mi', 'M', 'Trắng', 250000.00, 'aosomi_nam_trang.jpg', 50, 12500000.00),
('SP002', 'Áo sơ mi nam xanh', 'Áo sơ mi', 'L', 'Xanh', 250000.00, 'aosomi_nam_xanh.jpg', 30, 7500000.00),
('SP003', 'Quần âu nam đen', 'Quần âu', 'L', 'Đen', 350000.00, 'quanau_nam_den.jpg', 25, 8750000.00),
('SP004', 'Áo polo nữ hồng', 'Áo polo', 'S', 'Hồng', 180000.00, 'polo_nu_hong.jpg', 40, 7200000.00),
('SP005', 'Quần jean nam xanh', 'Quần jean', 'M', 'Xanh đậm', 400000.00, 'jean_nam_xanh.jpg', 35, 14000000.00),
('SP006', 'Áo thun nữ trắng', 'Áo thun', 'S', 'Trắng', 120000.00, 'thun_nu_trang.jpg', 60, 7200000.00),
('SP007', 'Váy công sở đen', 'Váy', 'M', 'Đen', 280000.00, 'vay_congso_den.jpg', 20, 5600000.00),
('SP008', 'Áo blazer nữ xám', 'Áo blazer', 'L', 'Xám', 450000.00, 'blazer_nu_xam.jpg', 15, 6750000.00);


-- Thêm đơn đặt hàng
INSERT INTO DonDatHang (maDonHang, khachHangId, nhanVienId, ngayDatHang, ngayGiaoHangDuKien, tongTien, tienDatCoc) VALUES
('DH001', 1, 2, '2024-12-01 09:00:00', '2024-12-05', 750000.00, 200000.00),
('DH002', 2, 2, '2024-12-02 10:30:00', '2024-12-06', 530000.00, 150000.00),
('DH003', 3, 2, '2024-12-03 14:15:00', '2024-12-07', 1200000.00, 300000.00),
('DH004', 4, 2, '2024-12-04 11:20:00', '2024-12-08', 460000.00, 100000.00),
('DH005', 5, 2, '2024-12-05 16:45:00', '2024-12-09', 820000.00, 200000.00);

-- Thêm chi tiết đơn hàng
INSERT INTO ChiTietDonHang (donDatHangId, sanPhamId, soLuong, giaBan, thanhTien) VALUES
-- Đơn hàng 1
(1, 1, 2, 250000.00, 500000.00),
(1, 3, 1, 250000.00, 250000.00),
-- Đơn hàng 2
(2, 4, 2, 180000.00, 360000.00),
(2, 6, 1, 120000.00, 120000.00),
(2, 1, 1, 250000.00, 50000.00),
-- Đơn hàng 3
(3, 5, 2, 400000.00, 800000.00),
(3, 8, 1, 450000.00, 400000.00),
-- Đơn hàng 4
(4, 7, 1, 280000.00, 280000.00),
(4, 6, 1, 120000.00, 120000.00),
(4, 4, 1, 180000.00, 60000.00),
-- Đơn hàng 5
(5, 2, 2, 250000.00, 500000.00),
(5, 3, 1, 350000.00, 320000.00);

-- Thêm phiếu xuất kho vật liệu
INSERT INTO PhieuXuatKhoVL (maPhieu, donDatHangId, nhanVienXuatId, ngayXuat, lyDoXuat) VALUES
('XK001', 1, 3, '2024-12-01 10:00:00', 'Sản xuất đơn hàng DH001'),
('XK002', 2, 3, '2024-12-02 11:00:00', 'Sản xuất đơn hàng DH002'),
('XK003', 3, 3, '2024-12-03 15:00:00', 'Sản xuất đơn hàng DH003');

-- Thêm chi tiết xuất kho vật liệu
INSERT INTO ChiTietXuatKhoVL (phieuXuatId, vatLieuId, soLuongXuat, donGia, thanhTien) VALUES
-- Phiếu XK001
(1, 1, 5.5, 50000.00, 275000.00),
(1, 4, 3, 15000.00, 45000.00),
(1, 6, 10, 1000.00, 10000.00),
-- Phiếu XK002
(2, 1, 3.2, 50000.00, 160000.00),
(2, 5, 2, 15000.00, 30000.00),
(2, 6, 8, 1000.00, 8000.00),
-- Phiếu XK003
(3, 3, 4.8, 70000.00, 336000.00),
(3, 2, 2.5, 45000.00, 112500.00),
(3, 8, 3, 25000.00, 75000.00);

-- Thêm phiếu nhập kho thành phẩm
INSERT INTO PhieuNhapKhoTP (maPhieu, nhanVienNhapId, ngayNhap, ghiChu) VALUES
('NK001', 3, '2024-12-03 08:00:00', 'Nhập thành phẩm từ xưởng sản xuất'),
('NK002', 3, '2024-12-04 09:30:00', 'Nhập thành phẩm batch 2'),
('NK003', 3, '2024-12-05 10:15:00', 'Nhập thành phẩm batch 3');

-- Thêm chi tiết nhập kho thành phẩm
INSERT INTO ChiTietNhapKhoTP (phieuNhapId, sanPhamId, soLuongNhap, soLuongDatChuan, soLuongLoi, giaThanh) VALUES
-- Phiếu NK001
(1, 1, 25, 24, 1, 180000.00),
(1, 3, 15, 15, 0, 250000.00),
-- Phiếu NK002
(2, 4, 20, 19, 1, 130000.00),
(2, 6, 30, 28, 2, 80000.00),
-- Phiếu NK003
(3, 5, 18, 17, 1, 300000.00),
(3, 8, 8, 8, 0, 320000.00);

--- - Thêm phiếu giao hàng
INSERT INTO PhieuGiaoHang (maPhieu, donDatHangId, nhanVienGiaoId, ngayGiao, diaChiGiao, nguoiNhan, sdtNguoiNhan, trangThai, ghiChu) VALUES
('GH001', 1, 5, '2024-12-05 08:30:00', '123 Lê Lợi, Q1, TP.HCM', 'Nguyễn Văn An', '0901234567', 'Đã giao', 'Giao hàng thành công'),
('GH002', 2, 5, '2024-12-06 09:45:00', '456 Nguyễn Huệ, Q1, TP.HCM', 'Trần Thị Bình', '0907654321', 'Đã giao', 'Khách hàng hài lòng'),
('GH003', 4, 5, '2024-12-08 14:20:00', '321 Lý Tự Trọng, Q1, TP.HCM', 'Phạm Thị Dung', '0923456789', 'Đang giao', 'Đang trên đường giao');

-- -- Thêm chi tiết giao hàng
INSERT INTO ChiTietGiaoHang (phieuGiaoHangId, sanPhamId, soLuongGiao) VALUES
-- Phiếu GH001
(1, 1, 2),
(1, 3, 1),
-- Phiếu GH002
(2, 4, 2),
(2, 6, 1),
-- Phiếu GH003
(3, 7, 1),
(3, 6, 1),
(3, 4, 1);
