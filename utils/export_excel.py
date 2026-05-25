from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill


def export_rows_to_excel(file_path, sheet_title, headers, rows):
    # Xuất danh sách dữ liệu ra file Excel bằng openpyxl.
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_title

    sheet.append(headers)
    for row in rows:
        sheet.append(list(row))

    workbook.save(file_path)
    return file_path


def _write_table(sheet, start_row, title, headers, rows):
    # Ghi một bảng dữ liệu có tiêu đề vào sheet Excel.
    title_fill = PatternFill("solid", fgColor="F59E0B")
    header_fill = PatternFill("solid", fgColor="F3F4F6")

    sheet.cell(start_row, 1, title)
    sheet.cell(start_row, 1).font = Font(bold=True, size=14, color="FFFFFF")
    sheet.cell(start_row, 1).fill = title_fill

    header_row = start_row + 1
    for col_index, header in enumerate(headers, start=1):
        cell = sheet.cell(header_row, col_index, header)
        cell.font = Font(bold=True)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    for row_index, row in enumerate(rows, start=header_row + 1):
        for col_index, value in enumerate(row, start=1):
            sheet.cell(row_index, col_index, value)

    return header_row + len(rows) + 3


def export_full_report_to_excel(file_path, report_data):
    # Xuất báo cáo tổng hợp đầy đủ gồm nhiều sheet.
    workbook = Workbook()
    workbook.remove(workbook.active)

    overview_sheet = workbook.create_sheet("TongQuan")
    overview_rows = [
        ("Tổng doanh thu", report_data["overview"].get("total_revenue", 0)),
        ("Tổng số đơn paid", report_data["overview"].get("total_orders", 0)),
        ("Giá trị đơn trung bình", report_data["overview"].get("avg_order", 0)),
        ("Doanh thu hôm nay", report_data["overview"].get("today_revenue", 0)),
        ("Số đơn hôm nay", report_data["overview"].get("today_orders", 0)),
        ("Tổng món bán hôm nay", report_data["overview"].get("today_items", 0)),
        ("Doanh thu tháng hiện tại", report_data["overview"].get("month_revenue", 0)),
        ("Tổng sản phẩm", report_data["overview"].get("total_products", 0)),
        ("Tổng user", report_data["overview"].get("total_users", 0)),
    ]
    _write_table(overview_sheet, 1, "TỔNG QUAN KINH DOANH", ["Chỉ số", "Giá trị"], overview_rows)

    sheets = [
        ("TheoNgay", "DOANH THU THEO NGÀY", ["Ngày", "Doanh thu", "Số đơn"], report_data["by_day"]),
        ("TheoThang", "DOANH THU THEO THÁNG", ["Tháng", "Doanh thu", "Số đơn"], report_data["by_month"]),
        ("TheoNam", "DOANH THU THEO NĂM", ["Năm", "Doanh thu", "Số đơn"], report_data["by_year"]),
        ("TopMon", "TOP MÓN BÁN CHẠY", ["Tên món", "Số lượng bán", "Doanh thu"], report_data["top_products"]),
    ]
    for sheet_name, title, headers, rows in sheets:
        sheet = workbook.create_sheet(sheet_name)
        _write_table(sheet, 1, title, headers, rows)

    for sheet in workbook.worksheets:
        for column_cells in sheet.columns:
            column_letter = column_cells[0].column_letter
            sheet.column_dimensions[column_letter].width = 22

    workbook.save(file_path)
    return file_path


def export_invoice_to_excel(file_path, invoice_info, details):
    # Xuất một hóa đơn bán hàng ra Excel cho nhân viên.
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "HoaDon"

    title_fill = PatternFill("solid", fgColor="F59E0B")
    header_fill = PatternFill("solid", fgColor="F3F4F6")

    sheet.merge_cells("A1:E1")
    sheet["A1"] = "TLU CAFÉ POS - HÓA ĐƠN BÁN HÀNG"
    sheet["A1"].font = Font(bold=True, size=16, color="FFFFFF")
    sheet["A1"].fill = title_fill
    sheet["A1"].alignment = Alignment(horizontal="center")

    info_rows = [
        ("Mã hóa đơn", invoice_info.get("code", "")),
        ("Thời gian", invoice_info.get("time", "")),
        ("Nhân viên", invoice_info.get("seller", "")),
        ("Trạng thái", invoice_info.get("status", "")),
    ]
    current_row = 3
    for label, value in info_rows:
        sheet.cell(current_row, 1, label).font = Font(bold=True)
        sheet.cell(current_row, 2, value)
        current_row += 1

    headers = ["STT", "Tên món", "Số lượng", "Đơn giá", "Thành tiền"]
    header_row = current_row + 1
    for col_index, header in enumerate(headers, start=1):
        cell = sheet.cell(header_row, col_index, header)
        cell.font = Font(bold=True)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    total_amount = 0
    for index, (name, qty, price) in enumerate(details, start=1):
        subtotal = qty * price
        total_amount += subtotal
        row_index = header_row + index
        sheet.cell(row_index, 1, index)
        sheet.cell(row_index, 2, name)
        sheet.cell(row_index, 3, qty)
        sheet.cell(row_index, 4, float(price))
        sheet.cell(row_index, 5, float(subtotal))

    total_row = header_row + len(details) + 2
    sheet.cell(total_row, 4, "Tổng tiền").font = Font(bold=True)
    sheet.cell(total_row, 5, float(total_amount)).font = Font(bold=True)

    for column, width in {"A": 8, "B": 28, "C": 12, "D": 15, "E": 15}.items():
        sheet.column_dimensions[column].width = width

    workbook.save(file_path)
    return file_path
