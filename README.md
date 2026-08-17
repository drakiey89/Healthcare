# Healthcare

## Ollama setup

To run local LLM inference with [Ollama](https://ollama.com), install it with:

```bash
./scripts/install-ollama.sh
```

This wraps the official install command (`curl -fsSL https://ollama.com/install.sh | sh`) with an idempotency check so it's safe to re-run.
