#!/bin/bash
# start_server.sh

# Ensure any previous server is stopped
if [ -f server.pid ]; then
    echo "Stopping existing server..."
    kill $(cat server.pid)
    rm server.pid
    sleep 2
fi

echo "Starting server in background..."
# Clear the log file for the new session
> server.log
# Run the server, redirect output, run in background, and get its PID
conda run -n jobcrawl python run_server.py > server.log 2>&1 &
PID=$!

# Save the PID to a file
echo $PID > server.pid

echo "Server started with PID: $PID"
echo "Logs are being written to server.log"