import os
import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import Canvas, messagebox
from config.database import connect_db
from controllers.auth_controller import AuthController

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="white", corner_radius=0)
        self.controller = controller

        # Thiết lập cột hàng (trái 4/7, phải 3/7)
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        self.bg_path = os.path.join(BASE_DIR, "assets", "images", "coffee_bg.jpg")

        # ================= LEFT IMAGE =================
        self.left_frame = ctk.CTkFrame(self, corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        self.canvas = Canvas(
            self.left_frame,
            highlightthickness=0,
            bd=0,
            bg="black"
        )
        self.canvas.pack(fill="both", expand=True)

        # Mở ảnh gốc
        if os.path.exists(self.bg_path):
            self.original_image = Image.open(self.bg_path)
        else:
            self.original_image = None
            print("Warning: Background image not found at", self.bg_path)

        self.bg_photo = None
        self.canvas.bind("<Configure>", self.resize_bg)

        # ================= RIGHT SIDE =================
        self.right_frame = ctk.CTkFrame(
            self,
            fg_color="#F9FAFB",
            corner_radius=0
        )
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        self.login_container = ctk.CTkFrame(
            self.right_frame,
            width=500,
            height=500,
            fg_color="transparent"
        )
        self.login_container.place(relx=0.5, rely=0.5, anchor="center")

        self.login_title = ctk.CTkLabel(
            self.login_container,
            text="Đăng nhập",
            font=("Arial", 40, "bold"),
            text_color="#111827"
        )
        self.login_title.pack(anchor="w", pady=(0, 10))

        self.login_desc = ctk.CTkLabel(
            self.login_container,
            text="Hệ thống quản lý quán café TLU",
            font=("Arial", 18),
            text_color="#9CA3AF"
        )
        self.login_desc.pack(anchor="w", pady=(0, 40))

        self.username_label = ctk.CTkLabel(
            self.login_container,
            text="Tên đăng nhập",
            font=("Arial", 16),
            text_color="#111827"
        )
        self.username_label.pack(anchor="w", pady=(0, 8))

        self.username_entry = ctk.CTkEntry(
            self.login_container,
            placeholder_text="Nhập tên đăng nhập",
            width=450,
            height=55,
            corner_radius=15,
            border_color="#E5E7EB",
            fg_color="white",
            text_color="black"
        )
        self.username_entry.pack(pady=(0, 25))
        self.username_entry.insert(0, "admin")  # Gợi ý nhập sẵn để dễ test

        self.password_label = ctk.CTkLabel(
            self.login_container,
            text="Mật khẩu",
            font=("Arial", 16),
            text_color="#111827"
        )
        self.password_label.pack(anchor="w", pady=(0, 8))

        self.password_entry = ctk.CTkEntry(
            self.login_container,
            placeholder_text="Nhập mật khẩu",
            show="*",
            width=450,
            height=55,
            corner_radius=15,
            border_color="#E5E7EB",
            fg_color="white",
            text_color="black"
        )
        self.password_entry.pack(pady=(0, 35))
        self.password_entry.insert(0, "123")  # Gợi ý mật khẩu mẫu

        self.login_btn = ctk.CTkButton(
            self.login_container,
            text="Đăng nhập",
            width=450,
            height=55,
            corner_radius=15,
            fg_color="#F59E0B",
            hover_color="#D97706",
            text_color="white",
            font=("Arial", 18, "bold"),
            command=self.login
        )
        self.login_btn.pack()

        # Ràng buộc phím Enter để đăng nhập nhanh
        self.username_entry.bind("<Return>", lambda event: self.login())
        self.password_entry.bind("<Return>", lambda event: self.login())

        self.demo_text = ctk.CTkLabel(
            self.login_container,
            text="Tài khoản mẫu: admin / 123  hoặc  staff1 / 123",
            font=("Arial", 14),
            text_color="#9CA3AF"
        )
        self.demo_text.pack(pady=25)

    def resize_bg(self, event):
        if not self.original_image:
            return

        frame_w = event.width
        frame_h = event.height

        img = self.original_image.copy()

        # Co giãn theo chiều cao để không bị méo
        scale = frame_h / img.height
        new_w = int(img.width * scale)
        new_h = frame_h

        img = img.resize((new_w, new_h), Image.LANCZOS)

        # Nếu ảnh rộng hơn frame thì cắt bên phải
        if new_w > frame_w:
            img = img.crop((0, 0, frame_w, frame_h))

        self.bg_photo = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if username == "" or password == "":
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu")
            return

        result, error = AuthController.login(username, password)
        if error:
            messagebox.showerror("Thất bại", error)
            return

        user_id, username_db, fullname, role = result

        # Gọi controller để chuyển sang Dashboard
        self.controller.show_dashboard(user_id, username_db, role)
