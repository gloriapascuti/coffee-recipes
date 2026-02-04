#!/bin/bash
# Script to run Django server with Groq API key
# 
# IMPORTANT: Set your GROQ_API_KEY environment variable before running this script:
#   export GROQ_API_KEY='your-api-key-here'
# Or add it to your ~/.zshrc or ~/.bash_profile for permanent setup

# Check if API key is set
if [ -z "$GROQ_API_KEY" ]; then
    echo "Error: GROQ_API_KEY environment variable is not set."
    echo "Please set it with: export GROQ_API_KEY='your-api-key-here'"
    echo "Or get a free key at: https://console.groq.com/"
    exit 1
fi

cd "$(dirname "$0")"

# Use the conda environment if available, otherwise use default python
if [ -f "/opt/homebrew/Caskroom/miniconda/base/envs/analiza_works/bin/python" ]; then
    /opt/homebrew/Caskroom/miniconda/base/envs/analiza_works/bin/python manage.py runserver
else
    python manage.py runserver
fi
