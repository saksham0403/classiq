#!/bin/bash
# Script to start Ollama for ClassIQ LLM feedback

echo "🚀 Starting Ollama for ClassIQ..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed."
    echo "Install it with: brew install ollama"
    exit 1
fi

# Check if Ollama is already running
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is already running"
    models=$(curl -s http://localhost:11434/api/tags | python3 -c "import json, sys; data = json.load(sys.stdin); print(', '.join([m.get('name', '') for m in data.get('models', [])]))" 2>/dev/null || echo "unknown")
    echo "   Models available: $models"
    exit 0
fi

# Start Ollama in background
echo "Starting Ollama server..."
ollama serve > /tmp/ollama.log 2>&1 &
OLLAMA_PID=$!

# Wait for it to start
sleep 3

# Check if it's running
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama started successfully (PID: $OLLAMA_PID)"
    echo "📝 Logs: /tmp/ollama.log"
    echo ""
    echo "To stop Ollama: kill $OLLAMA_PID"
    echo "Or use: brew services stop ollama"
else
    echo "❌ Failed to start Ollama. Check /tmp/ollama.log"
    exit 1
fi

