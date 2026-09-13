
import mysql.connector


def get_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="mitti_se_mandi",
        port=3307,
    )
    conn.set_charset_collation("utf8mb4")
    return conn
