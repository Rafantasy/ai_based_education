#!/bin/bash
# Script to run the AI-based education system with Python 3.8

if [ $# -eq 0 ]; then
    echo "Usage: $0 <student_number>"
    echo "Example: $0 0"
    exit 1
fi

python3.8 main.py "$1"
