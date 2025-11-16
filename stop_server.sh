#!/bin/bash
# stop_server.sh

PORT=8000
echo "Finding process listening on port $PORT..."
# Use lsof to find the PID. The -t flag gives just the PID.
# The command substitution will be empty if no process is found.
PID=$(lsof -t -i:$PORT)

if [ -n "$PID" ]; then
    echo "Stopping server with PID: $PID"
    kill -9 $PID
    echo "Server stopped."
else
    echo "No process found listening on port $PORT."
fi

# Clean up old pid file if it exists
if [ -f server.pid ]; then
    rm server.pid
fi