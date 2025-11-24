import os
from dotenv import load_dotenv
load_dotenv()
import mysql.connector

user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = int(os.getenv('DB_PORT', '3306'))
db = os.getenv('DB_NAME')
print('Attempting direct mysql.connector connect with:')
print('user=', user)
print('password=', password)
print('host=', host)
print('port=', port)
print('db=', db)
try:
    conn = mysql.connector.connect(user=user, password=password, host=host, port=port, database=db)
    print('Connected OK, server version:', conn.get_server_info())
    conn.close()
except Exception as e:
    print('Connect error:', type(e), e)
