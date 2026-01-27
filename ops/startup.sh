#!/bin/bash

################################################################################
# BB Agent Manager - Startup Script
# 
# Unified script for application lifecycle management
# Supports: start, stop, restart, status
# Works in Docker and local development environments
#
# Usage:
#   ./ops/startup.sh start    # Start application on port 8000
#   ./ops/startup.sh stop     # Stop running application
#   ./ops/startup.sh restart  # Restart application
#   ./ops/startup.sh status   # Check application status
################################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="${PROJECT_ROOT}/.venv"
PID_FILE="${PROJECT_ROOT}/.bb-agent.pid"
PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}
LOG_FILE="${PROJECT_ROOT}/logs/app.log"

# Create logs directory if it doesn't exist
mkdir -p "${PROJECT_ROOT}/logs"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

################################################################################
# Virtual Environment Setup
################################################################################

setup_venv() {
    print_info "Checking Python virtual environment..."
    
    if [ ! -d "$VENV_PATH" ]; then
        print_info "Creating virtual environment at $VENV_PATH..."
        python3 -m venv "$VENV_PATH"
        print_success "Virtual environment created"
    else
        print_info "Virtual environment exists"
    fi
}

activate_venv() {
    if [ -f "$VENV_PATH/bin/activate" ]; then
        source "$VENV_PATH/bin/activate"
        print_success "Virtual environment activated"
    else
        print_error "Failed to activate virtual environment"
        exit 1
    fi
}

install_requirements() {
    print_info "Checking and installing requirements..."
    
    local requirements_file="${PROJECT_ROOT}/requirements.txt"
    
    if [ ! -f "$requirements_file" ]; then
        print_error "requirements.txt not found at $requirements_file"
        exit 1
    fi
    
    # Upgrade pip first
    print_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel > /dev/null 2>&1
    
    # Install requirements
    print_info "Installing dependencies from requirements.txt..."
    pip install -r "$requirements_file" > /dev/null 2>&1
    
    print_success "Dependencies installed successfully"
}

################################################################################
# Application Control
################################################################################

check_port_available() {
    if lsof -i ":$PORT" > /dev/null 2>&1; then
        return 1  # Port in use
    else
        return 0  # Port available
    fi
}

start_application() {
    print_header "Starting BB Agent Manager"
    
    # Check if already running
    if [ -f "$PID_FILE" ]; then
        local existing_pid=$(cat "$PID_FILE")
        if kill -0 "$existing_pid" 2>/dev/null; then
            print_warning "Application is already running (PID: $existing_pid)"
            return 0
        fi
    fi
    
    # Check port availability
    if ! check_port_available; then
        print_error "Port $PORT is already in use"
        echo "Run 'lsof -i :$PORT' to see what's using it"
        exit 1
    fi
    
    # Setup virtual environment
    setup_venv
    activate_venv
    install_requirements
    
    # Start application
    print_info "Starting FastAPI application on http://$HOST:$PORT"
    print_info "Logging to: $LOG_FILE"
    
    # Run uvicorn in background
    cd "$PROJECT_ROOT"
    
    nohup python -m uvicorn \
        test_server:app \
        --host "$HOST" \
        --port "$PORT" \
        --reload \
        --log-level info \
        > "$LOG_FILE" 2>&1 &
    
    local app_pid=$!
    echo "$app_pid" > "$PID_FILE"
    
    # Wait a moment for startup
    sleep 2
    
    # Check if process is still running
    if kill -0 "$app_pid" 2>/dev/null; then
        print_success "Application started successfully (PID: $app_pid)"
        print_info "API Documentation: http://localhost:$PORT/docs"
        print_info "Health Check: http://localhost:$PORT/health"
        
        # Show first few lines of log
        print_info "Recent logs:"
        tail -5 "$LOG_FILE" | sed 's/^/  /'
    else
        print_error "Failed to start application"
        print_error "Last 20 lines of log:"
        tail -20 "$LOG_FILE" | sed 's/^/  /'
        rm -f "$PID_FILE"
        exit 1
    fi
}

stop_application() {
    print_header "Stopping BB Agent Manager"
    
    if [ ! -f "$PID_FILE" ]; then
        print_warning "No PID file found - application may not be running"
        return 0
    fi
    
    local pid=$(cat "$PID_FILE")
    
    if ! kill -0 "$pid" 2>/dev/null; then
        print_warning "Process $pid is not running"
        rm -f "$PID_FILE"
        return 0
    fi
    
    print_info "Stopping application (PID: $pid)..."
    
    # Try graceful shutdown first
    kill "$pid" 2>/dev/null || true
    
    # Wait for graceful shutdown
    local count=0
    while [ $count -lt 15 ] && kill -0 "$pid" 2>/dev/null; do
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill if still running
    if kill -0 "$pid" 2>/dev/null; then
        print_warning "Graceful shutdown timeout, force killing..."
        kill -9 "$pid" 2>/dev/null || true
    fi
    
    rm -f "$PID_FILE"
    print_success "Application stopped"
}

restart_application() {
    print_header "Restarting BB Agent Manager"
    stop_application
    sleep 2
    start_application
}

check_status() {
    print_header "Application Status"
    
    if [ ! -f "$PID_FILE" ]; then
        print_warning "Application is not running"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    
    if kill -0 "$pid" 2>/dev/null; then
        print_success "Application is running (PID: $pid)"
        
        # Check if port is responding
        if command -v curl > /dev/null; then
            if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
                print_success "Health check passed"
                print_info "Available endpoints:"
                echo "  • API Docs: http://localhost:$PORT/docs"
                echo "  • Health: http://localhost:$PORT/health"
                echo "  • Chat: http://localhost:$PORT/agent/chat"
            else
                print_warning "Health check failed (server may still be starting)"
            fi
        fi
        return 0
    else
        print_error "Process $pid is not running"
        rm -f "$PID_FILE"
        return 1
    fi
}

show_logs() {
    print_header "Application Logs"
    
    if [ ! -f "$LOG_FILE" ]; then
        print_warning "Log file not found: $LOG_FILE"
        return 1
    fi
    
    print_info "Last 50 lines of $LOG_FILE:"
    tail -50 "$LOG_FILE"
}

show_help() {
    cat << EOF
${BLUE}BB Agent Manager - Application Control Script${NC}

${BLUE}Usage:${NC}
    $(basename "$0") <command> [options]

${BLUE}Commands:${NC}
    start       Start the application
    stop        Stop the application
    restart     Restart the application
    status      Check application status
    logs        Show application logs
    help        Show this help message

${BLUE}Options:${NC}
    PORT=8080   Specify port (default: 8000)
    HOST=0.0.0.0 Specify host (default: 0.0.0.0)

${BLUE}Examples:${NC}
    ./ops/startup.sh start
    ./ops/startup.sh status
    ./ops/startup.sh restart
    PORT=9000 ./ops/startup.sh start
    ./ops/startup.sh logs

${BLUE}Documentation:${NC}
    See devdocs/ARCHITECTURE.md for more information

EOF
}

################################################################################
# Main Script
################################################################################

main() {
    local command=${1:-help}
    
    case "$command" in
        start)
            start_application
            ;;
        stop)
            stop_application
            ;;
        restart)
            restart_application
            ;;
        status)
            check_status
            ;;
        logs)
            show_logs
            ;;
        help)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
