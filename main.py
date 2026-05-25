import customtkinter as ctk
from views.login_view import LoginFrame
from views.dashboard_view import DashboardFrame
from controllers.order_controller import OrderController

class TLUCafeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1400x800")
        self.title("Hệ thống quản lý quán café TLU")
        
        # Cấu hình giao diện CustomTkinter
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Khởi chạy nâng cấp schema database tự động nếu cần
        self.init_database_schema()
        
        # Biến toàn cục để theo dõi phiên làm việc của người dùng hiện tại
        self.current_user = {
            "id": None,
            "username": None,
            "role": None
        }
        
        self.current_frame = None
        self.show_login()

    def init_database_schema(self):
        """Tự động nâng cấp bảng orders thêm cột status khi khởi động ứng dụng."""
        try:
            OrderController.initialize()
            print("Cơ sở dữ liệu đã được kiểm tra và sẵn sàng.")
        except Exception as e:
            print("Cảnh báo lỗi khởi tạo database schema:", e)

    def show_frame(self, frame_class, *args, **kwargs):
        """Huỷ frame cũ và khởi tạo hiển thị frame mới trên cùng một cửa sổ chính."""
        if self.current_frame is not None:
            self.current_frame.destroy()
            
        self.current_frame = frame_class(self, self, *args, **kwargs)
        self.current_frame.pack(fill="both", expand=True)

    def show_login(self):
        """Quay lại màn hình đăng nhập."""
        self.current_user = {"id": None, "username": None, "role": None}
        self.show_frame(LoginFrame)

    def show_dashboard(self, user_id, username, role):
        """Chuyển đổi sang Dashboard sau khi đăng nhập thành công."""
        self.current_user = {
            "id": user_id,
            "username": username,
            "role": role
        }
        self.show_frame(DashboardFrame, username=username, role=role)

if __name__ == "__main__":
    app = TLUCafeApp()
    app.mainloop()