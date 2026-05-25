USE cafe_management;

-- Dữ liệu mẫu tài khoản đăng nhập.
INSERT INTO users (username, password, fullname, role) VALUES
('admin', '123', 'Quản trị viên TLU Café', 'admin'),
('staff1', '123', 'Nhân viên bán hàng 1', 'staff')
ON DUPLICATE KEY UPDATE fullname=VALUES(fullname), role=VALUES(role);

-- Dữ liệu mẫu món café.
INSERT INTO products (product_name, category, price, quantity, image) VALUES
('Cà phê đen', 'Coffee', 25000, 100, ''),
('Cà phê sữa', 'Coffee', 30000, 100, ''),
('Bạc xỉu', 'Coffee', 35000, 80, ''),
('Trà đào', 'Tea', 35000, 80, ''),
('Trà sữa TLU', 'Tea', 40000, 70, ''),
('Bánh tiramisu', 'Cake', 45000, 30, '');
