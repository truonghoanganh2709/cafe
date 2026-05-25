from config.database import connect_db

class UserModel:
    # Model quản lý dữ liệu tài khoản người dùng trong bảng users.
    @staticmethod
    def ensure_status_column():
        # Thêm cột status nếu database cũ chưa có để khóa/mở tài khoản.
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SHOW COLUMNS FROM users LIKE 'status'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'active'")
            conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def _get_fullname_column(cursor):
        cursor.execute("SHOW COLUMNS FROM users")
        columns = [row[0] for row in cursor.fetchall()]
        for column in ["fullname", "full_name", "name"]:
            if column in columns:
                return column
        return None

    @staticmethod
    def authenticate(username, password):
        UserModel.ensure_status_column()
        conn = connect_db()
        cursor = conn.cursor()
        fullname_column = UserModel._get_fullname_column(cursor)
        fullname_select = fullname_column if fullname_column else "username"
        sql = f"""
            SELECT id, username, {fullname_select}, role, status
            FROM users
            WHERE username=%s AND password=%s
        """
        cursor.execute(sql, (username, password))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row

    @staticmethod
    def get_all(keyword=""):
        UserModel.ensure_status_column()
        conn = connect_db()
        cursor = conn.cursor()
        fullname_column = UserModel._get_fullname_column(cursor)
        fullname_select = fullname_column if fullname_column else "username"
        sql = f"""
            SELECT id, username, {fullname_select}, role, status
            FROM users
            WHERE username LIKE %s OR {fullname_select} LIKE %s OR role LIKE %s OR status LIKE %s
            ORDER BY id DESC
        """
        like_keyword = f"%{keyword}%"
        cursor.execute(sql, (like_keyword, like_keyword, like_keyword, like_keyword))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def get_by_id(user_id):
        UserModel.ensure_status_column()
        conn = connect_db()
        cursor = conn.cursor()
        fullname_column = UserModel._get_fullname_column(cursor)
        fullname_select = fullname_column if fullname_column else "username"
        cursor.execute(f"SELECT id, username, password, {fullname_select}, role, status FROM users WHERE id=%s", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row

    @staticmethod
    def username_exists(username, exclude_user_id=None):
        conn = connect_db()
        cursor = conn.cursor()
        if exclude_user_id:
            cursor.execute("SELECT COUNT(*) FROM users WHERE username=%s AND id<>%s", (username, exclude_user_id))
        else:
            cursor.execute("SELECT COUNT(*) FROM users WHERE username=%s", (username,))
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count > 0

    @staticmethod
    def create(username, password, fullname, role, status="active"):
        UserModel.ensure_status_column()
        conn = connect_db()
        cursor = conn.cursor()
        fullname_column = UserModel._get_fullname_column(cursor)
        if fullname_column:
            sql = f"INSERT INTO users (username, password, {fullname_column}, role, status) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (username, password, fullname, role, status))
        else:
            sql = "INSERT INTO users (username, password, role, status) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (username, password, role, status))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return new_id

    @staticmethod
    def update(user_id, username, password, fullname, role, status="active"):
        UserModel.ensure_status_column()
        conn = connect_db()
        cursor = conn.cursor()
        fullname_column = UserModel._get_fullname_column(cursor)
        if fullname_column:
            sql = f"UPDATE users SET username=%s, password=%s, {fullname_column}=%s, role=%s, status=%s WHERE id=%s"
            cursor.execute(sql, (username, password, fullname, role, status, user_id))
        else:
            sql = "UPDATE users SET username=%s, password=%s, role=%s, status=%s WHERE id=%s"
            cursor.execute(sql, (username, password, role, status, user_id))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        return affected > 0

    @staticmethod
    def set_status(user_id, status):
        UserModel.ensure_status_column()
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET status=%s WHERE id=%s", (status, user_id))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        return affected > 0

    @staticmethod
    def delete(user_id):
        # Không xóa vật lý để giữ lịch sử hóa đơn, chỉ vô hiệu hóa tài khoản.
        return UserModel.set_status(user_id, "inactive")

    @staticmethod
    def count_all():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return total
