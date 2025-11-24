-- ============================================================================
-- FACE RECOGNITION ATTENDANCE SYSTEM - SAMPLE DATA
-- This file contains sample data for development and testing
-- Load this AFTER running schema.sql
-- ============================================================================

USE face_attendance_db;

-- ============================================================================
-- INSERT DEPARTMENTS
-- ============================================================================
INSERT INTO departments (id, name, description, location, status) VALUES
('DEPT001', 'Engineering', 'Software and Hardware Development', 'Building A, Floor 1', 'Active'),
('DEPT002', 'Human Resources', 'HR and Recruitment', 'Building B, Floor 2', 'Active'),
('DEPT003', 'Sales', 'Sales and Business Development', 'Building A, Floor 2', 'Active'),
('DEPT004', 'Marketing', 'Marketing and Communications', 'Building C, Floor 1', 'Active'),
('DEPT005', 'Finance', 'Finance and Accounting', 'Building B, Floor 3', 'Active'),
('DEPT006', 'Operations', 'Operations and Logistics', 'Building D, Floor 1', 'Active');

-- ============================================================================
-- INSERT USERS - ADMIN USERS
-- ============================================================================
INSERT INTO users (id, name, email, password_hash, role, department, phone, status, join_date, created_at) VALUES
('ADM001', 'Admin User', 'admin@company.com', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'admin', 'DEPT002', '+1-555-0001', 'Active', '2024-01-01', NOW()),
('ADM002', 'Admin Manager', 'admin.manager@company.com', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'admin', 'DEPT002', '+1-555-0002', 'Active', '2024-01-05', NOW());

-- ============================================================================
-- INSERT USERS - EMPLOYEES
-- ============================================================================
INSERT INTO users (id, name, email, password_hash, role, department, phone, status, join_date, created_at) VALUES
-- Engineering Department
('EMP001', 'John Doe', 'john.doe@company.com', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'employee', 'DEPT001', '+1-555-1001', 'Active', '2024-02-01', NOW()),
('EMP002', 'Jane Smith', 'jane.smith@company.com', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'employee', 'DEPT001', '+1-555-1002', 'Active', '2024-02-05', NOW()),
('EMP003', 'Mike Johnson', 'mike.johnson@company.com', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'employee', 'DEPT001', '+1-555-1003', 'Active', '2024-02-10', NOW()),
('EMP004', 'Sarah Williams', 'sarah.williams@company.com', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'employee', 'DEPT001', '+1-555-1004', 'Active', '2024-02-15', NOW()),
('EMP005', 'Tom Brown', 'tom.brown@company.com', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'employee', 'DEPT001', '+1-555-1005', 'Active', '2024-02-20', NOW()),

-- HR Department
('EMP006', 'Emily Davis', 'emily.davis@company.com', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'employee', 'DEPT002', '+1-555-1006', 'Active', '2024-03-01', NOW()),
('EMP007', 'Robert Wilson', 'robert.wilson@company.com', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'employee', 'DEPT002', '+1-555-1007', 'Active', '2024-03-05', NOW()),

-- Sales Department
('EMP008', 'Lisa Anderson', 'lisa.anderson@company.com', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'employee', 'DEPT003', '+1-555-1008', 'Active', '2024-03-10', NOW()),
('EMP009', 'David Martinez', 'david.martinez@company.com', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'employee', 'DEPT003', '+1-555-1009', 'Active', '2024-03-15', NOW()),

-- Marketing Department
('EMP010', 'Jennifer Garcia', 'jennifer.garcia@company.com', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'employee', 'DEPT004', '+1-555-1010', 'Active', '2024-03-20', NOW()),
('EMP011', 'Christopher Lee', 'christopher.lee@company.com', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'employee', 'DEPT004', '+1-555-1011', 'Active', '2024-03-25', NOW()),

-- Finance Department
('EMP012', 'Amanda Taylor', 'amanda.taylor@company.com', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'employee', 'DEPT005', '+1-555-1012', 'Active', '2024-04-01', NOW()),

-- Operations Department
('EMP013', 'Kevin Thomas', 'kevin.thomas@company.com', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'employee', 'DEPT006', '+1-555-1013', 'Active', '2024-04-05', NOW());

-- ============================================================================
-- INSERT USERS - STUDENTS (For educational institutions)
-- ============================================================================
INSERT INTO users (id, name, email, password_hash, role, department, phone, status, join_date, created_at) VALUES
('STU001', 'Alex Kumar', 'alex.kumar@student.edu', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'student', 'DEPT001', '+1-555-2001', 'Active', '2024-08-15', NOW()),
('STU002', 'Sophia Chen', 'sophia.chen@student.edu', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'student', 'DEPT001', '+1-555-2002', 'Active', '2024-08-20', NOW()),
('STU003', 'Marcus Johnson', 'marcus.johnson@student.edu', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'student', 'DEPT001', '+1-555-2003', 'Active', '2024-08-25', NOW()),
('STU004', 'Isabella Rodriguez', 'isabella.rodriguez@student.edu', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'student', 'DEPT001', '+1-555-2004', 'Active', '2024-09-01', NOW()),
('STU005', 'Daniel Patel', 'daniel.patel@student.edu', '$2b$12$abcdefghijklmnopqrstuvwxyz123456', 'student', 'DEPT001', '+1-555-2005', 'Active', '2024-09-05', NOW());

-- ============================================================================
-- INSERT FACE ENCODINGS (Sample face data)
-- Note: In production, these would be real 128-dimensional vectors
-- For testing, we use placeholder binary data
-- ============================================================================
INSERT INTO face_encodings (id, user_id, encoding_vector, image_url, image_hash, captured_at, quality_score, face_confidence, status) VALUES
('FACE_ENC_001', 'EMP001', 0xABCDEF123456789, '/storage/faces/EMP001_1.jpg', 'abc123def456', NOW(), 0.95, 0.99, 'verified'),
('FACE_ENC_002', 'EMP001', 0xBCDEF123456789A, '/storage/faces/EMP001_2.jpg', 'abc124def457', NOW(), 0.93, 0.98, 'verified'),
('FACE_ENC_003', 'EMP002', 0xCDEF123456789AB, '/storage/faces/EMP002_1.jpg', 'bcd234efg567', NOW(), 0.94, 0.97, 'verified'),
('FACE_ENC_004', 'EMP002', 0xDEF123456789ABC, '/storage/faces/EMP002_2.jpg', 'bcd235efg568', NOW(), 0.92, 0.96, 'verified'),
('FACE_ENC_005', 'EMP003', 0xEF123456789ABCD, '/storage/faces/EMP003_1.jpg', 'cde345fgh678', NOW(), 0.96, 0.99, 'verified'),
('FACE_ENC_006', 'EMP004', 0xF123456789ABCDE, '/storage/faces/EMP004_1.jpg', 'def456ghi789', NOW(), 0.91, 0.95, 'verified'),
('FACE_ENC_007', 'EMP005', 0x123456789ABCDEF, '/storage/faces/EMP005_1.jpg', 'efg567hij890', NOW(), 0.94, 0.98, 'verified'),
('FACE_ENC_008', 'EMP006', 0x23456789ABCDEF1, '/storage/faces/EMP006_1.jpg', 'fgh678ijk901', NOW(), 0.93, 0.97, 'verified'),
('FACE_ENC_009', 'STU001', 0x3456789ABCDEF12, '/storage/faces/STU001_1.jpg', 'ghi789jkl012', NOW(), 0.95, 0.99, 'verified'),
('FACE_ENC_010', 'STU002', 0x456789ABCDEF123, '/storage/faces/STU002_1.jpg', 'hij890klm123', NOW(), 0.92, 0.96, 'verified');

-- ============================================================================
-- INSERT ATTENDANCE RECORDS (Last 30 days)
-- ============================================================================
-- November 18, 2024
INSERT INTO attendance_records (user_id, face_encoding_id, timestamp, date_only, time_only, status, recognition_confidence, location, device_id, source) VALUES
('EMP001', 'FACE_ENC_001', '2024-11-18 09:15:30', '2024-11-18', '09:15:30', 'Present', 0.98, 'Main Gate', 'CAM001', 'face_recognition'),
('EMP002', 'FACE_ENC_003', '2024-11-18 09:22:15', '2024-11-18', '09:22:15', 'Present', 0.95, 'Main Gate', 'CAM001', 'face_recognition'),
('EMP003', 'FACE_ENC_005', '2024-11-18 09:30:45', '2024-11-18', '09:30:45', 'Present', 0.97, 'Main Gate', 'CAM001', 'face_recognition'),
('EMP004', 'FACE_ENC_006', '2024-11-18 09:45:20', '2024-11-18', '09:45:20', 'Present', 0.94, 'Main Gate', 'CAM001', 'face_recognition'),
('EMP005', 'FACE_ENC_007', '2024-11-18 10:00:00', '2024-11-18', '10:00:00', 'Late', 0.96, 'Main Gate', 'CAM001', 'face_recognition'),
('EMP006', 'FACE_ENC_008', '2024-11-18 08:50:30', '2024-11-18', '08:50:30', 'Present', 0.99, 'Main Gate', 'CAM001', 'face_recognition'),

-- November 17, 2024
('EMP001', 'FACE_ENC_001', '2024-11-17 09:10:00', '2024-11-17', '09:10:00', 'Present', 0.97, 'Main Gate', 'CAM001', 'face_recognition'),
('EMP002', 'FACE_ENC_003', '2024-11-17 09:20:00', '2024-11-17', '09:20:00', 'Present', 0.96, 'Main Gate', 'CAM001', 'face_recognition'),
('EMP003', 'FACE_ENC_005', '2024-11-17 09:25:00', '2024-11-17', '09:25:00', 'Present', 0.98, 'Main Gate', 'CAM001', 'face_recognition'),
('EMP004', NULL, '2024-11-17 00:00:00', '2024-11-17', NULL, 'Absent', NULL, NULL, NULL, 'manual'),
('EMP005', 'FACE_ENC_007', '2024-11-17 09:30:00', '2024-11-17', '09:30:00', 'Present', 0.95, 'Main Gate', 'CAM001', 'face_recognition'),
('EMP006', 'FACE_ENC_008', '2024-11-17 08:45:00', '2024-11-17', '08:45:00', 'Present', 0.99, 'Main Gate', 'CAM001', 'face_recognition'),

-- November 16, 2024 (Weekend or Holiday - Optional)
('EMP001', 'FACE_ENC_001', '2024-11-16 09:00:00', '2024-11-16', '09:00:00', 'Present', 0.97, 'Office', 'CAM001', 'face_recognition'),
('EMP002', 'FACE_ENC_003', '2024-11-16 09:15:00', '2024-11-16', '09:15:00', 'Present', 0.96, 'Office', 'CAM001', 'face_recognition'),

-- November 15, 2024
('EMP001', 'FACE_ENC_001', '2024-11-15 09:05:00', '2024-11-15', '09:05:00', 'Present', 0.98, 'Main Gate', 'CAM001', 'face_recognition'),
('EMP002', 'FACE_ENC_003', '2024-11-15 09:18:00', '2024-11-15', '09:18:00', 'Present', 0.94, 'Main Gate', 'CAM001', 'face_recognition'),
('EMP003', 'FACE_ENC_005', '2024-11-15 10:30:00', '2024-11-15', '10:30:00', 'Late', 0.97, 'Main Gate', 'CAM001', 'face_recognition'),
('EMP004', 'FACE_ENC_006', '2024-11-15 09:40:00', '2024-11-15', '09:40:00', 'Present', 0.95, 'Main Gate', 'CAM001', 'face_recognition'),
('EMP005', 'FACE_ENC_007', '2024-11-15 09:20:00', '2024-11-15', '09:20:00', 'Present', 0.96, 'Main Gate', 'CAM001', 'face_recognition'),
('EMP006', 'FACE_ENC_008', '2024-11-15 08:55:00', '2024-11-15', '08:55:00', 'Present', 0.98, 'Main Gate', 'CAM001', 'face_recognition'),
('STU001', 'FACE_ENC_009', '2024-11-15 09:30:00', '2024-11-15', '09:30:00', 'Present', 0.93, 'Main Gate', 'CAM001', 'face_recognition'),
('STU002', 'FACE_ENC_010', '2024-11-15 09:35:00', '2024-11-15', '09:35:00', 'Present', 0.94, 'Main Gate', 'CAM001', 'face_recognition');

-- ============================================================================
-- INSERT USER SETTINGS
-- ============================================================================
INSERT INTO user_settings (user_id, camera_access_enabled, notifications_enabled, export_format, timezone, language, theme) VALUES
('ADM001', TRUE, TRUE, 'csv', 'America/New_York', 'en', 'dark'),
('ADM002', TRUE, TRUE, 'csv', 'America/New_York', 'en', 'light'),
('EMP001', TRUE, TRUE, 'csv', 'America/New_York', 'en', 'light'),
('EMP002', TRUE, TRUE, 'pdf', 'America/New_York', 'en', 'dark'),
('EMP003', TRUE, TRUE, 'excel', 'America/Chicago', 'en', 'light'),
('EMP004', TRUE, FALSE, 'csv', 'America/Los_Angeles', 'en', 'light'),
('EMP005', TRUE, TRUE, 'csv', 'America/Denver', 'en', 'dark'),
('EMP006', TRUE, TRUE, 'csv', 'UTC', 'en', 'light'),
('STU001', TRUE, TRUE, 'csv', 'America/New_York', 'en', 'light'),
('STU002', TRUE, TRUE, 'csv', 'America/New_York', 'en', 'dark');

-- ============================================================================
-- INSERT SYSTEM CONFIGURATION
-- ============================================================================
INSERT INTO system_config (config_key, config_value, data_type, description) VALUES
('face_recognition_threshold', '0.6', 'number', 'Minimum confidence score for face matching (0-1)'),
('attendance_marking_enabled', 'true', 'boolean', 'Enable/disable attendance marking'),
('face_registration_min_images', '5', 'number', 'Minimum images required for face registration'),
('face_registration_max_images', '7', 'number', 'Maximum images allowed for face registration'),
('working_hours_start', '09:00', 'string', 'Working hours start time'),
('working_hours_end', '17:00', 'string', 'Working hours end time'),
('late_mark_after_minutes', '15', 'number', 'Mark as late if arrival is after N minutes'),
('session_timeout_minutes', '30', 'number', 'Session timeout duration in minutes'),
('max_failed_login_attempts', '5', 'number', 'Lock account after N failed login attempts'),
('jwt_token_expiry_hours', '24', 'number', 'JWT token expiration in hours'),
('storage_path', '/storage', 'string', 'Base path for file storage'),
('max_file_upload_mb', '5', 'number', 'Maximum file upload size in MB'),
('enable_email_notifications', 'true', 'boolean', 'Enable email notifications'),
('smtp_server', 'smtp.gmail.com', 'string', 'SMTP server address'),
('maintenance_mode', 'false', 'boolean', 'System maintenance mode');

-- ============================================================================
-- INSERT ACTIVITY LOG SAMPLES
-- ============================================================================
INSERT INTO activity_log (user_id, action_type, action_description, table_name, status) VALUES
('ADM001', 'login', 'Admin user logged in', 'users', 'success'),
('EMP001', 'login', 'Employee user logged in', 'users', 'success'),
('EMP001', 'register_face', 'User registered 6 face images', 'face_encodings', 'success'),
('EMP002', 'mark_attendance', 'Attendance marked via face recognition', 'attendance_records', 'success'),
('ADM001', 'view_report', 'Generated monthly attendance report', 'reports', 'success'),
('EMP003', 'update_profile', 'User updated profile information', 'users', 'success'),
('STU001', 'login', 'Student user logged in', 'users', 'success'),
('ADM002', 'create_user', 'New user created', 'users', 'success'),
('EMP001', 'logout', 'User logged out', 'users', 'success'),
('ADM001', 'failed_login', 'Failed login attempt', 'users', 'failed');

-- ============================================================================
-- INSERT SAMPLE NOTIFICATIONS
-- ============================================================================
INSERT INTO notifications (user_id, notification_type, title, message, is_read) VALUES
('EMP001', 'attendance', 'Attendance Marked', 'Your attendance has been marked as Present', 1),
('EMP001', 'reminder', 'Face Registration', 'Please update your face encodings for better recognition', 0),
('EMP002', 'alert', 'Multiple Failed Logins', 'Multiple failed login attempts detected on your account', 0),
('ADM001', 'report', 'Monthly Report Ready', 'Your monthly attendance report is ready for download', 1),
('STU001', 'attendance', 'Attendance Marked', 'Your attendance has been marked as Present', 1);

-- ============================================================================
-- UPDATE DEPARTMENT MANAGERS
-- ============================================================================
UPDATE departments SET manager_id = 'EMP001' WHERE id = 'DEPT001';
UPDATE departments SET manager_id = 'EMP006' WHERE id = 'DEPT002';
UPDATE departments SET manager_id = 'EMP008' WHERE id = 'DEPT003';
UPDATE departments SET manager_id = 'EMP010' WHERE id = 'DEPT004';
UPDATE departments SET manager_id = 'EMP012' WHERE id = 'DEPT005';
UPDATE departments SET manager_id = 'EMP013' WHERE id = 'DEPT006';

-- ============================================================================
-- SAMPLE QUERIES FOR VERIFICATION
-- ============================================================================
-- SELECT * FROM users WHERE status = 'Active' LIMIT 5;
-- SELECT * FROM attendance_records WHERE date_only = CURDATE() ORDER BY timestamp;
-- SELECT * FROM face_encodings WHERE status = 'verified';
-- SELECT * FROM v_today_attendance;

-- ============================================================================
-- END OF SAMPLE DATA
-- ============================================================================
