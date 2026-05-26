import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from config.database import connect_db
from controllers.order_controller import OrderController
from views.staff.order_view import StaffOrderFrame
from views.staff.history_view import OrderHistoryFrame
from views.admin.product_view import ProductManagementFrame as AdminProductManagementFrame
from views.admin.user_view import UserManagementFrame as AdminUserManagementFrame
from views.admin.report_view import ReportFrame as AdminReportFrame
from models.product_model import ProductModel
from utils.icon_loader import load_icon, load_product_image
from utils.icon_loader import load_tinted_icon

# ==============================================================================
# 1. TRANG CHỦ (HomeFrame) - HIỂN THỊ THỐNG KÊ TỪ CONTROLLER (MVC)
# ==============================================================================
class HomeFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, username, role):
        super().__init__(parent, fg_color="#F5F2ED", corner_radius=0)
        self.controller = controller
        self.username = username
        self.role = role
        self.product_images = []
        self.icon_images = []

        # Tiêu đề trang
        self.header_label = ctk.CTkLabel(
            self,
            text="Trang chủ",
            font=("Arial", 28, "bold"),
            text_color="#1F1008"
        )
        self.header_label.pack(anchor="nw", padx=30, pady=(25, 5))

        self.date_label = ctk.CTkLabel(
            self,
            text=datetime.now().strftime("Hôm nay: %d/%m/%Y"),
            font=("Arial", 14),
            text_color="#8A7A70"
        )
        self.date_label.pack(anchor="nw", padx=30, pady=(0, 20))

        # Panel chứa các card thống kê
        self.stats_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_panel.pack(fill="x", padx=20, pady=10)

        # Lấy thống kê thật qua Controller (chỉ lấy từ hóa đơn 'paid')
        stats = OrderController.get_stats()

        # Tạo các card thống kê theo vai trò đăng nhập
        if self.role == "admin":
            self.create_card(self.stats_panel, "DOANH THU HÔM NAY", f"{stats['today_revenue']:,.0f}đ", "tổng tiền đã thu", "dollar-sign")
            self.create_card(self.stats_panel, "DOANH THU THÁNG", f"{stats.get('month_revenue', 0):,.0f}đ", "đơn đã thanh toán", "chart-column")
            self.create_card(self.stats_panel, "TỔNG SỐ ĐƠN", f"{stats['total_orders']}", "hóa đơn đã thanh toán", "shopping-bag")
            self.create_card(self.stats_panel, "TỔNG SẢN PHẨM", f"{stats['total_products']}", "món đang kinh doanh", "coffee")
            self.create_card(self.stats_panel, "TỔNG USER", f"{stats.get('total_users', 0)}", "tài khoản hệ thống", "users")
        else:
            self.create_card(self.stats_panel, "SỐ ĐƠN HÔM NAY", f"{stats['today_orders']}", "đơn đã thanh toán", "shopping-cart")
            self.create_card(self.stats_panel, "DOANH THU HÔM NAY", f"{stats['today_revenue']:,.0f}đ", "tổng tiền đã thu", "dollar-sign")
            self.create_card(self.stats_panel, "TỔNG MÓN BÁN HÔM NAY", f"{stats.get('today_items', 0)}", "món đã thanh toán", "coffee")

        # Top 5 món bán chạy nhất và Đơn hàng gần đây
        self.bottom_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_panel.pack(fill="both", expand=True, padx=30, pady=15)
        self.bottom_panel.grid_columnconfigure(0, weight=1)
        self.bottom_panel.grid_columnconfigure(1, weight=1)
        self.bottom_panel.grid_rowconfigure(0, weight=1)

        # Khung bên trái: Top món bán chạy
        self.best_seller_frame = ctk.CTkFrame(self.bottom_panel, fg_color="white", corner_radius=18)
        self.best_seller_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # trophy_icon = load_icon("trophy", size=(20, 20))
        # self.icon_images.append(trophy_icon)

        ctk.CTkLabel(
            self.best_seller_frame,
            text="Top Món Bán Chạy",
            # image=trophy_icon,
            compound="left",
            font=("Arial", 18, "bold"),
            text_color="#1F1008"
        ).pack(anchor="w", padx=25, pady=(20, 5))
        
        ctk.CTkLabel(
            self.best_seller_frame,
            text="Danh sách 5 món ăn bán chạy nhất",
            font=("Arial", 12),
            text_color="#8A7A70"
        ).pack(anchor="w", padx=25, pady=(0, 15))

        self.load_best_sellers()

        # Khung bên phải: Đơn hàng gần đây
        self.recent_orders_frame = ctk.CTkFrame(self.bottom_panel, fg_color="white", corner_radius=18)
        self.recent_orders_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        receipt_icon = load_icon("receipt", size=(20, 20))

        # if receipt_icon:
        #     self.icon_images.append(receipt_icon)

        ctk.CTkLabel(
            self.recent_orders_frame,
            text="Đơn Hàng Gần Đây",
            # image=receipt_icon,
            compound="left",
            font=("Arial", 18, "bold"),
            text_color="#1F1008"
        ).pack(anchor="w", padx=25, pady=(20, 5))
        ctk.CTkLabel(
            self.recent_orders_frame,
            text="5 hóa đơn vừa được tạo trên hệ thống",
            font=("Arial", 12),
            text_color="#8A7A70"
        ).pack(anchor="w", padx=25, pady=(0, 15))

        self.load_recent_orders()

    def create_card(self, parent, title, value, desc, icon):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=20, border_width=1, border_color="#F3E7D8")
        card.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        icon_box = ctk.CTkFrame(card, fg_color="#F59E0B", width=56, height=56, corner_radius=18)
        icon_box.place(relx=0.84, rely=0.34, anchor="center")
        icon_box.pack_propagate(False)

        card_icon = load_tinted_icon(icon, size=(30, 30), color="#FFFFFF")

        if card_icon:
            self.icon_images.append(card_icon)

            icon_label = ctk.CTkLabel(
                icon_box,
                text="",
                image=card_icon
            )

            icon_label.pack(expand=True)

        else:
            ctk.CTkLabel(
                icon_box,
                text="•",
                font=("Arial", 26),
                text_color="white"
            ).pack(expand=True)

        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 11, "bold"),
            text_color="#8A7A70"
        ).pack(anchor="w", padx=25, pady=(20, 2))

        ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 25, "bold"),
            text_color="#1F1008"
        ).pack(anchor="w", padx=25)

        ctk.CTkLabel(
            card,
            text=desc,
            font=("Arial", 13),
            text_color="#8A7A70"
        ).pack(anchor="w", padx=25, pady=(2, 20))

    def load_best_sellers(self):
        # Lấy từ Controller (chỉ lọc các hóa đơn 'paid')
        rows = OrderController.get_top_sellers(5)
        
        if not rows:
            ctk.CTkLabel(
                self.best_seller_frame,
                text="Chưa có dữ liệu bán hàng thành công",
                font=("Arial", 14),
                text_color="#9CA3AF"
            ).pack(pady=40)
        else:
            self.product_images.clear()
            products = ProductModel.get_all()
            image_by_name = {str(row[1]): row[5] for row in products}

            for idx, (name, qty) in enumerate(rows):
                row_frame = ctk.CTkFrame(self.best_seller_frame, fg_color="#F9FAFB", corner_radius=14)
                row_frame.pack(fill="x", padx=25, pady=6)
                
                rank_colors = ["#EF4444", "#F59E0B", "#10B981", "#6B7280", "#9CA3AF"]
                rank_color = rank_colors[idx] if idx < len(rank_colors) else "#9CA3AF"
                
                rank_badge = ctk.CTkLabel(
                    row_frame,
                    text=f"#{idx+1}",
                    width=30,
                    height=30,
                    corner_radius=15,
                    fg_color=rank_color,
                    text_color="white",
                    font=("Arial", 12, "bold")
                )
                rank_badge.pack(side="left", padx=(0, 15))

                product_image = load_product_image(image_by_name.get(str(name), ""), size=(46, 46))
                if product_image:
                    self.product_images.append(product_image)
                    ctk.CTkLabel(row_frame, text="", image=product_image).pack(side="left", padx=(0, 12), pady=7)

                flame_icon = load_icon("flame", size=(16, 16))

                if flame_icon:
                    self.icon_images.append(flame_icon)

                name_lbl = ctk.CTkLabel(
                    row_frame,
                    text=name,
                    image=flame_icon,
                    compound="left",
                    font=("Arial", 14, "bold"),
                    text_color="#1F1008",
                    anchor="w"
                )
                name_lbl.pack(side="left", fill="x", expand=True)
                
                qty_lbl = ctk.CTkLabel(
                    row_frame,
                    text=f"{qty} ly/món",
                    font=("Arial", 13, "bold"),
                    text_color="#F59E0B"
                )
                qty_lbl.pack(side="right")

    def load_recent_orders(self):
        # Lấy từ Controller
        rows = OrderController.get_recents(5)
        
        if not rows:
            ctk.CTkLabel(
                self.recent_orders_frame,
                text="Chưa có hóa đơn nào",
                font=("Arial", 14),
                text_color="#9CA3AF"
            ).pack(pady=40)
        else:
            for order_id, created_at, amount, status, seller in rows:
                row_frame = ctk.CTkFrame(self.recent_orders_frame, fg_color="#F9FAFB", corner_radius=10)
                row_frame.pack(fill="x", padx=20, pady=5)
                
                time_str = created_at.strftime("%H:%M")
                
                # Hiển thị tag trạng thái
                status_text = "Chờ"
                status_color = "#F59E0B"
                if status == "paid":
                    status_text = "Đã bán"
                    status_color = "#10B981"
                elif status == "cancelled":
                    status_text = "Hủy"
                    status_color = "#EF4444"

                info_lbl = ctk.CTkLabel(
                    row_frame,
                    text=f"HĐ-{order_id:04d} • {time_str} • Bán bởi: {seller}",
                    font=("Arial", 13),
                    text_color="#4B5563",
                    anchor="w"
                )
                info_lbl.pack(side="left", padx=15, pady=8, fill="x", expand=True)
                
                badge_status = ctk.CTkLabel(
                    row_frame,
                    text=status_text,
                    width=55,
                    height=22,
                    corner_radius=5,
                    fg_color=status_color,
                    text_color="white",
                    font=("Arial", 10, "bold")
                )
                badge_status.pack(side="right", padx=(5, 15))

                amount_lbl = ctk.CTkLabel(
                    row_frame,
                    text=f"{amount:,.0f}đ",
                    font=("Arial", 13, "bold"),
                    text_color="#D97706"
                )
                amount_lbl.pack(side="right", padx=5)


# ==============================================================================
# 2. TRANG QUẢN LÝ MÓN ĂN (ProductManagementFrame) - ADMIN CRUD
# ==============================================================================
class ProductManagementFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F5F2ED", corner_radius=0)
        self.controller = controller

        # Bố cục 2 phần: Trái là Bảng danh sách, Phải là Form CRUD
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---------------- TRÁI: BẢNG SẢN PHẨM ----------------
        self.left_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(25, 10), pady=20)

        ctk.CTkLabel(
            self.left_panel,
            text="Quản lý danh sách món ăn",
            font=("Arial", 24, "bold"),
            text_color="#1F1008"
        ).pack(anchor="w", pady=(0, 5))

        self.search_entry = ctk.CTkEntry(
            self.left_panel,
            placeholder_text="Tìm kiếm theo tên món...",
            width=280,
            height=38,
            corner_radius=10,
            fg_color="white",
            border_color="#E5E7EB",
            text_color="black"
        )
        self.search_entry.pack(anchor="w", pady=(0, 15))
        self.search_entry.bind("<KeyRelease>", lambda event: self.load_products())

        self.table_frame = ctk.CTkFrame(self.left_panel, fg_color="white", corner_radius=15)
        self.table_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            self.table_frame,
            columns=("id", "name", "price", "stock", "category"),
            show="headings",
            style="Custom.Treeview"
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="TÊN MÓN ĂN/UỐNG")
        self.tree.heading("price", text="ĐƠN GIÁ")
        self.tree.heading("stock", text="SỐ LƯỢNG TỒN")
        self.tree.heading("category", text="DANH MỤC")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("name", width=250, anchor="w")
        self.tree.column("price", width=120, anchor="center")
        self.tree.column("stock", width=120, anchor="center")
        self.tree.column("category", width=150, anchor="center")

        scr = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scr.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=15)
        scr.pack(side="right", fill="y", padx=(0, 15), pady=15)

        self.tree.bind("<<TreeviewSelect>>", self.on_product_select)

        # ---------------- PHẢI: FORM NHẬP LIỆU CRUD ----------------
        self.right_panel = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 25), pady=20)
        
        ctk.CTkLabel(
            self.right_panel,
            text="Thông tin món ăn",
            font=("Arial", 18, "bold"),
            text_color="#1F1008"
        ).pack(anchor="w", padx=20, pady=(20, 15))

        self.selected_product_id = None

        ctk.CTkLabel(self.right_panel, text="Tên sản phẩm *", font=("Arial", 13, "bold"), text_color="#1F1008").pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_name = ctk.CTkEntry(self.right_panel, height=35, fg_color="#F9FAFB", text_color="black")
        self.entry_name.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(self.right_panel, text="Đơn giá (VND) *", font=("Arial", 13, "bold"), text_color="#1F1008").pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_price = ctk.CTkEntry(self.right_panel, height=35, fg_color="#F9FAFB", text_color="black")
        self.entry_price.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(self.right_panel, text="Số lượng tồn kho *", font=("Arial", 13, "bold"), text_color="#1F1008").pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_stock = ctk.CTkEntry(self.right_panel, height=35, fg_color="#F9FAFB", text_color="black")
        self.entry_stock.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(self.right_panel, text="Danh mục sản phẩm *", font=("Arial", 13, "bold"), text_color="#1F1008").pack(anchor="w", padx=20, pady=(5, 2))
        self.combo_category = ctk.CTkComboBox(self.right_panel, height=35, values=[], state="readonly", fg_color="#F9FAFB", text_color="black")
        self.combo_category.pack(fill="x", padx=20, pady=(0, 25))

        self.categories_map = {}
        self.load_categories_combo()

        self.btn_add = ctk.CTkButton(self.right_panel, text="Thêm mới", image=load_icon("plus", size=(16, 16)), compound="left", height=38, fg_color="#10B981", hover_color="#059669", text_color="white", font=("Arial", 13, "bold"), command=self.add_product)
        self.btn_add.pack(fill="x", padx=20, pady=5)

        self.btn_update = ctk.CTkButton(self.right_panel, text="Cập nhật", image=load_icon("file-text", size=(16, 16)), compound="left", height=38, fg_color="#F59E0B", hover_color="#D97706", text_color="white", font=("Arial", 13, "bold"), command=self.update_product)
        self.btn_update.pack(fill="x", padx=20, pady=5)

        self.btn_delete = ctk.CTkButton(self.right_panel, text="Xóa món", height=38, fg_color="#EF4444", hover_color="#DC2626", text_color="white", font=("Arial", 13, "bold"), command=self.delete_product)
        self.btn_delete.pack(fill="x", padx=20, pady=5)

        self.btn_clear = ctk.CTkButton(self.right_panel, text="Làm sạch form", height=35, fg_color="#6B7280", hover_color="#4B5563", text_color="white", font=("Arial", 12), command=self.clear_form)
        self.btn_clear.pack(fill="x", padx=20, pady=(15, 5))

        self.load_products()

    def load_categories_combo(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM categories")
            rows = cursor.fetchall()
            
            names = []
            for cid, name in rows:
                display_name = name
                if name.lower() == "coffee":
                    display_name = "Cà Phê"
                elif name.lower() == "tea":
                    display_name = "Trà"
                elif name.lower() == "cake":
                    display_name = "Bánh Ngọt"
                
                names.append(display_name)
                self.categories_map[display_name] = cid

            self.combo_category.configure(values=names)
            if names:
                self.combo_category.set(names[0])

            cursor.close()
            conn.close()
        except Exception as e:
            print("Lỗi load categories combo:", e)

    def load_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_query = self.search_entry.get().strip()

        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            sql = """
                SELECT p.id, p.name, p.price, p.quantity, c.name
                FROM products p
                JOIN categories c ON p.category_id = c.id
                WHERE 1=1
            """
            params = []
            if search_query:
                sql += " AND p.name LIKE %s"
                params.append(f"%{search_query}%")
                
            sql += " ORDER BY p.id DESC"
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()

            for pid, name, price, stock, cat_name in rows:
                display_cat = cat_name
                if cat_name.lower() == "coffee":
                    display_cat = "Cà Phê"
                elif cat_name.lower() == "tea":
                    display_cat = "Trà"
                elif cat_name.lower() == "cake":
                    display_cat = "Bánh Ngọt"
                
                self.tree.insert("", "end", iid=str(pid), values=(pid, name, f"{price:,.0f}đ", stock, display_cat))

            cursor.close()
            conn.close()
        except Exception as e:
            print("Lỗi load products quản lý:", e)

    def on_product_select(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return

        pid = int(selected_item)
        self.selected_product_id = pid

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.name, p.price, p.quantity, c.name
                FROM products p
                JOIN categories c ON p.category_id = c.id
                WHERE p.id = %s
            """, (pid,))
            row = cursor.fetchone()
            
            if row:
                name, price, stock, cat_name = row
                self.entry_name.delete(0, "end")
                self.entry_name.insert(0, name)
                
                self.entry_price.delete(0, "end")
                self.entry_price.insert(0, f"{price:.0f}")
                
                self.entry_stock.delete(0, "end")
                self.entry_stock.insert(0, str(stock))
                
                display_cat = cat_name
                if cat_name.lower() == "coffee":
                    display_cat = "Cà Phê"
                elif cat_name.lower() == "tea":
                    display_cat = "Trà"
                elif cat_name.lower() == "cake":
                    display_cat = "Bánh Ngọt"
                self.combo_category.set(display_cat)

            cursor.close()
            conn.close()
        except Exception as e:
            print("Lỗi select sản phẩm:", e)

    def clear_form(self):
        self.selected_product_id = None
        self.entry_name.delete(0, "end")
        self.entry_price.delete(0, "end")
        self.entry_stock.delete(0, "end")
        if self.combo_category.cget("values"):
            self.combo_category.set(self.combo_category.cget("values")[0])
        self.tree.selection_remove(self.tree.selection())

    def add_product(self):
        name = self.entry_name.get().strip()
        price_str = self.entry_price.get().strip()
        stock_str = self.entry_stock.get().strip()
        cat_display = self.combo_category.get()

        if not name or not price_str or not stock_str:
            messagebox.showwarning("Nhập liệu", "Vui lòng nhập đầy đủ thông tin!")
            return

        try:
            price = float(price_str)
            stock = int(stock_str)
            cat_id = self.categories_map[cat_display]

            conn = connect_db()
            cursor = conn.cursor()
            sql = "INSERT INTO products (name, price, quantity, category_id) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (name, price, stock, cat_id))
            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Thành công", f"Đã thêm mới sản phẩm '{name}' thành công!")
            self.clear_form()
            self.load_products()
        except ValueError:
            messagebox.showerror("Định dạng sai", "Giá tiền và Số lượng phải là số hợp lệ!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Thêm sản phẩm thất bại:\n{str(e)}")

    def update_product(self):
        if not self.selected_product_id:
            messagebox.showwarning("Cập nhật", "Chọn món ăn cần cập nhật!")
            return

        name = self.entry_name.get().strip()
        price_str = self.entry_price.get().strip()
        stock_str = self.entry_stock.get().strip()
        cat_display = self.combo_category.get()

        if not name or not price_str or not stock_str:
            messagebox.showwarning("Nhập liệu", "Vui lòng điền đầy đủ các trường!")
            return

        try:
            price = float(price_str)
            stock = int(stock_str)
            cat_id = self.categories_map[cat_display]

            conn = connect_db()
            cursor = conn.cursor()
            sql = "UPDATE products SET name=%s, price=%s, quantity=%s, category_id=%s WHERE id=%s"
            cursor.execute(sql, (name, price, stock, cat_id, self.selected_product_id))
            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Thành công", "Cập nhật sản phẩm thành công!")
            self.clear_form()
            self.load_products()
        except ValueError:
            messagebox.showerror("Định dạng sai", "Giá tiền và Số lượng phải là số hợp lệ!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Cập nhật thất bại:\n{str(e)}")

    def delete_product(self):
        if not self.selected_product_id:
            messagebox.showwarning("Xóa món", "Chọn món ăn cần xóa!")
            return

        confirm = messagebox.askyesno("Xác nhận xóa", "Bạn có chắc chắn muốn xóa sản phẩm này?")
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            sql = "DELETE FROM products WHERE id=%s"
            cursor.execute(sql, (self.selected_product_id,))
            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Thành công", "Đã xóa sản phẩm ra khỏi hệ thống!")
            self.clear_form()
            self.load_products()
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", f"Không thể xóa sản phẩm do đã có trong hóa đơn cũ:\n{str(e)}")


# ==============================================================================
# 3. TRANG QUẢN LÝ TÀI KHÀN (UserManagementFrame) - ADMIN CRUD
# ==============================================================================
class UserManagementFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F5F2ED", corner_radius=0)
        self.controller = controller

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.left_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(25, 10), pady=20)

        ctk.CTkLabel(
            self.left_panel,
            text="Quản lý tài khoản nhân viên",
            font=("Arial", 24, "bold"),
            text_color="#1F1008"
        ).pack(anchor="w", pady=(0, 15))

        self.table_frame = ctk.CTkFrame(self.left_panel, fg_color="white", corner_radius=15)
        self.table_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            self.table_frame,
            columns=("id", "username", "role"),
            show="headings",
            style="Custom.Treeview"
        )
        self.tree.heading("id", text="ID TÀI KHOẢN")
        self.tree.heading("username", text="TÊN ĐĂNG NHẬP")
        self.tree.heading("role", text="VAI TRÒ (QUYỀN HẠN)")

        self.tree.column("id", width=120, anchor="center")
        self.tree.column("username", width=300, anchor="w")
        self.tree.column("role", width=250, anchor="center")

        scr = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scr.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=15)
        scr.pack(side="right", fill="y", padx=(0, 15), pady=15)

        self.tree.bind("<<TreeviewSelect>>", self.on_user_select)

        self.right_panel = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 25), pady=20)

        ctk.CTkLabel(
            self.right_panel,
            text="Thông tin tài khoản",
            font=("Arial", 18, "bold"),
            text_color="#1F1008"
        ).pack(anchor="w", padx=20, pady=(20, 15))

        self.selected_user_id = None

        ctk.CTkLabel(self.right_panel, text="Tên đăng nhập *", font=("Arial", 13, "bold"), text_color="#1F1008").pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_username = ctk.CTkEntry(self.right_panel, height=35, fg_color="#F9FAFB", text_color="black")
        self.entry_username.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(self.right_panel, text="Mật khẩu *", font=("Arial", 13, "bold"), text_color="#1F1008").pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_password = ctk.CTkEntry(self.right_panel, height=35, show="*", fg_color="#F9FAFB", text_color="black")
        self.entry_password.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(self.right_panel, text="Vai trò hệ thống *", font=("Arial", 13, "bold"), text_color="#1F1008").pack(anchor="w", padx=20, pady=(5, 2))
        self.combo_role = ctk.CTkComboBox(self.right_panel, height=35, values=["admin", "staff"], state="readonly", fg_color="#F9FAFB", text_color="black")
        self.combo_role.pack(fill="x", padx=20, pady=(0, 25))
        self.combo_role.set("staff")

        self.btn_add = ctk.CTkButton(self.right_panel, text="Tạo tài khoản", image=load_icon("plus", size=(16, 16)), compound="left", height=38, fg_color="#10B981", hover_color="#059669", text_color="white", font=("Arial", 13, "bold"), command=self.add_user)
        self.btn_add.pack(fill="x", padx=20, pady=5)

        self.btn_update = ctk.CTkButton(self.right_panel, text="Cập nhật mật khẩu/role", image=load_icon("file-text", size=(16, 16)), compound="left", height=38, fg_color="#F59E0B", hover_color="#D97706", text_color="white", font=("Arial", 13, "bold"), command=self.update_user)
        self.btn_update.pack(fill="x", padx=20, pady=5)

        self.btn_delete = ctk.CTkButton(self.right_panel, text="Xóa tài khoản", height=38, fg_color="#EF4444", hover_color="#DC2626", text_color="white", font=("Arial", 13, "bold"), command=self.delete_user)
        self.btn_delete.pack(fill="x", padx=20, pady=5)

        self.btn_clear = ctk.CTkButton(self.right_panel, text="Làm sạch form", height=35, fg_color="#6B7280", hover_color="#4B5563", text_color="white", font=("Arial", 12), command=self.clear_form)
        self.btn_clear.pack(fill="x", padx=20, pady=(15, 5))

        self.load_users()

    def load_users(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role FROM users ORDER BY id DESC")
            rows = cursor.fetchall()
            
            for uid, uname, role in rows:
                role_display = "Quản trị viên (admin)" if role == "admin" else "Nhân viên (staff)"
                self.tree.insert("", "end", iid=str(uid), values=(uid, uname, role_display))

            cursor.close()
            conn.close()
        except Exception as e:
            print("Lỗi tải users list:", e)

    def on_user_select(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return

        uid = int(selected_item)
        self.selected_user_id = uid

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT username, password, role FROM users WHERE id=%s", (uid,))
            row = cursor.fetchone()
            
            if row:
                uname, pwd, role = row
                self.entry_username.delete(0, "end")
                self.entry_username.insert(0, uname)
                self.entry_username.configure(state="disabled")
                
                self.entry_password.delete(0, "end")
                self.entry_password.insert(0, pwd)
                
                self.combo_role.set(role)

            cursor.close()
            conn.close()
        except Exception as e:
            print("Lỗi select user:", e)

    def clear_form(self):
        self.selected_user_id = None
        self.entry_username.configure(state="normal")
        self.entry_username.delete(0, "end")
        self.entry_password.delete(0, "end")
        self.combo_role.set("staff")
        self.tree.selection_remove(self.tree.selection())

    def add_user(self):
        uname = self.entry_username.get().strip()
        pwd = self.entry_password.get().strip()
        role = self.combo_role.get()

        if not uname or not pwd:
            messagebox.showwarning("Nhập liệu", "Tên đăng nhập và Mật khẩu không được để trống!")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM users WHERE username=%s", (uname,))
            if cursor.fetchone():
                messagebox.showerror("Trùng lặp", f"Tài khoản '{uname}' đã tồn tại!")
                cursor.close()
                conn.close()
                return

            sql = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
            cursor.execute(sql, (uname, pwd, role))
            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Thành công", f"Đã tạo tài khoản nhân viên '{uname}' thành công!")
            self.clear_form()
            self.load_users()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Tạo tài khoản thất bại:\n{str(e)}")

    def update_user(self):
        if not self.selected_user_id:
            messagebox.showwarning("Cập nhật", "Chọn tài khoản cần cập nhật!")
            return

        pwd = self.entry_password.get().strip()
        role = self.combo_role.get()

        if not pwd:
            messagebox.showwarning("Nhập liệu", "Mật khẩu không được bỏ trống!")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            sql = "UPDATE users SET password=%s, role=%s WHERE id=%s"
            cursor.execute(sql, (pwd, role, self.selected_user_id))
            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Thành công", "Cập nhật mật khẩu và vai trò thành công!")
            self.clear_form()
            self.load_users()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Cập nhật thất bại:\n{str(e)}")

    def delete_user(self):
        if not self.selected_user_id:
            messagebox.showwarning("Xóa tài khoản", "Hãy chọn tài khoản cần xóa!")
            return

        if self.selected_user_id == 1:
            messagebox.showerror("Lỗi bảo mật", "Không thể xóa tài khoản Admin gốc!")
            return

        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa tài khoản này?")
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            sql = "DELETE FROM users WHERE id=%s"
            cursor.execute(sql, (self.selected_user_id,))
            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Thành công", "Đã xóa tài khoản ra khỏi hệ thống!")
            self.clear_form()
            self.load_users()
        except Exception as e:
            messagebox.showerror("Ràng buộc khóa ngoại", f"Không thể xóa nhân viên này do đã có trong hóa đơn cũ:\n{str(e)}")


# ==============================================================================
# 4. TRANG THỐNG KÊ DOANH THU (RevenueStatisticsFrame) - CHỈ ADMIN (MVC)
# ==============================================================================
class RevenueStatisticsFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F5F2ED", corner_radius=0)
        self.controller = controller

        # Tiêu đề
        self.header_label = ctk.CTkLabel(
            self,
            text="Thống kê doanh thu",
            font=("Arial", 26, "bold"),
            text_color="#1F1008"
        )
        self.header_label.pack(anchor="nw", padx=30, pady=(20, 5))

        self.desc_label = ctk.CTkLabel(
            self,
            text="Báo cáo hiệu suất kinh doanh thực tế (chỉ tính đơn hàng đã thanh toán)",
            font=("Arial", 13),
            text_color="#8A7A70"
        )
        self.desc_label.pack(anchor="nw", padx=30, pady=(0, 15))

        # Panel tổng hợp thông tin nhanh
        self.summary_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_panel.pack(fill="x", padx=20, pady=10)

        # Lấy dữ liệu thống kê qua Controller (MVC - chỉ tính đơn 'paid')
        rev_data = OrderController.get_stats()

        self.create_stat_box(self.summary_panel, "TỔNG DOANH THU THỰC TẾ", f"{rev_data['total_revenue']:,.0f}đ", "Hóa đơn đã thanh toán thành công", "dollar-sign")
        self.create_stat_box(self.summary_panel, "TỔNG SỐ ĐƠN THÀNH CÔNG", f"{rev_data['total_orders']}", "Hóa đơn trạng thái 'paid'", "receipt")
        self.create_stat_box(self.summary_panel, "GIÁ TRỊ ĐƠN TRUNG BÌNH", f"{rev_data['avg_order']:,.0f}đ", "Doanh thu bình quân mỗi đơn", "chart-column")

        # Bảng xếp hạng bán chạy nhất
        self.details_panel = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        self.details_panel.pack(fill="both", expand=True, padx=30, pady=15)

        ctk.CTkLabel(
            self.details_panel,
            text="Xếp hạng doanh thu đóng góp theo món ăn",
            font=("Arial", 18, "bold"),
            text_color="#1F1008"
        ).pack(anchor="w", padx=25, pady=(20, 5))

        self.tree = ttk.Treeview(
            self.details_panel,
            columns=("name", "sold", "price", "subtotal"),
            show="headings",
            style="Custom.Treeview"
        )
        self.tree.heading("name", text="TÊN MÓN ĂN/UỐNG")
        self.tree.heading("sold", text="TỔNG SỐ LƯỢNG ĐÃ BÁN")
        self.tree.heading("price", text="ĐƠN GIÁ HIỆN TẠI")
        self.tree.heading("subtotal", text="TỔNG DOANH THU ĐẠT ĐƯỢC")

        self.tree.column("name", width=250, anchor="w")
        self.tree.column("sold", width=120, anchor="center")
        self.tree.column("price", width=150, anchor="center")
        self.tree.column("subtotal", width=200, anchor="center")

        scr = ttk.Scrollbar(self.details_panel, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scr.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=20)
        scr.pack(side="right", fill="y", padx=(0, 20), pady=20)

        self.load_revenue_by_product()

    def create_stat_box(self, parent, title, value, desc, icon):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=18)
        card.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(card, text=title, font=("Arial", 11, "bold"), text_color="#8A7A70").pack(anchor="w", padx=25, pady=(20, 2))
        ctk.CTkLabel(card, text=value, font=("Arial", 28, "bold"), text_color="#1F1008").pack(anchor="w", padx=25)
        ctk.CTkLabel(card, text=desc, font=("Arial", 13), text_color="#8A7A70").pack(anchor="w", padx=25, pady=(2, 20))

        icon_label = ctk.CTkLabel(card, text=icon, font=("Arial", 30))
        icon_label.place(relx=0.85, rely=0.4, anchor="center")

    def load_revenue_by_product(self):
        # Lấy top sản phẩm bán chạy qua Controller (chỉ tính từ hóa đơn 'paid')
        rows = OrderController.get_top_sellers(100)
        
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            for name, qty in rows:
                # Lấy giá của món
                cursor.execute("SELECT price FROM products WHERE name = %s", (name,))
                price_row = cursor.fetchone()
                price = price_row[0] if price_row else 0.0
                
                revenue = qty * price
                self.tree.insert(
                    "",
                    "end",
                    values=(name, qty, f"{price:,.0f}đ", f"{revenue:,.0f}đ")
                )
                
            cursor.close()
            conn.close()
        except Exception as e:
            print("Lỗi load revenue by product:", e)


# ==============================================================================
# LỚP ĐIỀU PHỐI CHÍNH (DashboardFrame) - QUẢN LÝ SIDEBAR VÀ HOÁN ĐỔI TRANG
# ==============================================================================
class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, username, role):
        super().__init__(parent, fg_color="#F5F2ED", corner_radius=0)
        self.controller = controller
        self.username = username
        self.role = role
        self.active_menu_btn = None

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---------------- SIDEBAR ----------------
        self.sidebar = ctk.CTkFrame(self, width=260, fg_color="#4A2C1A", corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        logo = ctk.CTkLabel(
            self.sidebar,
            text="TLU Café POS",
            font=("Arial", 22, "bold"),
            text_color="white"
        )
        logo.pack(anchor="w", padx=25, pady=(30, 10))
        
        line = ctk.CTkFrame(self.sidebar, height=2, fg_color="#6B4428")
        line.pack(fill="x", padx=15, pady=(0, 20))

        nav_title = ctk.CTkLabel(
            self.sidebar,
            text="DANH MỤC MENU",
            font=("Arial", 11, "bold"),
            text_color="#E8D6C8"
        )
        nav_title.pack(anchor="w", padx=25, pady=(0, 10))

        # ---------------- CONTENT CONTAINER ----------------
        self.content_container = ctk.CTkFrame(self, fg_color="#F5F2ED", corner_radius=0)
        self.content_container.grid(row=0, column=1, sticky="nsew")

        # ---------------- XÂY DỰNG SIDEBAR MENU DỰA VÀO VAI TRÒ ----------------
        self.menu_buttons = []
        self.build_navigation()

        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=20, pady=25)

        user_info_box = ctk.CTkFrame(bottom_frame, fg_color="#6B4428", corner_radius=10)
        user_info_box.pack(fill="x", pady=(0, 15))

        lbl_user = ctk.CTkLabel(
            user_info_box,
            text=f"Tài khoản:\n    {self.username}\n    [{self.role.upper()}]",
            font=("Arial", 13, "bold"),
            text_color="white",
            justify="left"
        )
        lbl_user.pack(anchor="w", padx=15, pady=12)

        logout_btn = ctk.CTkButton(
            bottom_frame,
            text="Đăng xuất",
            height=45,
            corner_radius=10,
            fg_color="transparent",
            hover_color="#8B5A34",
            text_color="#F5E6D8",
            font=("Arial", 14, "bold"),
            anchor="w",
            command=self.logout
        )
        logout_btn.pack(fill="x")

        # Hiển thị Trang chủ khi vừa đăng nhập
        self.show_home()

    def build_navigation(self):

        self.add_menu_item(
            "Trang chủ",
            self.show_home,
            "home"
        )

        if self.role == "admin":

            self.add_menu_item(
                "Quản lý món",
                self.show_product_mgmt,
                "coffee"
            )

            self.add_menu_item(
                "Quản lý nhân viên",
                self.show_user_mgmt,
                "user"
            )

            self.add_menu_item(
                "Báo cáo doanh thu",
                self.show_revenue,
                "report"
            )

            self.add_menu_item(
                "Lịch sử hóa đơn",
                self.show_history,
                "history"
            )

        elif self.role == "staff":

            self.add_menu_item(
                "Tạo đơn hàng",
                self.show_staff_order,
                "cart"
            )

            self.add_menu_item(
                "Lịch sử hóa đơn",
                self.show_history,
                "receipt"
            )

    def add_menu_item(self, text, command, icon_name=None):

        icon = None

        if icon_name:
            icon = load_icon(icon_name, size=(20, 20))

        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            image=icon,
            compound="left",
            height=45,
            corner_radius=12,
            fg_color="transparent",
            hover_color="#8B5A34",
            text_color="#F5E6D8",
            font=("Arial", 14, "bold"),
            anchor="w",
            command=lambda: self.set_active_menu(btn, command)
        )

        btn.image_ref = icon

        btn.pack(fill="x", padx=15, pady=4)

        self.menu_buttons.append(btn)

    def set_active_menu(self, btn, command):
        if self.active_menu_btn:
            self.active_menu_btn.configure(fg_color="transparent", text_color="#F5E6D8")
        btn.configure(fg_color="#F59E0B", text_color="white")
        self.active_menu_btn = btn
        command()

    def show_sub_frame(self, frame_class, *args, **kwargs):
        for widget in self.content_container.winfo_children():
            widget.destroy()
        sub_frame = frame_class(self.content_container, self, *args, **kwargs)
        sub_frame.pack(fill="both", expand=True)

    def show_home(self):
        if not self.active_menu_btn and self.menu_buttons:
            self.active_menu_btn = self.menu_buttons[0]
            self.active_menu_btn.configure(fg_color="#F59E0B", text_color="white")
        self.show_sub_frame(HomeFrame, username=self.username, role=self.role)

    def show_staff_order(self):
        user_id = self.controller.current_user["id"]
        # Sử dụng class StaffOrderFrame import từ views/staff/order_view.py
        self.show_sub_frame(StaffOrderFrame, user_id=user_id)

    def show_history(self):
        # Sử dụng class OrderHistoryFrame import từ views/staff/history_view.py
        self.show_sub_frame(OrderHistoryFrame)

    def show_product_mgmt(self):
        self.show_sub_frame(AdminProductManagementFrame)

    def show_user_mgmt(self):
        self.show_sub_frame(AdminUserManagementFrame)

    def show_revenue(self):
        self.show_sub_frame(AdminReportFrame)

    def show_report(self):
        self.show_sub_frame(AdminReportFrame)

    def logout(self):
        confirm = messagebox.askyesno("Đăng xuất", "Bạn có chắc chắn muốn đăng xuất?")
        if confirm:
            self.controller.show_login()


