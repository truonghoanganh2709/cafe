from config.database import connect_db
from models.order_model import OrderModel

class ReportModel:
    # Model truy vấn báo cáo doanh thu, chỉ tính hóa đơn đã thanh toán.
    @staticmethod
    def revenue_by_day():
        conn = connect_db()
        cursor = conn.cursor()
        date_column = OrderModel.get_order_date_column(cursor)
        sql = f"""
            SELECT DATE({date_column}) AS report_date, SUM(total_amount) AS revenue, COUNT(*) AS total_orders
            FROM orders
            WHERE status='paid'
            GROUP BY DATE({date_column})
            ORDER BY report_date DESC
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def revenue_by_month():
        conn = connect_db()
        cursor = conn.cursor()
        date_column = OrderModel.get_order_date_column(cursor)
        sql = f"""
            SELECT DATE_FORMAT({date_column}, '%Y-%m') AS report_month, SUM(total_amount) AS revenue, COUNT(*) AS total_orders
            FROM orders
            WHERE status='paid'
            GROUP BY DATE_FORMAT({date_column}, '%Y-%m')
            ORDER BY report_month DESC
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def revenue_by_year():
        conn = connect_db()
        cursor = conn.cursor()
        date_column = OrderModel.get_order_date_column(cursor)
        sql = f"""
            SELECT YEAR({date_column}) AS report_year, SUM(total_amount) AS revenue, COUNT(*) AS total_orders
            FROM orders
            WHERE status='paid'
            GROUP BY YEAR({date_column})
            ORDER BY report_year DESC
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def top_products(limit=10):
        conn = connect_db()
        cursor = conn.cursor()
        sql = """
            SELECT p.product_name, SUM(od.quantity) AS total_sold, SUM(od.quantity * od.price) AS revenue
            FROM order_details od
            JOIN products p ON p.id = od.product_id
            JOIN orders o ON o.id = od.order_id
            WHERE o.status='paid'
            GROUP BY p.id, p.product_name
            ORDER BY total_sold DESC
            LIMIT %s
        """
        cursor.execute(sql, (limit,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
