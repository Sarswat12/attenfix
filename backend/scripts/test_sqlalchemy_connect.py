import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()
from config import Config
from sqlalchemy import create_engine, text

uri = Config.SQLALCHEMY_DATABASE_URI
print('Using URI:', uri)
engine = create_engine(uri)
try:
    with engine.connect() as conn:
        r = conn.execute(text('SELECT 1'))
        print('SQLAlchemy connect OK, result:', r.scalar())
except Exception as e:
    print('SQLAlchemy connect error:', type(e), e)
