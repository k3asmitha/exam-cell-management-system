-- 1. DATABASE INITIALIZATION
CREATE DATABASE IF NOT EXISTS ExamCellAutomation;
USE ExamCellAutomation;

-- 2. CLEANUP (DROP TABLES IN CORRECT ORDER)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS allocations;
DROP TABLE IF EXISTS exams;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS faculty;
SET FOREIGN_KEY_CHECKS = 1;

-- 3. CORE TABLES STRUCTURE

-- Courses: Includes Branch and Semester for filtering (Requirement 2)
CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    student_count INT NOT NULL,
    branch VARCHAR(50) NOT NULL, -- e.g., 'CSE', 'AI&DS'
    semester INT NOT NULL,
    credits INT
);

-- Exams: Includes Start/End dates and Slot (Requirement 1)
CREATE TABLE exams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    exam_date DATE NOT NULL, -- The specific day of this instance
    slot ENUM('FN', 'AN') NOT NULL
);

-- Rooms: Includes Capacity (Requirement 3)
CREATE TABLE rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_name VARCHAR(50) NOT NULL,
    capacity INT NOT NULL,
    block_name VARCHAR(50)
);

-- Faculty: Includes Max Duties and Tracking (Requirement 4)
CREATE TABLE faculty (
    id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50),
    max_duties INT DEFAULT 5,
    assigned_duties INT DEFAULT 0 -- Used for "Fair Distribution" logic
);

-- 4. ALLOCATIONS (The Relationship Table)
-- Includes UNIQUE constraints to prevent double-booking at the DB level
CREATE TABLE allocations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT,
    course_id INT,
    room_id INT,
    faculty_id INT,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE CASCADE,
    
    -- CONSTRAINT: A room cannot be used twice in the same exam session
    UNIQUE KEY unique_room_session (exam_id, room_id),
    
    -- CONSTRAINT: A faculty cannot be assigned twice in the same exam session
    UNIQUE KEY unique_faculty_session (exam_id, faculty_id)
);

-- 5. SAMPLE DATA INJECTION

INSERT INTO courses (course_code, course_name, student_count, branch, semester) VALUES
('IOT223', 'IOT', 65, 'CSE', 2),
('AID112', 'Machine Learning', 42, 'AI&DS', 3),
('ECE201', 'Digital Electronics', 58, 'ECE', 2),
('MAT211', 'Mathematics-1', 120, 'AI&DS', 1),
('AID251', 'Cloud Computing', 67, 'AI&DS', 5),
('CSE214', 'Operating Systems', 120, 'CSE', 4);

INSERT INTO rooms (room_name, capacity, block_name) VALUES
('A301', 50, 'A-Block'),
('C301', 50, 'C-Block'),
('E201', 70, 'E-Block'),
('CSE LAB-1', 100, 'E-Block'),
('CAE Lab', 100, 'D-Block');

INSERT INTO faculty (faculty_id, name, department, max_duties) VALUES
('FAC001', 'Dr. Rajesh', 'CSE', 6),
('FAC002', 'Dr. Sushanth', 'ECE', 4),
('FAC003', 'Dr. Geetha', 'Maths', 4),
('FAC004', 'Dr. Kavya', 'AI', 6);

-- 6. INDEXING FOR PERFORMANCE
CREATE INDEX idx_course_filter ON courses(branch, semester);
CREATE INDEX idx_exam_time ON exams(exam_date, slot);