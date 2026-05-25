from models.product_model import ProductModel
from utils.validators import is_required, is_positive_integer, is_positive_number

class ProductController:
    # Controller kiểm tra dữ liệu món ăn trước khi gọi Model.
    @staticmethod
    def get_products(keyword=""):
        try:
            return ProductModel.get_all(keyword), None
        except Exception as e:
            return [], f"Lỗi lấy danh sách món: {str(e)}"

    @staticmethod
    def create_product(product_name, category, price, quantity, image=""):
        if not is_required(product_name) or not is_required(category):
            return None, "Tên món và loại món không được để trống."
        if not is_positive_number(price):
            return None, "Giá món phải là số không âm."
        if not is_positive_integer(quantity):
            return None, "Số lượng phải là số nguyên không âm."

        try:
            product_id = ProductModel.create(product_name, category, float(price), int(quantity), image)
            return product_id, None
        except Exception as e:
            return None, f"Lỗi thêm món: {str(e)}"

    @staticmethod
    def update_product(product_id, product_name, category, price, quantity, image=""):
        if not product_id:
            return False, "Chưa chọn món cần sửa."
        if not is_required(product_name) or not is_required(category):
            return False, "Tên món và loại món không được để trống."
        if not is_positive_number(price):
            return False, "Giá món phải là số không âm."
        if not is_positive_integer(quantity):
            return False, "Số lượng phải là số nguyên không âm."

        try:
            return ProductModel.update(product_id, product_name, category, float(price), int(quantity), image), None
        except Exception as e:
            return False, f"Lỗi sửa món: {str(e)}"

    @staticmethod
    def delete_product(product_id):
        if not product_id:
            return False, "Chưa chọn món cần xóa."
        try:
            return ProductModel.delete(product_id), None
        except Exception as e:
            return False, f"Không thể xóa món do đã phát sinh dữ liệu liên quan: {str(e)}"
