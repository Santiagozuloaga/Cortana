#!/usr/bin/env python3
"""
Ollama Benchmarking Tool for ClawSpring.
Measures latency and throughput (TPS) for Ollama models.
Supports Mock mode for testing environments without a live Ollama server.
"""
import time
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Generator

# ISO-SAGE nomenclature for results
RESULTS_FILE = "03_DOCS/2026-07-14_CLAW_OLLAMA_BENCHMARKS_RESULTS_V01.json"

class MockOllama:
    """Simulates Ollama API for benchmarking without a local server."""
    def __init__(self, tps=50.0, latency=0.05):
        self.tps = tps
        self.latency = latency

    def generate(self, model: str, prompt: str) -> Generator[Dict[str, Any], None, None]:
        # Simulate initial latency
        time.sleep(self.latency)

        response_text = f"Mock response for {model}: " + "word " * 50
        tokens = response_text.split()

        for i, token in enumerate(tokens):
            # Simulate per-token generation time
            time.sleep(1.0 / self.tps)
            yield {"response": token + " ", "done": i == len(tokens) - 1}

def ollama_generate(model: str, prompt: str, base_url: str = "http://localhost:11434") -> Generator[Dict[str, Any], None, None]:
    """Real Ollama API call using urllib."""
    url = f"{base_url.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")

    with urllib.request.urlopen(req) as response:
        for line in response:
            if line:
                yield json.loads(line.decode("utf-8"))

def run_benchmark(model_name: str, prompt: str, mock: bool = True) -> Dict[str, Any]:
    print(f"Benchmarking model: {model_name} (Mock: {mock})")

    start_time = time.time()
    first_token_time = None
    total_tokens = 0
    full_response = ""

    try:
        if mock:
            provider = MockOllama(tps=45.0, latency=0.1)
            stream = provider.generate(model_name, prompt)
        else:
            stream = ollama_generate(model_name, prompt)

        for chunk in stream:
            if first_token_time is None:
                first_token_time = time.time()

            full_response += chunk.get("response", "")
            total_tokens += 1 # Simplified token count (chunks)

            if chunk.get("done"):
                break
    except Exception as e:
        print(f"  Error during generation: {e}")
        return {"model": model_name, "error": str(e), "mock": mock}

    end_time = time.time()

    total_duration = end_time - start_time
    generation_duration = end_time - first_token_time if first_token_time else 0
    tps = total_tokens / generation_duration if generation_duration > 0 else 0
    ttft = first_token_time - start_time if first_token_time else 0

    return {
        "model": model_name,
        "ttft_ms": round(ttft * 1000, 2),
        "tps": round(tps, 2),
        "total_duration_s": round(total_duration, 2),
        "tokens": total_tokens,
        "mock": mock,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

def main():
    # Try to detect if Ollama is running
    ollama_online = False
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=1) as resp:
            if resp.status == 200:
                ollama_online = True
    except:
        pass

    models = ["qwen2.5:0.5b", "llama3.2:1b", "phi3:mini"]
    prompt = "Explain the P.A.R.A. method in two sentences."

    results = []
    # If Ollama is offline, we force mock=True for the whole run
    use_mock = not ollama_online
    if use_mock:
        print("Ollama server not detected. Running in MOCK mode.")

    for model in models:
        res = run_benchmark(model, prompt, mock=use_mock)
        results.append(res)

    # Ensure 03_DOCS exists
    Path("03_DOCS").mkdir(exist_ok=True)

    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=4)

    print(f"\nBenchmark complete. Results saved to {RESULTS_FILE}")

if __name__ == "__main__":
    main()
