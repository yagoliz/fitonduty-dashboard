#!/bin/bash

source ../.venv/bin/activate 

echo "=== Loading .env ==="
set -a  # Mark variables for export
source .env
set +a  # Unmark

cd .. && python3 main.py