#!/bin/bash
# Start FastAPI backend server
port=${1:-8000}

uvicorn main:app --host 0.0.0.0 --port $port --reload
