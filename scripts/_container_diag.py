import sys
import traceback
from run import app

with app.test_request_context('/api/auth/register', method='POST', json={'first_name':'Auto','last_name':'Tester','email':'container_diag@example.com','password':'TestPass!123','role':'employee'}):
    try:
        from app.routes.auth import register
        resp = register()
        print('REGISTER RESP:', resp)
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
