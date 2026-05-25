def is_required(value):
    # Kiểm tra chuỗi bắt buộc không được để trống.
    return value is not None and str(value).strip() != ""


def is_positive_number(value):
    # Kiểm tra giá trị là số dương.
    try:
        return float(value) >= 0
    except (TypeError, ValueError):
        return False


def is_positive_integer(value):
    # Kiểm tra giá trị là số nguyên không âm.
    try:
        return int(value) >= 0
    except (TypeError, ValueError):
        return False
