import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()
from app import create_app

app = create_app('development')
with app.test_client() as c:
    r = c.get('/api/health/detailed')
    print('Status:', r.status_code)
    try:
        print('JSON:', r.get_json())
    except Exception as e:
        print('Response text:', r.data)
