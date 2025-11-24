-- ============================================================================
-- FACE RECOGNITION ATTENDANCE SYSTEM - COMPLETE DATABASE SCHEMA
-- Database Name: face_attendance_db
-- Created: November 18, 2025
-- Purpose: Complete database structure for Face Recognition Attendance System
-- ============================================================================

-- Create Database
CREATE DATABASE IF NOT EXISTS face_attendance_db;
USE face_attendance_db;

-- ============================================================================
-- TABLE 1: USERS - Store all user information (employees, students, admins)
-- ============================================================================
CREATE TABLE users (
    id VARCHAR(20) PRIMARY KEY COMMENT 'User ID (EMP001, STU001, ADM001)',
    name VARCHAR(100) NOT NULL COMMENT 'Full name of user',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT 'Email address (unique)',
    password_hash VARCHAR(255) NOT NULL COMMENT 'Hashed password (bcrypt)',
    role ENUM('admin', 'employee', 'student') NOT NULL DEFAULT 'employee' COMMENT 'User role',
    department VARCHAR(100) COMMENT 'Department (Engineering, HR, Sales, etc)',
    phone VARCHAR(20) COMMENT 'Phone number',
    address TEXT COMMENT 'Residential address',
    status ENUM('Active', 'Inactive') NOT NULL DEFAULT 'Active' COMMENT 'Account status',
    join_date DATE NOT NULL COMMENT 'Date user joined',
    avatar_url VARCHAR(255) COMMENT 'Profile picture URL',
    last_login DATETIME COMMENT 'Last login timestamp',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation time',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update time',
    deleted_at TIMESTAMP NULL COMMENT 'Soft delete timestamp',
    
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_department (department),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    CONSTRAINT chk_email_format CHECK (email LIKE '%@%.%')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='User accounts table';

-- ============================================================================
-- TABLE 2: FACE_ENCODINGS - Store face recognition data for each user
-- ============================================================================
CREATE TABLE face_encodings (
    id VARCHAR(50) PRIMARY KEY COMMENT 'Encoding ID (FACE_ENC_001)',
    user_id VARCHAR(20) NOT NULL COMMENT 'Reference to users table',
    encoding_vector LONGBLOB NOT NULL COMMENT '128-dimensional face encoding (numpy array as binary)',
    image_url VARCHAR(255) NOT NULL COMMENT 'Path to original face image file',
    image_hash VARCHAR(64) COMMENT 'SHA256 hash of image for duplicate detection',
    captured_at DATETIME NOT NULL COMMENT 'When the face was captured',
    quality_score FLOAT CHECK (quality_score >= 0 AND quality_score <= 1) COMMENT 'Face quality (0-1)',
    face_confidence FLOAT CHECK (face_confidence >= 0 AND face_confidence <= 1) COMMENT 'Face detection confidence',
    status ENUM('pending', 'verified', 'rejected') NOT NULL DEFAULT 'pending' COMMENT 'Processing status',
    verification_notes TEXT COMMENT 'Notes on why face was rejected',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_captured_at (captured_at),
    INDEX idx_image_hash (image_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Face encoding data for recognition';

-- ============================================================================
-- TABLE 3: ATTENDANCE_RECORDS - Store attendance marking history
-- ============================================================================
CREATE TABLE attendance_records (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Attendance record ID',
    user_id VARCHAR(20) NOT NULL COMMENT 'Reference to users table',
    face_encoding_id VARCHAR(50) COMMENT 'Which face encoding was used for match',
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'When attendance was marked',
    date_only DATE NOT NULL COMMENT 'Date of attendance (for easy filtering)',
    time_only TIME COMMENT 'Time of attendance',
    status ENUM('Present', 'Absent', 'Late', 'Leave') NOT NULL DEFAULT 'Present' COMMENT 'Attendance status',
    recognition_confidence FLOAT CHECK (recognition_confidence >= 0 AND recognition_confidence <= 1) COMMENT 'Face match confidence (0-1)',
    recognition_distance FLOAT COMMENT 'Euclidean distance of match (lower is better)',
    location VARCHAR(100) COMMENT 'Physical location/device name',
    device_id VARCHAR(50) COMMENT 'Device/camera ID where marked',
    image_proof_url VARCHAR(255) COMMENT 'Path to attendance proof image',
    ip_address VARCHAR(45) COMMENT 'IP address of device',
    source ENUM('face_recognition', 'manual', 'api') DEFAULT 'face_recognition' COMMENT 'How attendance was marked',
    is_verified BOOLEAN DEFAULT FALSE COMMENT 'Admin verification status',
    verified_by VARCHAR(20) COMMENT 'Admin who verified this record',
    verification_notes TEXT COMMENT 'Notes on verification',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (face_encoding_id) REFERENCES face_encodings(id) ON DELETE SET NULL,
    FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_date_only (date_only),
    INDEX idx_timestamp (timestamp),
    INDEX idx_status (status),
    INDEX idx_user_date (user_id, date_only),
    INDEX idx_location (location),
    UNIQUE KEY unique_user_date (user_id, date_only)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Attendance records history';

-- ============================================================================
-- TABLE 4: USER_SETTINGS - Store user preferences and configurations
-- ============================================================================
CREATE TABLE user_settings (
    user_id VARCHAR(20) PRIMARY KEY COMMENT 'Reference to users table',
    camera_access_enabled BOOLEAN DEFAULT TRUE COMMENT 'Allow camera access',
    notifications_enabled BOOLEAN DEFAULT TRUE COMMENT 'Enable notifications',
    export_format ENUM('csv', 'pdf', 'excel') DEFAULT 'csv' COMMENT 'Preferred export format',
    lms_api_key VARCHAR(255) COMMENT 'LMS integration API key (encrypted)',
    hrm_api_key VARCHAR(255) COMMENT 'HRM integration API key (encrypted)',
    timezone VARCHAR(50) DEFAULT 'UTC' COMMENT 'User timezone',
    language ENUM('en', 'es', 'fr', 'de', 'zh') DEFAULT 'en' COMMENT 'Preferred language',
    theme ENUM('light', 'dark') DEFAULT 'light' COMMENT 'UI theme preference',
    auto_logout_minutes INT DEFAULT 30 COMMENT 'Auto logout after N minutes',
    enable_2fa BOOLEAN DEFAULT FALSE COMMENT 'Two-factor authentication enabled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='User settings and preferences';

-- ============================================================================
-- TABLE 5: ACTIVITY_LOG - Track all user activities for audit trail
-- ============================================================================
CREATE TABLE activity_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Log entry ID',
    user_id VARCHAR(20) COMMENT 'User who performed action',
    action_type VARCHAR(50) NOT NULL COMMENT 'Type of action (login, register_face, mark_attendance, etc)',
    action_description TEXT COMMENT 'Detailed description',
    table_name VARCHAR(50) COMMENT 'Which table was affected',
    record_id VARCHAR(50) COMMENT 'ID of affected record',
    old_value JSON COMMENT 'Previous value (for updates)',
    new_value JSON COMMENT 'New value (for updates)',
    ip_address VARCHAR(45) COMMENT 'IP address of requester',
    user_agent TEXT COMMENT 'Browser/device information',
    status ENUM('success', 'failed', 'warning') DEFAULT 'success' COMMENT 'Action result',
    error_message TEXT COMMENT 'Error details if failed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_action_type (action_type),
    INDEX idx_created_at (created_at),
    INDEX idx_table_name (table_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Audit trail of all activities';

-- ============================================================================
-- TABLE 6: AUTH_TOKENS - Store JWT tokens for session management
-- ============================================================================
CREATE TABLE auth_tokens (
    id VARCHAR(100) PRIMARY KEY COMMENT 'Token ID/JTI',
    user_id VARCHAR(20) NOT NULL COMMENT 'Reference to users table',
    token_hash VARCHAR(255) NOT NULL UNIQUE COMMENT 'Hash of token for lookup',
    token_type ENUM('access', 'refresh') DEFAULT 'access' COMMENT 'Type of token',
    expires_at DATETIME NOT NULL COMMENT 'Token expiration time',
    revoked_at TIMESTAMP NULL COMMENT 'When token was revoked',
    device_id VARCHAR(50) COMMENT 'Device identifier',
    ip_address VARCHAR(45) COMMENT 'IP address where token was issued',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at),
    INDEX idx_token_hash (token_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='JWT token management';

-- ============================================================================
-- TABLE 7: DEPARTMENTS - Store department/organization structure
-- ============================================================================
CREATE TABLE departments (
    id VARCHAR(50) PRIMARY KEY COMMENT 'Department ID',
    name VARCHAR(100) NOT NULL UNIQUE COMMENT 'Department name',
    description TEXT COMMENT 'Department description',
    manager_id VARCHAR(20) COMMENT 'Department manager user ID',
    location VARCHAR(100) COMMENT 'Physical location',
    status ENUM('Active', 'Inactive') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (manager_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_name (name),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Departments/Organization structure';

-- ============================================================================
-- TABLE 8: REPORTS - Store generated reports metadata
-- ============================================================================
CREATE TABLE reports (
    id VARCHAR(50) PRIMARY KEY COMMENT 'Report ID',
    user_id VARCHAR(20) NOT NULL COMMENT 'Who generated this report',
    report_type VARCHAR(50) NOT NULL COMMENT 'Type of report (attendance, summary, etc)',
    title VARCHAR(255) NOT NULL COMMENT 'Report title',
    description TEXT COMMENT 'Report description',
    start_date DATE COMMENT 'Report period start',
    end_date DATE COMMENT 'Report period end',
    filters JSON COMMENT 'Applied filters',
    file_url VARCHAR(255) COMMENT 'Path to generated file',
    file_size INT COMMENT 'File size in bytes',
    format ENUM('csv', 'pdf', 'excel', 'json') DEFAULT 'csv' COMMENT 'Report format',
    total_records INT COMMENT 'Total records in report',
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME COMMENT 'When report file expires/deletes',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_generated_at (generated_at),
    INDEX idx_report_type (report_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Generated reports metadata';

-- ============================================================================
-- TABLE 9: SYSTEM_CONFIG - Store system-wide configuration settings
-- ============================================================================
CREATE TABLE system_config (
    config_key VARCHAR(100) PRIMARY KEY COMMENT 'Configuration key',
    config_value VARCHAR(500) COMMENT 'Configuration value',
    data_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
    description TEXT COMMENT 'Config description',
    is_sensitive BOOLEAN DEFAULT FALSE COMMENT 'Contains sensitive data',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='System configuration settings';

-- ============================================================================
-- TABLE 10: NOTIFICATIONS - Store user notifications
-- ============================================================================
CREATE TABLE notifications (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Notification ID',
    user_id VARCHAR(20) NOT NULL COMMENT 'Recipient user',
    notification_type VARCHAR(50) NOT NULL COMMENT 'Type of notification',
    title VARCHAR(255) NOT NULL COMMENT 'Notification title',
    message TEXT NOT NULL COMMENT 'Notification message',
    related_table VARCHAR(50) COMMENT 'Related database table',
    related_id VARCHAR(50) COMMENT 'Related record ID',
    is_read BOOLEAN DEFAULT FALSE COMMENT 'Read status',
    read_at TIMESTAMP NULL COMMENT 'When notification was read',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='User notifications';

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View 1: Today's Attendance Summary
CREATE OR REPLACE VIEW v_today_attendance AS
SELECT 
    u.id,
    u.name,
    u.email,
    u.department,
    a.status,
    a.timestamp,
    a.recognition_confidence,
    CASE 
        WHEN a.status IS NULL THEN 'Absent'
        ELSE a.status 
    END AS final_status
FROM users u
LEFT JOIN attendance_records a ON u.id = a.user_id 
    AND DATE(a.timestamp) = CURDATE()
WHERE u.status = 'Active'
ORDER BY u.department, u.name;

-- View 2: Monthly Attendance Rate
CREATE OR REPLACE VIEW v_monthly_attendance_rate AS
SELECT 
    user_id,
    YEAR(date_only) AS year,
    MONTH(date_only) AS month,
    COUNT(*) AS total_days,
    SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present_days,
    ROUND(SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS attendance_percentage
FROM attendance_records
WHERE status IN ('Present', 'Absent')
GROUP BY user_id, YEAR(date_only), MONTH(date_only);

-- View 3: Department Statistics
CREATE OR REPLACE VIEW v_department_stats AS
SELECT 
    d.name AS department,
    COUNT(DISTINCT u.id) AS total_employees,
    SUM(CASE WHEN u.status = 'Active' THEN 1 ELSE 0 END) AS active_employees,
    COUNT(DISTINCT CASE WHEN DATE(a.timestamp) = CURDATE() AND a.status = 'Present' THEN u.id END) AS present_today,
    COUNT(DISTINCT CASE WHEN DATE(a.timestamp) = CURDATE() AND a.status IN ('Absent', NULL) THEN u.id END) AS absent_today
FROM departments d
LEFT JOIN users u ON d.id = u.department
LEFT JOIN attendance_records a ON u.id = a.user_id
GROUP BY d.id, d.name;

-- View 4: Face Enrollment Status
CREATE OR REPLACE VIEW v_face_enrollment_status AS
SELECT 
    u.id,
    u.name,
    u.email,
    COUNT(f.id) AS total_face_encodings,
    MAX(CASE WHEN f.status = 'verified' THEN 1 ELSE 0 END) AS is_verified,
    MAX(f.captured_at) AS last_face_captured
FROM users u
LEFT JOIN face_encodings f ON u.id = f.user_id AND f.status = 'verified'
WHERE u.status = 'Active'
GROUP BY u.id, u.name, u.email;

-- ============================================================================
-- INSERT STATEMENTS FOR VIEWS AND TRIGGERS
-- ============================================================================

-- Create indexes for better performance
CREATE INDEX idx_attendance_user_date ON attendance_records(user_id, date_only);
CREATE INDEX idx_attendance_status_date ON attendance_records(status, date_only);
CREATE INDEX idx_face_user_status ON face_encodings(user_id, status);

-- ============================================================================
-- END OF DATABASE SCHEMA
-- ============================================================================
-- Total Tables: 10
-- Total Views: 4
-- Total Indexes: 30+
-- Estimated Storage: 500MB-1GB for 10,000 users with 2 years of records
-- ============================================================================
