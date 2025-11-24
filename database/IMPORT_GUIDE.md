# MySQL Workbench Import Guide
## Face Recognition Attendance System Database Setup

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Step-by-Step Import Instructions](#step-by-step-import-instructions)
3. [Verification Steps](#verification-steps)
4. [Troubleshooting](#troubleshooting)
5. [Connection String Examples](#connection-string-examples)

---

## Prerequisites

Before importing the database schema, ensure you have:

✅ **MySQL Server 8.0+** installed and running
- Default location: `C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe`
- Service should be running (check Windows Services)

✅ **MySQL Workbench 8.0+** installed
- Download from: https://www.mysql.com/products/workbench/
- Latest stable version recommended

✅ **Database Files** downloaded
- `schema.sql` - Database schema and structure (400+ lines)
- `sample_data.sql` - Sample data for testing (300+ lines)

✅ **MySQL Root Access** or user with CREATE DATABASE privilege
- Default root password or your custom password

---

## Step-by-Step Import Instructions

### **METHOD 1: Using MySQL Workbench GUI (Recommended for beginners)**

#### **Step 1: Open MySQL Workbench**
1. Launch MySQL Workbench from your Start Menu
2. Wait for it to fully load (this may take 30 seconds)

#### **Step 2: Create a Connection**
1. In the home screen, click **"MySQL Connections"** section
2. Click the **"+"** button to create a new connection
3. Fill in the following details:
   - **Connection Name**: `face_attendance_dev` (or any name you prefer)
   - **Connection Method**: `Standard (TCP/IP)`
   - **Hostname**: `127.0.0.1` or `localhost`
   - **Port**: `3306` (default)
   - **Username**: `root` (or your MySQL user)
   - Click **"Store in Vault..."** to save your password
   - **Password**: Enter your MySQL root password

4. Click **"Test Connection"** to verify
5. If successful, click **"OK"** to save the connection

#### **Step 3: Connect to MySQL**
1. Double-click your newly created connection to open it
2. You should see the connection tab open at the bottom of the workbench
3. Wait for connection to establish (you'll see "Connected" status)

#### **Step 4: Create the Database**
1. Go to **File → New Query Tab** (or press `Ctrl + T`)
2. You'll see a blank SQL editor window
3. **Copy and paste the following SQL command:**
   ```sql
   CREATE DATABASE IF NOT EXISTS face_attendance_db 
   CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   USE face_attendance_db;
   ```
4. Click the **"Execute"** button (lightning bolt icon ⚡)
5. You should see the message: `Query executed successfully`

#### **Step 5: Import Schema File**
1. Go to **File → Open SQL Script** (or press `Ctrl + O`)
2. Navigate to your `schema.sql` file location:
   - Path: `c:\projects\face\database\schema.sql`
3. Click **"Open"**
4. The entire schema file will load into the editor
5. Click **"Execute"** button (⚡) to run all SQL commands
6. Watch the output panel at the bottom - you should see:
   - `Query executed successfully` messages
   - Table creation confirmations
   - View creation confirmations
7. When complete, you should see **"All executed"** status

#### **Step 6: Import Sample Data File**
1. Go to **File → Open SQL Script** (Ctrl + O)
2. Navigate to `sample_data.sql`:
   - Path: `c:\projects\face\database\sample_data.sql`
3. Click **"Open"**
4. Click **"Execute"** button (⚡)
5. Wait for all INSERT statements to complete
6. You should see success messages for all data insertion

#### **Step 7: Verify Import Success**
1. In the **left panel** under your connection, expand **"Schemas"** section
2. Right-click **"face_attendance_db"** and select **"Refresh"**
3. You should see:
   - **Tables** folder with 10 tables:
     - `users`
     - `face_encodings`
     - `attendance_records`
     - `user_settings`
     - `activity_log`
     - `auth_tokens`
     - `departments`
     - `reports`
     - `system_config`
     - `notifications`
   - **Views** folder with 4 views:
     - `v_today_attendance`
     - `v_monthly_attendance_rate`
     - `v_department_stats`
     - `v_face_enrollment_status`

---

### **METHOD 2: Using Command Line (For experienced users)**

#### **Windows PowerShell / Command Prompt**

```powershell
# Connect to MySQL and run schema
mysql -u root -p < C:\projects\face\database\schema.sql

# When prompted, enter your MySQL root password

# Import sample data
mysql -u root -p face_attendance_db < C:\projects\face\database\sample_data.sql
```

#### **Using MySQL Command Line Client**

1. Open **MySQL Command Line Client** from Start Menu
2. Enter your password when prompted
3. Run the following commands:

```sql
-- Create database
CREATE DATABASE IF NOT EXISTS face_attendance_db 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE face_attendance_db;

-- Execute schema file (Windows)
SOURCE C:\projects\face\database\schema.sql;

-- Execute sample data file
SOURCE C:\projects\face\database\sample_data.sql;

-- Verify import
SHOW TABLES;
SELECT * FROM users LIMIT 5;
```

---

## Verification Steps

### **Verify Database Created**
```sql
SHOW DATABASES;
-- You should see: face_attendance_db in the list
```

### **Verify All Tables Created**
```sql
USE face_attendance_db;
SHOW TABLES;
-- Should show 10 tables
```

### **Verify Table Structure**
```sql
DESCRIBE users;
DESCRIBE face_encodings;
DESCRIBE attendance_records;
-- Check if all columns are present
```

### **Verify Sample Data Loaded**
```sql
SELECT COUNT(*) FROM users;
-- Should show: 20 (1 admin + 13 employees + 5 students)

SELECT COUNT(*) FROM face_encodings;
-- Should show: 10

SELECT COUNT(*) FROM attendance_records;
-- Should show: 18

SELECT COUNT(*) FROM user_settings;
-- Should show: 10
```

### **Verify Views Created**
```sql
SHOW FULL TABLES IN face_attendance_db WHERE TABLE_TYPE LIKE 'VIEW';
-- Should show 4 views

SELECT * FROM v_today_attendance;
SELECT * FROM v_monthly_attendance_rate;
SELECT * FROM v_department_stats;
SELECT * FROM v_face_enrollment_status;
```

### **Quick Health Check Query**
```sql
-- Run this to verify everything is working
SELECT 
    'users' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'face_encodings', COUNT(*) FROM face_encodings
UNION ALL
SELECT 'attendance_records', COUNT(*) FROM attendance_records
UNION ALL
SELECT 'user_settings', COUNT(*) FROM user_settings
UNION ALL
SELECT 'departments', COUNT(*) FROM departments;
```

---

## Troubleshooting

### **Problem: "Connection refused" or "Cannot connect to MySQL"**

**Solution:**
1. Verify MySQL Server is running:
   - Windows: Open **Services** → Search for "MySQL80"
   - If not running, click **Start** to start the service
2. Check the correct port (default: 3306)
3. Verify hostname is `localhost` or `127.0.0.1`

### **Problem: "Access denied for user 'root'@'localhost'"**

**Solution:**
1. Verify your MySQL password is correct
2. Reset MySQL password:
   - Stop MySQL service
   - Use MySQL recovery procedure
   - Restart service

### **Problem: "The table 'users' already exists"**

**Solution:**
1. Drop the existing database and recreate:
   ```sql
   DROP DATABASE face_attendance_db;
   CREATE DATABASE face_attendance_db;
   ```
2. Then run the schema and sample data files again

### **Problem: "File not found" when opening SQL scripts**

**Solution:**
1. Verify file paths are correct
2. Ensure files are in: `c:\projects\face\database\`
3. Use forward slashes in Windows paths: `C:/projects/face/database/schema.sql`
4. Or use raw string with backslashes: `C:\\projects\\face\\database\\schema.sql`

### **Problem: "ERROR 1215: Cannot add foreign key constraint"**

**Solution:**
1. Ensure all parent tables are created first (schema.sql creates them in correct order)
2. Verify data types match between foreign key and parent key
3. Try importing schema file again, ensuring it completes without errors

### **Problem: Sample data insertion fails**

**Solution:**
1. Verify schema was successfully imported first
2. Check that department IDs in sample_data match those in schema
3. Run schema again if needed, then sample_data

---

## Connection String Examples

### **For Backend Development**

**Python (Flask with SQLAlchemy)**
```python
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/face_attendance_db"
# or
DATABASE_URL = "mysql+mysqlconnector://root:password@localhost:3306/face_attendance_db"
```

**Node.js (Express with MySQL2)**
```javascript
const connection = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: 'your_password',
  database: 'face_attendance_db',
  port: 3306
});
```

**Java (JDBC)**
```java
String url = "jdbc:mysql://localhost:3306/face_attendance_db?useSSL=false&serverTimezone=UTC";
String user = "root";
String password = "your_password";
Connection conn = DriverManager.getConnection(url, user, password);
```

**C# (.NET)**
```csharp
string connectionString = "Server=localhost;Database=face_attendance_db;Uid=root;Pwd=password;";
MySqlConnection connection = new MySqlConnection(connectionString);
```

**PHP**
```php
$conn = new mysqli("localhost", "root", "password", "face_attendance_db");
// or
$dsn = "mysql:host=localhost;dbname=face_attendance_db";
$pdo = new PDO($dsn, "root", "password");
```

---

## Common Queries for Backend Development

### **Get User with Face Encodings**
```sql
SELECT u.*, COUNT(fe.id) as face_count
FROM users u
LEFT JOIN face_encodings fe ON u.id = fe.user_id
WHERE u.status = 'Active'
GROUP BY u.id;
```

### **Get Today's Attendance**
```sql
SELECT * FROM v_today_attendance ORDER BY user_id;
```

### **Get Monthly Attendance Rate**
```sql
SELECT * FROM v_monthly_attendance_rate
WHERE year_month = DATE_FORMAT(NOW(), '%Y-%m');
```

### **Get Department Statistics**
```sql
SELECT * FROM v_department_stats;
```

### **Get User's Recent Attendance (Last 7 days)**
```sql
SELECT ar.*
FROM attendance_records ar
WHERE ar.user_id = 'EMP001'
AND ar.date_only >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
ORDER BY ar.timestamp DESC;
```

---

## Next Steps

1. ✅ **Verify database is working** using the verification steps above
2. 📝 **Review the Fixed Schema Specification** document for API design
3. 🔌 **Start backend development** using the connection strings provided
4. 🧪 **Write test cases** for each database operation
5. 📊 **Set up data backup** strategy

---

## Support & Documentation

- **MySQL Documentation**: https://dev.mysql.com/doc/
- **MySQL Workbench Guide**: https://dev.mysql.com/doc/workbench/en/
- **Database Schema Details**: See `FIXED_SCHEMA_SPECIFICATION.md`

---

## File Location Reference

```
c:\projects\face\
├── database\
│   ├── schema.sql                    (Main database structure)
│   ├── sample_data.sql              (Test data for development)
│   └── IMPORT_GUIDE.md              (This file)
├── documents\
│   └── FIXED_SCHEMA_SPECIFICATION.md (API & Database mapping)
└── frontend\                         (React application)
```

---

**Last Updated**: 2024-11-18  
**Database Version**: 1.0  
**Status**: Production Ready ✅
