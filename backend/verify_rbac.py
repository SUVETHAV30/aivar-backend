import os, sys
sys.path.insert(0, '.')
os.environ['DATABASE_URL'] = 'sqlite:///./app.db'

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test login with each role
for user, pwd, role in [('admin','admin123','admin'), ('analyst','analyst123','analyst'), ('viewer','viewer123','viewer')]:
    r = client.post('/auth/login', json={'username': user, 'password': pwd})
    assert r.status_code == 200, f'Login failed for {user}: {r.text}'
    data = r.json()
    assert 'access_token' in data
    assert data['role'] == role
    print(f'OK: {user} -> role={data["role"]}')

# Test RBAC: viewer cannot create agent
r_login = client.post('/auth/login', json={'username': 'viewer', 'password': 'viewer123'})
token = r_login.json()['access_token']
r = client.post('/agents', json={'name': 'X', 'prompt': 'X', 'tool_list': []}, headers={'Authorization': f'Bearer {token}'})
assert r.status_code == 403, f'Viewer should be denied: got {r.status_code}'
print('OK: viewer blocked from creating agent (403)')

# Test RBAC: admin can create agent
r_login = client.post('/auth/login', json={'username': 'admin', 'password': 'admin123'})
token = r_login.json()['access_token']
r = client.post('/agents', json={'name': 'Auth Test Agent', 'prompt': 'Test', 'tool_list': ['search']}, headers={'Authorization': f'Bearer {token}'})
assert r.status_code == 200, f'Admin should succeed: got {r.status_code}'
print('OK: admin can create agent (200)')

print('\nAll RBAC tests passed!')
