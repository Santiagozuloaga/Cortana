"""
[2024-06-19]_[CLAW]_[OLLAMA_BENCHMARKS]_V01.py

Benchmarking utility for Ollama models in ClawSpring.
Measures Time To First Token (TTFT) and Tokens Per Second (TPS).

Usage:
    python 02_TESTS/2024-06-19_CLAW_OLLAMA_BENCHMARKS_V01.py [--model NAME] [--simulate]
"""

import time
import json
import sys
import os
import argparse
import urllib.request
import urllib.error

def run_benchmark(model_name, base_url="http://localhost:11434", simulate=False):
    print(f"Benchmarking model: {model_name} (Simulate: {simulate})")

    if simulate:
        # Realistic simulated values for a small model like qwen2.5:0.5b
        time.sleep(0.5)  # Simulate some processing
        return {
            "model": model_name,
            "success": True,
            "total_duration_s": 0.42,
            "ttft_s": 0.045,
            "tokens_per_second": 165.0,
            "total_tokens": 62,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "simulated": True
        }

    url = f"{base_url.rstrip('/')}/api/chat"
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "Write a short poem about AI."}],
        "stream": True
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

        start_time = time.perf_counter()
        first_token_time = None
        tokens_count = 0

        with urllib.request.urlopen(req, timeout=30) as response:
            for line in response:
                if not line: continue
                chunk = json.loads(line.decode("utf-8"))
                if first_token_time is None:
                    first_token_time = time.perf_counter()

                if not chunk.get("done"):
                    tokens_count += 1
                else:
                    end_time = time.perf_counter()
                    total_duration = end_time - start_time
                    ttft = first_token_time - start_time
                    # TPS calculation: tokens after the first one divided by the time after TTFT
                    tps_time = total_duration - ttft
                    tps = (tokens_count - 1) / tps_time if tps_time > 0 else 0

                    return {
                        "model": model_name,
                        "success": True,
                        "total_duration_s": round(total_duration, 4),
                        "ttft_s": round(ttft, 4),
                        "tokens_per_second": round(tps, 2),
                        "total_tokens": tokens_count,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "simulated": False
                    }
    except Exception as e:
        return {"model": model_name, "success": False, "error": str(e)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen2.5:0.5b")
    parser.add_argument("--simulate", action="store_true", help="Run in simulation mode if Ollama is unavailable")
    args = parser.parse_args()

    # Try real first, fallback to simulate if requested and real fails
    result = run_benchmark(args.model, simulate=False)
    if not result["success"] and args.simulate:
        print(f"Real benchmark failed ({result.get('error')}), falling back to simulation...")
        result = run_benchmark(args.model, simulate=True)

    print(json.dumps(result, indent=2))

    output_path = f"03_DOCS/2024-06-19_CLAW_OLLAMA_BENCHMARKS_{args.model.replace(':', '_')}_V01.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    main()
