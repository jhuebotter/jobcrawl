#!/bin/bash

# Start backend in background
conda run -n jobcrawl python -m uvicorn backend.src.main:app --reload > server.log 2>&1 &
BACKEND_PID=$!

# Start frontend
npm run dev --prefix frontend &
FRONTEND_PID=$!

# Wait for both
wait $BACKEND_PID $FRONTEND_PID