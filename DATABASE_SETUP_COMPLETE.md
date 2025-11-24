# Database Setup & MySQL Workbench Connection Guide
## Step-by-Step Instructions to Import Your Database

---

## ✅ System Status Check

- ✅ **MySQL Server 8.0** - Installed and Running
- ✅ **MySQL Workbench 8.0** - Installed
- ✅ **Windows PowerShell** - Ready
- ✅ **Database Files** - Ready in `c:\projects\face\database\`

---

## 🎯 QUICK START (5 Minutes)

### Option 1: Using MySQL Command Line (Fastest)

```powershell
# Navigate to database folder
cd c:\projects\face\database

# Run schema first
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root < schema.sql

# Then run sample data
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root face_attendance_db < sample_data.sql

# Verify
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -e "SELECT COUNT(*) as users FROM face_attendance_db.users;"
```

### Option 2: Using MySQL Workbench GUI (Detailed Below)

---

## 📖 DETAILED GUIDE: MySQL Workbench Method

### **Step 1: Open MySQL Workbench**

1. Click **Start Menu** → Search for **"MySQL Workbench"**
2. Click to open MySQL Workbench
3. Wait for it to fully load (may take 30 seconds)

### **Step 2: Create/Configure Connection**

1. In the **MySQL Connections** section, look for an existing connection or create one:
   - If you see **"Local instance MySQL80"** → Click it to connect
   - If not, click the **"+"** button to create a new connection

2. **Fill in connection details:**
   - **Connection Name**: `face_attendance_local`
   - **Connection Method**: `Standard (TCP/IP)`
   - **Hostname**: `127.0.0.1` or `localhost`
   - **Port**: `3306`
   - **Username**: `root`
   - **Password**: Leave blank (or enter if you set one)

3. Click **"Test Connection"**
   - Should show: **"Successfully made the MySQL connection"** ✅

4. Click **"OK"** to save

### **Step 3: Connect to MySQL**

1. Double-click your connection (e.g., **"Local instance MySQL80"**)
2. You should see tabs open at the bottom with connection details
3. Wait for connection to establish (status: **Connected**)

### **Step 4: Create the Database**

1. Go to **File → New Query Tab** (or press `Ctrl + T`)
2. Copy and paste this command:

```sql
CREATE DATABASE IF NOT EXISTS face_attendance_db 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE face_attendance_db;
```

3. Click the **"Execute"** button (⚡ lightning bolt icon)
4. Check output panel at bottom - should see: **"Query executed successfully"** ✅

### **Step 5: Import Database Schema**

1. Go to **File → Open SQL Script** (or press `Ctrl + O`)
2. Navigate to: `c:\projects\face\database\schema.sql`
3. Click **"Open"**
4. The entire schema file loads into editor window
5. Click **"Execute"** button (⚡)
6. Watch the output panel - you should see:
   - "Query executed successfully" messages
   - Table creation confirmations
   - View creation confirmations
7. **Wait for all queries to complete** - it may take 10-20 seconds
8. Status should show: **"All executed"** ✅

### **Step 6: Import Sample Data**

1. Go to **File → Open SQL Script** (Ctrl + O)
2. Navigate to: `c:\projects\face\database\sample_data.sql`
3. Click **"Open"**
4. Click **"Execute"** button (⚡)
5. **Wait for completion** - should see:
   - "Query executed successfully" messages for all INSERT statements
   - Status: **"All executed"** ✅

### **Step 7: Verify Everything Works**

1. In left panel, expand **"Schemas"** section
2. Right-click **"face_attendance_db"** → Select **"Refresh"**
3. Expand **face_attendance_db** folder
4. Verify you see:

**Tables (should be 10):**
- ✅ users
- ✅ face_encodings
- ✅ attendance_records
- ✅ user_settings
- ✅ activity_log
- ✅ auth_tokens
- ✅ departments
- ✅ reports
- ✅ system_config
- ✅ notifications

**Views (should be 4):**
- ✅ v_today_attendance
- ✅ v_monthly_attendance_rate
- ✅ v_department_stats
- ✅ v_face_enrollment_status

### **Step 8: Test with Sample Queries**

Run these verification queries to confirm everything is working:

```sql
-- Test 1: Count users (should return 20)
SELECT COUNT(*) as total_users FROM users;

-- Test 2: List all users
SELECT id, name, email, role FROM users LIMIT 10;

-- Test 3: Check face encodings (should return 10)
SELECT COUNT(*) as face_count FROM face_encodings;

-- Test 4: Check attendance records (should return 18)
SELECT COUNT(*) as attendance_count FROM attendance_records;

-- Test 5: View today's attendance
SELECT * FROM v_today_attendance LIMIT 5;

-- Test 6: Check departments
SELECT id, name FROM departments;
```

To run queries:
1. Click **"File → New Query Tab"** (Ctrl + T)
2. Copy the queries above
3. Highlight the query you want to run
4. Click **"Execute"** (⚡) or press `Ctrl + Enter`
5. See results in the panel below

---

## 🐛 Troubleshooting

### **Problem: "Connection refused" or "Cannot connect to MySQL"**

**Solution:**
1. Check if MySQL service is running:
   - Click **Start → Services** (services.msc)
   - Look for **"MySQL80"**
   - If stopped, right-click → **"Start"**

2. Or use PowerShell:
   ```powershell
   Get-Service MySQL80 | Start-Service
   ```

### **Problem: "Access denied for user 'root'@'localhost'"**

**Solution:**
1. You may have a password set. Try:
   ```powershell
   cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"
   .\mysql.exe -u root -p
   # When prompted, enter your MySQL password
   ```

2. If you forgot the password, see MySQL password reset guide

### **Problem: "The table 'users' already exists"**

**Solution:**
1. Drop and recreate the database:
   ```sql
   DROP DATABASE face_attendance_db;
   CREATE DATABASE face_attendance_db;
   ```

2. Then run schema.sql and sample_data.sql again

### **Problem: "File not found" when opening SQL scripts**

**Solution:**
1. Verify files exist:
   - `c:\projects\face\database\schema.sql`
   - `c:\projects\face\database\sample_data.sql`

2. Try copy-paste instead of file open:
   - Open schema.sql in notepad
   - Copy all content
   - Paste in MySQL Workbench
   - Execute

### **Problem: Queries execute but show "Query OK, 0 rows affected"**

**Solution:**
1. Make sure you're in the correct database:
   ```sql
   USE face_attendance_db;
   ```

2. Then run the query again

---

## ✅ Verification Checklist

After importing, verify you have:

- [ ] Database `face_attendance_db` created
- [ ] 10 tables visible in MySQL Workbench
- [ ] 4 views visible
- [ ] Can run: `SELECT COUNT(*) FROM users;` → Returns **20**
- [ ] Can run: `SELECT COUNT(*) FROM face_encodings;` → Returns **10**
- [ ] Can run: `SELECT COUNT(*) FROM attendance_records;` → Returns **18**
- [ ] Can run: `SELECT * FROM v_today_attendance;` → Shows data
- [ ] Can view all table structures (right-click table → "Select Rows")

---

## 📊 Sample Query Results Expected

### Query 1: Get All Users
```sql
SELECT id, name, email, role FROM users LIMIT 5;
```

**Expected Result:**
```
id     | name              | email                    | role
-------|-------------------|--------------------------|----------
ADM001 | Admin User        | admin@company.com        | admin
ADM002 | Admin Manager     | admin.manager@company.com| admin
EMP001 | John Doe          | john.doe@company.com     | employee
EMP002 | Jane Smith        | jane.smith@company.com   | employee
EMP003 | Mike Johnson      | mike.johnson@company.com | employee
```

### Query 2: Get Today's Attendance
```sql
SELECT * FROM v_today_attendance;
```

**Expected Result:**
Shows attendance status for all users (Present/Absent/Late)

### Query 3: Get Departments
```sql
SELECT id, name, location FROM departments;
```

**Expected Result:**
```
id      | name          | location
--------|---------------|------------------
DEPT001 | Engineering   | Building A, Floor 1
DEPT002 | HR            | Building B, Floor 2
DEPT003 | Sales         | Building A, Floor 2
...
```

---

## 🔧 MySQL Workbench Key Features

### **View Table Data**
1. Right-click table name in left panel
2. Select **"Select Rows - Limit 1000"**
3. View data in results panel

### **View Table Structure**
1. Right-click table name
2. Select **"Inspect Table"** or **"Show Create Statement"**
3. See all columns, types, and constraints

### **Run Multiple Queries**
1. Separate queries with semicolon (;)
2. Click **"Execute All"** (or Ctrl+Shift+Enter)
3. Results show in separate tabs

### **Export Data**
1. Right-click table
2. Select **"Send to Excel"** or **"Export"**
3. Choose format (CSV, Excel, etc.)

### **Create New Queries**
- **File → New Query Tab** (Ctrl+T)
- **Or**: Click **"+"** tab at bottom

---

## 📝 Connection String for Backend

Once connected, use this connection string in your backend:

**Python/Flask:**
```python
DATABASE_URL = "mysql+mysqlconnector://root@localhost:3306/face_attendance_db"
```

**Node.js:**
```javascript
const connection = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  database: 'face_attendance_db'
});
```

**Java:**
```java
String url = "jdbc:mysql://localhost:3306/face_attendance_db";
String user = "root";
Connection conn = DriverManager.getConnection(url, user, "");
```

**C#/.NET:**
```csharp
string connectionString = "Server=localhost;Database=face_attendance_db;Uid=root;Pwd=;";
```

---

## 🎉 Database is Connected!

Once you complete all verification steps, your database is **100% ready** for the backend team to:

1. ✅ Start development
2. ✅ Create ORM models
3. ✅ Build API endpoints
4. ✅ Write tests
5. ✅ Deploy to production

---

## 📞 Next Steps

### For Backend Team:
1. Copy the connection string above
2. Add to your `.env` file
3. Create SQLAlchemy models matching table structure
4. Start building API endpoints

### For All Teams:
1. Reference: `FIXED_SCHEMA_SPECIFICATION.md` for table details
2. Reference: `IMPORT_GUIDE.md` for database structure
3. Test: All provided sample queries

---

**✅ Your database is now connected and ready for development!**

Last Updated: November 18, 2025
Status: Ready for Backend Development
