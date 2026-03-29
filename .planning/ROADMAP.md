# Roadmap: Xander Operator

## Overview

Xander Operator evolves from a prototype to a robust, production-grade autonomous agent platform with comprehensive memory, skills, and orchestration capabilities.

## Phases

- [ ] **Phase 1: Stabilization** - Tests, CI, reliability fixes
- [ ] **Phase 2: Memory** - Improved vector store, retrieval, summarization
- [ ] **Phase 3: Skills** - Standardize skill API, add core skills
- [ ] **Phase 4: Orchestration** - Multi-agent coordination, workflows
- [ ] **Phase 5: Observatory** - Dashboards, logging, metrics

## Phase Details

### Phase 1: Stabilization
**Goal**: Improve reliability and set up development infrastructure
**Depends on**: None
**Success Criteria**:
  1. All core modules have unit tests with >80% coverage
  2. GitHub Actions CI runs tests and lints on pushes
  3. Operator runs 100 iterations without crashing on benchmark task
  4. Configuration validation catches errors early
  5. Contributing guide and security policy are published
**Plans**: 6 plans

Plans:
- [ ] 01-01: Add unit tests for memory layer (FAISS + metadata)
- [ ] 01-02: Add unit tests for skill execution engine
- [ ] 01-03: Configure CI (pytest, ruff, markdown-lint)
- [ ] 01-04: Implement configuration validation on startup
- [ ] 01-05: Run stability benchmark (100 iterations, report failures)
- [ ] 01-06: Profile memory usage, add GC improvements

### Phase 2: Memory
**Goal**: Enhance long-term memory with better retrieval and summarization
**Depends on**: Phase 1
**Success Criteria**:
  1. Memory supports semantic search with embeddings
  2. Automatic summarization caches for old conversations
  3. Memory pruning based on relevance and age
  4. Export/import of memory snapshots
**Plans**: TBD

### Phase 3: Skills
**Goal**: Standardize the skill interface and add 5 core skills
**Depends on**: Phase 2
**Success Criteria**:
  1. Skills conform to a clear contract (input/output schema)
  2. Documentation for skill developers
  3. Built-in skills: web_search, file_read, shell_exec (sandboxed), email, api_call
  4. Skill permission system
**Plans**: TBD

### Phase 4: Orchestration
**Goal**: Multi-agent coordination and workflow definition
**Depends on**: Phase 3
**Success Criteria**:
  1. Operator can spawn sub-agents and manage their lifecycle
  2. Workflow language for sequential and parallel steps
  3. Error recovery and retry policies
**Plans**: TBD

### Phase 5: Observatory
**Goal**: Observability for operators and developers
**Depends on**: Phase 4
**Success Criteria**:
  1. Structured logging (JSON) with levels
  2. Prometheus metrics endpoint
  3. Optional web UI for monitoring active tasks
**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Stabilization | 0/6 | Not started | - |
| 2. Memory | 0 | Not started | - |
| 3. Skills | 0 | Not started | - |
| 4. Orchestration | 0 | Not started | - |
| 5. Observatory | 0 | Not started | - |

---

*Early roadmap — subject to change.*