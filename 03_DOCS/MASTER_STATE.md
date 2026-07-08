# MASTER STATE - CLAW

## Última Actualización: 2026-07-07 (Performance Update)

## Estado General
El repositorio CLAW_FINAL está organizado bajo el estándar **P.A.R.A.** y utiliza la nomenclatura **ISO-SAGE**. El núcleo del sistema es **ClawSpring v3.05.5**, una implementación minimalista en Python de Claude Code. Se han aplicado optimizaciones de rendimiento significativas.

## Arquitectura
- **00_SOPORTE**: Configuración, dependencias y lanzadores.
- **01_SRC**: Lógica central, proveedores de LLM, memoria y multi-agentes.
- **02_TESTS**: Pruebas unitarias, integradas y benchmarks.
- **03_DOCS**: Documentación técnica, reportes de performance y estados de proyecto.
- **04_ASSETS**: Recursos estáticos.

## Componentes Críticos
- **clawspring.py**: Punto de entrada principal (REPL).
- **providers.py**: Abstracción de múltiples proveedores (Anthropic, OpenAI, Ollama, etc.).
- **thinking.py**: Gestión de capacidades de razonamiento extendido.
- **config.py**: Gestión centralizada de configuración.

## Cambios Recientes (2026-07-07)
- **Optimización de Ejecución**: Implementación de caché de estimación de tokens en `compaction.py`, reduciendo el procesamiento redundante de historial.
- **Caché de Memoria**: Añadido caché TTL (30s) para la carga de entradas de memoria en `memory/store.py`, minimizando el I/O de disco durante sesiones largas.
- **Optimización de Contexto**: Incrementado el TTL de caché de información de Git y CLAUDE.md a 10s para reducir llamadas a subprocesos.
- **Perfilado Empírico**: Realizado análisis completo de cuellos de botella (ver `03_DOCS/2026-07-07_CLAW_BOTTLENECK_ANALYSIS_V01.md`).
- **Benchmarking Comparativo**: Nuevo script de benchmark para múltiples modelos Ollama (ver `03_DOCS/2026-07-07_CLAW_OLLAMA_BENCHMARKS_V02.md`).

## Riesgos Conocidos
- Dependencia de servicios externos (APIs) para funcionalidad completa.
- El entorno de ejecución actual no cuenta con una instancia de Ollama activa para benchmarks reales.
