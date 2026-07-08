"""
Comparative Ollama Benchmarking Script for ClawSpring.

Measures TTFT, TPS, Duration, and Estimated Memory for multiple models.
Usage:
    PYTHONPATH=01_SRC:00_SOPORTE python3 2026-07-07_CLAW_OLLAMA_COMPARATIVE_BENCHMARK_V01.py [model1] [model2] ...
"""

import time
import json
import sys
import os
import urllib.request
import urllib.error
from typing import Dict, List

# Add relevant directories to sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(BASE_DIR, "01_SRC"))
sys.path.append(os.path.join(BASE_DIR, "00_SOPORTE"))

DEFAULT_MODELS = ["gemma:2b", "qwen2.5:0.5b", "llama3.2:1b", "mistral:7b"]

def benchmark_model(model_name: str, base_url: str = "http://localhost:11434") -> Dict:
    prompt = "Write a one-sentence summary of the Python programming language."
    url = f"{base_url.rstrip('/')}/api/chat"

    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")

    print(f"Benchmarking {model_name}...", end="", flush=True)

    start_time = time.perf_counter()
    first_token_time = None
    tokens_count = 0

    try:
        # Use a short timeout for the connection attempt
        with urllib.request.urlopen(req, timeout=10) as response:
            for line in response:
                if not line: continue
                chunk = json.loads(line.decode("utf-8"))
                if first_token_time is None:
                    first_token_time = time.perf_counter()
                if not chunk.get("done"):
                    tokens_count += 1
                else:
                    total_duration = time.perf_counter() - start_time
                    ttft = first_token_time - start_time
                    tps = tokens_count / (total_duration - ttft) if (total_duration - ttft) > 0 else 0
                    print(" Done.")
                    return {
                        "model": model_name,
                        "success": True,
                        "ttft_s": round(ttft, 4),
                        "tps": round(tps, 2),
                        "duration_s": round(total_duration, 4),
                        "tokens": tokens_count,
                        "memory_est_gb": _estimate_memory(model_name)
                    }
    except Exception as e:
        print(f" Failed ({type(e).__name__})")
        # Return simulated data if Ollama is not available, marked as simulated
        return _simulate_benchmark(model_name)

def _estimate_memory(model_name: str) -> float:
    """Rough estimation based on parameter count in name."""
    if "7b" in model_name: return 5.5
    if "3b" in model_name: return 2.5
    if "2b" in model_name: return 1.6
    if "1b" in model_name: return 1.1
    if "0.5b" in model_name: return 0.6
    return 4.0

def _simulate_benchmark(model_name: str) -> Dict:
    """Returns realistic simulated data for a given model type."""
    is_large = "7b" in model_name
    return {
        "model": model_name,
        "success": True,
        "simulated": True,
        "ttft_s": 0.15 if is_large else 0.05,
        "tps": 15.0 if is_large else 120.0,
        "duration_s": 2.5 if is_large else 0.4,
        "tokens": 40,
        "memory_est_gb": _estimate_memory(model_name)
    }

def generate_report(results: List[Dict]):
    print("\n" + "="*80)
    print(f"{'Model':<20} | {'TTFT(s)':<8} | {'TPS':<8} | {'Dur(s)':<8} | {'Mem(GB)':<8} | {'Status'}")
    print("-"*80)
    for r in results:
        status = "Simulated" if r.get("simulated") else "Live"
        print(f"{r['model']:<20} | {r['ttft_s']:<8.4f} | {r['tps']:<8.2f} | {r['duration_s']:<8.4f} | {r['memory_est_gb']:<8.1f} | {status}")
    print("="*80)

def main():
    models = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_MODELS
    results = []
    for m in models:
        results.append(benchmark_model(m))

    generate_report(results)

    report_path = os.path.join(BASE_DIR, "03_DOCS", "2026-07-07_CLAW_OLLAMA_BENCHMARKS_V02.md")
    with open(report_path, "w") as f:
        f.write("# Ollama Comparative Benchmarks\n\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("| Model | TTFT (s) | TPS | Duration (s) | Est. Memory (GB) | Status |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for r in results:
            status = "Simulated" if r.get("simulated") else "Live"
            f.write(f"| {r['model']} | {r['ttft_s']} | {r['tps']} | {r['duration_s']} | {r['memory_est_gb']} | {status} |\n")

    print(f"\nMarkdown report saved to {report_path}")

if __name__ == "__main__":
    main()
