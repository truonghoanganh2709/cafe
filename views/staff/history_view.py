import os
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from controllers.order_controller import OrderController

class OrderHistoryFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F5F2ED", corner_radius=0)
        self.controller = controller

        # Tiêu đề
        self.header_label = ctk.CTkLabel(
            self,
            text="Lịch sử hóa đơn",
            font=("Arial", 26, "bold"),
            text_color="#1F1008"
        )
        self.header_label.pack(anchor="nw", padx=30, pady=(20, 5))
        
        self.desc_label = ctk.CTkLabel(
            self,
            text="Quản lý thanh toán và xem chi tiết hóa đơn",
            font=("Arial", 13),
            text_color="#8A7A70"
        )
        self.desc_label.pack(anchor="nw", padx=30, pady=(0, 15))

        # Panel tìm kiếm & tải lại
        self.tools_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.tools_frame.pack(fill="x", padx=30, pady=5)

        self.search_entry = ctk.CTkEntry(
            self.tools_frame,
            placeholder_text="Tìm mã hóa đơn (gõ số ID, VD: 1, 2...)...",
            width=280,
            height=38,
            corner_radius=10,
            fg_color="#F3F4F6",
            border_color="#E5E7EB",
            text_color="black"
        )
        self.search_entry.pack(side="left", padx=15, pady=12)
        self.search_entry.bind("<KeyRelease>", self.filter_history)

        self.refresh_btn = ctk.CTkButton(
            self.tools_frame,
            text="↻ Tải lại danh sách",
            width=140,
            height=38,
            corner_radius=10,
            fg_color="#F59E0B",
            hover_color="#D97706",
            text_color="white",
            font=("Arial", 12, "bold"),
            command=self.load_orders_history
        )
        self.refresh_btn.pack(side="right", padx=15)

        # Bảng hiển thị Treeview
        self.table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        self.table_frame.pack(fill="both", expand=True, padx=30, pady=15)

        # Configure style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Treeview",
            background="white",
            foreground="black",
            rowheight=35,
            fieldbackground="white",
            font=("Arial", 13)
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#F3F4F6",
            foreground="#1F1008",
            font=("Arial", 13, "bold"),
            borderwidth=0
        )
        style.map("Custom.Treeview", background=[("selected", "#F59E0B")], foreground=[("selected", "white")])

        self.tree = ttk.Treeview(
            self.table_frame,
            columns=("id", "time", "seller", "amount", "status"),
            show="headings",
            style="Custom.Treeview"
        )
        
        self.tree.heading("id", text="MÃ HÓA ĐƠN")
        self.tree.heading("time", text="THỜI GIAN LẬP")
        self.tree.heading("seller", text="NHÂN VIÊN LẬP ĐƠN")
        self.tree.heading("amount", text="TỔNG TIỀN")
        self.tree.heading("status", text="TRẠNG THÁI")

        self.tree.column("id", width=120, anchor="center")
        self.tree.column("time", width=220, anchor="center")
        self.tree.column("seller", width=200, anchor="center")
        self.tree.column("amount", width=180, anchor="center")
        self.tree.column("status", width=200, anchor="center")

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=15)
        scrollbar.pack(side="right", fill="y", padx=(0, 15), pady=15)

        self.tree.bind("<<TreeviewSelect>>", self.on_order_select)
        self.tree.bind("<Double-1>", self.show_order_details)

        # Panel điều khiển thanh toán ở phía dưới
        self.action_panel = ctk.CTkFrame(self, fg_color="white", corner_radius=15, height=75)
        self.action_panel.pack(fill="x", padx=30, pady=(0, 20))
        self.action_panel.pack_propagate(False)

        self.lbl_selected_info = ctk.CTkLabel(
            self.action_panel,
            text="Hãy chọn một hóa đơn từ danh sách trên để xem chi tiết / thanh toán.",
            font=("Arial", 14),
            text_color="#4B5563"
        )
        self.lbl_selected_info.pack(side="left", padx=25, pady=20)

        self.btn_pay_confirm = ctk.CTkButton(
            self.action_panel,
            text="✓ Xác nhận thanh toán",
            width=180,
            height=40,
            corner_radius=10,
            fg_color="#10B981",
            hover_color="#059669",
            text_color="white",
            font=("Arial", 13, "bold"),
            command=self.confirm_payment
        )
        self.btn_export_invoice = ctk.CTkButton(
            self.action_panel,
            text="📤 Xuất hóa đơn",
            width=150,
            height=40,
            corner_radius=10,
            fg_color="#F59E0B",
            hover_color="#D97706",
            text_color="white",
            font=("Arial", 13, "bold"),
            command=self.export_selected_invoice
        )
        # Ẩn nút mặc định
        self.selected_order_id = None

        self.load_orders_history()

    def load_orders_history(self):
        # Ẩn nút thanh toán
        self.btn_pay_confirm.pack_forget()
        self.btn_export_invoice.pack_forget()
        self.selected_order_id = None
        self.lbl_selected_info.configure(text="Hãy chọn một hóa đơn từ danh sách trên để xem chi tiết / thanh toán.")

        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = OrderController.get_history()
        self.insert_rows_to_tree(rows)

    def filter_history(self, event):
        search_val = self.search_entry.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = OrderController.get_history(search_val)
        self.insert_rows_to_tree(rows)

    def insert_rows_to_tree(self, rows):
        if not rows:
            return

        for order_id, created_at, amount, status, username in rows:
            time_str = created_at.strftime("%d/%m/%Y %H:%M:%S")
            amount_str = f"{amount:,.0f}đ"
            code_str = f"HĐ-{order_id:04d}"
            
            # Map status hiển thị tiếng Việt
            status_display = "Chờ thanh toán"
            if status == "paid":
                status_display = "Đã thanh toán"
            elif status == "cancelled":
                status_display = "Đã hủy"

            # Insert
            item_id = self.tree.insert(
                "",
                "end",
                iid=str(order_id),
                values=(code_str, time_str, username, amount_str, status_display)
            )
            
            # Thêm tag màu cho trạng thái (sử dụng tag để map màu sắc)
            if status == "paid":
                self.tree.tag_configure("tag_paid", foreground="#10B981")
                self.tree.item(item_id, tags=("tag_paid",))
            elif status == "pending":
                self.tree.tag_configure("tag_pending", foreground="#F59E0B")
                self.tree.item(item_id, tags=("tag_pending",))
            elif status == "cancelled":
                self.tree.tag_configure("tag_cancelled", foreground="#EF4444")
                self.tree.item(item_id, tags=("tag_cancelled",))

    def on_order_select(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return

        order_id = int(selected_item)
        self.selected_order_id = order_id
        
        values = self.tree.item(selected_item, "values")
        code = values[0]
        amount = values[3]
        status_display = values[4]

        # Kiểm tra xem có pending không
        if status_display == "Chờ thanh toán":
            self.lbl_selected_info.configure(
                text=f"Đang chọn: {code} | Số tiền: {amount} | Trạng thái: {status_display}",
                text_color="#F59E0B"
            )
            # Hiển thị nút xác nhận thanh toán ở bên phải panel
            self.btn_pay_confirm.pack(side="right", padx=25, pady=15)
            self.btn_export_invoice.pack_forget()
        else:
            color = "#10B981" if status_display == "Đã thanh toán" else "#EF4444"
            self.lbl_selected_info.configure(
                text=f"Đang chọn: {code} | Số tiền: {amount} | Trạng thái: {status_display}",
                text_color=color
            )
            # Ẩn nút xác nhận thanh toán
            self.btn_pay_confirm.pack_forget()
            if status_display == "Đã thanh toán":
                self.btn_export_invoice.pack(side="right", padx=25, pady=15)
            else:
                self.btn_export_invoice.pack_forget()

    def confirm_payment(self):
        if not self.selected_order_id:
            return

        confirm = messagebox.askyesno(
            "Xác nhận", 
            f"Bạn có chắc muốn xác nhận thanh toán cho hóa đơn HĐ-{self.selected_order_id:04d}?"
        )
        if not confirm:
            return

        success, err = OrderController.confirm_order_payment(self.selected_order_id)
        if err:
            messagebox.showerror("Thất bại", err)
            return

        messagebox.showinfo("Thành công", f"Hóa đơn HĐ-{self.selected_order_id:04d} đã được thanh toán thành công!")
        
        # Tải lại bảng lịch sử hóa đơn
        self.load_orders_history()

    def export_selected_invoice(self):
        if not self.selected_order_id:
            messagebox.showwarning("Thông báo", "Vui lòng chọn hóa đơn cần xuất.")
            return

        selected_item = self.tree.focus()
        values = self.tree.item(selected_item, "values")
        invoice_info = {
            "code": values[0],
            "time": values[1],
            "seller": values[2],
            "amount": values[3],
            "status": values[4],
        }

        file_path = filedialog.asksaveasfilename(
            initialdir=os.path.abspath("reports/excel"),
            initialfile=f"hoa_don_{self.selected_order_id:04d}.xlsx",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if not file_path:
            return

        success, error = OrderController.export_invoice(file_path, invoice_info, self.selected_order_id)
        if error:
            messagebox.showerror("Lỗi", error)
            return
        messagebox.showinfo("Thành công", f"Đã xuất hóa đơn:\n{file_path}")

    def show_order_details(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return

        order_id = int(selected_item)
        values = self.tree.item(selected_item, "values")
        code = values[0]

        # Cửa sổ popup
        detail_win = ctk.CTkToplevel(self)
        detail_win.geometry("650x550")
        detail_win.title(f"Chi tiết đơn hàng {code}")
        detail_win.transient(self)
        detail_win.grab_set()

        ctk.CTkLabel(
            detail_win,
            text=f"CHI TIẾT HÓA ĐƠN {code}",
            font=("Arial", 18, "bold"),
            text_color="#1F1008"
        ).pack(pady=(20, 10))

        tbl_frame = ctk.CTkFrame(detail_win, fg_color="white", corner_radius=12)
        tbl_frame.pack(fill="both", expand=True, padx=25, pady=10)

        dt_tree = ttk.Treeview(
            tbl_frame,
            columns=("name", "qty", "price", "subtotal"),
            show="headings",
            style="Custom.Treeview"
        )
        dt_tree.heading("name", text="TÊN MÓN ĂN/UỐNG")
        dt_tree.heading("qty", text="SL")
        dt_tree.heading("price", text="ĐƠN GIÁ")
        dt_tree.heading("subtotal", text="THÀNH TIỀN")

        dt_tree.column("name", width=250, anchor="w")
        dt_tree.column("qty", width=60, anchor="center")
        dt_tree.column("price", width=120, anchor="center")
        dt_tree.column("subtotal", width=120, anchor="center")

        scr = ttk.Scrollbar(tbl_frame, orient="vertical", command=dt_tree.yview)
        dt_tree.configure(yscrollcommand=scr.set)
        dt_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scr.pack(side="right", fill="y", pady=10)

        # Lấy dữ liệu chi tiết
        details = OrderController.get_details(order_id)
        total_amount = 0.0
        for name, qty, price in details:
            sub = qty * price
            total_amount += sub
            dt_tree.insert(
                "",
                "end",
                values=(name, qty, f"{price:,.0f}đ", f"{sub:,.0f}đ")
            )

        footer_frame = ctk.CTkFrame(detail_win, fg_color="transparent")
        footer_frame.pack(fill="x", padx=25, pady=(5, 20))

        ctk.CTkLabel(
            footer_frame,
            text=f"Tổng tiền thanh toán: {total_amount:,.0f}đ",
            font=("Arial", 16, "bold"),
            text_color="#D97706"
        ).pack(side="left")

        ctk.CTkButton(
            footer_frame,
            text="Đóng cửa sổ",
            width=110,
            height=35,
            corner_radius=8,
            fg_color="#374151",
            hover_color="#1F2937",
            text_color="white",
            font=("Arial", 12, "bold"),
            command=detail_win.destroy
        ).pack(side="right")
