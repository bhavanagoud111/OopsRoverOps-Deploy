# Database Query Examples

## How to Connect to the Database

### Option 1: Interactive MySQL Client
```bash
docker exec -it roverops-mysql mysql -uroot -p[YOUR_ROOT_PASSWORD] roverops_db
```

Once connected, you can run SQL queries directly:
```sql
SELECT * FROM mission_counts;
SELECT * FROM mission_statistics;
SELECT * FROM mission_reports ORDER BY created_at DESC LIMIT 10;
```

### Option 2: Run Single Query from Shell
```bash
docker exec roverops-mysql mysql -uroot -p[YOUR_ROOT_PASSWORD] roverops_db -e "SELECT * FROM mission_counts;"
```

### Option 3: Run SQL File
```bash
docker exec -i roverops-mysql mysql -uroot -p[YOUR_ROOT_PASSWORD] roverops_db < your_query.sql
```

## Common Queries

### View Mission Counts
```bash
docker exec roverops-mysql mysql -uroot -p[YOUR_ROOT_PASSWORD] roverops_db -e "SELECT * FROM mission_counts;"
```

### View Mission Statistics
```bash
docker exec roverops-mysql mysql -uroot -p[YOUR_ROOT_PASSWORD] roverops_db -e "SELECT * FROM mission_statistics;"
```

### View All Mission Reports
```bash
docker exec roverops-mysql mysql -uroot -p[YOUR_ROOT_PASSWORD] roverops_db -e "SELECT mission_id, goal, mission_status, steps_completed, total_steps, created_at FROM mission_reports ORDER BY created_at DESC LIMIT 10;"
```

### View Mission Logs for a Specific Mission
```bash
docker exec roverops-mysql mysql -uroot -p[YOUR_ROOT_PASSWORD] roverops_db -e "SELECT timestamp, agent_type, level, message FROM mission_logs WHERE mission_id = 'your-mission-id' ORDER BY timestamp;"
```

### View Mission Status History
```bash
docker exec roverops-mysql mysql -uroot -p[YOUR_ROOT_PASSWORD] roverops_db -e "SELECT mission_id, status, previous_status, changed_at FROM mission_status ORDER BY changed_at DESC LIMIT 10;"
```

### View Mission Steps
```bash
docker exec roverops-mysql mysql -uroot -p[YOUR_ROOT_PASSWORD] roverops_db -e "SELECT mission_id, step_number, action, completed, description FROM mission_steps WHERE mission_id = 'your-mission-id' ORDER BY step_number;"
```

## Quick Reference

**Container Name**: `roverops-mysql`  
**Database**: `roverops_db`  
**Root User**: `root`  
**Root Password**: `[Set in Docker environment]`  
**Port**: `3307` (host) → `3306` (container)

## Troubleshooting

If you get "command not found" errors, remember:
- SQL commands must be run inside MySQL client
- Use `docker exec` to run commands inside the container
- Use `-e` flag to execute SQL directly
- Use `-it` flags for interactive mode

