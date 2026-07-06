# MERGE PLAN — Proyecto CLAW

**Fecha**: 2026-07-06  
**Objetivo**: Planificar integración de cambios sin modificar código  
**Estado Actual**: Repositorio local sin remoto, sin conflictos de merge activos

---

## 1. Resumen de Estado para Merge

### 1.1 Situación Actual

| Elemento | Estado | Acción Requerida |
|----------|--------|------------------|
| Remote Git | No configurado | Configurar antes de cualquier merge |
| Ramas locales | 2 (master + rama temporal) | Consolidar en master |
| Conflictos de merge activos | Ninguno | N/A |
| Duplicidad de archivos | 7 carpetas espejo + archivos | Limpieza previa recomendada |

### 1.2 Premisas del Plan

1. **NO se modificará código fuente** (solo operaciones Git y documentación)
2. **Prioridad a estándar ISO-SAGE**: Versiones con fecha son canónicas
3. **Preservar trabajo de Jules**: Todos sus fixes ya están en la versión actual
4. **Validar antes de eliminar**: Verificar imports antes de remover duplicados

---

## 2. Estrategia de Merge por Escenario

### Escenario A: Conexión a Remoto Restaurada

**Precondición**: `git remote add origin https://github.com/Santiagozuloaga/claw`

#### Paso 1: Fetch del estado remoto
```bash
git fetch origin --all
```

#### Paso 2: Análisis de divergencia
```bash
git log --oneline --graph --all master origin/master
git diff master..origin/master --stat
```

#### Paso 3: Clasificación de commits remotos

Una vez obtenido el historial remoto, clasificar cada commit por tipo:

| Tipo | Criterio de Clasificación | Ejemplo de Mensaje |
|------|--------------------------|---------------------|
| **documentación** | Cambios en .md, README, docs | "docs: update README", "Add contributor guide" |
| **refactor** | Reorganización sin cambio funcional | "refactor: apply P.A.R.A. structure" |
| **rendimiento** | Optimizaciones, caching, lazy loading | "perf: REPL startup optimization" |
| **bugs** | Fixes de errores reportados | "fix: Bug #7 env cache", "fix: UTF-8 encoding" |
| **arquitectura** | Cambios estructurales mayores | "arch: implement shims for ISO-SAGE" |
| **cambios funcionales** | Nuevas features, comportamiento | "feat: voice pipeline phase 2" |

#### Paso 4: Estrategia de Merge

| Situación | Comando | Riesgo |
|-----------|---------|--------|
| Fast-forward posible | `git merge origin/master` | Bajo |
| Commits divergentes | `git merge --no-commit origin/master` | Medio (requiere revisión) |
| Conflictos detectados | `git merge --abort` + análisis manual | Alto |

---

### Escenario B: Sin Remoto (Estado Actual)

**Situación**: Solo existen ramas locales apuntando al mismo commit

#### Paso 1: Eliminar rama temporal
```bash
git checkout master
git branch -d qwen-code-a657ce75-86c9-4a53-b181-ae1d1fd13616
```

#### Paso 2: Crear tag de referencia
```bash
git tag -a v3.05.5-jules-complete -m "Jules optimization complete - P.A.R.A. + ISO-SAGE applied"
```

---

## 3. Plan de Resolución de Duplicados

### 3.1 Fase Pre-Merge: Auditoría de Imports

**Objetivo**: Identificar qué archivos duplicados son referenciados activamente

#### Script de auditoría (solo lectura):
```bash
# Buscar imports que usan rutas no-canónicas
grep -r "from mcp\." 01_SRC/ --include="*.py"
grep -r "from memory\." 01_SRC/ --include="*.py"
grep -r "from task\." 01_SRC/ --include="*.py"
# ... repetir para cada carpeta espejo
```

**Criterio de decisión**:
- Si hay imports activos → Mantener symlink o actualizar imports
- Si no hay imports → Eliminar carpeta no-canónica

### 3.2 Fase Post-Merge: Limpieza

| Carpeta | Versión Canónica | Acción si sin imports |
|---------|------------------|----------------------|
| `01_SRC/mcp/` | `01_SRC/2024-06-19_CLAW_MCP_V01/` | Eliminar |
| `01_SRC/memory/` | `01_SRC/2024-06-19_CLAW_MEMORY_PACKAGE_V01/` | Eliminar |
| `01_SRC/multi_agent/` | `01_SRC/2024-06-19_CLAW_MULTI_AGENT_V01/` | Eliminar |
| `01_SRC/plugin/` | `01_SRC/2024-06-19_CLAW_PLUGIN_V01/` | Eliminar |
| `01_SRC/skill/` | `01_SRC/2024-06-19_CLAW_SKILL_V01/` | Eliminar |
| `01_SRC/task/` | `01_SRC/2024-06-19_CLAW_TASK_V01/` | Eliminar |
| `01_SRC/voice/` | `01_SRC/2024-06-19_CLAW_VOICE_V01/` | Eliminar |

---

## 4. Decisiones Humanas Requeridas

### D1: Destino del directorio `claw-code/`

**Opciones**:
- A) Eliminar (si es backup obsoleto)
- B) Integrar como submódulo (si es versión paralela)
- C) Mover a `04_ASSETS/` como archivo histórico

**Información necesaria**:
- ¿Contiene código activo?
- ¿Es una versión anterior completa?
- ¿Tiene algo que no esté en `01_SRC/`?

**Recomendación preliminar**: Opción C (mover a assets) hasta verificar contenido

---

### D2: Archivos en raíz fuera de P.A.R.A.

**Archivos identificados**:
- `README.md` → ¿Mover a `03_DOCS/` o mantener en raíz (estándar GitHub)?
- `2024-06-19_CLAW_EXPLICACION_SESION_V01.md` → `03_DOCS/`
- `2024-06-19_CLAW_INFORME_FASE2_V01.md` → `03_DOCS/`
- `CLAUDE_C_ENTREGA_COMPLETA.zip` → ¿Eliminar o `04_ASSETS/`?
- `run_claw_traceback.txt` → Eliminar (debug temporal)

**Decisión requerida**: ¿Mantener README.md en raíz por convención GitHub?

**Recomendación**: 
- README.md → Mantener en raíz (convención GitHub)
- Otros .md → Mover a `03_DOCS/`
- .zip → Evaluar contenido antes de decidir

---

### D3: Symlinks vs Imports Directos

**Situación actual**: Jules creó symlinks para compatibilidad

**Opciones**:
- A) Mantener symlinks (compatibilidad máxima)
- B) Eliminar symlinks y actualizar todos los imports a nombres ISO-SAGE
- C) Híbrido: symlinks solo para módulos críticos

**Trade-offs**:
| Opción | Ventaja | Desventaja |
|--------|---------|------------|
| A | Sin breaking changes | Complejidad de mantenimiento |
| B | Código limpio y explícito | Requiere actualizar muchos archivos |
| C | Balance | Decidir qué es "crítico" es subjetivo |

**Recomendación**: Opción A a corto plazo, planificar migración a B

---

## 5. Rollback Plan

En caso de problemas post-merge:

### Nivel 1: Deshacer merge reciente
```bash
git reset --hard HEAD~1
```

### Nivel 2: Restaurar desde tag conocido
```bash
git checkout v3.05.5-jules-complete
```

### Nivel 3: Recuperar archivos eliminados
```bash
# Si se eliminaron duplicados prematuramente
git checkout <commit-hash> -- 01_SRC/mcp/
```

### Punto de Restauración Crítico
Antes de cualquier eliminación de duplicados:
```bash
git tag pre-cleanup-audit
```

---

## 6. Checklist Pre-Merge

### Obligatorio
- [ ] Remote Git configurado y verificado
- [ ] Backup del estado actual (tag creado)
- [ ] Auditoría de imports completada
- [ ] Lista de archivos a eliminar documentada

### Recomendado
- [ ] Tests ejecutados y aprobados
- [ ] Documentación actualizada
- [ ] Equipo notificado (si hay colaboración)

### Validación Post-Merge
- [ ] `git status` limpio
- [ ] Tests pasan
- [ ] Imports críticos funcionan
- [ ] Documentación accesible

---

## 7. Cronograma Estimado

| Fase | Duración | Dependencias |
|------|----------|--------------|
| Configuración remote | 5 min | Acceso a GitHub |
| Fetch y análisis | 10-30 min | Tamaño del repo remoto |
| Auditoría de imports | 15 min | Ninguna |
| Decisiones humanas | Variable | Disponibilidad del usuario |
| Ejecución de merge | 5 min | Decisiones tomadas |
| Limpieza de duplicados | 30 min | Auditoría completada |
| Validación final | 15 min | Tests disponibles |

**Total estimado**: 1.5 - 2 horas (excluyendo tiempo de decisión humana)

---

## 8. Matriz de Responsabilidades

| Tarea | Responsable | Aprobación Requerida |
|-------|-------------|---------------------|
| Configurar remote | Usuario/Admin | N/A |
| Ejecutar merge | Jules/Usuario | Usuario |
| Decidir sobre duplicados | Usuario | N/A |
| Validar tests | Opal/Usuario | Usuario |
| Actualizar docs | Copilot Gemini/Usuario | Sage |

---

*Documento de planificación - Ejecución pendiente de configuración de remote y decisiones humanas*
