@echo off
echo ========================================
echo  Face Attendance System - Full Startup
echo ========================================
echo.

echo [1/3] Checking MySQL Database...
net start MySQL80 >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✓ MySQL is running
) else (
    echo    ✗ MySQL failed to start or already running
)
echo.

echo [2/3] Starting Backend Server...
echo    Opening backend in new window...
start "Face Attendance - Backend" cmd /k "cd /d C:\projects\face\backend && C:\projects\face\venv\Scripts\python.exe run.py"
timeout /t 5 /nobreak >nul
echo    ✓ Backend starting on http://localhost:5000
echo.

echo [3/3] Starting Frontend Server...
echo    Opening frontend in new window...
start "Face Attendance - Frontend" cmd /k "cd /d C:\projects\face\frontend && npm run dev"
timeout /t 3 /nobreak >nul
echo    ✓ Frontend starting on http://localhost:5173
echo.

echo ========================================
echo  All services started successfully!
echo ========================================
echo.
echo  Frontend:  http://localhost:5173
echo  Backend:   http://localhost:5000/api
echo  Database:  localhost:3306 (face_attendance_db)
echo.
echo  Press any key to exit...
pause >nul
