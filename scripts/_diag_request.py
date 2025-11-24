import requests
url='http://localhost:5000/api/auth/register'
body={'first_name':'Auto','last_name':'Tester','email':'diag3@example.com','password':'TestPass!123','role':'employee'}
try:
    r = requests.post(url, json=body, timeout=15)
    print('STATUS', r.status_code)
    print('TEXT', r.text)
except Exception as e:
    print('EXCEPTION', e)
