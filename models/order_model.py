from config.database import connect_db
from datetime import datetime

class OrderModel:
    @staticmethod
    def check_and_update_schema():
        """Tu dong kiem tra va nang cap schema database them cot status vao bang orders neu chua co."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # Kiem tra xem cot status da ton tai trong bang orders chua
            cursor.execute("SHOW COLUMNS FROM orders LIKE 'status'")
            result = cursor.fetchone()
            
            if not result:
                print("Column 'status' does not exist. Adding status column to orders table...")
                cursor.execute("ALTER TABLE orders ADD COLUMN status VARCHAR(20) DEFAULT 'pending'")
                conn.commit()
                print("Added column 'status' successfully.")
            
            cursor.close()
            conn.close()
        except Exception as e:
            print("Error updating database schema for orders status:", e)

    @staticmethod
    def get_order_date_column(cursor):
        cursor.execute("SHOW COLUMNS FROM orders LIKE 'order_date'")
        if cursor.fetchone():
            return "order_date"

        cursor.execute("SHOW COLUMNS FROM orders LIKE 'created_at'")
        if cursor.fetchone():
            return "created_at"

        cursor.execute("ALTER TABLE orders ADD COLUMN order_date DATETIME DEFAULT CURRENT_TIMESTAMP")
        return "order_date"

    @staticmethod
    def create_pending_order(user_id, total_amount, cart):
        """
        Tao hoa don moi o trang thai cho thanh toan (pending) va luu chi tiet hoa don.
        Giam so luong ton kho cua cac san pham tuong ung.
        
        cart: dictionary chua thong tin gio hang {product_id: {name, price, quantity, max_stock}}
        """
        conn = None
        cursor = None
        try:
            conn = connect_db()
            cursor = conn.cursor()
            date_column = OrderModel.get_order_date_column(cursor)
            
            # 1. Bat dau luu hoa don chinh
            sql_order = f"INSERT INTO orders (user_id, total_amount, {date_column}, status) VALUES (%s, %s, %s, 'pending')"
            now = datetime.now()
            cursor.execute(sql_order, (user_id, total_amount, now))
            order_id = cursor.lastrowid
            
            # 2. Luu chi tiet tung san pham trong don va tru kho
            for p_id, item in cart.items():
                qty = item["quantity"]
                price = item["price"]
                
                # Insert chi tiet don hang
                sql_detail = "INSERT INTO order_details (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql_detail, (order_id, p_id, qty, price))
                
                # Cap nhat tru ton kho cua san pham
                sql_update_stock = "UPDATE products SET quantity = quantity - %s WHERE id = %s"
                cursor.execute(sql_update_stock, (qty, p_id))
            
            conn.commit()
            return order_id
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def confirm_payment(order_id):
        """Xac nhan thanh toan cho mot hoa don: Doi trang thai status sang 'paid'."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            sql = "UPDATE orders SET status = 'paid' WHERE id = %s AND status = 'pending'"
            cursor.execute(sql, (order_id,))
            affected_rows = cursor.rowcount
            
            conn.commit()
            cursor.close()
            conn.close()
            return affected_rows > 0
        except Exception as e:
            raise e

    @staticmethod
    def get_orders_history(search_val=None):
        """Truy van danh sach lich su hoa don tu DB, sap xep theo thoi gian lap gan nhat."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            date_column = OrderModel.get_order_date_column(cursor)
            
            sql = f"""
                SELECT o.id, o.{date_column}, o.total_amount, COALESCE(o.status, 'pending'), u.username
                FROM orders o
                JOIN users u ON o.user_id = u.id
                WHERE 1=1
            """
            params = []
            if search_val:
                sql += " AND o.id LIKE %s"
                params.append(f"%{search_val}%")
                
            sql += f" ORDER BY o.{date_column} DESC"
            
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            return rows
        except Exception as e:
            raise e

    @staticmethod
    def get_order_details(order_id):
        """Lay danh sach chi tiet cac mon an co trong mot hoa don."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            sql = """
                SELECT p.product_name, od.quantity, od.price
                FROM order_details od
                JOIN products p ON od.product_id = p.id
                WHERE od.order_id = %s
            """
            cursor.execute(sql, (order_id,))
            rows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            return rows
        except Exception as e:
            raise e

    @staticmethod
    def get_revenue_stats():
        """
        Tinh toan tong hop doanh thu va so don tu database.
        CHI TINH tu cac don hang co trang thai status = 'paid'.
        """
        res = {"total_revenue": 0.0, "total_orders": 0, "avg_order": 0.0, "today_orders": 0, "today_revenue": 0.0, "total_products": 0}
        try:
            conn = connect_db()
            cursor = conn.cursor()
            date_column = OrderModel.get_order_date_column(cursor)

            # 1. Tong doanh thu luy ke & Tong don tu cac don 'paid'
            cursor.execute("SELECT SUM(total_amount), COUNT(*) FROM orders WHERE status = 'paid'")
            row = cursor.fetchone()
            if row:
                tot = row[0]
                res["total_revenue"] = float(tot) if tot else 0.0
                res["total_orders"] = row[1] if row[1] else 0
                if res["total_orders"] > 0:
                    res["avg_order"] = res["total_revenue"] / res["total_orders"]

            # 2. So đơn hom nay (chi tinh don 'paid')
            cursor.execute(f"SELECT COUNT(*) FROM orders WHERE DATE({date_column}) = CURDATE() AND status = 'paid'")
            res["today_orders"] = cursor.fetchone()[0]

            # 3. Doanh thu hom nay (chi tinh don 'paid')
            cursor.execute(f"SELECT SUM(total_amount) FROM orders WHERE DATE({date_column}) = CURDATE() AND status = 'paid'")
            rev = cursor.fetchone()[0]
            res["today_revenue"] = float(rev) if rev else 0.0

            # 4. Tong so san pham dang co
            cursor.execute("SELECT COUNT(*) FROM products")
            res["total_products"] = cursor.fetchone()[0]

            cursor.close()
            conn.close()
        except Exception as e:
            print("Error calculating revenue stats in Model:", e)
        return res

    @staticmethod
    def get_top_selling_products(limit=5):
        """
        Lay danh sach cac mon an ban chay nhat.
        CHI TINH tu cac hoa don da thanh toan thanh cong (status = 'paid').
        """
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            sql = """
                SELECT p.product_name, SUM(od.quantity) as total_sold
                FROM order_details od
                JOIN products p ON od.product_id = p.id
                JOIN orders o ON od.order_id = o.id
                WHERE o.status = 'paid'
                GROUP BY od.product_id
                ORDER BY total_sold DESC
                LIMIT %s
            """
            cursor.execute(sql, (limit,))
            rows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            return rows
        except Exception as e:
            raise e

    @staticmethod
    def get_recent_orders(limit=5):
        """Lay cac don hang vua tao gan day (hien thi tren trang chu)."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            date_column = OrderModel.get_order_date_column(cursor)
            
            sql = f"""
                SELECT o.id, o.{date_column}, o.total_amount, COALESCE(o.status, 'pending'), u.username
                FROM orders o
                JOIN users u ON o.user_id = u.id
                ORDER BY o.{date_column} DESC
                LIMIT %s
            """
            cursor.execute(sql, (limit,))
            rows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            return rows
        except Exception as e:
            raise e
