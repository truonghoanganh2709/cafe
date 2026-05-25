from models.report_model import ReportModel
from utils.export_excel import export_rows_to_excel

class ReportController:
    # Controller gom dữ liệu báo cáo và hỗ trợ xuất Excel.
    @staticmethod
    def get_report(report_type):
        try:
            if report_type == "day":
                return ["Ngày", "Doanh thu", "Số đơn"], ReportModel.revenue_by_day(), None
            if report_type == "month":
                return ["Tháng", "Doanh thu", "Số đơn"], ReportModel.revenue_by_month(), None
            if report_type == "year":
                return ["Năm", "Doanh thu", "Số đơn"], ReportModel.revenue_by_year(), None
            if report_type == "top":
                return ["Tên món", "Số lượng bán", "Doanh thu"], ReportModel.top_products(), None
            return [], [], "Loại báo cáo không hợp lệ."
        except Exception as e:
            return [], [], f"Lỗi lấy báo cáo: {str(e)}"

    @staticmethod
    def export_report(file_path, report_type):
        headers, rows, error = ReportController.get_report(report_type)
        if error:
            return False, error
        try:
            export_rows_to_excel(file_path, "BaoCao", headers, rows)
            return True, None
        except Exception as e:
            return False, f"Lỗi xuất Excel: {str(e)}"
