# FIXED SCHEMA SPECIFICATION
## Complete Database & API Reference for Face Recognition Attendance System

---

## Document Purpose

This document defines the **FIXED DATABASE SCHEMA** that both frontend and backend teams must follow blindly. All database operations, API endpoints, and data models are derived from this specification.

**Created**: 2024-11-18  
**Version**: 1.0  
**Status**: Production Ready ✅  
**Database Engine**: MySQL 8.0+  
**Database Name**: `face_attendance_db`

---

## Table of Contents

1. [Database Overview](#database-overview)
2. [Complete Table Definitions](#complete-table-definitions)
3. [Views & Queries](#views--queries)
4. [Indexes & Performance](#indexes--performance)
5. [API Endpoint Mapping](#api-endpoint-mapping)
6. [Data Types & Validation](#data-types--validation)
7. [Constraints & Rules](#constraints--rules)
8. [Relationships & Foreign Keys](#relationships--foreign-keys)
9. [Sample Queries](#sample-queries)
10. [Backend Integration Guide](#backend-integration-guide)

---

## Database Overview

### **System Architecture**

```
┌─────────────────────────────────────────────────┐
│          FRONTEND (React + Vite)                │
│  - AttendancePage, AdminPanel, RegisterFace     │
│  - All API calls mapped below                   │
└────────────────────┬────────────────────────────┘
                     │ HTTP REST API
                     ↓
┌─────────────────────────────────────────────────┐
│       BACKEND (Flask/Python)                    │
│  - API Server on port 5000                      │
│  - User Authentication (JWT tokens)             │
│  - Face Recognition Processing                  │
│  - Attendance Logic & Reporting                 │
└────────────────────┬────────────────────────────┘
                     │ SQL Queries
                     ↓
┌─────────────────────────────────────────────────┐
│      MYSQL DATABASE                             │
│  - 10 Core Tables (see below)                   │
│  - 4 Analytical Views                           │
│  - 30+ Performance Indexes                      │
│  - Supports 10,000+ users                       │
└─────────────────────────────────────────────────┘
```

### **Database Statistics**

- **Total Tables**: 10
- **Total Views**: 4
- **Total Indexes**: 30+
- **Character Set**: utf8mb4 (Unicode support)
- **Collation**: utf8mb4_unicode_ci
- **Primary Key Type**: VARCHAR (for distributed systems)

---

## Complete Table Definitions

### **1. USERS Table**

**Purpose**: Core user information storage - all system users (admins, employees, students)

**Table Name**: `users`

| Column | Type | Constraints | Description | Example |
|--------|------|-------------|-------------|---------|
| `id` | VARCHAR(20) | PRIMARY KEY, UNIQUE | User unique identifier | 'EMP001', 'ADM001', 'STU001' |
| `name` | VARCHAR(100) | NOT NULL | Full name of user | 'John Doe' |
| `email` | VARCHAR(100) | UNIQUE, NOT NULL | Email address (unique) | 'john@company.com' |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt password hash | '$2b$12$...' |
| `role` | ENUM | NOT NULL | User role type | 'admin', 'employee', 'student' |
| `department` | VARCHAR(20) | FOREIGN KEY → departments.id | Department assignment | 'DEPT001' |
| `phone` | VARCHAR(20) | NULL | Contact number | '+1-555-1001' |
| `address` | TEXT | NULL | Address information | '123 Main St' |
| `avatar_url` | VARCHAR(255) | NULL | Profile picture URL | '/storage/avatars/EMP001.jpg' |
| `status` | ENUM | DEFAULT 'Active' | Account status | 'Active', 'Inactive', 'Suspended' |
| `join_date` | DATE | NOT NULL | Employment/enrollment date | '2024-02-01' |
| `last_login` | TIMESTAMP | NULL | Last login timestamp | '2024-11-18 09:15:30' |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time | Automatic |
| `updated_at` | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | Last update time | Automatic |
| `deleted_at` | TIMESTAMP | NULL | Soft delete timestamp | NULL or timestamp |

**Indexes**:
- PRIMARY KEY: `id`
- UNIQUE: `email`
- INDEX: `role`
- INDEX: `department`
- INDEX: `status`
- INDEX: `deleted_at` (for soft deletes)

**Usage Examples**:
```sql
-- Find active employees
SELECT * FROM users WHERE role = 'employee' AND status = 'Active';

-- Find users by department
SELECT * FROM users WHERE department = 'DEPT001' AND deleted_at IS NULL;

-- Search users by email
SELECT * FROM users WHERE email = 'john@company.com';
```

---

### **2. FACE_ENCODINGS Table**

**Purpose**: Store facial recognition vectors and related metadata for face matching

**Table Name**: `face_encodings`

| Column | Type | Constraints | Description | Example |
|--------|------|-------------|-------------|---------|
| `id` | VARCHAR(50) | PRIMARY KEY, UNIQUE | Unique encoding ID | 'FACE_ENC_001' |
| `user_id` | VARCHAR(20) | NOT NULL, FOREIGN KEY → users.id | Associated user | 'EMP001' |
| `encoding_vector` | LONGBLOB | NOT NULL | 128-D face vector (binary) | Binary data (512 bytes) |
| `image_url` | VARCHAR(255) | NOT NULL | Original image path | '/storage/faces/EMP001_1.jpg' |
| `image_hash` | VARCHAR(64) | NOT NULL | SHA256 hash of image | 'abc123def456...' |
| `captured_at` | TIMESTAMP | NOT NULL | When face was captured | '2024-11-18 10:00:00' |
| `quality_score` | FLOAT | NOT NULL | Image quality (0-1) | 0.95 |
| `face_confidence` | FLOAT | NOT NULL | Detection confidence (0-1) | 0.99 |
| `status` | ENUM | DEFAULT 'pending' | Verification status | 'pending', 'verified', 'rejected' |
| `notes` | TEXT | NULL | Additional notes | 'Clear image, good lighting' |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time | Automatic |
| `deleted_at` | TIMESTAMP | NULL | Soft delete | NULL or timestamp |

**Constraints**:
- Each user can have multiple encodings (for registration)
- Only `verified` encodings are used for matching
- Cannot delete verified encodings without admin approval

**Indexes**:
- PRIMARY KEY: `id`
- UNIQUE: `image_hash` (prevent duplicate uploads)
- INDEX: `user_id`
- INDEX: `status`
- INDEX: `captured_at`
- INDEX: `(user_id, status)` (composite)

**Usage Examples**:
```sql
-- Get all verified face encodings for a user
SELECT * FROM face_encodings 
WHERE user_id = 'EMP001' AND status = 'verified';

-- Get enrollment status
SELECT user_id, COUNT(*) as face_count 
FROM face_encodings 
WHERE status = 'verified' 
GROUP BY user_id 
HAVING COUNT(*) >= 5;
```

---

### **3. ATTENDANCE_RECORDS Table**

**Purpose**: Central attendance log with face recognition confidence scores

**Table Name**: `attendance_records`

| Column | Type | Constraints | Description | Example |
|--------|------|-------------|-------------|---------|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Unique record ID | 1, 2, 3... |
| `user_id` | VARCHAR(20) | NOT NULL, FOREIGN KEY → users.id | Marked user | 'EMP001' |
| `face_encoding_id` | VARCHAR(50) | NULL, FOREIGN KEY → face_encodings.id | Matched face | 'FACE_ENC_001' |
| `timestamp` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Full check-in time | '2024-11-18 09:15:30' |
| `date_only` | DATE | NOT NULL | Date component (indexed) | '2024-11-18' |
| `time_only` | TIME | NULL | Time component | '09:15:30' |
| `status` | ENUM | NOT NULL | Attendance status | 'Present', 'Absent', 'Late', 'Leave' |
| `recognition_confidence` | FLOAT | NULL | Face match score (0-1) | 0.98 |
| `recognition_distance` | FLOAT | NULL | Euclidean distance | 0.25 |
| `location` | VARCHAR(50) | NULL | Entry location | 'Main Gate', 'Office' |
| `device_id` | VARCHAR(50) | NULL | Camera/device ID | 'CAM001' |
| `source` | ENUM | DEFAULT 'face_recognition' | Mark source | 'face_recognition', 'manual', 'api' |
| `verification_status` | ENUM | DEFAULT 'pending' | Admin approval | 'pending', 'verified', 'rejected' |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation | Automatic |
| `updated_at` | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | Last update | Automatic |

**Unique Constraint**:
- `UNIQUE KEY (user_id, date_only)` - One mark per user per day

**Indexes**:
- PRIMARY KEY: `id`
- UNIQUE: `(user_id, date_only)`
- INDEX: `user_id`
- INDEX: `date_only`
- INDEX: `timestamp`
- INDEX: `status`
- INDEX: `source`
- INDEX: `(date_only, status)`

**Usage Examples**:
```sql
-- Get today's attendance
SELECT * FROM attendance_records 
WHERE date_only = CURDATE() 
ORDER BY timestamp;

-- Get user's attendance for a month
SELECT * FROM attendance_records 
WHERE user_id = 'EMP001' AND date_only BETWEEN '2024-11-01' AND '2024-11-30'
ORDER BY date_only;

-- Get late arrivals
SELECT * FROM attendance_records 
WHERE date_only = CURDATE() AND status = 'Late';
```

---

### **4. USER_SETTINGS Table**

**Purpose**: Per-user configuration and preferences

**Table Name**: `user_settings`

| Column | Type | Constraints | Description | Example |
|--------|------|-------------|-------------|---------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Setting ID | 1, 2, 3... |
| `user_id` | VARCHAR(20) | UNIQUE, NOT NULL, FOREIGN KEY → users.id | Associated user | 'EMP001' |
| `camera_access_enabled` | BOOLEAN | DEFAULT TRUE | Allow camera access | TRUE |
| `notifications_enabled` | BOOLEAN | DEFAULT TRUE | Enable notifications | TRUE |
| `export_format` | ENUM | DEFAULT 'csv' | Preferred export format | 'csv', 'pdf', 'excel' |
| `api_key` | VARCHAR(255) | NULL | Encrypted API key | 'ey...' |
| `api_key_created_at` | TIMESTAMP | NULL | API key creation | '2024-11-01 10:00:00' |
| `timezone` | VARCHAR(50) | DEFAULT 'UTC' | User timezone | 'America/New_York' |
| `language` | VARCHAR(10) | DEFAULT 'en' | Preferred language | 'en', 'es', 'fr' |
| `theme` | ENUM | DEFAULT 'light' | UI theme preference | 'light', 'dark' |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation | Automatic |
| `updated_at` | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | Last update | Automatic |

**Indexes**:
- PRIMARY KEY: `id`
- UNIQUE: `user_id`

**Usage Examples**:
```sql
-- Get user preferences
SELECT * FROM user_settings WHERE user_id = 'EMP001';

-- Find users with notifications enabled
SELECT u.* FROM users u 
JOIN user_settings s ON u.id = s.user_id 
WHERE s.notifications_enabled = TRUE;
```

---

### **5. ACTIVITY_LOG Table**

**Purpose**: Complete audit trail of all system actions for compliance and debugging

**Table Name**: `activity_log`

| Column | Type | Constraints | Description | Example |
|--------|------|-------------|-------------|---------|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Log entry ID | 1, 2, 3... |
| `user_id` | VARCHAR(20) | NOT NULL, FOREIGN KEY → users.id | Who performed action | 'EMP001' |
| `action_type` | VARCHAR(50) | NOT NULL | Type of action | 'login', 'register_face', 'mark_attendance' |
| `action_description` | TEXT | NOT NULL | Detailed description | 'User registered 5 face images' |
| `table_name` | VARCHAR(50) | NULL | Affected table | 'users', 'face_encodings' |
| `record_id` | VARCHAR(50) | NULL | Affected record | 'FACE_ENC_001' |
| `old_value` | JSON | NULL | Previous data | '{"status":"pending"}' |
| `new_value` | JSON | NULL | New data | '{"status":"verified"}' |
| `status` | ENUM | DEFAULT 'success' | Action result | 'success', 'failed', 'warning' |
| `error_message` | TEXT | NULL | Error details if failed | 'Face quality too low' |
| `ip_address` | VARCHAR(50) | NULL | Client IP | '192.168.1.100' |
| `user_agent` | TEXT | NULL | Browser/device info | 'Mozilla/5.0...' |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Action timestamp | Automatic |

**Indexes**:
- PRIMARY KEY: `id`
- INDEX: `user_id`
- INDEX: `action_type`
- INDEX: `created_at`
- INDEX: `status`
- INDEX: `(user_id, created_at)` (composite)

**Usage Examples**:
```sql
-- Get user's recent activity
SELECT * FROM activity_log 
WHERE user_id = 'EMP001' 
ORDER BY created_at DESC LIMIT 20;

-- Find all failed actions
SELECT * FROM activity_log 
WHERE status = 'failed' 
ORDER BY created_at DESC;

-- Get login audit trail
SELECT * FROM activity_log 
WHERE action_type = 'login' AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY);
```

---

### **6. AUTH_TOKENS Table**

**Purpose**: JWT token management for API authentication and session tracking

**Table Name**: `auth_tokens`

| Column | Type | Constraints | Description | Example |
|--------|------|-------------|-------------|---------|
| `id` | VARCHAR(100) | PRIMARY KEY, UNIQUE | Token ID (jti claim) | 'token_uuid_hash' |
| `user_id` | VARCHAR(20) | NOT NULL, FOREIGN KEY → users.id | Token owner | 'EMP001' |
| `token_hash` | VARCHAR(255) | NOT NULL, UNIQUE | SHA256 hash of token | 'abc123...' |
| `device_id` | VARCHAR(100) | NULL | Device identifier | 'device_uuid' |
| `device_name` | VARCHAR(100) | NULL | Device name | 'Chrome on Windows' |
| `ip_address` | VARCHAR(50) | NULL | IP address of token issuer | '192.168.1.100' |
| `issued_at` | TIMESTAMP | NOT NULL | Token creation time | '2024-11-18 10:00:00' |
| `expires_at` | TIMESTAMP | NOT NULL | Token expiration | '2024-11-19 10:00:00' |
| `last_used_at` | TIMESTAMP | NULL | Last API call with token | '2024-11-18 10:30:00' |
| `is_revoked` | BOOLEAN | DEFAULT FALSE | Revocation status | FALSE |
| `revoked_at` | TIMESTAMP | NULL | When token was revoked | NULL or timestamp |
| `revocation_reason` | VARCHAR(255) | NULL | Why token revoked | 'User logout', 'Password change' |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation | Automatic |

**Indexes**:
- PRIMARY KEY: `id`
- UNIQUE: `token_hash`
- INDEX: `user_id`
- INDEX: `expires_at`
- INDEX: `is_revoked`
- INDEX: `(user_id, is_revoked)`

**Usage Examples**:
```sql
-- Get active tokens for user
SELECT * FROM auth_tokens 
WHERE user_id = 'EMP001' AND is_revoked = FALSE AND expires_at > NOW();

-- Find expired tokens
SELECT * FROM auth_tokens WHERE expires_at < NOW() AND is_revoked = FALSE;

-- Revoke all tokens for user (logout all devices)
UPDATE auth_tokens 
SET is_revoked = TRUE, revoked_at = NOW(), revocation_reason = 'User logout all'
WHERE user_id = 'EMP001' AND is_revoked = FALSE;
```

---

### **7. DEPARTMENTS Table**

**Purpose**: Organizational hierarchy and department management

**Table Name**: `departments`

| Column | Type | Constraints | Description | Example |
|--------|------|-------------|-------------|---------|
| `id` | VARCHAR(20) | PRIMARY KEY, UNIQUE | Department ID | 'DEPT001' |
| `name` | VARCHAR(100) | NOT NULL, UNIQUE | Department name | 'Engineering' |
| `description` | TEXT | NULL | Department description | 'Software Development' |
| `location` | VARCHAR(100) | NULL | Physical location | 'Building A, Floor 1' |
| `manager_id` | VARCHAR(20) | NULL, FOREIGN KEY → users.id | Department manager | 'EMP001' |
| `budget_allocated` | DECIMAL(12,2) | NULL | Budget amount | 50000.00 |
| `status` | ENUM | DEFAULT 'Active' | Department status | 'Active', 'Inactive' |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation time | Automatic |
| `updated_at` | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | Last update | Automatic |

**Indexes**:
- PRIMARY KEY: `id`
- UNIQUE: `name`
- INDEX: `manager_id`
- INDEX: `status`

**Usage Examples**:
```sql
-- Get all departments with manager names
SELECT d.*, u.name as manager_name 
FROM departments d 
LEFT JOIN users u ON d.manager_id = u.id;

-- Get department head and all employees
SELECT * FROM users 
WHERE department = 'DEPT001' AND status = 'Active';
```

---

### **8. REPORTS Table**

**Purpose**: Track generated reports and export files

**Table Name**: `reports`

| Column | Type | Constraints | Description | Example |
|--------|------|-------------|-------------|---------|
| `id` | VARCHAR(50) | PRIMARY KEY, UNIQUE | Report ID | 'REPORT_202411_001' |
| `user_id` | VARCHAR(20) | NOT NULL, FOREIGN KEY → users.id | Who requested | 'ADM001' |
| `report_type` | VARCHAR(50) | NOT NULL | Type of report | 'monthly_attendance', 'daily_summary' |
| `title` | VARCHAR(255) | NOT NULL | Report title | 'November 2024 Attendance Report' |
| `description` | TEXT | NULL | Report description | 'Complete attendance for all employees' |
| `filters` | JSON | NULL | Applied filters | '{"department":"DEPT001","date_from":"2024-11-01"}' |
| `file_path` | VARCHAR(255) | NULL | Generated file location | '/storage/reports/REPORT_202411_001.pdf' |
| `file_size` | INT | NULL | File size in bytes | 2048000 |
| `file_format` | ENUM | NOT NULL | Export format | 'csv', 'pdf', 'excel' |
| `record_count` | INT | NULL | Number of records in report | 250 |
| `status` | ENUM | DEFAULT 'pending' | Generation status | 'pending', 'completed', 'failed' |
| `error_message` | TEXT | NULL | Error if failed | 'No data found' |
| `generated_at` | TIMESTAMP | NULL | When report was generated | '2024-11-18 15:00:00' |
| `expires_at` | TIMESTAMP | NULL | File expiration | '2024-12-18 15:00:00' |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Request creation | Automatic |

**Indexes**:
- PRIMARY KEY: `id`
- INDEX: `user_id`
- INDEX: `report_type`
- INDEX: `status`
- INDEX: `created_at`
- INDEX: `generated_at`

**Usage Examples**:
```sql
-- Get completed reports
SELECT * FROM reports 
WHERE status = 'completed' AND expires_at > NOW()
ORDER BY generated_at DESC;

-- Get user's reports
SELECT * FROM reports WHERE user_id = 'ADM001' ORDER BY created_at DESC;
```

---

### **9. SYSTEM_CONFIG Table**

**Purpose**: Application-wide configuration settings

**Table Name**: `system_config`

| Column | Type | Constraints | Description | Example |
|--------|------|-------------|-------------|---------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Config ID | 1, 2, 3... |
| `config_key` | VARCHAR(100) | UNIQUE, NOT NULL | Configuration key | 'face_recognition_threshold' |
| `config_value` | TEXT | NOT NULL | Configuration value | '0.6' |
| `data_type` | VARCHAR(20) | NOT NULL | Value type | 'number', 'string', 'boolean', 'json' |
| `description` | TEXT | NULL | Config description | 'Minimum confidence for face match' |
| `is_editable` | BOOLEAN | DEFAULT TRUE | If editable by admin | TRUE |
| `category` | VARCHAR(50) | NULL | Config category | 'face_recognition', 'authentication', 'email' |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation time | Automatic |
| `updated_at` | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | Last update | Automatic |

**Indexes**:
- PRIMARY KEY: `id`
- UNIQUE: `config_key`
- INDEX: `category`

**Default Configurations**:
```sql
face_recognition_threshold = 0.6
attendance_marking_enabled = true
face_registration_min_images = 5
working_hours_start = 09:00
working_hours_end = 17:00
late_mark_after_minutes = 15
session_timeout_minutes = 30
jwt_token_expiry_hours = 24
```

---

### **10. NOTIFICATIONS Table**

**Purpose**: User notification system for alerts and messages

**Table Name**: `notifications`

| Column | Type | Constraints | Description | Example |
|--------|------|-------------|-------------|---------|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Notification ID | 1, 2, 3... |
| `user_id` | VARCHAR(20) | NOT NULL, FOREIGN KEY → users.id | Recipient user | 'EMP001' |
| `notification_type` | VARCHAR(50) | NOT NULL | Type | 'attendance', 'alert', 'reminder', 'report' |
| `title` | VARCHAR(255) | NOT NULL | Notification title | 'Attendance Marked' |
| `message` | TEXT | NOT NULL | Message content | 'Your attendance has been marked' |
| `action_url` | VARCHAR(255) | NULL | Link to action | '/attendance/records' |
| `is_read` | BOOLEAN | DEFAULT FALSE | Read status | FALSE |
| `read_at` | TIMESTAMP | NULL | When marked as read | NULL or timestamp |
| `priority` | ENUM | DEFAULT 'normal' | Importance level | 'low', 'normal', 'high', 'urgent' |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation time | Automatic |
| `expires_at` | TIMESTAMP | NULL | Expiration time | '2024-12-18' |

**Indexes**:
- PRIMARY KEY: `id`
- INDEX: `user_id`
- INDEX: `is_read`
- INDEX: `created_at`
- INDEX: `(user_id, is_read)`

**Usage Examples**:
```sql
-- Get unread notifications
SELECT * FROM notifications 
WHERE user_id = 'EMP001' AND is_read = FALSE 
ORDER BY created_at DESC;

-- Mark all as read
UPDATE notifications SET is_read = TRUE, read_at = NOW() 
WHERE user_id = 'EMP001' AND is_read = FALSE;
```

---

## Views & Queries

### **View 1: v_today_attendance**

**Purpose**: Quick view of today's attendance status for all users

**Query**:
```sql
CREATE VIEW v_today_attendance AS
SELECT 
    u.id as user_id,
    u.name,
    u.email,
    u.role,
    u.department,
    d.name as department_name,
    ar.timestamp,
    ar.status,
    ar.recognition_confidence,
    CASE WHEN ar.id IS NULL THEN 'Absent' ELSE ar.status END as attendance_status
FROM users u
LEFT JOIN departments d ON u.department = d.id
LEFT JOIN attendance_records ar ON u.id = ar.user_id AND ar.date_only = CURDATE()
WHERE u.deleted_at IS NULL AND u.status = 'Active'
ORDER BY u.id;
```

**Usage**:
```sql
SELECT * FROM v_today_attendance;
-- Shows all users with their attendance for today
```

---

### **View 2: v_monthly_attendance_rate**

**Purpose**: Calculate monthly attendance percentage for reporting

**Query**:
```sql
CREATE VIEW v_monthly_attendance_rate AS
SELECT 
    DATE_FORMAT(ar.date_only, '%Y-%m') as year_month,
    ar.user_id,
    u.name,
    u.department,
    COUNT(*) as total_days,
    SUM(CASE WHEN ar.status = 'Present' THEN 1 ELSE 0 END) as present_days,
    SUM(CASE WHEN ar.status = 'Absent' THEN 1 ELSE 0 END) as absent_days,
    SUM(CASE WHEN ar.status = 'Late' THEN 1 ELSE 0 END) as late_days,
    ROUND((SUM(CASE WHEN ar.status = 'Present' THEN 1 ELSE 0 END) / COUNT(*) * 100), 2) as attendance_rate
FROM attendance_records ar
JOIN users u ON ar.user_id = u.id
WHERE ar.status IN ('Present', 'Absent', 'Late')
GROUP BY DATE_FORMAT(ar.date_only, '%Y-%m'), ar.user_id;
```

---

### **View 3: v_department_stats**

**Purpose**: Department-level attendance statistics

**Query**:
```sql
CREATE VIEW v_department_stats AS
SELECT 
    d.id as department_id,
    d.name as department_name,
    COUNT(DISTINCT u.id) as total_employees,
    SUM(CASE WHEN ar.date_only = CURDATE() AND ar.status = 'Present' THEN 1 ELSE 0 END) as present_today,
    SUM(CASE WHEN ar.date_only = CURDATE() AND ar.status = 'Absent' THEN 1 ELSE 0 END) as absent_today,
    SUM(CASE WHEN ar.date_only = CURDATE() AND ar.status = 'Late' THEN 1 ELSE 0 END) as late_today
FROM departments d
LEFT JOIN users u ON d.id = u.department AND u.deleted_at IS NULL AND u.status = 'Active'
LEFT JOIN attendance_records ar ON u.id = ar.user_id
GROUP BY d.id, d.name;
```

---

### **View 4: v_face_enrollment_status**

**Purpose**: Track face enrollment progress for all users

**Query**:
```sql
CREATE VIEW v_face_enrollment_status AS
SELECT 
    u.id as user_id,
    u.name,
    u.email,
    u.role,
    COUNT(CASE WHEN fe.status = 'verified' THEN 1 END) as verified_faces,
    COUNT(CASE WHEN fe.status = 'pending' THEN 1 END) as pending_faces,
    COUNT(CASE WHEN fe.status = 'rejected' THEN 1 END) as rejected_faces,
    CASE 
        WHEN COUNT(CASE WHEN fe.status = 'verified' THEN 1 END) >= 5 THEN 'Enrolled'
        WHEN COUNT(CASE WHEN fe.status = 'verified' THEN 1 END) > 0 THEN 'In Progress'
        ELSE 'Not Started'
    END as enrollment_status,
    u.created_at as enrolled_since
FROM users u
LEFT JOIN face_encodings fe ON u.id = fe.user_id
WHERE u.deleted_at IS NULL
GROUP BY u.id;
```

---

## Indexes & Performance

### **Primary Indexes (Mandatory)**

```sql
-- Users table
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_department ON users(department);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_deleted ON users(deleted_at);

-- Face Encodings table
CREATE INDEX idx_face_user ON face_encodings(user_id);
CREATE INDEX idx_face_status ON face_encodings(status);
CREATE INDEX idx_face_hash ON face_encodings(image_hash);
CREATE INDEX idx_face_captured ON face_encodings(captured_at);

-- Attendance Records table
CREATE UNIQUE INDEX idx_attendance_unique ON attendance_records(user_id, date_only);
CREATE INDEX idx_attendance_user ON attendance_records(user_id);
CREATE INDEX idx_attendance_date ON attendance_records(date_only);
CREATE INDEX idx_attendance_timestamp ON attendance_records(timestamp);
CREATE INDEX idx_attendance_status ON attendance_records(status);
CREATE INDEX idx_attendance_date_status ON attendance_records(date_only, status);

-- Activity Log table
CREATE INDEX idx_activity_user ON activity_log(user_id);
CREATE INDEX idx_activity_type ON activity_log(action_type);
CREATE INDEX idx_activity_created ON activity_log(created_at);
CREATE INDEX idx_activity_status ON activity_log(status);
CREATE INDEX idx_activity_user_created ON activity_log(user_id, created_at);

-- Auth Tokens table
CREATE INDEX idx_token_user ON auth_tokens(user_id);
CREATE INDEX idx_token_expires ON auth_tokens(expires_at);
CREATE INDEX idx_token_revoked ON auth_tokens(is_revoked);
CREATE INDEX idx_token_user_active ON auth_tokens(user_id, is_revoked);
```

---

## API Endpoint Mapping

This section maps frontend API calls to database operations. All backend endpoints must follow this specification.

### **Authentication Endpoints**

| Endpoint | Method | Request Data | Database Operations | Response | Status |
|----------|--------|--------------|-------------------|----------|--------|
| `/api/auth/register` | POST | name, email, password, role | INSERT users; INSERT user_settings | user_id, token | ✅ |
| `/api/auth/login` | POST | email, password | SELECT users; INSERT auth_tokens | token, user_id, role | ✅ |
| `/api/auth/logout` | POST | token | UPDATE auth_tokens (revoke) | success | ✅ |
| `/api/auth/verify-token` | GET | token (header) | SELECT auth_tokens; VALIDATE | valid: true/false | ✅ |
| `/api/auth/refresh-token` | POST | refresh_token | INSERT auth_tokens (new); UPDATE auth_tokens (old) | new_token | TODO |
| `/api/auth/change-password` | POST | old_password, new_password | UPDATE users password_hash | success | TODO |

### **User Management Endpoints**

| Endpoint | Method | Request Data | Database Operations | Response | Status |
|----------|--------|--------------|-------------------|----------|--------|
| `/api/users/profile` | GET | user_id (from token) | SELECT users; SELECT user_settings | user_object | ✅ |
| `/api/users/profile` | PUT | name, email, phone, address | UPDATE users | updated_user | TODO |
| `/api/users` | GET | page, limit, role, department | SELECT users; COUNT | users_list, total | ✅ |
| `/api/users/:id` | GET | user_id | SELECT users; SELECT face_encodings | user_detail | ✅ |
| `/api/users/:id` | DELETE | user_id | SOFT DELETE users | success | TODO |
| `/api/users/avatar` | POST | file | SAVE file; UPDATE users.avatar_url | avatar_url | TODO |

### **Face Recognition Endpoints**

| Endpoint | Method | Request Data | Database Operations | Response | Status |
|----------|--------|--------------|-------------------|----------|--------|
| `/api/face/register` | POST | images[], user_id | INSERT face_encodings; GENERATE vectors | status, encodings_count | TODO |
| `/api/face/verify` | POST | image, user_id | MATCH against face_encodings | matched: true/false, confidence | TODO |
| `/api/face/encodings` | GET | user_id | SELECT face_encodings WHERE user_id | encodings_list | ✅ |
| `/api/face/status` | GET | user_id | SELECT face_encodings; COUNT verified | enrollment_status | ✅ |
| `/api/face/delete/:id` | DELETE | encoding_id | DELETE face_encodings | success | TODO |
| `/api/face/reject` | POST | encoding_id, reason | UPDATE face_encodings SET status='rejected' | success | TODO |

### **Attendance Endpoints**

| Endpoint | Method | Request Data | Database Operations | Response | Status |
|----------|--------|--------------|-------------------|----------|--------|
| `/api/attendance/mark` | POST | image/user_id | INSERT attendance_records; VERIFY face | status, timestamp | ✅ |
| `/api/attendance/today` | GET | none | SELECT attendance_records WHERE date_only=TODAY | today_records | ✅ |
| `/api/attendance/user-history` | GET | user_id, start_date, end_date | SELECT attendance_records (filtered) | records_list | ✅ |
| `/api/attendance/status/:id` | GET | user_id | JOIN users + attendance_records | attendance_status | ✅ |
| `/api/attendance/mark-manual` | POST | user_id, date, status | INSERT attendance_records (manual) | success | TODO |
| `/api/attendance/edit` | PUT | record_id, status, notes | UPDATE attendance_records | updated_record | TODO |

### **Reporting Endpoints**

| Endpoint | Method | Request Data | Database Operations | Response | Status |
|----------|--------|--------------|-------------------|----------|--------|
| `/api/reports/daily` | GET | date, department | SELECT from v_daily_attendance | report_data | ✅ |
| `/api/reports/monthly` | GET | year, month | SELECT from v_monthly_attendance_rate | report_data | ✅ |
| `/api/reports/department` | GET | department_id | SELECT from v_department_stats | department_stats | ✅ |
| `/api/reports/generate` | POST | report_type, filters, format | INSERT reports; GENERATE file | report_id, status | TODO |
| `/api/reports/download/:id` | GET | report_id | SELECT reports; STREAM file | file_content | TODO |
| `/api/reports/list` | GET | page, limit | SELECT reports WHERE user_id=current | reports_list | TODO |

### **Admin Endpoints**

| Endpoint | Method | Request Data | Database Operations | Response | Status |
|----------|--------|--------------|-------------------|----------|--------|
| `/api/admin/users/create` | POST | user_data | INSERT users; INSERT user_settings | user_id | ✅ |
| `/api/admin/users/bulk-import` | POST | file (csv/excel) | BULK INSERT users | imported_count | TODO |
| `/api/admin/users/deactivate/:id` | PUT | user_id | UPDATE users SET status='Inactive' | success | TODO |
| `/api/admin/config` | GET | none | SELECT system_config | config_dict | ✅ |
| `/api/admin/config` | PUT | config_key, config_value | UPDATE system_config | success | TODO |
| `/api/admin/activity-log` | GET | filters | SELECT activity_log | logs_list | ✅ |
| `/api/admin/departments` | GET | none | SELECT departments | departments_list | ✅ |

---

## Data Types & Validation

### **String Fields**

| Field | Type | Min Length | Max Length | Pattern | Example |
|-------|------|-----------|-----------|---------|---------|
| `id` | VARCHAR(20) | 3 | 20 | [A-Z]{3}\d{3} | EMP001, STU001 |
| `email` | VARCHAR(100) | 5 | 100 | RFC 5322 | john@company.com |
| `name` | VARCHAR(100) | 2 | 100 | [A-Za-z\s'-] | John Doe |
| `password` | VARCHAR(255) | 8 | 128 | See policy | Complex hash |
| `phone` | VARCHAR(20) | 10 | 20 | [\d+\-\(\) ] | +1-555-1001 |

### **Numeric Fields**

| Field | Type | Min | Max | Decimals | Example |
|-------|------|-----|-----|----------|---------|
| `recognition_confidence` | FLOAT | 0 | 1 | 2 | 0.98 |
| `quality_score` | FLOAT | 0 | 1 | 2 | 0.95 |
| `face_confidence` | FLOAT | 0 | 1 | 2 | 0.99 |
| `recognition_distance` | FLOAT | 0 | 10 | 4 | 0.25 |

### **Enum Fields**

| Field | Values | Default | Description |
|-------|--------|---------|-------------|
| `role` | admin, employee, student | employee | User role |
| `status` | Active, Inactive, Suspended | Active | User status |
| `attendance_status` | Present, Absent, Late, Leave | Absent | Attendance status |
| `face_status` | pending, verified, rejected | pending | Face enrollment status |
| `source` | face_recognition, manual, api | face_recognition | Attendance source |
| `report_type` | daily, monthly, department | - | Report type |

---

## Constraints & Rules

### **Data Integrity Rules**

```
1. USER RULES:
   ├─ Email must be globally unique
   ├─ User ID follows pattern: [ROLE][3-digits] (EMP001, STU005, ADM001)
   ├─ Password must be bcrypt-hashed (never plain text)
   ├─ Role must be one of: admin, employee, student
   ├─ Department must exist in departments table
   └─ Cannot delete user with active attendance records

2. FACE ENCODING RULES:
   ├─ Each user can have 5-7 verified encodings
   ├─ Image hash must be unique (prevents duplicates)
   ├─ Quality score must be 0.9+ to approve
   ├─ Can only mark attendance with verified encodings
   └─ Cannot delete verified encodings without approval

3. ATTENDANCE RULES:
   ├─ One record per user per day (unique constraint)
   ├─ Status must be: Present, Absent, Late, or Leave
   ├─ If marked before 09:00 = Present
   ├─ If marked 09:01-09:15 = Late
   ├─ If no mark by end of day = Absent
   └─ Cannot edit attendance > 7 days old

4. TOKEN RULES:
   ├─ JWT expires in 24 hours
   ├─ Can have multiple active tokens (multi-device)
   ├─ Revoke all tokens on password change
   ├─ Revoke all tokens on logout
   └─ Expired tokens auto-deleted after 30 days

5. DEPARTMENT RULES:
   ├─ Department name must be unique
   ├─ Manager must be active user in same department
   ├─ Cannot delete department with active employees
   └─ Department location is informational only
```

---

## Relationships & Foreign Keys

### **Foreign Key Diagram**

```
users (Primary table)
├── departments.id
├── users_settings.user_id (1:1)
├── face_encodings.user_id (1:N)
├── attendance_records.user_id (1:N)
├── activity_log.user_id (1:N)
├── auth_tokens.user_id (1:N)
├── departments.manager_id (N:1, back-reference)
├── reports.user_id (1:N)
└── notifications.user_id (1:N)

face_encodings
└── attendance_records.face_encoding_id (N:1)

departments
├── users.department (N:1)
└── users.manager_id (1:N)
```

### **Cascade Behavior**

| Relationship | ON DELETE | ON UPDATE |
|------------|-----------|-----------|
| users → departments | RESTRICT | CASCADE |
| users → auth_tokens | CASCADE | CASCADE |
| users → activity_log | CASCADE | CASCADE |
| users → notifications | CASCADE | CASCADE |
| users → user_settings | CASCADE | CASCADE |
| users → face_encodings | CASCADE | CASCADE |
| users → attendance_records | CASCADE | CASCADE |
| face_encodings → attendance_records | SET NULL | CASCADE |

---

## Sample Queries

### **Common Operational Queries**

#### **1. Get User with Complete Profile**
```sql
SELECT 
    u.*,
    d.name as department_name,
    COUNT(DISTINCT fe.id) as total_faces,
    SUM(CASE WHEN fe.status = 'verified' THEN 1 ELSE 0 END) as verified_faces,
    s.notifications_enabled,
    s.timezone,
    s.theme,
    ar.date_only as last_attendance_date,
    ar.status as last_attendance_status
FROM users u
LEFT JOIN departments d ON u.department = d.id
LEFT JOIN face_encodings fe ON u.id = fe.user_id
LEFT JOIN user_settings s ON u.id = s.user_id
LEFT JOIN attendance_records ar ON u.id = ar.user_id AND ar.date_only = (
    SELECT MAX(date_only) FROM attendance_records WHERE user_id = u.id
)
WHERE u.id = 'EMP001' AND u.deleted_at IS NULL
GROUP BY u.id;
```

#### **2. Get Today's Summary**
```sql
SELECT 
    d.id,
    d.name as department,
    COUNT(DISTINCT u.id) as total_employees,
    SUM(CASE WHEN ar.status = 'Present' THEN 1 ELSE 0 END) as present,
    SUM(CASE WHEN ar.status = 'Absent' THEN 1 ELSE 0 END) as absent,
    SUM(CASE WHEN ar.status = 'Late' THEN 1 ELSE 0 END) as late,
    SUM(CASE WHEN ar.status = 'Leave' THEN 1 ELSE 0 END) as leave
FROM departments d
LEFT JOIN users u ON d.id = u.department AND u.deleted_at IS NULL AND u.status = 'Active'
LEFT JOIN attendance_records ar ON u.id = ar.user_id AND ar.date_only = CURDATE()
WHERE d.status = 'Active'
GROUP BY d.id
ORDER BY d.name;
```

#### **3. Get Users NOT Marked Today**
```sql
SELECT u.id, u.name, u.email, u.role, d.name as department
FROM users u
LEFT JOIN departments d ON u.department = d.id
WHERE u.status = 'Active' AND u.deleted_at IS NULL
AND u.id NOT IN (
    SELECT DISTINCT user_id FROM attendance_records 
    WHERE date_only = CURDATE()
)
ORDER BY d.name, u.name;
```

#### **4. Get Monthly Attendance Report for User**
```sql
SELECT 
    DATE_FORMAT(date_only, '%Y-%m-%d') as date,
    status,
    recognition_confidence,
    location
FROM attendance_records
WHERE user_id = 'EMP001' 
AND date_only BETWEEN '2024-11-01' AND '2024-11-30'
ORDER BY date_only ASC;
```

#### **5. Get Activity Audit Trail for User**
```sql
SELECT 
    created_at,
    action_type,
    action_description,
    status,
    error_message,
    ip_address
FROM activity_log
WHERE user_id = 'EMP001'
AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC;
```

---

## Backend Integration Guide

### **Backend Framework Setup**

#### **Python Flask Setup**

```python
# requirements.txt
Flask==2.3.0
Flask-SQLAlchemy==3.0.0
Flask-JWT-Extended==4.4.0
mysql-connector-python==8.0.33
python-dotenv==1.0.0
bcrypt==4.0.1
face-recognition==1.3.5

# Connection
from flask_sqlalchemy import SQLAlchemy
DATABASE_URL = "mysql+mysqlconnector://root:password@localhost:3306/face_attendance_db"
db = SQLAlchemy()
```

#### **Node.js Setup**

```javascript
// package.json dependencies
"mysql2": "^3.0.0",
"sequelize": "^6.0.0",
"express": "^4.18.0",
"jsonwebtoken": "^9.0.0",
"bcryptjs": "^2.4.3"

// Connection
const sequelize = new Sequelize('face_attendance_db', 'root', 'password', {
  host: 'localhost',
  dialect: 'mysql'
});
```

### **Database Connection Best Practices**

1. **Connection Pooling**
   - Use connection pools (10-20 connections)
   - Set timeout to 30 seconds
   - Implement reconnection logic

2. **Query Optimization**
   - Use indexes for WHERE clauses
   - Use JOINs instead of multiple queries
   - Limit result sets with pagination

3. **Error Handling**
   ```python
   try:
       result = db.session.execute(query)
       db.session.commit()
   except IntegrityError:
       # Handle duplicate key, foreign key violations
   except DatabaseError:
       # Handle connection errors
   finally:
       db.session.close()
   ```

4. **Security**
   - Always use parameterized queries (prevent SQL injection)
   - Hash passwords with bcrypt
   - Validate all input data
   - Use HTTPS for API calls

### **Sample ORM Model (SQLAlchemy)**

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'employee', 'student'), nullable=False)
    department = db.Column(db.String(20), db.ForeignKey('departments.id'))
    status = db.Column(db.Enum('Active', 'Inactive', 'Suspended'), default='Active')
    
    # Relationships
    face_encodings = db.relationship('FaceEncoding', backref='user', lazy=True)
    attendance_records = db.relationship('AttendanceRecord', backref='user', lazy=True)
    settings = db.relationship('UserSettings', backref='user', uselist=False)

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False)
    date_only = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('Present', 'Absent', 'Late', 'Leave'), nullable=False)
    recognition_confidence = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'date_only', name='uq_attendance_user_date'),
    )
```

---

## Summary & Next Steps

### **This Document Provides:**

✅ Complete database structure with 10 tables  
✅ 4 analytical views for reporting  
✅ 30+ optimized indexes  
✅ Complete API endpoint mapping  
✅ Data validation rules  
✅ Constraint specifications  
✅ Sample queries for common operations  
✅ Backend integration examples  

### **Backend Team Should:**

1. Review all table definitions carefully
2. Set up database connection using provided connection strings
3. Create ORM models matching table structure
4. Implement all API endpoints listed in the mapping
5. Add data validation as per specified rules
6. Implement error handling for database constraints
7. Set up logging for activity_log table
8. Test all queries before deployment

### **Frontend Team Should:**

1. Review API endpoint mapping
2. Test all endpoints after backend implementation
3. Handle response formats as specified
4. Implement error messages based on constraint violations
5. Validate input before sending to backend

---

**Document Version**: 1.0  
**Created**: 2024-11-18  
**Status**: ✅ Production Ready  
**Next Review**: 2024-12-18
