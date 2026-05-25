import customtkinter as ctk
from tkinter import messagebox
from config.database import connect_db
from controllers.order_controller import OrderController

class StaffOrderFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, user_id):
        super().__init__(parent, fg_color="#F5F2ED", corner_radius=0)
        self.controller = controller
        self.user_id = user_id
        
        # Giỏ hàng hiện tại: {product_id: {"name": ..., "price": ..., "quantity": ..., "max_stock": ...}}
        self.cart = {}

        # Bố cục POS (Trái: Menu & Tìm kiếm, Phải: Giỏ hàng)
        self.pos_body = ctk.CTkFrame(self, fg_color="transparent")
        self.pos_body.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Khung trái: Tìm kiếm + Lọc + Grid sản phẩm
        self.left_panel = ctk.CTkFrame(self.pos_body, fg_color="transparent")
        self.left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Khung phải: Panel hóa đơn
        self.right_panel = ctk.CTkFrame(self.pos_body, fg_color="white", corner_radius=18, width=380)
        self.right_panel.pack(side="right", fill="y", padx=(10, 0))
        self.right_panel.pack_propagate(False)

        # ---------------- PANEL TRÁI (MENU) ----------------
        self.search_filter_bar = ctk.CTkFrame(self.left_panel, fg_color="white", corner_radius=15)
        self.search_filter_bar.pack(fill="x", pady=(0, 15))

        self.search_entry = ctk.CTkEntry(
            self.search_filter_bar,
            placeholder_text="Tìm kiếm món ăn...",
            width=280,
            height=40,
            corner_radius=10,
            fg_color="#F3F4F6",
            border_color="#E5E7EB",
            text_color="black"
        )
        self.search_entry.pack(side="left", padx=15, pady=15)
        self.search_entry.bind("<KeyRelease>", self.on_search_change)

        # Filter categories load động từ DB
        self.filter_buttons_frame = ctk.CTkFrame(self.search_filter_bar, fg_color="transparent")
        self.filter_buttons_frame.pack(side="left", fill="x", expand=True, padx=10)
        
        self.selected_category_id = "All"
        self.category_buttons = {}
        self.load_category_filters()

        self.menu_scroll = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.menu_scroll.pack(fill="both", expand=True)

        self.load_products_menu()

        # ---------------- PANEL PHẢI (GIỎ HÀNG) ----------------
        self.setup_cart_panel()

    def load_category_filters(self):
        btn_all = ctk.CTkButton(
            self.filter_buttons_frame,
            text="Tất cả",
            width=80,
            height=35,
            corner_radius=18,
            fg_color="#F59E0B",
            text_color="white",
            font=("Arial", 13, "bold"),
            command=lambda: self.select_category("All")
        )
        btn_all.pack(side="left", padx=5)
        self.category_buttons["All"] = btn_all

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM categories")
            categories = cursor.fetchall()
            
            for cat_id, cat_name in categories:
                cat_display = cat_name
                if cat_name.lower() == "coffee":
                    cat_display = "Cà Phê"
                elif cat_name.lower() == "tea":
                    cat_display = "Trà"
                elif cat_name.lower() == "cake":
                    cat_display = "Bánh Ngọt"
                
                btn = ctk.CTkButton(
                    self.filter_buttons_frame,
                    text=cat_display,
                    width=80,
                    height=35,
                    corner_radius=18,
                    fg_color="white",
                    text_color="#4B5563",
                    hover_color="#F3F4F6",
                    font=("Arial", 13, "bold"),
                    command=lambda cid=cat_id: self.select_category(cid)
                )
                btn.pack(side="left", padx=5)
                self.category_buttons[cat_id] = btn

            cursor.close()
            conn.close()
        except Exception as e:
            print("Lỗi tải danh mục filter:", e)

    def select_category(self, cat_id):
        for cid, btn in self.category_buttons.items():
            if cid == cat_id:
                btn.configure(fg_color="#F59E0B", text_color="white")
            else:
                btn.configure(fg_color="white", text_color="#4B5563")

        self.selected_category_id = cat_id
        self.load_products_menu()

    def on_search_change(self, event):
        self.load_products_menu()

    def load_products_menu(self):
        for widget in self.menu_scroll.winfo_children():
            widget.destroy()

        search_query = self.search_entry.get().strip()

        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            sql = "SELECT id, name, price, quantity, category_id FROM products WHERE 1=1"
            params = []
            
            if search_query:
                sql += " AND name LIKE %s"
                params.append(f"%{search_query}%")
                
            if self.selected_category_id != "All":
                sql += " AND category_id = %s"
                params.append(self.selected_category_id)
                
            cursor.execute(sql, tuple(params))
            products = cursor.fetchall()
            
            if not products:
                empty_lbl = ctk.CTkLabel(
                    self.menu_scroll,
                    text="Không tìm thấy món ăn nào",
                    font=("Arial", 16),
                    text_color="#9CA3AF"
                )
                empty_lbl.pack(pady=50)
            else:
                row_frame = None
                for idx, (p_id, p_name, price, stock, cat_id) in enumerate(products):
                    if idx % 3 == 0:
                        row_frame = ctk.CTkFrame(self.menu_scroll, fg_color="transparent")
                        row_frame.pack(fill="x", pady=6)
                        
                    self.create_product_card(row_frame, p_id, p_name, price, stock, cat_id)

            cursor.close()
            conn.close()
        except Exception as e:
            print("Lỗi load danh sách món POS:", e)

    def create_product_card(self, parent, p_id, name, price, stock, cat_id):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=15, width=220, height=210)
        card.pack_propagate(False)
        card.pack(side="left", padx=8, pady=5)

        emoji = "☕"
        if cat_id == 1:
            emoji = "☕"
        elif cat_id == 2:
            emoji = "🍵"
        elif cat_id == 3:
            emoji = "🍰"

        img_frame = ctk.CTkFrame(card, fg_color="#F9FAFB", height=100, corner_radius=12)
        img_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        emoji_lbl = ctk.CTkLabel(img_frame, text=emoji, font=("Arial", 38))
        emoji_lbl.pack(expand=True)

        name_lbl = ctk.CTkLabel(
            card,
            text=name,
            font=("Arial", 14, "bold"),
            text_color="#1F1008",
            anchor="w"
        )
        name_lbl.pack(anchor="w", padx=12, pady=(5, 1))

        stock_text = f"Tồn: {stock}" if stock > 0 else "Hết hàng"
        stock_color = "#10B981" if stock > 0 else "#EF4444"
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=12, pady=(2, 10))
        
        price_lbl = ctk.CTkLabel(
            info_frame,
            text=f"{price:,.0f}đ",
            font=("Arial", 14, "bold"),
            text_color="#D97706"
        )
        price_lbl.pack(side="left")

        stock_lbl = ctk.CTkLabel(
            info_frame,
            text=stock_text,
            font=("Arial", 11),
            text_color=stock_color
        )
        stock_lbl.pack(side="right")

        add_btn = ctk.CTkButton(
            card,
            text="+ Thêm",
            width=80,
            height=30,
            corner_radius=15,
            fg_color="#F59E0B" if stock > 0 else "#E5E7EB",
            hover_color="#D97706" if stock > 0 else "#E5E7EB",
            text_color="white" if stock > 0 else "#9CA3AF",
            font=("Arial", 12, "bold"),
            state="normal" if stock > 0 else "disabled",
            command=lambda: self.add_to_cart(p_id, name, price, stock)
        )
        add_btn.place(relx=0.5, rely=0.86, anchor="center")

    def setup_cart_panel(self):
        ctk.CTkLabel(
            self.right_panel,
            text="Đơn Hiện Tại",
            font=("Arial", 18, "bold"),
            text_color="#1F1008"
        ).pack(anchor="w", padx=20, pady=(20, 2))
        
        self.cart_desc_label = ctk.CTkLabel(
            self.right_panel,
            text="0 món đã chọn",
            font=("Arial", 12),
            text_color="#8A7A70"
        )
        self.cart_desc_label.pack(anchor="w", padx=20, pady=(0, 15))

        self.cart_scroll = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent")
        self.cart_scroll.pack(fill="both", expand=True, padx=10)

        self.empty_cart_lbl = ctk.CTkLabel(
            self.cart_scroll,
            text="🛍️\n\nChưa có món ăn\nHãy chọn món từ menu bên trái",
            font=("Arial", 14),
            text_color="#CBD5E1"
        )
        self.empty_cart_lbl.pack(expand=True, pady=100)

        self.checkout_panel = ctk.CTkFrame(self.right_panel, fg_color="#F9FAFB", corner_radius=15)
        self.checkout_panel.pack(fill="x", padx=15, pady=15)

        total_frame = ctk.CTkFrame(self.checkout_panel, fg_color="transparent")
        total_frame.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            total_frame,
            text="Tổng cộng",
            font=("Arial", 16, "bold"),
            text_color="#4B5563"
        ).pack(side="left")

        self.total_price_label = ctk.CTkLabel(
            total_frame,
            text="0đ",
            font=("Arial", 22, "bold"),
            text_color="#D97706"
        )
        self.total_price_label.pack(side="right")

        self.pay_btn = ctk.CTkButton(
            self.checkout_panel,
            text="Tạo đơn",
            height=50,
            corner_radius=12,
            fg_color="#F59E0B",
            hover_color="#D97706",
            text_color="white",
            font=("Arial", 16, "bold"),
            command=self.create_order
        )
        self.pay_btn.pack(fill="x", padx=15, pady=(0, 15))

    def add_to_cart(self, p_id, name, price, stock):
        if p_id in self.cart:
            if self.cart[p_id]["quantity"] < stock:
                self.cart[p_id]["quantity"] += 1
            else:
                messagebox.showwarning("Cảnh báo", "Đạt giới hạn tồn kho tối đa!")
                return
        else:
            self.cart[p_id] = {
                "name": name,
                "price": price,
                "quantity": 1,
                "max_stock": stock
            }
        self.update_cart_display()

    def update_cart_display(self):
        if not self.cart:
            self.empty_cart_lbl.pack(expand=True, pady=100)
            self.cart_desc_label.configure(text="0 món đã chọn")
            self.total_price_label.configure(text="0đ")
            for widget in self.cart_scroll.winfo_children():
                if widget != self.empty_cart_lbl:
                    widget.destroy()
            return
        
        self.empty_cart_lbl.pack_forget()

        for widget in self.cart_scroll.winfo_children():
            if widget != self.empty_cart_lbl:
                widget.destroy()

        total_price = 0
        total_items = 0

        for p_id, item in self.cart.items():
            qty = item["quantity"]
            price = item["price"]
            subtotal = price * qty
            total_price += subtotal
            total_items += qty

            item_frame = ctk.CTkFrame(self.cart_scroll, fg_color="#F9FAFB", corner_radius=10)
            item_frame.pack(fill="x", pady=4, padx=5)

            lbl_name = ctk.CTkLabel(
                item_frame,
                text=f"{item['name']}\n{price:,.0f}đ",
                font=("Arial", 12, "bold"),
                text_color="#1F1008",
                justify="left",
                anchor="w"
            )
            lbl_name.pack(side="left", padx=10, pady=8, fill="x", expand=True)

            ctrl_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            ctrl_frame.pack(side="right", padx=10)

            btn_minus = ctk.CTkButton(
                ctrl_frame,
                text="-",
                width=24,
                height=24,
                corner_radius=12,
                fg_color="#E5E7EB",
                hover_color="#D1D5DB",
                text_color="#4B5563",
                font=("Arial", 12, "bold"),
                command=lambda pid=p_id: self.change_qty(pid, -1)
            )
            btn_minus.pack(side="left", padx=2)

            lbl_qty = ctk.CTkLabel(
                ctrl_frame,
                text=str(qty),
                font=("Arial", 13, "bold"),
                text_color="black"
            )
            lbl_qty.pack(side="left", padx=6)

            btn_plus = ctk.CTkButton(
                ctrl_frame,
                text="+",
                width=24,
                height=24,
                corner_radius=12,
                fg_color="#E5E7EB",
                hover_color="#D1D5DB",
                text_color="#4B5563",
                font=("Arial", 12, "bold"),
                command=lambda pid=p_id: self.change_qty(pid, 1)
            )
            btn_plus.pack(side="left", padx=2)

            btn_del = ctk.CTkButton(
                ctrl_frame,
                text="✕",
                width=20,
                height=20,
                corner_radius=10,
                fg_color="transparent",
                hover_color="#FEE2E2",
                text_color="#EF4444",
                font=("Arial", 10, "bold"),
                command=lambda pid=p_id: self.delete_item(pid)
            )
            btn_del.pack(side="left", padx=(8, 0))

        self.cart_desc_label.configure(text=f"{total_items} món đã chọn")
        self.total_price_label.configure(text=f"{total_price:,.0f}đ")

    def change_qty(self, p_id, delta):
        item = self.cart[p_id]
        new_qty = item["quantity"] + delta
        if new_qty <= 0:
            self.delete_item(p_id)
        elif new_qty > item["max_stock"]:
            messagebox.showwarning("Cảnh báo", "Đạt giới hạn tồn kho tối đa!")
        else:
            item["quantity"] = new_qty
            self.update_cart_display()

    def delete_item(self, p_id):
        if p_id in self.cart:
            del self.cart[p_id]
            self.update_cart_display()

    def create_order(self):
        if not self.cart:
            messagebox.showwarning("Lỗi tạo đơn", "Danh sách món đang trống!")
            return

        order_id, err = OrderController.create_order(self.user_id, self.cart)
        if err:
            messagebox.showerror("Thất bại", err)
            return

        # Thành công
        messagebox.showinfo("Thành công", f"Tạo đơn thành công - chờ thanh toán\nMã hóa đơn: HĐ-{order_id:04d}")
        
        # Reset giỏ hàng
        self.cart.clear()
        self.update_cart_display()
        
        # Tải lại sản phẩm menu để cập nhật số tồn
        self.load_products_menu()
