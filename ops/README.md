# Operations - Application Management

This directory contains operational scripts and configurations for managing the BB Agent Manager application.

## Scripts

### startup.sh
**Unified application lifecycle management script**

Handles application startup, shutdown, and management with automatic environment setup.

#### Features
- ✓ Automatic virtual environment creation and activation
- ✓ Dependency installation with caching
- ✓ Port availability checking
- ✓ Graceful startup/shutdown with timeout
- ✓ PID-based process management
- ✓ Health checks and status monitoring
- ✓ Colored output for easy reading
- ✓ Works in Docker and local environments

#### Usage

**Start the application**
```bash
./ops/startup.sh start
```
- Creates/activates .venv
- Installs requirements
- Starts FastAPI on port 8000
- Logs to logs/app.log

**Stop the application**
```bash
./ops/startup.sh stop
```
- Graceful shutdown with 15s timeout
- Force kill if needed
- Cleans up PID file

**Restart the application**
```bash
./ops/startup.sh restart
```
- Stops then starts the application
- 2-second delay between operations

**Check application status**
```bash
./ops/startup.sh status
```
- Shows PID if running
- Runs health check
- Lists available endpoints

**View application logs**
```bash
./ops/startup.sh logs
```
- Shows last 50 lines of logs
- Streams from logs/app.log

**Show help**
```bash
./ops/startup.sh help
```

#### Configuration

**Environment Variables**
```bash
# Specify custom port (default: 8000)
PORT=9000 ./ops/startup.sh start

# Specify custom host (default: 0.0.0.0)
HOST=127.0.0.1 ./ops/startup.sh start

# Both together
PORT=9000 HOST=127.0.0.1 ./ops/startup.sh start
```

#### Examples

```bash
# Start on default port 8000
./ops/startup.sh start

# Check it's running
./ops/startup.sh status

# View logs
./ops/startup.sh logs

# Start on custom port
PORT=8080 ./ops/startup.sh start

# Restart application
./ops/startup.sh restart

# Stop it
./ops/startup.sh stop
```

#### Output

Success case:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Starting BB Agent Manager
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ℹ Checking Python virtual environment...
ℹ Virtual environment exists
✓ Virtual environment activated
ℹ Checking and installing requirements...
✓ Dependencies installed successfully
ℹ Starting FastAPI application on http://0.0.0.0:8000
✓ Application started successfully (PID: 12345)
ℹ API Documentation: http://localhost:8000/docs
ℹ Health Check: http://localhost:8000/health
```

## Docker Integration

The startup.sh script works seamlessly in Docker environments:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN chmod +x ops/startup.sh
CMD ["./ops/startup.sh", "start"]
```

## Process Files

- **.bb-agent.pid** - Process ID file (created at runtime)
- **logs/app.log** - Application output logs

## Directory Structure

```
ops/
├── README.md           # This file
└── startup.sh          # Application lifecycle management
```

## Integration with Services

### Systemd Integration (Linux)

Create `/etc/systemd/system/bb-agent.service`:
```ini
[Unit]
Description=BB Agent Manager
After=network.target

[Service]
Type=simple
User=bbagent
WorkingDirectory=/opt/bb-agent
ExecStart=/opt/bb-agent/ops/startup.sh start
ExecStop=/opt/bb-agent/ops/startup.sh stop
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start with systemd:
```bash
sudo systemctl start bb-agent
sudo systemctl status bb-agent
sudo systemctl logs -f bb-agent
```

### Docker Compose Integration

In `docker-compose.yml`:
```yaml
services:
  bb-agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      PORT: 8000
      HOST: 0.0.0.0
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

## Health Checks

The startup script includes health checks:

```bash
./ops/startup.sh status
```

Manual health check:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "bb-agent-manager",
  "version": "0.1.0"
}
```

## Troubleshooting

### Port Already in Use
```
✗ Port 8000 is already in use
Run 'lsof -i :8000' to see what's using it
```

Solution:
```bash
# Kill process using port
kill -9 $(lsof -ti :8000)

# Or use different port
PORT=8001 ./ops/startup.sh start
```

### Virtual Environment Issues
```bash
# Recreate venv
rm -rf .venv
./ops/startup.sh start
```

### Dependency Issues
```bash
# Clear pip cache and reinstall
rm -rf .venv
pip cache purge
./ops/startup.sh start
```

### Check Logs
```bash
./ops/startup.sh logs

# Follow logs in real-time
tail -f logs/app.log
```

## Performance

Typical startup times:
- First run (with venv + deps): ~60-90 seconds
- Subsequent runs: ~3-5 seconds
- Graceful shutdown: <2 seconds

## Security

- PID file is created with restrictive permissions
- Environment variables from `.env` are loaded automatically
- No hardcoded secrets in script
- Logs contain no sensitive data

## Advanced Usage

### Custom Python Executable
```bash
# Use specific Python version
python3.11 -m venv .venv
./ops/startup.sh start
```

### Multiple Instances
```bash
# Terminal 1 - Default port
./ops/startup.sh start

# Terminal 2 - Alternative port
PORT=8001 ./ops/startup.sh start
```

### Daemonize
```bash
# Run in background
nohup ./ops/startup.sh start &

# With output redirection
./ops/startup.sh start > startup.log 2>&1 &
```

## See Also

- [Architecture Documentation](../devdocs/ARCHITECTURE.md)
- [Development Roadmap](../devdocs/TODO.md)
- [Main README](../README.md)
- [Scripts Directory](../scripts/README.md)
