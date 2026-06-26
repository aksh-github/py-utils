#!/bin/bash
# Run both scheduler and serve_stock_file in parallel

python -u src/scheduler.py &
SCHEDULER_PID=$!

python -u src/scripts/serve_stock_file.py &
SERVE_PID=$!

# Keep the container running and handle termination gracefully
wait $SCHEDULER_PID $SERVE_PID
