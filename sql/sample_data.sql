USE cafe_management;

-- Dữ liệu mẫu tài khoản đăng nhập.
INSERT INTO users (username, password, fullname, role) VALUES
('admin', '123', 'Quản trị viên TLU Café', 'admin'),
('staff1', '123', 'Nhân viên bán hàng 1', 'staff')
ON DUPLICATE KEY UPDATE fullname=VALUES(fullname), role=VALUES(role);

-- Dữ liệu mẫu món café.
INSERT INTO products (product_name, category, price, quantity, image) VALUES
('Cà phê đen', 'Coffee', 25000, 100, 'assets/images/products/default_food.png'),
('Cà phê sữa', 'Coffee', 30000, 100, 'assets/images/products/default_food.png'),
('Bạc xỉu', 'Coffee', 35000, 80, 'assets/images/products/default_food.png'),
('Trà đào', 'Tea', 35000, 80, 'assets/images/products/default_food.png'),
('Trà sữa TLU', 'Tea', 40000, 70, 'assets/images/products/default_food.png'),
('Bánh tiramisu', 'Cake', 45000, 30, 'assets/images/products/default_food.png');
