from models.user_model import UserModel

class AuthController:
    # Controller xử lý đăng nhập và trả thông tin người dùng cho giao diện.
    @staticmethod
    def login(username, password):
        if not username or not password:
            return None, "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu."

        try:
            user = UserModel.authenticate(username, password)
            if not user:
                return None, "Sai tài khoản hoặc mật khẩu."
            if len(user) >= 5 and user[4] == "inactive":
                return None, "Tài khoản đã bị vô hiệu hóa. Vui lòng liên hệ quản trị viên."
            return user[:4], None
        except Exception as e:
            return None, f"Lỗi đăng nhập: {str(e)}"
