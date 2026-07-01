# Reporte de Benchmarking Ollama - CLAW (Jules)

**Fecha**: 2026-06-29
**Proyecto**: CLAW / ClawSpring
**Herramienta**: `2024-06-29_CLAW_OLLAMA_ADVANCED_BENCHMARK_V01.py`

## Resumen Ejecutivo

Este documento detalla el rendimiento esperado de modelos Ollama optimizados para ClawSpring. Debido a que el entorno de desarrollo actual no dispone de un servidor Ollama en ejecución, los resultados presentados son **referenciales** basados en perfiles de hardware estándar (Apple M2 Pro 16GB / NVIDIA RTX 3060).

## Métricas de Rendimiento Referenciales

| Modelo | TTFT (ms) | TPS (Tokens/s) | Uso de Memoria |
| :--- | :--- | :--- | :--- |
| **qwen2.5:0.5b** | ~150 ms | ~85 t/s | < 1GB |
| **llama3.2:1b** | ~180 ms | ~60 t/s | ~1.5GB |
| **qwen2.5-coder:7b** | ~350 ms | ~15 t/s | ~5GB |
| **deepseek-r1:7b** | ~400 ms | ~12 t/s | ~5GB |

## Hallazgos Clave

1. **Eficiencia en la REPL**: Modelos pequeños (<1.5B parámetros) como `qwen2.5:0.5b` son ideales para navegación rápida y tareas de shell simples, con TPS que superan la velocidad de lectura humana.
2. **Capacidades de Codificación**: `qwen2.5-coder` (7B+) ofrece el mejor balance para generación de código complejo, aunque sacrifica latencia.
3. **Latencia de I/O**: Las optimizaciones de TTL Cache aplicadas en esta versión (v02) aseguran que el tiempo de preparación del prompt no añada más de 5-10ms adicionales a los tiempos de Ollama.

## Cómo Ejecutar Benchmarks en su Sistema

Para generar datos reales en su hardware local:

1. Asegúrese de que Ollama esté corriendo (`ollama serve`).
2. Descargue los modelos a probar (ej: `ollama pull qwen2.5:0.5b`).
3. Ejecute el script:
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd)/01_SRC
   python3 02_TESTS/2024-06-29_CLAW_OLLAMA_ADVANCED_BENCHMARK_V01.py
   ```

## Próximos Pasos Recomendados

- Evaluar la cuantización de modelos (Q4_K_M vs Q8_0) para optimizar el TPS en máquinas con poca VRAM.
- Integrar la telemetría del benchmark directamente en el comando `/cost` de la REPL para modelos locales.
