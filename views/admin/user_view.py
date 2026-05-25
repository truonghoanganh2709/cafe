import customtkinter as ctk
from tkinter import messagebox, ttk
from controllers.user_controller import UserController

class UserManagementFrame(ctk.CTkFrame):
    # Giao diện CRUD tài khoản dành cho Admin.
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F5F2ED", corner_radius=0)
        self.controller = controller
        self.selected_user_id = None

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        left_panel = ctk.CTkFrame(self, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(25, 10), pady=20)
        ctk.CTkLabel(left_panel, text="Quản lý user", font=("Arial", 24, "bold"), text_color="#1F1008").pack(anchor="w")

        self.search_entry = ctk.CTkEntry(left_panel, placeholder_text="Tìm user...", height=38, fg_color="white", text_color="black")
        self.search_entry.pack(fill="x", pady=(10, 12))
        self.search_entry.bind("<KeyRelease>", lambda event: self.load_users())

        table_frame = ctk.CTkFrame(left_panel, fg_color="white", corner_radius=15)
        table_frame.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(table_frame, columns=("id", "username", "fullname", "role"), show="headings")
        for col, text, width in [("id", "ID", 70), ("username", "USERNAME", 160), ("fullname", "HỌ TÊN", 220), ("role", "ROLE", 120)]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=12, pady=12)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        right_panel = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 25), pady=20)
        ctk.CTkLabel(right_panel, text="Thông tin user", font=("Arial", 18, "bold"), text_color="#1F1008").pack(anchor="w", padx=20, pady=(20, 15))

        self.entry_username = self.create_entry(right_panel, "Tên đăng nhập")
        self.entry_password = self.create_entry(right_panel, "Mật khẩu", show="*")
        self.entry_fullname = self.create_entry(right_panel, "Họ tên")
        ctk.CTkLabel(right_panel, text="Vai trò", font=("Arial", 13, "bold"), text_color="#1F1008").pack(anchor="w", padx=20, pady=(5, 2))
        self.combo_role = ctk.CTkComboBox(right_panel, values=["admin", "staff"], state="readonly", fg_color="#F9FAFB", text_color="black")
        self.combo_role.pack(fill="x", padx=20, pady=(0, 15))
        self.combo_role.set("staff")

        ctk.CTkButton(right_panel, text="➕ Thêm user", height=38, fg_color="#10B981", command=self.add_user).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(right_panel, text="📝 Sửa user", height=38, fg_color="#F59E0B", command=self.update_user).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(right_panel, text="🗑️ Xóa user", height=38, fg_color="#EF4444", command=self.delete_user).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(right_panel, text="🧹 Làm sạch", height=35, fg_color="#6B7280", command=self.clear_form).pack(fill="x", padx=20, pady=(15, 5))

        self.load_users()

    def create_entry(self, parent, label, show=None):
        ctk.CTkLabel(parent, text=label, font=("Arial", 13, "bold"), text_color="#1F1008").pack(anchor="w", padx=20, pady=(5, 2))
        entry = ctk.CTkEntry(parent, height=35, show=show, fg_color="#F9FAFB", text_color="black")
        entry.pack(fill="x", padx=20, pady=(0, 10))
        return entry

    def load_users(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for uid, username, fullname, role in UserController.get_users(self.search_entry.get().strip()):
            self.tree.insert("", "end", iid=str(uid), values=(uid, username, fullname, role))

    def on_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        row = UserController.get_user(int(selected))
        if not row:
            return
        uid, username, password, fullname, role = row
        self.clear_form(False)
        self.selected_user_id = uid
        self.entry_username.insert(0, username)
        self.entry_password.insert(0, password)
        self.entry_fullname.insert(0, fullname)
        self.combo_role.set(role)

    def get_form_data(self):
        return self.entry_username.get().strip(), self.entry_password.get().strip(), self.entry_fullname.get().strip(), self.combo_role.get()

    def add_user(self):
        user_id, error = UserController.create_user(*self.get_form_data())
        if error:
            messagebox.showerror("Lỗi", error)
            return
        messagebox.showinfo("Thành công", f"Đã thêm user ID {user_id}.")
        self.clear_form()
        self.load_users()

    def update_user(self):
        success, error = UserController.update_user(self.selected_user_id, *self.get_form_data())
        if error:
            messagebox.showerror("Lỗi", error)
            return
        messagebox.showinfo("Thành công", "Đã cập nhật user.")
        self.clear_form()
        self.load_users()

    def delete_user(self):
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa user này?"):
            return
        success, error = UserController.delete_user(self.selected_user_id)
        if error:
            messagebox.showerror("Lỗi", error)
            return
        messagebox.showinfo("Thành công", "Đã xóa user.")
        self.clear_form()
        self.load_users()

    def clear_form(self, clear_selection=True):
        if clear_selection:
            self.selected_user_id = None
            self.tree.selection_remove(self.tree.selection())
        self.entry_username.delete(0, "end")
        self.entry_password.delete(0, "end")
        self.entry_fullname.delete(0, "end")
        self.combo_role.set("staff")
