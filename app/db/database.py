import mysql.connector

from app.config import Config


def get_connection():
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
        port=Config.MYSQL_PORT,
    )

    conn.set_charset_collation("utf8mb4")

    return conn