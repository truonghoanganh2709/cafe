import mysql.connector

def connect_db():
    # Tạo kết nối thật tới MySQL database cafe_management.
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="cafe_management"
    )

    return conn