# ADR-006: Local LLM via Ollama instead of a hosted API

- **Status:** Accepted
- **Date:** 2026-10-25
- **Deciders:** Vish
- **Changes stack:** LLM provider: Anthropic API → **Ollama** (local), via `langchain-ollama`.

## Context
The original plan used a hosted LLM through LangChain. The budget is now **$0**, and the
Anthropic API has no permanent free tier. The LLM is needed for (1) categorizing unknown
merchants, (2) phrasing anomaly explanations and (3) the tool-calling agent.
Vish's laptop: **16 GB RAM, no GPU.**

## Options considered

| | **A. Ollama (local open model)** | **B. Hosted free tier (e.g. Gemini, Groq)** |
|---|---|---|
| Cost | $0 forever | $0 within rate limits that can change |
| Privacy | Data never leaves the machine | Sent to a third party; free tiers may use prompts for training |
| Setup | One Docker service + a one-time model download (several GB) | API key sign-up |
| Speed | Slower on CPU | Fast |
| Quality / tool calling | Good for small classification; weaker agents at small sizes | Stronger models |
| Works offline / in CI | Yes (CI uses a fake LLM anyway) | No |

## Decision
**A. Ollama**, as a `ollama` service in Docker Compose, using LangChain's `ChatOllama`.

**Model sizing for 16 GB RAM / CPU only:**
- Docker Desktop on Windows gives its Linux VM a share of the RAM (by default about half), and
  Postgres + API + web need ~1–2 GB of it.
- **Default:** a ~7–8B instruct model with tool-calling support, 4-bit quantized
  (~5 GB RAM), e.g. `qwen2.5:7b`. It's better at structured output and tool calls, which the
  agent needs (risk R-05).
- **Fallback:** a ~3B model (~2–3 GB), e.g. `qwen2.5:3b` or `llama3.2:3b`, if the 7B is too slow
  (first upload > 120 s, NFR-08).
- The model is set by the `OLLAMA_MODEL` env var, so switching is a config change. The
  exact tag is confirmed in US-01 (check that it's available in Ollama's library) and measured in
  the agent spike (Sprint 2).

## Consequences
- ✅ $0, private, works offline: a strong privacy story for a banking interview.
- ✅ The "no amounts to the LLM" rule still applies (defence in depth), even though the model is local.
- ❌ CPU inference is slow → mitigated by rules-first (most rows never reach the LLM),
  batching (≤ 20 merchants per call), caching, and the background job (ADR-007).
- ❌ The first `docker compose up` downloads several GB → documented in the README; the model
  is kept in a named volume.
- ❌ If the laptop can't run it, the app still works without the LLM (NFR-10).
