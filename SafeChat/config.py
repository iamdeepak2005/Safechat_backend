import os

DB_USER = "root"
DB_PASSWORD = "Deepak%402005"
DB_HOST = "localhost"
DB_NAME = "safechat"

SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
