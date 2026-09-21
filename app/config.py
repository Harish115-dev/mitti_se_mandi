import os


class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "dev-key-change-me"
    )

    # MySQL
    MYSQL_HOST = os.getenv(
        "MYSQL_HOST",
        "localhost"
    )

    MYSQL_USER = os.getenv(
        "MYSQL_USER",
        "root"
    )

    MYSQL_PASSWORD = os.getenv(
        "MYSQL_PASSWORD",
        ""
    )

    MYSQL_DATABASE = os.getenv(
        "MYSQL_DATABASE",
        "mitti_se_mandi"
    )

    MYSQL_PORT = int(
        os.getenv(
            "MYSQL_PORT",
            "3307"
        )
    )


    RAZORPAY_KEY_ID = os.getenv(
        "RAZORPAY_KEY_ID"
    )

    RAZORPAY_KEY_SECRET = os.getenv(
        "RAZORPAY_KEY_SECRET"
    )