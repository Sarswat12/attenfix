# 🧪 Complete Testing Guide

## Quick Start (3 Simple Steps)

1. **Double-click** `START_ALL.bat` in the root folder
2. **Wait** for 2 windows to open (Backend + Frontend)
3. **Open browser** to http://localhost:5173

That's it! Everything should be running.

---

## Manual Testing Steps

### Step 1: Test MySQL Database

```powershell
# Check if MySQL is running
Get-Service MySQL80

# Should show: Status = Running

# Connect to database
mysql -u root -p
# Password: (press Enter - empty password)

# Once connected:
USE face_attendance_db;
SHOW TABLES;

# Expected: 10 tables
# users, face_encodings, attendance_records, user_settings, 
# departments, activity_log, auth_tokens, reports, 
# system_config, notifications

# Check views
SHOW FULL TABLES WHERE TABLE_TYPE = 'VIEW';

# Expected: 4 views
# v_today_attendance, v_monthly_attendance_rate,
# v_department_stats, v_face_enrollment_status

# Exit
EXIT;
```

**✅ Database Test Passed** if you see all 10 tables and 4 views.

---

### Step 2: Test Backend API

#### Option A: Using Browser
1. Open: http://localhost:5000/api/health
2. Expected response:
   ```json
   {
     "status": "healthy",
     "message": "Face Attendance API is running"
   }
   ```

#### Option B: Using PowerShell
```powershell
cd C:\projects\face

# Start backend
C:\projects\face\venv\Scripts\python.exe backend\run.py

# You should see:
#  * Running on http://127.0.0.1:5000
#  * Debug mode: on
```

#### Test Endpoints

```powershell
# In a NEW PowerShell window:

# Test 1: Health check
Invoke-WebRequest http://localhost:5000/api/health | Select-Object -ExpandProperty Content

# Test 2: Register user (should work)
$body = @{
    name = "Test User"
    email = "test@example.com"
    password = "Test@123"
    role = "employee"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:5000/api/auth/register `
    -Method POST `
    -Body $body `
    -ContentType "application/json"

# Test 3: Login (should return JWT token)
$loginBody = @{
    email = "test@example.com"
    password = "Test@123"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri http://localhost:5000/api/auth/login `
    -Method POST `
    -Body $loginBody `
    -ContentType "application/json"

$response.Content
# Should contain: "access_token": "eyJ..."
```

**✅ Backend Test Passed** if:
- Health endpoint returns 200 OK
- You can register a new user
- You can login and get a JWT token

---

### Step 3: Test Frontend

```powershell
cd C:\projects\face\frontend

# Install dependencies (if not already installed)
npm install

# Start dev server
npm run dev

# Expected output:
#   VITE v6.3.5  ready in 450 ms
#   ➜  Local:   http://localhost:5173/
```

#### Manual UI Tests

1. **Landing Page**
   - Open http://localhost:5173
   - Should see landing page with "Welcome to Face Attendance System"
   - Click "Get Started" → should redirect to login

2. **Login Page**
   - Try login with test credentials (from backend test)
   - Email: test@example.com
   - Password: Test@123
   - Should show loading indicator
   - Should redirect to dashboard (or show API error if not connected)

3. **Registration**
   - Click "Sign Up"
   - Fill in registration form
   - Submit
   - Should create new user (or show API error)

**✅ Frontend Test Passed** if:
- Page loads without console errors
- Navigation works
- Forms are interactive
- UI is responsive

---

### Step 4: Test Full Integration

#### Test Flow 1: User Registration & Login

1. Start backend: `.\START_BACKEND.bat`
2. Start frontend: `cd frontend && npm run dev`
3. Open browser: http://localhost:5173
4. Click "Sign Up"
5. Register new user:
   - Name: John Doe
   - Email: john@test.com
   - Password: John@123456
   - Department: Engineering
6. Click "Create Account"
7. **Expected**: Success message, redirect to login
8. Login with john@test.com / John@123456
9. **Expected**: Redirect to dashboard

#### Test Flow 2: Face Registration

1. Login as user (from Test Flow 1)
2. Navigate to "Register Face" page
3. Allow camera access when prompted
4. Position face in frame
5. Click "Capture" to take 5-7 images
6. Click "Submit for Verification"
7. **Expected**: Images uploaded to backend
8. **Note**: Face recognition won't process until dlib is installed

#### Test Flow 3: Attendance Marking

1. Login as user with registered face
2. Navigate to "Mark Attendance"
3. Allow camera access
4. Position face in frame
5. Click "Mark Attendance"
6. **Expected**: Attendance marked (date/time recorded)
7. Navigate to dashboard
8. **Expected**: Today's attendance visible

#### Test Flow 4: Admin Dashboard

1. Login as admin user
   - **Note**: You need to create admin in database first:
   ```sql
   mysql -u root face_attendance_db
   UPDATE users SET role = 'admin' WHERE email = 'john@test.com';
   EXIT;
   ```
2. Navigate to "Admin Panel"
3. View users list
4. View attendance records
5. View activity logs
6. **Expected**: All admin features accessible

**✅ Integration Test Passed** if:
- User can register and login
- Dashboard loads user data
- Forms submit to backend
- Errors display properly

---

## Common Issues & Solutions

### Issue 1: Backend won't start

**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```powershell
C:\projects\face\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

---

### Issue 2: Database connection error

**Error**: `sqlalchemy.exc.OperationalError: (2003, "Can't connect to MySQL")`

**Solution**:
```powershell
# Check MySQL service
Get-Service MySQL80

# If stopped, start it
net start MySQL80

# Verify database exists
mysql -u root -p
SHOW DATABASES;
# Should see "face_attendance_db"
```

---

### Issue 3: Frontend API calls fail

**Error**: `Network Error` or `CORS error` in browser console

**Solution**:
1. Check backend is running on port 5000
2. Check CORS settings in backend\.env:
   ```
   CORS_ORIGINS=http://localhost:3000,http://localhost:5173
   ```
3. Restart backend after changing .env

---

### Issue 4: Face recognition doesn't work

**Error**: `ModuleNotFoundError: No module named 'dlib'`

**Solution**:
```powershell
# Option 1: Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/downloads/

# Option 2: Use pre-built wheel
# Download from: https://github.com/z-mahmud22/Dlib_Windows_Python3.x
# Then:
C:\projects\face\venv\Scripts\python.exe -m pip install dlib-xxx.whl
```

**Temporary Workaround**: Face features will return errors but other APIs work fine.

---

### Issue 5: Port already in use

**Error**: `Address already in use` (port 5000 or 5173)

**Solution**:
```powershell
# Kill process on port 5000 (backend)
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process -Force

# Kill process on port 5173 (frontend)
Get-Process -Id (Get-NetTCPConnection -LocalPort 5173).OwningProcess | Stop-Process -Force
```

---

## Performance Testing

### Test 1: API Response Time

```powershell
# Measure health endpoint response
Measure-Command {
    Invoke-WebRequest http://localhost:5000/api/health
}

# Expected: < 100ms
```

### Test 2: Database Query Performance

```sql
-- In MySQL
USE face_attendance_db;

-- Test 1: Get all users
SELECT SQL_NO_CACHE * FROM users;
-- Expected: < 50ms for < 1000 users

-- Test 2: Today's attendance
SELECT SQL_NO_CACHE * FROM v_today_attendance;
-- Expected: < 100ms

-- Test 3: Monthly statistics
SELECT SQL_NO_CACHE * FROM v_monthly_attendance_rate 
WHERE month = MONTH(CURDATE()) AND year = YEAR(CURDATE());
-- Expected: < 200ms
```

### Test 3: Frontend Load Time

1. Open browser DevTools (F12)
2. Go to "Network" tab
3. Navigate to http://localhost:5173
4. Check "Load" time at bottom
5. **Expected**: < 2 seconds for initial load

---

## Automated Testing

### Backend Unit Tests

```powershell
cd C:\projects\face\backend

# Run all tests
C:\projects\face\venv\Scripts\python.exe -m pytest tests/ -v

# Run with coverage
C:\projects\face\venv\Scripts\python.exe -m pytest tests/ --cov=app --cov-report=html

# View coverage report
start htmlcov/index.html
```

### Frontend Unit Tests

```powershell
cd C:\projects\face\frontend

# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

---

## Verification Checklist

After completing all tests, verify:

- [ ] MySQL service running
- [ ] Database has 10 tables + 4 views
- [ ] Backend starts without errors
- [ ] Health endpoint returns 200 OK
- [ ] Can register new user via API
- [ ] Can login and get JWT token
- [ ] Frontend builds successfully
- [ ] Frontend dev server starts
- [ ] Can navigate between pages
- [ ] Can submit forms
- [ ] API calls reach backend (check Network tab)
- [ ] Errors display properly
- [ ] CORS works (no CORS errors in console)

**If all checkboxes are ticked: 🎉 Your system is fully functional!**

---

## Next Steps After Testing

1. **Fix any failing tests** before proceeding
2. **Install dlib** for face recognition (optional)
3. **Connect frontend to backend** (replace all `// TODO: Connect to API`)
4. **Add sample data** to database for realistic testing
5. **Configure production settings** when ready to deploy

---

## Support & Troubleshooting

### View Backend Logs
```powershell
cd C:\projects\face\backend
type logs\app.log
```

### View Database Logs
```powershell
# MySQL error log location (default)
type "C:\ProgramData\MySQL\MySQL Server 8.0\Data\*.err"
```

### View Frontend Console Logs
- Open browser DevTools (F12)
- Go to "Console" tab
- Look for red errors

### Common Log Patterns

**Success Pattern** (Backend):
```
INFO:werkzeug:127.0.0.1 - - [18/Nov/2025 14:00:00] "GET /api/health HTTP/1.1" 200 -
```

**Error Pattern** (Backend):
```
ERROR:app:Database connection failed: ...
```

**Success Pattern** (Frontend):
```
[vite] hmr update /src/App.jsx
```

**Error Pattern** (Frontend):
```
Failed to fetch: http://localhost:5000/api/auth/login
```

---

## Test Results Template

Use this to document your test results:

```
FACE ATTENDANCE SYSTEM - TEST RESULTS
Date: _______________
Tester: _______________

[ ] MySQL Database Running
    Tables: ___ / 10
    Views: ___ / 4

[ ] Backend API Running
    Health: [ ] Pass [ ] Fail
    Register: [ ] Pass [ ] Fail
    Login: [ ] Pass [ ] Fail

[ ] Frontend Running
    Load Time: ___ seconds
    Navigation: [ ] Pass [ ] Fail
    Forms: [ ] Pass [ ] Fail

[ ] Integration
    User Registration: [ ] Pass [ ] Fail
    User Login: [ ] Pass [ ] Fail
    Dashboard Load: [ ] Pass [ ] Fail
    Face Registration: [ ] Pass [ ] Fail
    Attendance Marking: [ ] Pass [ ] Fail

Issues Found:
1. ___________________________
2. ___________________________
3. ___________________________

Overall Status: [ ] All Tests Pass [ ] Some Failures [ ] Major Issues
```

---

**Happy Testing! 🚀**
