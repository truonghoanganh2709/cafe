import os
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from controllers.report_controller import ReportController

class ReportFrame(ctk.CTkFrame):
    # Giao diện báo cáo doanh thu và xuất Excel cho Admin.
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F5F2ED", corner_radius=0)
        self.controller = controller
        self.current_type = "day"

        ctk.CTkLabel(self, text="Báo cáo doanh thu", font=("Arial", 26, "bold"), text_color="#1F1008").pack(anchor="w", padx=30, pady=(25, 5))
        ctk.CTkLabel(self, text="Doanh thu chỉ tính các hóa đơn đã thanh toán", font=("Arial", 13), text_color="#8A7A70").pack(anchor="w", padx=30, pady=(0, 15))

        tools = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        tools.pack(fill="x", padx=30, pady=5)

        self.combo_type = ctk.CTkComboBox(tools, values=["day", "month", "year", "top"], state="readonly", width=160, command=self.change_type)
        self.combo_type.pack(side="left", padx=15, pady=12)
        self.combo_type.set("day")

        ctk.CTkButton(tools, text="↻ Tải báo cáo", fg_color="#F59E0B", command=self.load_report).pack(side="left", padx=8)
        ctk.CTkButton(tools, text="📤 Xuất Excel", fg_color="#10B981", command=self.export_excel).pack(side="right", padx=15)

        table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        table_frame.pack(fill="both", expand=True, padx=30, pady=15)
        self.tree = ttk.Treeview(table_frame, show="headings")
        self.tree.pack(fill="both", expand=True, padx=15, pady=15)

        self.load_report()

    def change_type(self, value):
        self.current_type = value
        self.load_report()

    def load_report(self):
        headers, rows, error = ReportController.get_report(self.current_type)
        if error:
            messagebox.showerror("Lỗi", error)
            return

        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = headers
        for header in headers:
            self.tree.heading(header, text=header.upper())
            self.tree.column(header, anchor="center", width=180)

        for row in rows:
            values = []
            for value in row:
                if isinstance(value, float):
                    values.append(f"{value:,.0f}")
                else:
                    values.append(value)
            self.tree.insert("", "end", values=values)

    def export_excel(self):
        default_name = f"bao_cao_{self.current_type}.xlsx"
        file_path = filedialog.asksaveasfilename(
            initialdir=os.path.abspath("reports/excel"),
            initialfile=default_name,
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if not file_path:
            return
        success, error = ReportController.export_report(file_path, self.current_type)
        if error:
            messagebox.showerror("Lỗi", error)
            return
        messagebox.showinfo("Thành công", f"Đã xuất Excel:\n{file_path}")
