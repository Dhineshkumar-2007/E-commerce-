import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    SECRET_KEY = os.getenv("SECRET_KEY")

    # ===========================
    # LOCAL DATABASE - ACTIVE
    # ===========================
    """
    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_USER = "root"
    DB_PASSWORD = "Sql.dk2007@14"
    DB_NAME = "mydb1"
    """
    # ===========================
    # CLOUD DATABASE - LATER
    # ===========================

    
    DB_HOST = os.getenv("CLOUD_DB_HOST")
    DB_PORT = os.getenv("CLOUD_DB_PORT")
    DB_USER = os.getenv("CLOUD_DB_USER")
    DB_PASSWORD = os.getenv("CLOUD_DB_PASSWORD")
    DB_NAME = os.getenv("CLOUD_DB_NAME")
    DB_SSL_CA = os.getenv("CLOUD_DB_SSL_CA")
    

    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"