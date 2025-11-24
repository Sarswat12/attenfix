import json
import requests
import sys
url='http://localhost:5001/api/auth/register'
with open('temp_reg.json') as f:
    payload=json.load(f)
try:
    r = requests.post(url, json=payload, timeout=10)
    print(r.status_code)
    print(r.text)
except Exception as e:
    print('ERR', e)
    sys.exit(1)
