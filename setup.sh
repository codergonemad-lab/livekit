#!/bin/bash

# LiveKit Video Calling Backend Setup Script

echo "Setting up LiveKit Video Calling Backend..."

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment (Linux/Mac)
if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
    source venv/bin/activate
# Activate virtual environment (Windows)
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    source venv/Scripts/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file from example
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please update the .env file with your actual configuration values."
fi

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update the .env file with your database and LiveKit configuration"
echo "2. Set up your PostgreSQL database"
echo "3. Run the server with: python main.py"
echo ""
echo "API Documentation will be available at: http://localhost:8000/docs"
