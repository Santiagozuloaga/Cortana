# Ollama Benchmarking - Technical Note

## Environment Limitations

In the current development/sandbox environment, benchmarking of Ollama models could not be executed due to:
- The Ollama service not being installed or running on `localhost:11434`.
- Lack of access to local GPU/CPU resources required for running LLMs via Ollama.

## Execution Instructions

To run these benchmarks in a real environment (where Ollama is installed and models are downloaded):

1. **Ensure Ollama is running**:
   ```bash
   ollama serve
   ```

2. **Pull the required models**:
   ```bash
   ollama pull qwen2.5:0.5b
   ollama pull llama3.2:1b
   ```

3. **Execute the benchmark script**:
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd)/01_SRC
   python3 02_TESTS/2024-06-19_CLAW_OLLAMA_BENCHMARK_V01.py
   ```

4. **Verify results**:
   The results will be saved to `03_DOCS/2024-06-19_CLAW_OLLAMA_BENCHMARKS_V01.json`.

## Cold vs. Warm Execution

The benchmark script is designed to measure:
- **Cold execution**: First run of a model (includes loading time into VRAM).
- **Warm execution**: Subsequent runs (measured via TTFT and TPS metrics).

The script `02_TESTS/2024-06-19_CLAW_OLLAMA_BENCHMARK_V01.py` contains the logic to capture these metrics once a connection to the Ollama API is established.
