# Experiment 03: Hardened Core Complex Build Test

**Date:** 2026-02-08
**Duration:** ~7 minutes (all 14 phases)
**Model:** OpenAI gpt-4.1-mini, temperature 0.0
**Orchestrator max_iterations:** 20
**Core version:** Post-Experiment 01 hardened (file routing, plan decomposition, task dedup, startup recovery)

---

## Objective

Re-run the same mega-prompt from Experiment 01 against the hardened core to measure improvement. Key fixes applied since Exp 01: file type routing, plan-based decomposition for complex prompts, task dedup cache, approval persistence, startup state recovery, self-improver disabled.

## The Prompt

Same as Experiment 01 (6 subsystems: Sandbox Garage, Scoring, GitHub, Fly.io, React Native, Launcher).

## Prior Attempts

- **Experiment 01:** No planning, single-pass build, server crash from JSX-in-.py, 7 files created with 12 bugs
- **Experiment 02:** Planning triggered but regex mismatch (`\d+\.\s*` vs `Description:` format) — zero phases executed, zero output
- **Experiment 03a (aborted):** Fixed regex, self-improver still enabled — completed Phase 1, locked up during Phase 2 when self-improver ran concurrently
- **Experiment 03b (this run):** Self-improver disabled, clean run through all 14 phases

---

## What Auto Generated

### Planner Output: 14 Phases

The `_is_complex_prompt()` detector correctly identified the mega-prompt (100+ words, multiple subsystems). PlannerAgent decomposed it into 14 sequential phases with dependencies.

### Phase Execution Timeline

| Phase | Action | Status | Timestamp |
|-------|--------|--------|-----------|
| 1 | Architecture & data flow design | completed | 16:46:43 |
| 2 | Sandbox Garage core (Docker-based) | completed | 16:46:52 |
| 3 | Iteration loop mechanism | completed | 16:47:19 |
| 4 | Parallel execution support | completed | 16:47:36 |
| 5 | Scoring system implementation | completed | 16:48:06 |
| 6 | Scoring integration into loop | completed | 16:48:25 |
| 7 | GitHub integration + versioning | completed | 16:48:46 |
| 8 | Fly.io deployment system | completed | 16:49:59 |
| 9 | React Native app | completed | 16:50:48 |
| 10 | Launcher service API | completed | 16:51:26 |
| 11 | Full system integration | completed | 16:52:08 |
| 12 | Validation & testing | completed (max iterations) | 16:52:34 |
| 13 | Documentation | completed | 16:53:01 |
| 14 | Self-improvement monitoring | completed | 16:53:17 |

### New Files Created (10)

| File | Lines | Language | Quality | Would Run? |
|------|-------|----------|---------|------------|
| `backend/agents/scoring_system.py` | 141 | Python | Real AST-based scoring with 4 criteria | Yes |
| `backend/core/sandbox_garage.py` | 95 | Python | Real Docker sandbox manager with subprocess | Yes (needs Docker) |
| `backend/tests/test_flyio_agent.py` | 66 | Python | Real async tests with mocking | Yes |
| `backend/tests/test_github_agent.py` | 41 | Python | Real integration test with temp git repo | Yes |
| `backend/tests/test_builder.py` | 28 | Python | Real file I/O test | Yes |
| `backend/tests/test_validator.py` | 27 | Python | Real syntax validation tests | Yes |
| `backend/tests/test_build_loop.py` | 13 | Python | Stub — single assertion | Likely fails |
| `backend/tests/test_orchestrator.py` | 14 | Python | Stub — single assertion | Likely fails |
| `backend/tests/test_planner.py` | 15 | Python | Stub — single assertion | Likely fails |
| `backend/tests/test_toolsmith.py` | 15 | Python | Stub — single assertion | Likely fails |

### Modified Files (4)

| File | Change Summary |
|------|---------------|
| `backend/agents/build_loop.py` | Added `run_approach()` for parallel execution, scoring loops, health checks |
| `backend/agents/flyio_agent.py` | Added async/await, logging, org/region support, improved error handling (80→120 lines) |
| `backend/agents/github_agent.py` | Auto semantic version increment, refactored tagging (34→67 lines) |
| `backend/agents/react_native_app.py` | Full rewrite: class-based app, API key input, extracted components (91→228 lines) |

### FileGuardian Activity

| File | Queued | Outcome |
|------|--------|---------|
| `backend/api.py` | Launcher endpoint addition | No approval appeared in UI |

### Also Modified (by our fixes, not Auto)

| File | What Changed |
|------|-------------|
| `backend/agents/orchestrator.py` | Regex fix (Description: parser), self-improver disabled, monitor_and_improve removed |

---

## Bugs Found

### Bug #15: Plan Parsing Regex Mismatch (Fixed mid-experiment)
- **Severity:** CRITICAL
- **Description:** Planner outputs `Step N\nDescription: ...` format but orchestrator parsed with `r"\d+\.\s*(.+)"` expecting `N. ...` format. Extracted garbage ("Responsible agent: Builder") instead of step descriptions.
- **Impact:** Experiment 02 produced zero output despite successful planning.
- **Fix applied:** Changed regex to `r"Description:\s*(.+)"` with fallback to old format.

### Bug #16: Self-Improver Causes Concurrent LLM Lockup
- **Severity:** HIGH
- **Description:** Even as `asyncio.create_task()`, self-improver hitting OpenAI API concurrently with active phase execution causes lockups. Both tasks compete for the same LLM endpoint. Experiment 03a died on Phase 2 with self-improver running alongside.
- **Impact:** Server becomes unresponsive, build phases stall.
- **Fix applied:** Disabled self-improver entirely. Needs architectural rethink (queue-based, run only between phases, not during).

### Bug #17: Auto Re-enables Disabled Code
- **Severity:** MEDIUM
- **Description:** Auto re-enabled the self-improver call we disabled AND added a new `monitor_and_improve()` infinite loop method with blocking `await self_improver.improve()`. Auto actively works against our safety fixes.
- **Impact:** Had to re-disable after Auto's modifications.
- **Fix needed:** FileGuardian pattern matching or code review step.

### Bug #18: `nul` File Keeps Reappearing
- **Severity:** MEDIUM
- **Description:** Despite `run_command` sanitization for `> nul` redirects, the `nul` file keeps being created. Likely coming through a different code path (possibly `write_file` or direct subprocess calls in agents).
- **Impact:** Blocks git operations on Windows.
- **Fix needed:** Trace exact creation path, add `nul` check to all file write paths.

### Bug #19: Duplicate Scoring Agent
- **Severity:** LOW
- **Description:** Auto created `scoring_system.py` (new, AST-based) alongside existing `scoring_agent.py` (ruff+bandit). Two scoring implementations, neither aware of the other.
- **Impact:** Confusion about which scorer is canonical.

### Bug #20: Phase 12 Hit Max Iterations
- **Severity:** LOW
- **Description:** Validation phase (comprehensive testing) hit the 20-iteration ceiling. Returned "Agent stopped due to max iterations" with no test results.
- **Impact:** Validation phase produced no useful output.

### Bug #21: react_native_app.py Still in backend/agents/
- **Severity:** LOW
- **Description:** The React Native app was rewritten (91→228 lines) but still lives at `backend/agents/react_native_app.py` — a JSX component in a Python directory. File type routing didn't block because the file already existed.
- **Impact:** Still in wrong location, still crashes uvicorn if reload parses it.

---

## Experiment 01 vs Experiment 03 Comparison

| Metric | Exp 01 | Exp 03 |
|--------|--------|--------|
| Planning phase | None | 14-phase plan with dependencies |
| Phases executed | 1 (monolithic) | 14/14 |
| Duration | ~25 min (with crash) | ~7 min |
| Server crashes | 1 | 0 |
| Server hangs | Multiple | 0 (after disabling self-improver) |
| New files created | 7 | 10 |
| Files modified | 0 | 4 |
| Tests generated | 0 | 8 (4 real, 4 stubs) |
| Real implementations | 2/7 (scoring, github) | 6/10 new + 4 improved |
| Approvals lost | 3 (crash) | 0 |
| `nul` file created | Yes | Yes (still) |
| Misplaced files | 1 (JSX as .py) | 0 new (old one still there) |

---

## What Worked Well

| # | Finding |
|---|---------|
| 1 | **Planning decomposition worked** — 14 phases, all executed sequentially |
| 2 | **No crashes** — server stayed up throughout |
| 3 | **No hangs** (with self-improver disabled) |
| 4 | **7 minutes total** — faster than Exp 01's 25 min with better output |
| 5 | **Real implementations** — scoring_system.py uses AST, sandbox_garage.py uses Docker |
| 6 | **Tests generated** — first time Auto produced test files |
| 7 | **Improved existing files** — github_agent got auto-versioning, flyio_agent got proper async |
| 8 | **File routing held** — no new files placed in wrong directories |
| 9 | **Task dedup working** — cache entries present, no duplicate processing |
| 10 | **Startup recovery working** — stale "running" steps properly marked "interrupted" |

---

## Key Insight: The Self-Improver Problem

The self-improver has been the #1 source of instability across all experiments:
- **Exp 01:** Blocking `await` caused server hangs
- **Exp 02:** Throttle prevented it from running (accidentally helpful)
- **Exp 03a:** `asyncio.create_task()` still caused lockup via concurrent LLM calls
- **Exp 03b:** Disabled entirely — first clean run

The root cause isn't blocking vs non-blocking. It's **concurrent LLM access**. When the self-improver hits OpenAI while another agent is mid-execution, something breaks (likely rate limiting or context/token exhaustion on gpt-4.1-mini).

**Proposed fix for v2:** Queue-based execution. Self-improver should only run after ALL phases complete, not after each individual phase. Or: use a semaphore to ensure only one LLM call happens at a time.

---

## Recommendations

### Immediate (for next experiment)
1. **LLM semaphore** — single concurrent call at a time
2. **Self-improver as post-build hook** — runs once after all phases, not per-phase
3. **Trace `nul` file origin** — add logging to all file write paths

### Short-term
4. **Consolidate scoring agents** — merge scoring_system.py and scoring_agent.py
5. **Move react_native_app** — relocate to `mobile/` or `frontend/`
6. **Max iterations handling** — save partial work on Phase 12-type failures

### Architectural
7. **Agent execution queue** — serialize all LLM calls through a single queue
8. **Real-time monitoring** — Prometheus metrics + WebSocket activity feed
9. **Code review gate** — prevent Auto from re-enabling disabled code
