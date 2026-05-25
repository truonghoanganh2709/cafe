from models.user_model import UserModel
from utils.validators import is_required

class UserController:
    # Controller kiểm tra dữ liệu tài khoản trước khi gọi Model.
    @staticmethod
    def get_users(keyword=""):
        try:
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
    def create_user(username, password, fullname, role):
        if not is_required(username) or not is_required(password) or not is_required(fullname):
            return None, "Tên đăng nhập, mật khẩu và họ tên không được để trống."
        if role not in ["admin", "staff"]:
            return None, "Vai trò không hợp lệ."

        try:
            return UserModel.create(username, password, fullname, role), None
        except Exception as e:
            return None, f"Lỗi thêm user: {str(e)}"

    @staticmethod
    def update_user(user_id, username, password, fullname, role):
        if not user_id:
            return False, "Chưa chọn user cần sửa."
        if not is_required(username) or not is_required(password) or not is_required(fullname):
            return False, "Tên đăng nhập, mật khẩu và họ tên không được để trống."
        if role not in ["admin", "staff"]:
            return False, "Vai trò không hợp lệ."

        try:
            return UserModel.update(user_id, username, password, fullname, role), None
        except Exception as e:
            return False, f"Lỗi sửa user: {str(e)}"

    @staticmethod
    def delete_user(user_id):
        if not user_id:
            return False, "Chưa chọn user cần xóa."
        try:
            return UserModel.delete(user_id), None
        except Exception as e:
            return False, f"Không thể xóa user do đã phát sinh dữ liệu liên quan: {str(e)}"
