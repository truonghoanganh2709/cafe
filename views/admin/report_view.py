import os
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from controllers.report_controller import ReportController
from utils.icon_loader import load_icon, load_product_image

class ReportFrame(ctk.CTkFrame):
    # Giao diện dashboard báo cáo doanh thu hiện đại cho Admin.
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F5F2ED", corner_radius=0)
        self.controller = controller
        self.current_filter = "7days"
        self.product_images = []
        self.icon_images = []
        self.chart_canvas = None
        self.filter_buttons = {}

        self.build_header()
        self.content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        self.kpi_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.kpi_frame.pack(fill="x", pady=(0, 14))

        self.middle_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.middle_frame.pack(fill="both", expand=True, pady=(0, 14))
        self.middle_frame.grid_columnconfigure(0, weight=7)
        self.middle_frame.grid_columnconfigure(1, weight=3)

        self.chart_card = ctk.CTkFrame(self.middle_frame, fg_color="white", corner_radius=22, border_width=1, border_color="#F3E7D8")
        self.chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.top_card = ctk.CTkFrame(self.middle_frame, fg_color="white", corner_radius=22, border_width=1, border_color="#F3E7D8")
        self.top_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.recent_card = ctk.CTkFrame(self.content, fg_color="white", corner_radius=22, border_width=1, border_color="#F3E7D8")
        self.recent_card.pack(fill="x", pady=(0, 10))

        self.load_dashboard()

    def build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(22, 14))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(title_box, text="Báo cáo doanh thu", font=("Arial", 28, "bold"), text_color="#1F1008").pack(anchor="w")
        ctk.CTkLabel(title_box, text="Dashboard tổng hợp hiệu suất bán hàng theo dữ liệu đã thanh toán", font=("Arial", 13), text_color="#8A7A70").pack(anchor="w", pady=(3, 0))

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(side="right")
        refresh_icon = load_icon("history", size=(16, 16))
        excel_icon = load_icon("chart-column", size=(16, 16))
        pdf_icon = load_icon("receipt", size=(16, 16))
        for icon in [refresh_icon, excel_icon, pdf_icon]:
            if icon:
                self.icon_images.append(icon)
        ctk.CTkButton(actions, text="Refresh", image=refresh_icon, compound="left", width=108, height=38, corner_radius=12, fg_color="#F59E0B", hover_color="#D97706", command=self.load_dashboard).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Excel", image=excel_icon, compound="left", width=94, height=38, corner_radius=12, fg_color="#10B981", hover_color="#059669", command=self.export_excel).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="PDF", image=pdf_icon, compound="left", width=84, height=38, corner_radius=12, fg_color="#1F1008", hover_color="#3A2114", command=self.export_pdf).pack(side="left", padx=5)

        filters = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        filters.pack(fill="x", padx=30, pady=(0, 16))
        filter_items = [("today", "Hôm nay"), ("7days", "7 ngày"), ("30days", "30 ngày"), ("month", "Tháng này"), ("year", "Năm nay")]
        for key, label in filter_items:
            btn = ctk.CTkButton(filters, text=label, width=100, height=34, corner_radius=18, fg_color="transparent", hover_color="#FFF7ED", text_color="#4B5563", font=("Arial", 12, "bold"), command=lambda k=key: self.change_filter(k))
            btn.pack(side="left", padx=8, pady=10)
            self.filter_buttons[key] = btn
        self.update_filter_buttons()

    def update_filter_buttons(self):
        for key, btn in self.filter_buttons.items():
            if key == self.current_filter:
                btn.configure(fg_color="#F59E0B", text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color="#4B5563")

    def change_filter(self, filter_key):
        self.current_filter = filter_key
        self.update_filter_buttons()
        self.load_dashboard()

    def load_dashboard(self):
        data, error = ReportController.get_dashboard_data(self.current_filter)
        if error:
            messagebox.showerror("Lỗi", error)
            return
        self.data = data
        self.render_kpis(data["kpi"])
        self.render_chart(data["chart"])
        self.render_top_products(data["top_products"])
        self.render_recent_orders(data["recent_orders"])

    def render_kpis(self, kpi):
        for widget in self.kpi_frame.winfo_children():
            widget.destroy()
        cards = [
            ("Tổng doanh thu", f"{kpi['total_revenue']:,.0f}đ", f"{kpi['growth_percent']:+}% so với hôm qua", "dollar-sign"),
            ("Tổng số đơn", f"{kpi['total_orders']} đơn", "Đơn đã thanh toán", "shopping-bag"),
            ("Tổng sản phẩm", f"{kpi['total_products']} món", "Món đang bán", "coffee"),
            ("Tổng user", f"{kpi['total_users']} tài khoản", "Người dùng hệ thống", "users"),
        ]
        for title, value, desc, icon in cards:
            card = ctk.CTkFrame(self.kpi_frame, fg_color="white", corner_radius=22, border_width=1, border_color="#F3E7D8", height=120)
            card.pack(side="left", fill="both", expand=True, padx=8)
            icon_box = ctk.CTkFrame(card, fg_color="#FFF7ED", width=50, height=50, corner_radius=25)
            icon_box.place(relx=0.86, rely=0.32, anchor="center")
            icon_box.pack_propagate(False)
            card_icon = load_icon(icon, size=(24, 24))

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
                    font=("Arial", 24),
                    text_color="#F59E0B"
                ).pack(expand=True)
            ctk.CTkLabel(card, text=title.upper(), font=("Arial", 11, "bold"), text_color="#8A7A70").pack(anchor="w", padx=20, pady=(18, 2))
            ctk.CTkLabel(card, text=value, font=("Arial", 26, "bold"), text_color="#1F1008").pack(anchor="w", padx=20)
            ctk.CTkLabel(card, text=desc, font=("Arial", 12), text_color="#10B981" if "+" in desc else "#8A7A70").pack(anchor="w", padx=20, pady=(2, 16))

    def render_chart(self, chart_rows):
        for widget in self.chart_card.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self.chart_card, text="Doanh thu 7 ngày gần nhất", font=("Arial", 18, "bold"), text_color="#1F1008").pack(anchor="w", padx=22, pady=(18, 4))
        ctk.CTkLabel(self.chart_card, text="Chỉ tính hóa đơn có trạng thái paid", font=("Arial", 12), text_color="#8A7A70").pack(anchor="w", padx=22)

        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except Exception:
            ctk.CTkLabel(self.chart_card, text="Chưa cài matplotlib. Hãy cài: pip install matplotlib", text_color="#EF4444").pack(pady=40)
            return

        labels = []
        values = []
        for day, revenue in chart_rows:
            labels.append(day.strftime("%a"))
            values.append(float(revenue or 0))
        if not labels:
            labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            values = [0, 0, 0, 0, 0, 0, 0]

        fig = Figure(figsize=(6.8, 3.1), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(labels, values, color="#F59E0B", width=0.55)
        ax.set_facecolor("#FFFFFF")
        fig.patch.set_facecolor("#FFFFFF")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#E5E7EB")
        ax.spines["bottom"].set_color("#E5E7EB")
        ax.tick_params(colors="#6B7280")
        ax.grid(axis="y", color="#F3F4F6")
        fig.tight_layout()

        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_card)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True, padx=18, pady=14)

    def render_top_products(self, rows):
        for widget in self.top_card.winfo_children():
            widget.destroy()
        self.product_images.clear()
        title_icon = load_icon("trophy", size=(20, 20))
        if title_icon:
            self.icon_images.append(title_icon)
        ctk.CTkLabel(self.top_card, text="Top 5 món bán chạy", image=title_icon, compound="left", font=("Arial", 18, "bold"), text_color="#1F1008").pack(anchor="w", padx=20, pady=(18, 8))
        if not rows:
            ctk.CTkLabel(self.top_card, text="Chưa có dữ liệu", font=("Arial", 13), text_color="#9CA3AF").pack(pady=50)
            return
        for index, (name, qty, revenue, image_path) in enumerate(rows):
            item = ctk.CTkFrame(self.top_card, fg_color="#F9FAFB", corner_radius=16)
            item.pack(fill="x", padx=16, pady=6)
            image = load_product_image(image_path, size=(48, 48))
            if image:
                self.product_images.append(image)
                ctk.CTkLabel(item, text="", image=image).pack(side="left", padx=10, pady=8)
            rank = ctk.CTkLabel(item, text=str(index + 1), font=("Arial", 14, "bold"), width=30, height=30, corner_radius=15, fg_color="#F59E0B", text_color="white")
            rank.pack(side="left", padx=(0, 4))
            info = ctk.CTkFrame(item, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=8)
            ctk.CTkLabel(info, text=str(name), font=("Arial", 13, "bold"), text_color="#1F1008", anchor="w").pack(anchor="w")
            ctk.CTkLabel(info, text=f"{qty} ly/món", font=("Arial", 12), text_color="#8A7A70", anchor="w").pack(anchor="w")

    def render_recent_orders(self, rows):
        for widget in self.recent_card.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self.recent_card, text="Đơn hàng gần đây", font=("Arial", 18, "bold"), text_color="#1F1008").pack(anchor="w", padx=22, pady=(18, 8))
        tree = ttk.Treeview(self.recent_card, columns=("id", "time", "staff", "amount", "status"), show="headings", height=10)
        headings = [("id", "Mã đơn"), ("time", "Thời gian"), ("staff", "Nhân viên"), ("amount", "Tổng tiền"), ("status", "Trạng thái")]
        for col, text in headings:
            tree.heading(col, text=text)
            tree.column(col, anchor="center", width=150)
        tree.pack(fill="x", padx=18, pady=(0, 18))
        for order_id, created_at, seller, amount, status in rows:
            time_text = created_at.strftime("%d/%m/%Y %H:%M") if hasattr(created_at, "strftime") else str(created_at)
            status_text = "Đã thanh toán" if status == "paid" else ("Chờ thanh toán" if status == "pending" else "Đã hủy")
            tree.insert("", "end", values=(f"HĐ-{order_id:04d}", time_text, seller, f"{float(amount or 0):,.0f}đ", status_text))

    def export_excel(self):
        file_path = filedialog.asksaveasfilename(initialdir=os.path.abspath("reports/excel"), initialfile="bao_cao_doanh_thu.xlsx", defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return
        success, error = ReportController.export_report(file_path, self.current_filter)
        if error:
            messagebox.showerror("Lỗi", error)
            return
        messagebox.showinfo("Thành công", f"Đã xuất Excel:\n{file_path}")

    def export_pdf(self):
        file_path = filedialog.asksaveasfilename(initialdir=os.path.abspath("reports"), initialfile="bao_cao_doanh_thu.pdf", defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return
        success, error = ReportController.export_pdf(file_path, self.current_filter)
        if error:
            messagebox.showerror("Lỗi", error)
            return
        messagebox.showinfo("Thành công", f"Đã xuất PDF:\n{file_path}")
