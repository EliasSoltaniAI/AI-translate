#!/bin/bash

# Exit on error
set -e

# Function to run FastAPI
run_fastapi() {
    echo "Starting FastAPI..."
    uvicorn src.main:app --host 0.0.0.0 --port 8000
}

# Function to run Streamlit
run_streamlit() {
    echo "Starting Streamlit..."
    streamlit run src/app/app.py --server.port 8501 --server.address 0.0.0.0
}

# Run both FastAPI and Streamlit
run_fastapi &
run_streamlit &

# Wait for both processes to finish
wait
