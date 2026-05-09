#!/bin/bash
set -e

echo "========================================"
echo " StreamVault AI Insights — Startup"
echo "========================================"

# Check for .env
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found. Copy .env.example to .env and add your ANTHROPIC_API_KEY."
    exit 1
fi

if grep -q "your_anthropic_api_key_here" .env; then
    echo "ERROR: Please set your ANTHROPIC_API_KEY in .env"
    exit 1
fi

echo ""
echo "▶  Starting Backend (FastAPI)..."
cd backend
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || true
pip install -r requirements.txt -q
cp ../.env .env 2>/dev/null || true
uvicorn app.main:app --port 8000 --reload &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
cd ..

echo ""
echo "▶  Starting Frontend (React)..."
cd frontend
npm install -q
npm run dev &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
cd ..

echo ""
echo "========================================"
echo " ✅ Running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "========================================"
echo ""
echo " Press Ctrl+C to stop both servers"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
