from models.order_model import OrderModel

class OrderController:
    @staticmethod
    def initialize():
        """Tu dong kiem tra va nang cap schema co so du lieu khi khoi dong ung dung."""
        OrderModel.check_and_update_schema()

    @staticmethod
    def create_order(user_id, cart):
        """
        Xu ly nghiep vu tao hoa don moi.
        Tinh tong so tien va gui den Model de luu don hang trang thai 'pending'.
        
        cart: dictionary chua thong tin gio hang
        """
        if not cart:
            return None, "Giỏ hàng hiện đang trống!"
            
        total_amount = 0
        for item in cart.values():
            total_amount += item["price"] * item["quantity"]
            
        try:
            order_id = OrderModel.create_pending_order(user_id, total_amount, cart)
            return order_id, None
        except Exception as e:
            return None, f"Lỗi tạo đơn hàng: {str(e)}"

    @staticmethod
    def confirm_order_payment(order_id):
        """Xac nhan hoa don da duoc thanh toan, ghi nhan doanh thu."""
        try:
            success = OrderModel.confirm_payment(order_id)
            if not success:
                return False, "Hóa đơn không ở trạng thái chờ thanh toán hoặc không tồn tại."
            return success, None
        except Exception as e:
            return False, f"Lỗi xác nhận thanh toán: {str(e)}"

    @staticmethod
    def get_history(search_val=None):
        """Lay danh sach lich su hoa don."""
        try:
            return OrderModel.get_orders_history(search_val)
        except Exception as e:
            print("Error in get_history controller:", e)
            return []

    @staticmethod
    def get_details(order_id):
        """Lay danh sach cac san pham va so luong co trong hoa don."""
        try:
            return OrderModel.get_order_details(order_id)
        except Exception as e:
            print("Error in get_details controller:", e)
            return []

    @staticmethod
    def get_stats():
        """Lay so lieu thong ke doanh thu ban hang thuc te."""
        return OrderModel.get_revenue_stats()

    @staticmethod
    def get_top_sellers(limit=5):
        """Lay danh sach san pham ban chay nhat."""
        try:
            return OrderModel.get_top_selling_products(limit)
        except Exception as e:
            print("Error in get_top_sellers controller:", e)
            return []

    @staticmethod
    def get_recents(limit=5):
        """Lay danh sach don hang vua tao."""
        try:
            return OrderModel.get_recent_orders(limit)
        except Exception as e:
            print("Error in get_recents controller:", e)
            return []
