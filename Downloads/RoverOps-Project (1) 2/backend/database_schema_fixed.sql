-- RoverOps Database Schema - Fixed Version
-- This file creates/updates all necessary tables for storing mission data

USE roverops_db;

-- 1. Mission Reports Table (Update if exists, create if not)
CREATE TABLE IF NOT EXISTS mission_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mission_id VARCHAR(255) UNIQUE NOT NULL,
    goal TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'complete',
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    duration_seconds FLOAT,
    steps_completed INT DEFAULT 0,
    total_steps INT DEFAULT 0,
    rover_final_position_x INT DEFAULT 0,
    rover_final_position_y INT DEFAULT 0,
    outcome TEXT,
    summary TEXT,
    collected_data JSON,
    mission_photos JSON,
    apod_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_mission_id (mission_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Mission Logs Table
CREATE TABLE IF NOT EXISTS mission_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mission_id VARCHAR(255) NOT NULL,
    timestamp DATETIME NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    level VARCHAR(20) DEFAULT 'info',
    data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_mission_id (mission_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_agent_type (agent_type),
    INDEX idx_level (level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Mission Status Table
-- Tracks mission status changes over time
CREATE TABLE IF NOT EXISTS mission_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mission_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    previous_status VARCHAR(50),
    changed_at DATETIME NOT NULL,
    changed_by VARCHAR(50) DEFAULT 'system',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_mission_id (mission_id),
    INDEX idx_status (status),
    INDEX idx_changed_at (changed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Mission Steps Table
CREATE TABLE IF NOT EXISTS mission_steps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mission_id VARCHAR(255) NOT NULL,
    step_number INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    target_position_x INT,
    target_position_y INT,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    nasa_image_url VARCHAR(500),
    completed_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_mission_id (mission_id),
    INDEX idx_step_number (step_number),
    INDEX idx_completed (completed)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Mission Statistics Table
-- Tracks overall mission statistics and counts
CREATE TABLE IF NOT EXISTS mission_statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    total_missions INT DEFAULT 0,
    completed_missions INT DEFAULT 0,
    aborted_missions INT DEFAULT 0,
    error_missions INT DEFAULT 0,
    total_steps_executed INT DEFAULT 0,
    total_duration_seconds FLOAT DEFAULT 0,
    average_duration_seconds FLOAT DEFAULT 0,
    last_mission_id VARCHAR(255),
    last_mission_at DATETIME,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_stats (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Initialize mission statistics with default values
INSERT IGNORE INTO mission_statistics (id, total_missions, completed_missions, aborted_missions, error_missions, total_steps_executed, total_duration_seconds, average_duration_seconds)
VALUES (1, 0, 0, 0, 0, 0, 0, 0);

-- Create a view for easy access to mission counts
CREATE OR REPLACE VIEW mission_counts AS
SELECT 
    COUNT(*) as total_missions,
    SUM(CASE WHEN status = 'complete' THEN 1 ELSE 0 END) as completed_missions,
    SUM(CASE WHEN status = 'aborted' THEN 1 ELSE 0 END) as aborted_missions,
    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_missions,
    SUM(CASE WHEN status = 'executing' THEN 1 ELSE 0 END) as executing_missions,
    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_missions,
    SUM(CASE WHEN status = 'planning' THEN 1 ELSE 0 END) as planning_missions
FROM mission_reports;

