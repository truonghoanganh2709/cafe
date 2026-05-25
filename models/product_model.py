from config.database import connect_db

class ProductModel:
    # Model xử lý toàn bộ thao tác dữ liệu của bảng products.
    @staticmethod
    def ensure_image_column():
        # Thêm cột image nếu database cũ chưa có cột lưu đường dẫn ảnh.
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SHOW COLUMNS FROM products LIKE 'image'")
        has_image = cursor.fetchone()
        cursor.execute("SHOW COLUMNS FROM products LIKE 'image_path'")
        has_image_path = cursor.fetchone()
        if not has_image and not has_image_path:
            cursor.execute("ALTER TABLE products ADD COLUMN image VARCHAR(255) NULL")
            conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def _get_columns(cursor):
        # Tự nhận diện tên cột để tương thích database cũ và mới.
        cursor.execute("SHOW COLUMNS FROM products")
        columns = [row[0] for row in cursor.fetchall()]
        name_col = "product_name" if "product_name" in columns else "name"
        category_col = "category" if "category" in columns else ("category_id" if "category_id" in columns else None)
        quantity_col = "quantity" if "quantity" in columns else ("stock" if "stock" in columns else None)
        image_col = "image" if "image" in columns else ("image_path" if "image_path" in columns else None)
        return name_col, category_col, quantity_col, image_col

    @staticmethod
    def get_all(keyword=""):
        conn = connect_db()
        cursor = conn.cursor()
        name_col, category_col, quantity_col, image_col = ProductModel._get_columns(cursor)
        category_select = category_col if category_col else "''"
        quantity_select = quantity_col if quantity_col else "0"
        image_select = image_col if image_col else "''"
        sql = f"""
            SELECT id, {name_col}, {category_select}, price, {quantity_select}, {image_select}
            FROM products
            WHERE {name_col} LIKE %s OR CAST({category_select} AS CHAR) LIKE %s
            ORDER BY id DESC
        """
        like_keyword = f"%{keyword}%"
        cursor.execute(sql, (like_keyword, like_keyword))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def get_by_id(product_id):
        conn = connect_db()
        cursor = conn.cursor()
        name_col, category_col, quantity_col, image_col = ProductModel._get_columns(cursor)
        category_select = category_col if category_col else "''"
        quantity_select = quantity_col if quantity_col else "0"
        image_select = image_col if image_col else "''"
        cursor.execute(f"SELECT id, {name_col}, {category_select}, price, {quantity_select}, {image_select} FROM products WHERE id=%s", (product_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row

    @staticmethod
    def create(product_name, category, price, quantity, image=""):
        conn = connect_db()
        cursor = conn.cursor()
        name_col, category_col, quantity_col, image_col = ProductModel._get_columns(cursor)
        columns = [name_col, "price"]
        values = [product_name, price]
        if category_col:
            columns.append(category_col)
            values.append(category)
        if quantity_col:
            columns.append(quantity_col)
            values.append(quantity)
        if image_col:
            columns.append(image_col)
            values.append(image)
        placeholders = ", ".join(["%s"] * len(values))
        sql = f"INSERT INTO products ({', '.join(columns)}) VALUES ({placeholders})"
        cursor.execute(sql, tuple(values))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return new_id

    @staticmethod
    def update(product_id, product_name, category, price, quantity, image=""):
        conn = connect_db()
        cursor = conn.cursor()
        name_col, category_col, quantity_col, image_col = ProductModel._get_columns(cursor)
        set_parts = [f"{name_col}=%s", "price=%s"]
        values = [product_name, price]
        if category_col:
            set_parts.append(f"{category_col}=%s")
            values.append(category)
        if quantity_col:
            set_parts.append(f"{quantity_col}=%s")
            values.append(quantity)
        if image_col:
            set_parts.append(f"{image_col}=%s")
            values.append(image)
        values.append(product_id)
        sql = f"UPDATE products SET {', '.join(set_parts)} WHERE id=%s"
        cursor.execute(sql, tuple(values))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        return affected > 0

    @staticmethod
    def delete(product_id):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        return affected > 0

    @staticmethod
    def count_all():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        total = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return total
