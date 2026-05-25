from models.user_model import UserModel
from utils.validators import is_required

class UserController:
    # Controller kiểm tra dữ liệu tài khoản trước khi gọi Model.
    @staticmethod
    def initialize():
        UserModel.ensure_status_column()

    @staticmethod
    def get_users(keyword=""):
        try:
            UserModel.ensure_status_column()
            return UserModel.get_all(keyword)
        except Exception as e:
            print("Lỗi lấy danh sách user:", e)
            return []

    @staticmethod
    def get_user(user_id):
        try:
            return UserModel.get_by_id(user_id)
        except Exception as e:
            print("Lỗi lấy user:", e)
            return None

    @staticmethod
    def create_user(username, password, fullname, role, status="active"):
        if not is_required(username) or not is_required(password) or not is_required(fullname):
            return None, "Tên đăng nhập, mật khẩu và họ tên không được để trống."
        if role not in ["admin", "staff"]:
            return None, "Vai trò không hợp lệ."
        if status not in ["active", "inactive"]:
            return None, "Trạng thái không hợp lệ."
        if UserModel.username_exists(username):
            return None, "Tên đăng nhập đã tồn tại. Vui lòng chọn tên đăng nhập khác."

        try:
            return UserModel.create(username, password, fullname, role, status), None
        except Exception as e:
            return None, f"Lỗi thêm user: {str(e)}"

    @staticmethod
    def update_user(user_id, username, password, fullname, role, status="active"):
        if not user_id:
            return False, "Chưa chọn user cần sửa."
        if not is_required(username) or not is_required(password) or not is_required(fullname):
            return False, "Tên đăng nhập, mật khẩu và họ tên không được để trống."
        if role not in ["admin", "staff"]:
            return False, "Vai trò không hợp lệ."
        if status not in ["active", "inactive"]:
            return False, "Trạng thái không hợp lệ."
        if UserModel.username_exists(username, user_id):
            return False, "Tên đăng nhập đã tồn tại. Vui lòng chọn tên đăng nhập khác."

        try:
            return UserModel.update(user_id, username, password, fullname, role, status), None
        except Exception as e:
            return False, f"Lỗi sửa user: {str(e)}"

    @staticmethod
    def set_user_status(user_id, status):
        if not user_id:
            return False, "Chưa chọn user."
        if status not in ["active", "inactive"]:
            return False, "Trạng thái không hợp lệ."
        try:
            return UserModel.set_status(user_id, status), None
        except Exception as e:
            return False, f"Lỗi cập nhật trạng thái user: {str(e)}"

    @staticmethod
    def delete_user(user_id):
        # Không xóa user khỏi database, chỉ chuyển inactive để giữ lịch sử hóa đơn.
        return UserController.set_user_status(user_id, "inactive")
