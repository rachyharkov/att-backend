
import os
from dotenv import load_dotenv

load_dotenv()
def get_db_config():
    return {
        'MYSQL_HOST': os.getenv('MYSQL_HOST'),
        'MYSQL_USER': os.getenv('MYSQL_USER'),
        'MYSQL_PASSWORD': os.getenv('MYSQL_PASSWORD'),
        'MYSQL_DB': os.getenv('MYSQL_DATABASE'),
        'SECRET_KEY': os.getenv('SECRET_KEY')
    }