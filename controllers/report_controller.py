from models.report_model import ReportModel
from models.order_model import OrderModel
from utils.export_excel import export_full_report_to_excel

class ReportController:
    # Controller gom dữ liệu báo cáo và hỗ trợ xuất Excel/PDF.
    @staticmethod
    def get_dashboard_data(filter_key="7days"):
        try:
            return ReportModel.get_dashboard_data(filter_key), None
        except Exception as e:
            return None, f"Lỗi tải dashboard báo cáo: {str(e)}"

    @staticmethod
    def get_full_report_data():
        try:
            return {
                "overview": OrderModel.get_revenue_stats(),
                "by_day": ReportModel.revenue_by_day(),
                "by_month": ReportModel.revenue_by_month(),
                "by_year": ReportModel.revenue_by_year(),
                "top_products": ReportModel.top_products(20),
            }, None
        except Exception as e:
            return None, f"Lỗi lấy báo cáo tổng hợp: {str(e)}"

    @staticmethod
    def export_report(file_path, filter_key="7days"):
        try:
            report_data, error = ReportController.get_full_report_data()
            if error:
                return False, error
            export_full_report_to_excel(file_path, report_data)
            return True, None
        except Exception as e:
            return False, f"Lỗi xuất Excel: {str(e)}"

    @staticmethod
    def export_pdf(file_path, filter_key="7days"):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except Exception:
            return False, "Chưa cài thư viện reportlab. Hãy cài: pip install reportlab"

        try:
            data = ReportModel.get_dashboard_data(filter_key)
            kpi = data["kpi"]
            pdf = canvas.Canvas(file_path, pagesize=A4)
            width, height = A4

            y = height - 50
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(50, y, "TLU Cafe POS - Bao cao doanh thu")
            y -= 35

            pdf.setFont("Helvetica", 11)
            pdf.drawString(50, y, f"Tong doanh thu: {kpi['total_revenue']:,.0f} VND")
            y -= 20
            pdf.drawString(50, y, f"Tong so don paid: {kpi['total_orders']}")
            y -= 20
            pdf.drawString(50, y, f"Tong san pham: {kpi['total_products']}")
            y -= 20
            pdf.drawString(50, y, f"Tong user: {kpi['total_users']}")
            y -= 35

            pdf.setFont("Helvetica-Bold", 13)
            pdf.drawString(50, y, "Top 5 mon ban chay")
            y -= 25
            pdf.setFont("Helvetica", 10)
            for index, row in enumerate(data["top_products"], start=1):
                name, qty, revenue, image = row
                pdf.drawString(60, y, f"{index}. {name} - {qty} mon - {float(revenue or 0):,.0f} VND")
                y -= 18

            y -= 15
            pdf.setFont("Helvetica-Bold", 13)
            pdf.drawString(50, y, "Don hang gan day")
            y -= 25
            pdf.setFont("Helvetica", 9)
            for order_id, created_at, seller, amount, status in data["recent_orders"]:
                pdf.drawString(60, y, f"HD-{order_id:04d} | {created_at} | {seller} | {float(amount or 0):,.0f} VND | {status}")
                y -= 16
                if y < 60:
                    pdf.showPage()
                    y = height - 50

            pdf.save()
            return True, None
        except Exception as e:
            return False, f"Lỗi xuất PDF: {str(e)}"
