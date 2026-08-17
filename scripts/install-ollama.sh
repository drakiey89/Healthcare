#!/usr/bin/env bash
# Installs Ollama (https://ollama.com) for local LLM inference.
set -euo pipefail

if command -v ollama >/dev/null 2>&1; then
  echo "Ollama is already installed: $(ollama --version)"
  exit 0
fi

echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

echo "Ollama installed: $(ollama --version)"
