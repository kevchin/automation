#!/bin/bash

echo "Setting up JIRA Automation Environment"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "pip is not installed. Installing..."
    python3 -m ensurepip --upgrade
fi

# Install required packages
echo "Installing required packages..."
pip install -r requirements.txt

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit .env file with your JIRA credentials:"
    echo "  nano .env"
fi

echo "Setup complete!"
echo ""
echo "To use the JIRA automation tools:"
echo "1. Edit the .env file with your JIRA credentials"
echo "2. Run the example: python example_usage.py"
echo "3. Or use the CLI: python cli.py --help"