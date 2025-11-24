import json
import requests
import sys

BASE='http://localhost:5000'
reg_payload = {
    'name': 'E2E Tester',
    'email': 'e2e_tester@example.com',
    'password': 'Password1!',
    'role': 'employee'
}
login_payload = {
    'email': 'e2e_tester@example.com',
    'password': 'Password1!'
}

try:
    r = requests.post(BASE + '/api/auth/register', json=reg_payload, timeout=10)
    print('REGISTER', r.status_code, r.text)
except Exception as e:
    print('REGISTER ERR', e)

try:
    r2 = requests.post(BASE + '/api/auth/login', json=login_payload, timeout=10)
    print('LOGIN', r2.status_code, r2.text)
except Exception as e:
    print('LOGIN ERR', e)
    sys.exit(1)
