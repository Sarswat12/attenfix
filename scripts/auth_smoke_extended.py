#!/usr/bin/env python3
"""
Extended auth smoke tests
- register -> login -> verify -> logout -> verify-fails

Usage: python scripts/auth_smoke_extended.py --base-url http://localhost:5000
"""
import requests
import sys
import uuid
import argparse


def register(base_url, email, password, role='employee'):
    url = f"{base_url}/api/auth/register"
    body = {
        'first_name': 'Auto',
        'last_name': 'Tester',
        'email': email,
        'password': password,
        'role': role
    }
    r = requests.post(url, json=body, timeout=10)
    r.raise_for_status()
    return r.json()


def login(base_url, email, password):
    url = f"{base_url}/api/auth/login"
    r = requests.post(url, json={'email': email, 'password': password}, timeout=10)
    r.raise_for_status()
    return r.json()


def verify(base_url, token):
    url = f"{base_url}/api/auth/verify-token"
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(url, headers=headers, timeout=10)
    return r


def logout(base_url, token):
    url = f"{base_url}/api/auth/logout"
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.post(url, headers=headers, timeout=10)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base-url', default='http://localhost:5000')
    args = ap.parse_args()
    base = args.base_url.rstrip('/')

    email = f"autotest+{uuid.uuid4().hex[:6]}@example.com"
    password = 'TestPass!123'

    print('Registering', email)
    reg = register(base, email, password)
    print('Register response:', reg)

    print('Logging in')
    log = login(base, email, password)
    print('Login response:', log)
    token = log.get('token') or reg.get('token')
    if not token:
        print('No token returned, aborting')
        sys.exit(2)

    print('Verifying token (should be valid)')
    r = verify(base, token)
    print('Verify status:', r.status_code, r.text)

    print('Logging out (revoking token)')
    r = logout(base, token)
    print('Logout status:', r.status_code, r.text)

    print('Verifying token again (should fail)')
    r = verify(base, token)
    print('Verify after logout status:', r.status_code, r.text)


if __name__ == '__main__':
    main()
