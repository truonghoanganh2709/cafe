from config.database import connect_db
from models.order_model import OrderModel

class ReportModel:
    # Model truy vấn báo cáo doanh thu, chỉ tính hóa đơn đã thanh toán.
    @staticmethod
    def _date_filter_sql(date_column, filter_key):
        if filter_key == "today":
            return f"DATE(o.{date_column}) = CURDATE()"
        if filter_key == "7days":
            return f"DATE(o.{date_column}) >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)"
        if filter_key == "30days":
            return f"DATE(o.{date_column}) >= DATE_SUB(CURDATE(), INTERVAL 29 DAY)"
        if filter_key == "month":
            return f"YEAR(o.{date_column}) = YEAR(CURDATE()) AND MONTH(o.{date_column}) = MONTH(CURDATE())"
        if filter_key == "year":
            return f"YEAR(o.{date_column}) = YEAR(CURDATE())"
        return "1=1"

    @staticmethod
    def get_dashboard_data(filter_key="7days"):
        conn = connect_db()
        cursor = conn.cursor()
        date_column = OrderModel.get_order_date_column(cursor)
        product_name_column, stock_column = OrderModel.get_product_columns(cursor)
        cursor.execute("SHOW COLUMNS FROM products")
        product_columns = [row[0] for row in cursor.fetchall()]
        image_expr = "p.image" if "image" in product_columns else ("p.image_path" if "image_path" in product_columns else "''")
        date_filter = ReportModel._date_filter_sql(date_column, filter_key)

        cursor.execute(f"""
            SELECT COALESCE(SUM(o.total_amount), 0), COUNT(o.id)
            FROM orders o
            WHERE o.status='paid' AND {date_filter}
        """)
        revenue, total_orders = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        cursor.execute(f"""
            SELECT COALESCE(SUM(o.total_amount), 0)
            FROM orders o
            WHERE o.status='paid' AND DATE(o.{date_column}) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
        """)
        yesterday_revenue = cursor.fetchone()[0] or 0
        growth_percent = 0
        if yesterday_revenue > 0:
            growth_percent = round(((float(revenue) - float(yesterday_revenue)) / float(yesterday_revenue)) * 100, 1)

        cursor.execute(f"""
            SELECT DATE(o.{date_column}) AS report_date, COALESCE(SUM(o.total_amount), 0) AS revenue
            FROM orders o
            WHERE o.status='paid' AND DATE(o.{date_column}) >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
            GROUP BY DATE(o.{date_column})
            ORDER BY report_date ASC
        """)
        chart_rows = cursor.fetchall()

        cursor.execute(f"""
            SELECT p.{product_name_column}, SUM(od.quantity) AS total_sold,
                   SUM(od.quantity * od.price) AS revenue,
                   COALESCE(MAX({image_expr}), '') AS image
            FROM order_details od
            JOIN orders o ON o.id = od.order_id
            JOIN products p ON p.id = od.product_id
            WHERE o.status='paid' AND {date_filter}
            GROUP BY p.id, p.{product_name_column}
            ORDER BY total_sold DESC
            LIMIT 5
        """)
        top_products = cursor.fetchall()

        cursor.execute(f"""
            SELECT o.id, o.{date_column}, u.username, o.total_amount, COALESCE(o.status, 'pending')
            FROM orders o
            JOIN users u ON u.id = o.user_id
            ORDER BY o.{date_column} DESC
            LIMIT 10
        """)
        recent_orders = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "kpi": {
                "total_revenue": float(revenue or 0),
                "total_orders": int(total_orders or 0),
                "total_products": int(total_products or 0),
                "total_users": int(total_users or 0),
                "growth_percent": growth_percent,
            },
            "chart": chart_rows,
            "top_products": top_products,
            "recent_orders": recent_orders,
        }

    @staticmethod
    def revenue_by_day():
        conn = connect_db()
        cursor = conn.cursor()
        date_column = OrderModel.get_order_date_column(cursor)
        cursor.execute(f"""
            SELECT DATE({date_column}), SUM(total_amount), COUNT(*)
            FROM orders
            WHERE status='paid'
            GROUP BY DATE({date_column})
            ORDER BY DATE({date_column}) DESC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def revenue_by_month():
        conn = connect_db()
        cursor = conn.cursor()
        date_column = OrderModel.get_order_date_column(cursor)
        cursor.execute(f"""
            SELECT DATE_FORMAT({date_column}, '%Y-%m'), SUM(total_amount), COUNT(*)
            FROM orders
            WHERE status='paid'
            GROUP BY DATE_FORMAT({date_column}, '%Y-%m')
            ORDER BY DATE_FORMAT({date_column}, '%Y-%m') DESC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def revenue_by_year():
        conn = connect_db()
        cursor = conn.cursor()
        date_column = OrderModel.get_order_date_column(cursor)
        cursor.execute(f"""
            SELECT YEAR({date_column}), SUM(total_amount), COUNT(*)
            FROM orders
            WHERE status='paid'
            GROUP BY YEAR({date_column})
            ORDER BY YEAR({date_column}) DESC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def top_products(limit=10):
        conn = connect_db()
        cursor = conn.cursor()
        product_name_column, stock_column = OrderModel.get_product_columns(cursor)
        cursor.execute(f"""
            SELECT p.{product_name_column}, SUM(od.quantity), SUM(od.quantity * od.price)
            FROM order_details od
            JOIN products p ON p.id = od.product_id
            JOIN orders o ON o.id = od.order_id
            WHERE o.status='paid'
            GROUP BY p.id, p.{product_name_column}
            ORDER BY SUM(od.quantity) DESC
            LIMIT %s
        """, (limit,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
