import customtkinter as ctk
from tkinter import messagebox, ttk
from controllers.product_controller import ProductController

class ProductManagementFrame(ctk.CTkFrame):
    # Giao diện CRUD món ăn dành cho Admin.
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F5F2ED", corner_radius=0)
        self.controller = controller
        self.selected_product_id = None

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        left_panel = ctk.CTkFrame(self, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(25, 10), pady=20)

        ctk.CTkLabel(left_panel, text="Quản lý món café", font=("Arial", 24, "bold"), text_color="#1F1008").pack(anchor="w")
        self.search_entry = ctk.CTkEntry(left_panel, placeholder_text="Tìm kiếm món hoặc loại món...", height=38, fg_color="white", text_color="black")
        self.search_entry.pack(fill="x", pady=(10, 12))
        self.search_entry.bind("<KeyRelease>", lambda event: self.load_products())

        table_frame = ctk.CTkFrame(left_panel, fg_color="white", corner_radius=15)
        table_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, columns=("id", "name", "category", "price", "quantity", "image"), show="headings")
        for col, text, width in [
            ("id", "ID", 60), ("name", "TÊN MÓN", 180), ("category", "LOẠI", 120),
            ("price", "GIÁ", 110), ("quantity", "SL", 70), ("image", "ẢNH", 160)
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=12, pady=12)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        right_panel = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 25), pady=20)

        ctk.CTkLabel(right_panel, text="Thông tin món", font=("Arial", 18, "bold"), text_color="#1F1008").pack(anchor="w", padx=20, pady=(20, 15))
        self.entry_name = self.create_entry(right_panel, "Tên món")
        self.entry_category = self.create_entry(right_panel, "Loại món")
        self.entry_price = self.create_entry(right_panel, "Giá")
        self.entry_quantity = self.create_entry(right_panel, "Số lượng")
        self.entry_image = self.create_entry(right_panel, "Đường dẫn ảnh")

        ctk.CTkButton(right_panel, text="➕ Thêm món", height=38, fg_color="#10B981", command=self.add_product).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(right_panel, text="📝 Sửa món", height=38, fg_color="#F59E0B", command=self.update_product).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(right_panel, text="🗑️ Xóa món", height=38, fg_color="#EF4444", command=self.delete_product).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(right_panel, text="🧹 Làm sạch", height=35, fg_color="#6B7280", command=self.clear_form).pack(fill="x", padx=20, pady=(15, 5))

        self.load_products()

    def create_entry(self, parent, label):
        ctk.CTkLabel(parent, text=label, font=("Arial", 13, "bold"), text_color="#1F1008").pack(anchor="w", padx=20, pady=(5, 2))
        entry = ctk.CTkEntry(parent, height=35, fg_color="#F9FAFB", text_color="black")
        entry.pack(fill="x", padx=20, pady=(0, 10))
        return entry

    def load_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows, error = ProductController.get_products(self.search_entry.get().strip())
        if error:
            messagebox.showerror("Lỗi", error)
            return
        for pid, name, category, price, quantity, image in rows:
            self.tree.insert("", "end", iid=str(pid), values=(pid, name, category, f"{price:,.0f}", quantity, image or ""))

    def on_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        self.selected_product_id = int(selected)
        values = self.tree.item(selected, "values")
        self.clear_form(False)
        self.selected_product_id = int(values[0])
        for entry, value in zip([self.entry_name, self.entry_category, self.entry_price, self.entry_quantity, self.entry_image], values[1:]):
            entry.insert(0, str(value).replace(",", ""))

    def get_form_data(self):
        return (
            self.entry_name.get().strip(), self.entry_category.get().strip(), self.entry_price.get().strip(),
            self.entry_quantity.get().strip(), self.entry_image.get().strip()
        )

    def add_product(self):
        product_id, error = ProductController.create_product(*self.get_form_data())
        if error:
            messagebox.showerror("Lỗi", error)
            return
        messagebox.showinfo("Thành công", f"Đã thêm món mới ID {product_id}.")
        self.clear_form()
        self.load_products()

    def update_product(self):
        success, error = ProductController.update_product(self.selected_product_id, *self.get_form_data())
        if error:
            messagebox.showerror("Lỗi", error)
            return
        messagebox.showinfo("Thành công", "Đã cập nhật món.")
        self.clear_form()
        self.load_products()

    def delete_product(self):
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa món này?"):
            return
        success, error = ProductController.delete_product(self.selected_product_id)
        if error:
            messagebox.showerror("Lỗi", error)
            return
        messagebox.showinfo("Thành công", "Đã xóa món.")
        self.clear_form()
        self.load_products()

    def clear_form(self, clear_selection=True):
        if clear_selection:
            self.selected_product_id = None
            self.tree.selection_remove(self.tree.selection())
        for entry in [self.entry_name, self.entry_category, self.entry_price, self.entry_quantity, self.entry_image]:
            entry.delete(0, "end")
