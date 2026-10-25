# ADR-001: FastAPI instead of Spring Boot for the backend

- **Status:** Accepted
- **Date:** 2026-10-25
- **Deciders:** Vish

## Context
We need a REST API that parses CSVs, talks to Postgres, calls an LLM through LangChain
and runs a tool-calling agent. The original brief framed this as "on AWS Lambda". After
ADR-002 it runs in a container, but the framework choice still matters. Spring Boot is
very common in banks, so it's a fair question for a fintech portfolio.

## Options considered

| | **FastAPI (Python 3.12)** | **Spring Boot (Java 21)** |
|---|---|---|
| LLM / agent ecosystem | LangChain, LangGraph, Ollama clients are Python-first | LangChain4j / Spring AI exist but are younger, with fewer examples |
| Validation & API docs | Pydantic models give validation + OpenAPI `/docs` for free | Bean Validation + springdoc; more setup |
| Speed to build (3 days, new developer) | Little boilerplate; one file can be a working endpoint | More structure (controllers, services, beans, config) before the first endpoint |
| Startup / footprint | Fast startup, small image | Slower JVM startup (matters on Lambda), bigger image |
| Data work (stats, CSV) | `csv`, `decimal`, `statistics` built in; plus SQL | Fine, but more verbose |
| Bank industry fit | Common in data/ML teams in banks | Very common in core banking services |

## Decision
Use **FastAPI**. The project centres on LLM + data work, where Python's ecosystem is
strongest, and the 3-day timebox favours less boilerplate.

## Consequences
- ✅ Typed request/response models (Pydantic) double as documentation and validation.
- ✅ Same language for the API, data generator, eval script and agent.
- ❌ The portfolio doesn't show Java/Spring skills. **Interview answer:** "I chose
  Python because of the LLM ecosystem and the timebox. The architecture (layers,
  migrations, typed schemas, tests) carries over directly to Spring Boot."
- Risk: Python's dynamic typing → mitigated with type hints, Pydantic and ruff.
