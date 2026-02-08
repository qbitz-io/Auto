# Auto v1.0

## What is Auto?

Auto is a foundational, self-building AI system designed to autonomously plan, build, validate, and improve software projects using a suite of specialized agents. It leverages advanced language models to orchestrate complex development workflows, enabling users to iteratively build and enhance features through a conversational chat interface.

Auto is not a finished product but a robust base system intended for developers and researchers to fork, customize, and extend according to their unique needs.

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

Auto includes a Guardian system that oversees critical modifications to core files and sensitive operations. When a change requires approval:

- The system will prompt you via the chat interface.
- You can review the proposed changes in detail.
- Approve or reject the changes to control the system's evolution.

This workflow ensures safety and human oversight over the autonomous development process.

---

## ResearchAgent

The ResearchAgent is a specialized agent that autonomously gathers information, explores new ideas, and supports the planning process by providing relevant knowledge and insights. It helps Auto stay informed and make better decisions during feature development.

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

- **Tools:**
  - Base tools for file operations and system interaction.
  - Dynamically generated tools created by the ToolsmithAgent.

- **Build Loop:**
  - Iterative cycle of planning, building, validating, and approval.
  - Continuous improvement and self-enhancement.

- **Frontend:**
  - Next.js UI for monitoring, control, and chat-based interaction.

- **Backend:**
  - FastAPI server exposing APIs for frontend communication.
  - Persistent state management and configuration.

---

## Contributing

This repository contains the locked core of Auto. It is designed to be a stable foundation for others to fork and specialize. 

If you want to extend or customize Auto for your own projects, please fork this repository and build on top of it.

For core improvements or bug fixes, please submit pull requests with detailed explanations.

---

## License

Auto is released under the MIT License. See the LICENSE file for details.

---

## Vision Statement

Auto aims to empower developers and researchers by providing a foundational autonomous AI system that can self-build, self-improve, and adapt to diverse software development needs. It is a stepping stone towards fully autonomous software engineering, enabling rapid innovation and reducing manual overhead.

By open-sourcing this core, we invite the community to collaborate, specialize, and push the boundaries of autonomous AI-driven development.

---

Thank you for exploring Auto. We look forward to seeing what you build with it!