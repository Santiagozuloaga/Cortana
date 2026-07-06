# MASTER STATE - CLAW

## Última Actualización: 2026-07-06

## Estado General
El repositorio CLAW_FINAL está organizado bajo el estándar **P.A.R.A.** y utiliza la nomenclatura **ISO-SAGE**. El núcleo del sistema es **ClawSpring v3.05.5**, una implementación minimalista en Python de Claude Code.

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

## Cambios Recientes (2026-07-06)
- **Reporte Consolidado**: Generación del reporte de acciones integral y flujo de trabajo de las 11 IAs (`2026-07-06_CLAW_REPORTE_ACCIONES_V01.md`).
- **Fix Bug #7**: Implementación de caché TTL (5s) para variables de entorno en `providers.py` (2026-07-04).
- **Optimización REPL**: Caché de `SubAgentManager` en `clawspring.py` para evitar re-importaciones costosas en el bucle principal (2026-07-04).
- **Git Fix**: Reparación de bucle infinito en el enlace simbólico de `.gitignore` (2026-07-04).
- **Benchmarking**: Creado script estandarizado para pruebas de modelos locales Ollama (2026-07-04).

## Riesgos Conocidos
- Dependencia de servicios externos (APIs) para funcionalidad completa.
- El entorno de ejecución actual no cuenta con una instancia de Ollama activa para benchmarks reales.
