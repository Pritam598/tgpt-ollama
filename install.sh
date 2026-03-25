#!/bin/bash

echo "[+] Installing TGPT (Ollama version)..."

# ---------- CHECK OLLAMA ----------
if ! command -v ollama &> /dev/null
then
    echo "[+] Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# ---------- START OLLAMA ----------
echo "[+] Starting Ollama..."
pkill ollama 2>/dev/null
ollama serve &>/dev/null &

sleep 3

# ---------- PULL FAST MODEL ----------
echo "[+] Downloading model (qwen:0.5b)..."
ollama pull qwen:0.5b

# ---------- PYTHON ENV ----------
echo "[+] Setting up Python environment..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null

# ---------- FIX PERMISSIONS ----------
chmod +x tgpt.py

# ---------- GLOBAL COMMAND ----------
echo "[+] Creating global command..."
sudo ln -sf "$(pwd)/tgpt.py" /usr/local/bin/tgpt

# ---------- DONE ----------
echo ""
echo "[+] Done! Run:"
echo "tgpt \"hello\""
