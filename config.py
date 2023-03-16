import os


from dotenv import load_dotenv
from pathlib import Path


base_dir = Path(__file__).resolve().parent
env_file = base_dir / '.env'
load_dotenv(env_file)
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = ''
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PER_PAGE = 5
    JWT_EXPIRED_MINUTES = 30


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')


class TestingConfig(Config):
    DB_FILE_PATH = base_dir / 'tests' / 'test.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_FILE_PATH}'
    DEBUG = True
    TESTING = True

class ProductionConfig(Config):
    HOST_DB = os.environ.get('HOST_DB')
    PASSWORD_DB = os.environ.get('PASSWORD_DB')
    DB_USERNAME = os.environ.get('DB_USERNAME')
    DB_NAME = os.environ.get('DB_NAME')
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USERNAME}:{PASSWORD_DB}@{HOST_DB}/{DB_NAME}?charset=utf8mb4'



config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
