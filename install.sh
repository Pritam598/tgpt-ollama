#!/bin/bash

echo "[+] Installing TGPT..."

# Install Ollama
if ! command -v ollama &> /dev/null
then
    echo "[+] Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Start Ollama
pkill ollama 2>/dev/null
ollama serve &>/dev/null &
sleep 3

# Pull model
echo "[+] Downloading model..."
ollama pull qwen2:1.5b

# Setup Python
python3 -m venv venv 2>/dev/null
source venv/bin/activate

pip install requests >/dev/null

# Make executable
chmod +x tgpt.py

# Global command
sudo ln -sf "$(pwd)/tgpt.py" /usr/local/bin/tgpt

echo ""
echo "[+] Done!"
echo "Run: tgpt -c \"binary search in c\""
