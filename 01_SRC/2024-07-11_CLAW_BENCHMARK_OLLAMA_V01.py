import time
import json
import os
import sys
import psutil
import urllib.request
import urllib.error
from typing import Dict, List, Any

# Ensure we can import from 01_SRC
sys.path.append("01_SRC")
try:
    import providers
except ImportError:
    # Fallback for different directory structures
    sys.path.append(".")
    import providers

BENCHMARK_PROMPT = "Explain the importance of open-source software in three short paragraphs."

def benchmark_model(model_name: str, base_url: str = "http://localhost:11434") -> Dict[str, Any]:
    print(f"\n--- Benchmarking: {model_name} ---")

    result = {
        "model": model_name,
        "success": False,
        "ttft_s": None,
        "total_time_s": None,
        "tokens_per_sec": None,
        "avg_ram_usage_mb": None,
        "avg_cpu_usage_pct": None,
        "response_quality": "",
        "context_limit": providers.PROVIDERS.get("ollama", {}).get("context_limit", 128000),
        "error": None
    }

    # Prepare request
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": BENCHMARK_PROMPT}],
        "stream": True,
        "options": {"num_ctx": 4096}  # Use a safe default for benchmarking
    }

    headers = {"Content-Type": "application/json"}
    url = f"{base_url.rstrip('/')}/api/chat"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    start_time = time.time()
    ttft = None
    full_response = []

    # Resource tracking
    process = psutil.Process(os.getpid())
    ram_samples = []
    cpu_samples = []

    try:
        response = urllib.request.urlopen(req, timeout=120)

        for line in response:
            line = line.decode("utf-8", errors="replace").strip()
            if not line:
                continue

            chunk = json.loads(line)

            # Record TTFT on first content chunk
            if ttft is None and chunk.get("message", {}).get("content"):
                ttft = time.time() - start_time

            content = chunk.get("message", {}).get("content", "")
            if content:
                full_response.append(content)

            # Sample resources
            ram_samples.append(process.memory_info().rss / (1024 * 1024))
            cpu_samples.append(process.cpu_percent())

            if chunk.get("done"):
                break

        total_time = time.time() - start_time
        response_text = "".join(full_response)

        # Calculate tokens (rough estimate: 4 chars per token)
        token_count = len(response_text) / 4

        result.update({
            "success": True,
            "ttft_s": round(ttft, 3) if ttft else None,
            "total_time_s": round(total_time, 3),
            "tokens_per_sec": round(token_count / total_time, 2) if total_time > 0 else 0,
            "avg_ram_usage_mb": round(sum(ram_samples) / len(ram_samples), 2) if ram_samples else 0,
            "avg_cpu_usage_pct": round(sum(cpu_samples) / len(cpu_samples), 2) if cpu_samples else 0,
            "response_quality": response_text[:200] + "...",
        })

        print(f"  Result: Success | TTFT: {result['ttft_s']}s | Total: {result['total_time_s']}s | Speed: {result['tokens_per_sec']} tok/s")

    except Exception as e:
        result["error"] = str(e)
        print(f"  Result: Failed | Error: {e}")

    return result

def main():
    models_to_test = [
        "qwen2.5:1.5b",
        "qwen2.5:3b",
        "qwen2.5:7b"
    ]

    # Try to detect any other models from providers.py
    for m in providers.PROVIDERS.get("ollama", {}).get("models", []):
        if m not in [mod.split(":")[0] for mod in models_to_test]:
            models_to_test.append(m)

    results = []
    print(f"Starting CLAW Ollama Benchmarks - {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Prompt: {BENCHMARK_PROMPT}")

    for model in models_to_test:
        res = benchmark_model(model)
        results.append(res)

    output_file = f"03_DOCS/2024-07-11_CLAW_OLLAMA_BENCHMARKS_V01.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nBenchmark complete. Results saved to {output_file}")

if __name__ == "__main__":
    main()
