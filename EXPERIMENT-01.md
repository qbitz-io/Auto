# Experiment 01: Complex Multi-System Build Test

**Date:** 2026-02-08
**Duration:** ~25 minutes (including crash recovery)
**Model:** OpenAI gpt-4.1-mini, temperature 0.0
**Orchestrator max_iterations:** 20

---

## Objective

Give Auto ONE massive prompt to build an entire production system and observe what happens. The goal is to identify limitations, bugs, and areas for improvement in the v1.0 core.

## The Prompt

```
Build a complete production system with these capabilities:

SANDBOX GARAGE: Create a system that spawns isolated Fly.io clone instances where you can
test code changes. Implement an iteration loop that builds a feature, tests it, scores it
0-10, and refines until it achieves 10/10. Use multiple approaches in parallel if needed.

SCORING SYSTEM: Evaluate code based on: functionality (4pts), code quality (2pts),
performance (2pts), and safety (2pts). Only accept 10/10 scores.

GITHUB INTEGRATION: When code scores 10/10, automatically commit to GitHub with detailed
messages including iteration count and final score. Tag versions appropriately.

FLY.IO DEPLOYMENT: After GitHub commit, spawn new Fly.io instance, pull latest code, run
health checks, switch DNS to new instance, cleanup old instance after grace period.

REACT NATIVE APP: Create a mobile app with single chat interface and approval popups
(modal/bottom sheet). App connects to user's Fly instance via API key.

LAUNCHER SERVICE: Build API endpoint that spins up new Fly instances for users, generates
API keys, returns connection details to app.

Build whatever agents, tools, and infrastructure you need to make this production-ready.
```

---

## What Auto Generated

### Files Created (7 total)

| File | Lines | Language | Purpose |
|------|-------|----------|---------|
| `backend/agents/sandbox_manager.py` | 62 | Python | Fly.io sandbox spawning (stubs) |
| `backend/agents/scoring_agent.py` | 44 | Python | Code scoring 0-10 (always returns 10) |
| `backend/agents/github_agent.py` | 36 | Python | Git commit/tag/push via subprocess |
| `backend/agents/flyio_agent.py` | 53 | Python | Fly.io deployment (stubs, duplicate of sandbox_manager) |
| `backend/agents/launcher_agent.py` | 40 | Python | FastAPI router for user instance launching |
| `backend/agents/build_loop.py` | 69 | Python | Iteration loop orchestrating all agents |
| `backend/agents/react_native_app.py` | 91 | **JSX** | React Native chat UI (**wrong file extension**) |

### FileGuardian Approvals Triggered (3)

| File | Reason | Outcome |
|------|--------|---------|
| `backend/api.py` | Add launcher endpoints | **Lost on crash** |
| `frontend/components/ChatInterface.tsx` | Update chat UI | **Lost on crash** |
| `backend/agents/toolsmith.py` | Modify core agent | **Lost on crash** |

---

## Bugs Identified (12)

### Critical

#### Bug #12: Approvals Not Persisted
- **Severity:** CRITICAL
- **Description:** FileGuardian stores approvals in an in-memory Python dict (`self._approvals`). When the server crashed (Bug #2), all 3 pending approvals were permanently lost with no way to recover them.
- **Impact:** Defeats the entire purpose of the approval system. Auto can effectively bypass FileGuardian by crashing its own server.
- **Fix:** Persist approvals to `approvals.json` or add to `system_state.json`.

### High

#### Bug #1: No Planning Phase
- **Severity:** HIGH
- **Description:** The orchestrator handled the entire mega-prompt in a single pass. The PlannerAgent was never invoked to decompose the task into phases or identify dependencies between subsystems.
- **Impact:** No task prioritization, no dependency tracking, no parallel execution strategy.
- **Fix:** Force planner invocation for prompts above a complexity threshold.

#### Bug #2: File Extension Blindness
- **Severity:** HIGH (caused server crash)
- **Description:** Auto wrote JSX/React Native code into a `.py` file (`backend/agents/react_native_app.py`). Uvicorn's `--reload` watcher detected the new `.py` file, tried to parse JSX as Python, and crashed the server.
- **Impact:** Server crash, loss of pending approvals, interrupted self_improver run.
- **Fix:** BuilderAgent needs a file type routing system — map language to correct extension and target directory.

#### Bug #3: Directory Blindness
- **Severity:** HIGH
- **Description:** React Native code was placed in `backend/agents/` instead of a `mobile/` or `frontend/` directory. The builder doesn't understand project structure conventions.
- **Impact:** Wrong location for generated code, contributed to the crash.
- **Fix:** Project structure awareness — route files to correct directories based on language and purpose.

#### Bug #9: Stale Running State After Crash
- **Severity:** HIGH
- **Description:** When the server crashed mid-execution, the self_improver build step remained stuck at `"status": "running"` in `system_state.json` forever. No cleanup mechanism exists.
- **Impact:** Misleading state data, potential for agents to think a task is still active.
- **Fix:** Implement startup state recovery — mark stale "running" steps as "interrupted" on boot.

### Medium

#### Bug #4: Rubber Stamp Scoring
- **Severity:** MEDIUM
- **Description:** `scoring_agent.py` has `_check_code_quality()` and `_check_safety()` that both unconditionally `return True`. Every piece of code scores 10/10 automatically.
- **Impact:** The entire iteration/refinement loop (the core value proposition) never executes.
- **Fix:** Implement real scoring using AST analysis, linting (ruff/pylint), and security scanning (bandit).

#### Bug #5: Code Duplication
- **Severity:** MEDIUM
- **Description:** `sandbox_manager.py` and `flyio_agent.py` are nearly identical — same in-memory dict pattern, same `asyncio.sleep()` stubs, same interface. Two files doing the same thing.
- **Impact:** Wasted generation, inconsistent interfaces, maintenance burden.
- **Fix:** Deduplication awareness — check existing files before generating similar ones.

#### Bug #6: Broken Imports
- **Severity:** MEDIUM
- **Description:** `build_loop.py` uses `from backend.agents import orchestrator, scoring_agent, ...` — an absolute import path that won't resolve when running from within `backend/`.
- **Impact:** File would crash at runtime if imported.
- **Fix:** Import path awareness — understand relative vs absolute imports based on project structure.

#### Bug #10: Duplicate Prompt Processing
- **Severity:** MEDIUM
- **Description:** The same mega-prompt was processed twice by the orchestrator (12:43 and 12:55). No deduplication or idempotency check.
- **Impact:** Wasted API calls (OpenAI tokens), duplicate work, second run hit max_iterations with no useful output.
- **Fix:** Task dedup — hash recent prompts, reject or warn on duplicates.

#### Bug #11: Silent Max Iterations Failure
- **Severity:** MEDIUM
- **Description:** The second orchestrator run hit the 20-iteration ceiling and returned `"Agent stopped due to max iterations."` with no useful output or partial results.
- **Impact:** OpenAI tokens spent with nothing to show for it.
- **Fix:** Better max_iterations handling — save partial work, report what was accomplished, suggest breaking the task down.

#### Bug #13: Windows Reserved Filename
- **Severity:** MEDIUM
- **Description:** Auto created a file literally called `nul` in the repo root. On Windows, `nul` is a reserved device name — Git cannot add it to the index, blocking all commits.
- **Impact:** `git add -A` fails with `fatal: adding files failed`. Entire repo becomes uncommittable until the file is manually removed from WSL.
- **Fix:** File path sanitization — reject Windows reserved names (nul, con, prn, aux, com1-9, lpt1-9) in the write_file tool.

### Low

#### Bug #7: Incomplete Output
- **Severity:** LOW
- **Description:** The orchestrator mentioned creating a React Native app in its response but the actual file was a single component, not a scaffolded project. No `package.json`, no app entry point, no navigation.
- **Impact:** Misleading completion message.
- **Fix:** Output validation — verify claims match generated files.

#### Bug #8: No Capability Registration
- **Severity:** LOW
- **Description:** Auto generated 7 new files but didn't register any of them in the `capabilities` array in `system_state.json`. The state still shows only the original 9 capabilities.
- **Impact:** System doesn't know about its own new components.
- **Fix:** Auto-register new files as capabilities when they're written.

---

## What Worked Well

| # | Finding | Significance |
|---|---------|--------------|
| 1 | **FileGuardian blocked correctly** | Protected `api.py`, `ChatInterface.tsx`, `toolsmith.py` from modification |
| 2 | **Created 6 functional agent files** | Correct Python patterns, proper class structure, reasonable interfaces |
| 3 | **Self-aware limitations** | Orchestrator's response correctly listed "next steps" acknowledging gaps |
| 4 | **Research agent triggered** | Attempted to research unfamiliar APIs (Fly.io, React Native) |
| 5 | **Self-improver auto-ran** | Triggered doc sync after orchestrator completed |
| 6 | **GitHub agent structurally correct** | Real `subprocess.run` git commands that would actually work |
| 7 | **Launcher used proper FastAPI patterns** | APIRouter with correct endpoint structure |
| 8 | **Async patterns used correctly** | All agents used proper async/await throughout |

---

## Code Quality Analysis

| File | Structural Quality | Functional Quality | Would Run? |
|------|-------------------|-------------------|------------|
| `sandbox_manager.py` | Good class structure | All stubs (asyncio.sleep) | Yes (does nothing real) |
| `scoring_agent.py` | Clean interface | Always returns 10/10 | Yes (useless) |
| `github_agent.py` | Correct subprocess usage | Would actually commit/push | Yes (dangerous) |
| `flyio_agent.py` | Good async pattern | Duplicate of sandbox_manager | Yes (does nothing real) |
| `launcher_agent.py` | Proper FastAPI router | Hardcoded dummy values | Yes (returns fake data) |
| `build_loop.py` | Good loop structure | Wrong import path | No (ImportError) |
| `react_native_app.py` | Valid React Native JSX | Wrong file type and location | No (not Python) |

---

## Timeline

| Time | Event |
|------|-------|
| 12:43:44 | Prompt submitted via chat interface |
| 12:43:44 | Orchestrator starts processing |
| ~12:44:30 | 6 Python agent files written to `backend/agents/` |
| ~12:44:45 | 3 FileGuardian approval requests queued (api.py, ChatInterface.tsx, toolsmith.py) |
| ~12:45:00 | JSX written as `react_native_app.py` |
| 12:45:42 | Orchestrator completes, self_improver starts |
| ~12:45:50 | Uvicorn detects new .py file, triggers reload |
| ~12:45:51 | **SERVER CRASH** — Python can't parse JSX |
| 12:55:41 | Server restarted, prompt re-processed (duplicate) |
| ~12:56:00 | Second run hits max_iterations (20), returns nothing useful |
| 13:06:01 | Self_improver triggered again |
| ~13:10:00 | Server stabilized, approvals confirmed lost |

---

## Recommendations for v2.0 Core

### Priority 1 (Must Fix)
1. **Persist approvals to disk** — JSON file alongside system_state.json
2. **File type routing** — Language → extension + target directory mapping
3. **Pre-write validation** — Syntax check BEFORE writing, not after
4. **Startup state recovery** — Clean up stale "running" states on boot

### Priority 2 (Should Fix)
5. **Force planner for complex prompts** — Complexity detection → mandatory decomposition
6. **Real scoring system** — AST analysis, linting, security scanning
7. **Import path awareness** — Relative vs absolute based on project structure
8. **Task deduplication** — Hash-based dedup for recent prompts

### Priority 3 (Nice to Have)
9. **Capability auto-registration** — Track new files in state automatically
10. **Deduplication detection** — Warn when generating similar files
11. **Max iterations handling** — Save partial work, report progress
12. **Output validation** — Verify generated files match completion claims

---

## Conclusion

Auto v1.0 successfully demonstrates the core concept: an AI system that can analyze a complex prompt, generate multiple agent files with correct patterns, protect core files via FileGuardian, and self-improve after each task. However, it lacks the robustness needed for production use.

The most critical finding is **Bug #12**: the approval system — the primary safety mechanism — doesn't survive server restarts. Combined with Auto's ability to crash its own server (Bug #2), this creates a path where safety checks are effectively bypassed.

The second most important finding is the **absence of planning** (Bug #1). Auto treated a 6-subsystem architecture as a single task, producing shallow scaffolding instead of deep, iterative implementation. A proper planning phase would decompose this into manageable chunks, each built and validated before moving on.

These are all fixable. The foundation is solid — the architecture works, the patterns are correct, and the safety concepts are right. The implementation just needs hardening.

**This experiment provides the roadmap for v2.0.**
