from openpyxl import Workbook


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
