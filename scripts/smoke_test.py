import requests
import time
import os
from pprint import pprint

API = os.environ.get('API_URL', 'http://localhost:5000')

def register_user():
    url = f"{API}/api/auth/register"
    email = f'smoke_test_{int(time.time())}@example.com'
    payload = {
        'name': 'Smoke Test User',
        'email': email,
        'password': 'P@ssw0rd123',
        'role': 'user'
    }
    r = requests.post(url, json=payload)
    r.raise_for_status()
    data = r.json()
    data['_email'] = email
    data['_password'] = payload['password']
    return data

def login(email, password):
    url = f"{API}/api/auth/login"
    r = requests.post(url, json={'email': email, 'password': password})
    r.raise_for_status()
    return r.json()

def mark_attendance(token):
    url = f"{API}/api/attendance/mark"
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.post(url, headers=headers, json={})
    return r

def main():
    print('Registering test user...')
    reg = register_user()
    pprint(reg)

    email = reg['_email']
    password = reg['_password']

    print('\nLogging in...')
    login_resp = login(email, password)
    pprint(login_resp)
    token = login_resp.get('token')

    print('\nMarking attendance via API...')
    mark_resp = mark_attendance(token)
    print('Attendance response status:', mark_resp.status_code)
    try:
        pprint(mark_resp.json())
    except Exception:
        print(mark_resp.text)

    print('\nSmoke test completed.')


if __name__ == '__main__':
    main()
