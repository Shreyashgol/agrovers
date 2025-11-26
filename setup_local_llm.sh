# #!/bin/bash

# echo "🚀 Setting up Local LLM for Argovers Soil Assistant"
# echo "=================================================="

# # Check if Ollama is installed
# if ! command -v ollama &> /dev/null; then
#     echo "📦 Installing Ollama..."
#     curl -fsSL https://ollama.com/install.sh | sh
#     echo "✅ Ollama installed"
# else
#     echo "✅ Ollama already installed"
# fi

# # Start Ollama service (if not running)
# echo ""
# echo "🔄 Starting Ollama service..."
# ollama serve > /dev/null 2>&1 &
# sleep 3

# # Pull a good model for Hindi/English (Mistral 7B is excellent)
# echo ""
# echo "📥 Downloading Mistral 7B model (this may take a few minutes)..."
# echo "   Model size: ~4.1GB"
# ollama pull mistral

# echo ""
# echo "✅ Setup complete!"
# echo ""
# echo "Test the model:"
# echo "  ollama run mistral 'Hello, how are you?'"
# echo ""
# echo "Next steps:"
# echo "  1. Update backend/.env with: LLM_PROVIDER=ollama"
# echo "  2. Restart backend"
# echo "  3. Test the app!"
