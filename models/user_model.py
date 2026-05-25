from config.database import connect_db

class UserModel:
    # Model quản lý dữ liệu tài khoản người dùng trong bảng users.
    @staticmethod
    def _get_fullname_column(cursor):
        # Tự nhận diện tên cột họ tên để tương thích với database đã tạo trước đó.
        cursor.execute("SHOW COLUMNS FROM users")
        columns = [row[0] for row in cursor.fetchall()]
        for column in ["fullname", "full_name", "name"]:
            if column in columns:
                return column
        return "username"

    @staticmethod
    def authenticate(username, password):
        conn = connect_db()
        cursor = conn.cursor()
        fullname_column = UserModel._get_fullname_column(cursor)
        sql = f"SELECT id, username, {fullname_column}, role FROM users WHERE username=%s AND password=%s"
        cursor.execute(sql, (username, password))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row

    @staticmethod
    def get_all(keyword=""):
        conn = connect_db()
        cursor = conn.cursor()
        fullname_column = UserModel._get_fullname_column(cursor)
        sql = f"""
            SELECT id, username, {fullname_column}, role
            FROM users
            WHERE username LIKE %s OR {fullname_column} LIKE %s OR role LIKE %s
            ORDER BY id DESC
        """
        like_keyword = f"%{keyword}%"
        cursor.execute(sql, (like_keyword, like_keyword, like_keyword))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def get_by_id(user_id):
        conn = connect_db()
        cursor = conn.cursor()
        fullname_column = UserModel._get_fullname_column(cursor)
        cursor.execute(f"SELECT id, username, password, {fullname_column}, role FROM users WHERE id=%s", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row

    @staticmethod
    def create(username, password, fullname, role):
        conn = connect_db()
        cursor = conn.cursor()
        fullname_column = UserModel._get_fullname_column(cursor)
        sql = f"INSERT INTO users (username, password, {fullname_column}, role) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (username, password, fullname, role))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return new_id

    @staticmethod
    def update(user_id, username, password, fullname, role):
        conn = connect_db()
        cursor = conn.cursor()
        fullname_column = UserModel._get_fullname_column(cursor)
        sql = f"UPDATE users SET username=%s, password=%s, {fullname_column}=%s, role=%s WHERE id=%s"
        cursor.execute(sql, (username, password, fullname, role, user_id))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        return affected > 0

    @staticmethod
    def delete(user_id):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        return affected > 0

    @staticmethod
    def count_all():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return total
