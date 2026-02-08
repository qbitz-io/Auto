# Auto v1.0.0 - Stable Foundation

## What is Auto?
A self-building AI system that autonomously plans, builds, validates, and improves software through conversational interaction.

## Core Features
✅ Self-building agent pipeline  
✅ Chat-based interface  
✅ FileGuardian protection system  
✅ Human-in-the-loop approvals  
✅ ResearchAgent for live documentation  
✅ Sandbox Garage for isolated Fly.io testing
✅ Scoring System for rigorous code evaluation
✅ GitHub Integration for automated commits and tagging
✅ Fly.io Deployment with health checks and DNS switching
✅ React Native App for mobile interaction
✅ Launcher Service for user instance management

> **🔒 Repository Status: LOCKED CORE v1.0.0**  
> This is the stable foundation. **No PRs accepted.** Fork to extend.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/solight111/CompassAGI-Auto/releases)
[![Forks](https://img.shields.io/github/forks/solight111/CompassAGI-Auto.svg)](https://github.com/solight111/CompassAGI-Auto/network)

---

**To extend Auto:** Fork this repository and build your specialized version.

## Getting Started
See the [README](https://github.com/solight111/CompassAGI-Auto/blob/master/README.md) for setup instructions.

## License
MIT License - See LICENSE file for details.

---

## Prerequisites

Before setting up Auto, ensure you have the following installed:

- **Python 3.11**
- **Node.js** (v16 or higher recommended)
- **pnpm** (for managing frontend dependencies)
- **OpenAI API Key** (for language model access)

---

## Setup Instructions

### Backend Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd compassAGI-Auto/backend
   ```

2. Create and activate a Python 3.11 virtual environment:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY="your_api_key_here"  # On Windows: set OPENAI_API_KEY=your_api_key_here
   ```

5. Run the backend server:
   ```bash
   uvicorn api:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```

2. Install frontend dependencies using pnpm:
   ```bash
   pnpm install
   ```

3. Start the frontend development server:
   ```bash
   pnpm dev
   ```

4. Open your browser and go to `http://localhost:3000` to access the chat interface.

---

## Using the Chat Interface

The chat interface is your primary way to interact with Auto. You can:

- Submit high-level goals or feature requests.
- Monitor the system's planning, building, and validation steps.
- Approve or reject critical changes via the Guardian system.

Auto will decompose your goals into executable steps, build or update code, validate changes, and iterate until the feature is complete.

---

## Guardian System and Approval Workflow

Auto includes a **FileGuardian** that protects core system files from accidental modification:

**Protected files include:**
- All agent files (orchestrator, planner, builder, validator, toolsmith)
- Core tools and API endpoints
- Key frontend components
- Configuration files

When Auto attempts to modify a protected file:
1. The change is queued for approval
2. You review it in the Approvals panel
3. You can approve or deny the change
4. Only approved changes are applied

This ensures Auto cannot break itself without human oversight.

---

## ResearchAgent

The ResearchAgent is a specialized agent that autonomously gathers information, explores new ideas, and supports the planning process by providing relevant knowledge and insights. It helps Auto stay informed and make better decisions during feature development.

---

## Sandbox Garage

The Sandbox Garage system spawns isolated Fly.io clone instances where code changes can be tested safely. It supports iterative building, testing, scoring, and refining until features meet high-quality standards.

---

## Scoring System

Auto evaluates code changes rigorously based on:
- Functionality (4 points)
- Code Quality (2 points)
- Performance (2 points)
- Safety (2 points)

Only code scoring a perfect 10/10 is accepted and committed.

---

## GitHub Integration

When code achieves a 10/10 score, Auto automatically commits changes to GitHub with detailed messages including iteration counts and final scores. It also tags versions appropriately.

---

## Fly.io Deployment

After committing to GitHub, Auto deploys the latest code to a new Fly.io instance, runs health checks, switches DNS to the new instance, and cleans up old instances after a grace period.

---

## React Native App

A mobile app with a single chat interface and approval popups (modal/bottom sheet) connects to the user's Fly.io instance via API key, enabling on-the-go interaction with Auto.

---

## Launcher Service

The Launcher Service provides an API endpoint to spin up new Fly.io instances for users, generate API keys, and return connection details to the mobile app.

---

## Architecture Overview

Auto's architecture consists of:

- **Agents:**
  - *OrchestratorAgent:* Coordinates the overall system workflow.
  - *PlannerAgent:* Breaks down goals into actionable steps.
  - *BuilderAgent:* Writes and updates code files.
  - *ValidatorAgent:* Checks code correctness and quality.
  - *ToolsmithAgent:* Creates new tools to extend capabilities.
  - *ResearchAgent:* Conducts autonomous research to inform planning.
  - *SandboxManagerAgent:* Manages isolated testing environments.
  - *ScoringAgent:* Evaluates code quality and safety.
  - *GitHubAgent:* Handles automated commits and tagging.
  - *FlyioAgent:* Manages Fly.io deployments and health checks.
  - *LauncherAgent:* Provides user instance management API.

- **Tools:**
  - Base tools for file operations and system interaction.
  - Dynamically generated tools created by the ToolsmithAgent.

- **Build Loop:**
  - Iterative cycle of planning, building, validating, scoring, approval, and deployment.
  - Continuous improvement and self-enhancement.

- **Frontend:**
  - Next.js UI for monitoring, control, and chat-based interaction.
  - React Native mobile app for on-the-go access.

- **Backend:**
  - FastAPI server exposing APIs for frontend communication and launcher service.
  - Persistent state management and configuration.

---

## Contributing

## Repository Status: LOCKED CORE

**Version:** 1.0.0 (Stable Foundation)

This repository contains the **minimal, stable core** of Auto. 

### For Users
Fork this repo and build your specialized Auto on top of it.

### For Contributors  
We are **not accepting pull requests** to modify the core. To contribute:
1. Build your enhancement as a fork
2. Share your fork publicly  
3. Document your additions

The core stays minimal by design.

### Critical Bugs Only
Security issues or critical bugs: open an issue and we'll evaluate.

---

## License

Auto is released under the MIT License. See the LICENSE file for details.

---

## Vision Statement

Auto aims to empower developers and researchers by providing a foundational autonomous AI system that can self-build, self-improve, and adapt to diverse software development needs. It is a stepping stone towards fully autonomous software engineering, enabling rapid innovation and reducing manual overhead.

By open-sourcing this core, we invite the community to collaborate, specialize, and push the boundaries of autonomous AI-driven development.

---

Thank you for exploring Auto. We look forward to seeing what you build with it!
