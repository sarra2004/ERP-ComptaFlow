from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:password@localhost:3306/erp_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
