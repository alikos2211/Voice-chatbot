import os
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

if __name__ == "__main__":
    model = os.environ.get("MODEL_NAME", "Qwen/Qwen3.5-0.8B")
    host = os.environ.get("HOST", "0.0.0.0")
    port = os.environ.get("PORT", "8000")
    dtype = os.environ.get("DTYPE", "auto")
    max_len = os.environ.get("MAX_MODEL_LEN", "1024")

    log.info(f"Starting vLLM with model: {model}")

    # Replace this process with `vllm serve` so signals (Ctrl+C, docker stop)
    # go straight to the server.
    os.execvp("vllm", [
        "vllm", "serve", model,
        "--host", host,
        "--port", port,
        "--dtype", dtype,
        "--max-model-len", max_len,
    ])