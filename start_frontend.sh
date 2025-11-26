#!/bin/bash
# Start frontend on port 5174

cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start dev server on port 5174
echo " Starting frontend on http://localhost:5174"
npm run dev
