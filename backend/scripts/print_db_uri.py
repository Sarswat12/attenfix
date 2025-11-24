import os
import sys
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import Config
print('ENV DB_PASSWORD:', os.getenv('DB_PASSWORD'))
print('Config.DB_PASSWORD:', Config.DB_PASSWORD)
print('SQLALCHEMY_DATABASE_URI:', Config.SQLALCHEMY_DATABASE_URI)
