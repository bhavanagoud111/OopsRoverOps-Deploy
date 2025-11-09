# RoverOps Database Schema

## Database: `roverops_db`
**Container**: `roverops-mysql`  
**Port**: 3307  
**Credentials**:
- Root User: `root`
- Root Password: `[Set in Docker environment]`
- Database: `roverops_db`
- User: `roverops_user`
- Password: `[Set in Docker environment]`

## Tables Created

### 1. `mission_reports`
Stores comprehensive mission reports with all details.

**Columns**:
- `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `mission_id` (VARCHAR(255), UNIQUE, NOT NULL)
- `goal` (TEXT, NOT NULL)
- `status` (VARCHAR(50), DEFAULT 'complete')
- `start_time` (DATETIME, NOT NULL)
- `end_time` (DATETIME)
- `duration_seconds` (FLOAT)
- `steps_completed` (INT, DEFAULT 0)
- `total_steps` (INT, DEFAULT 0)
- `rover_final_position_x` (INT, DEFAULT 0)
- `rover_final_position_y` (INT, DEFAULT 0)
- `outcome` (TEXT)
- `summary` (TEXT)
- `collected_data` (JSON)
- `mission_photos` (JSON)
- `apod_data` (JSON)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**Indexes**:
- `idx_mission_id` on `mission_id`
- `idx_status` on `status`
- `idx_created_at` on `created_at`

### 2. `mission_logs`
Stores all mission logs from different agents.

**Columns**:
- `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `mission_id` (VARCHAR(255), NOT NULL)
- `timestamp` (DATETIME, NOT NULL)
- `agent_type` (VARCHAR(50), NOT NULL)
- `message` (TEXT, NOT NULL)
- `level` (VARCHAR(20), DEFAULT 'info')
- `data` (JSON)
- `created_at` (TIMESTAMP)

**Indexes**:
- `idx_mission_id` on `mission_id`
- `idx_timestamp` on `timestamp`
- `idx_agent_type` on `agent_type`
- `idx_level` on `level`

### 3. `mission_status`
Tracks mission status changes over time.

**Columns**:
- `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `mission_id` (VARCHAR(255), NOT NULL)
- `status` (VARCHAR(50), NOT NULL)
- `previous_status` (VARCHAR(50))
- `changed_at` (DATETIME, NOT NULL)
- `changed_by` (VARCHAR(50), DEFAULT 'system')
- `notes` (TEXT)
- `created_at` (TIMESTAMP)

**Indexes**:
- `idx_mission_id` on `mission_id`
- `idx_status` on `status`
- `idx_changed_at` on `changed_at`

### 4. `mission_steps`
Stores individual mission steps with their details.

**Columns**:
- `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `mission_id` (VARCHAR(255), NOT NULL)
- `step_number` (INT, NOT NULL)
- `action` (VARCHAR(100), NOT NULL)
- `target_position_x` (INT)
- `target_position_y` (INT)
- `description` (TEXT)
- `completed` (BOOLEAN, DEFAULT FALSE)
- `nasa_image_url` (VARCHAR(500))
- `completed_at` (DATETIME)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**Indexes**:
- `idx_mission_id` on `mission_id`
- `idx_step_number` on `step_number`
- `idx_completed` on `completed`

### 5. `mission_statistics`
Tracks overall mission statistics and counts.

**Columns**:
- `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `total_missions` (INT, DEFAULT 0)
- `completed_missions` (INT, DEFAULT 0)
- `aborted_missions` (INT, DEFAULT 0)
- `error_missions` (INT, DEFAULT 0)
- `total_steps_executed` (INT, DEFAULT 0)
- `total_duration_seconds` (FLOAT, DEFAULT 0)
- `average_duration_seconds` (FLOAT, DEFAULT 0)
- `last_mission_id` (VARCHAR(255))
- `last_mission_at` (DATETIME)
- `updated_at` (TIMESTAMP)

## Views

### `mission_counts`
Provides easy access to mission counts by status.

**Columns**:
- `total_missions`
- `completed_missions`
- `aborted_missions`
- `error_missions`
- `executing_missions`
- `pending_missions`
- `planning_missions`

## Usage Examples

### Connect to Database
```bash
docker exec -it roverops-mysql mysql -uroot -p[YOUR_ROOT_PASSWORD] roverops_db
```

### Query Mission Counts
```sql
SELECT * FROM mission_counts;
```

### Query Mission Statistics
```sql
SELECT * FROM mission_statistics;
```

### Query All Mission Reports
```sql
SELECT mission_id, goal, status, steps_completed, total_steps, created_at 
FROM mission_reports 
ORDER BY created_at DESC;
```

### Query Mission Logs
```sql
SELECT mission_id, timestamp, agent_type, level, message 
FROM mission_logs 
WHERE mission_id = 'your-mission-id' 
ORDER BY timestamp;
```

### Query Mission Status History
```sql
SELECT mission_id, status, previous_status, changed_at, changed_by 
FROM mission_status 
WHERE mission_id = 'your-mission-id' 
ORDER BY changed_at;
```

## Current Status

✅ All tables created successfully  
✅ Mission statistics initialized  
✅ Mission counts view created  
✅ Database ready for use

