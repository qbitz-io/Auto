"""Orchestrator agent - the core agent responsible for planning and coordination."""
from typing import List, Dict, Any, AsyncIterator, Optional
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from ..core import get_llm, state_manager, BuildStep, SystemCapability
from ..tools import BASE_TOOLS
from .self_improver import self_improver
from .researcher import ResearchAgent
from .planner import PlannerAgent, planner
import uuid
import re
import hashlib


ORCHESTRATOR_PROMPT = """You are the Orchestrator agent for a self-building LangChain system.

Your responsibilities:
1. Analyze the current system state and identify missing or broken components
2. Plan build steps to implement missing capabilities
3. Coordinate specialized agents (Planner, Builder, Validator, Toolsmith)
4. Track progress and ensure system coherence
5. Decide when the system is complete (no more deltas)

Current system state:
- Project root: {project_root}
- Backend root: {backend_root}
- Generated files: {generated_files}
- Capabilities: {capabilities}

You have access to tools for:
- Reading and writing files
- Listing directories
- Validating Python syntax
- Running commands
- Checking system state

When analyzing the system:
1. Check what files exist
2. Compare against required architecture
3. Identify gaps (missing agents, tools, or infrastructure)
4. Generate or update code to fill gaps
5. Validate changes

Required system architecture:
- backend/agents/: PlannerAgent, BuilderAgent, ValidatorAgent, ToolsmithAgent
- backend/tools/: base_tools.py and any dynamically generated tools
- backend/core/: config.py, state.py, llm.py
- backend/memory/: persistent state storage
- backend/main.py: entry point
- backend/api.py: FastAPI server
- frontend/: Next.js UI

Work systematically. Generate complete, executable code. No placeholders or TODOs.
"""


class OrchestratorAgent:
    """The core orchestrator agent that manages the self-building process."""
    
    def __init__(self):
        self.llm = get_llm()
        self.tools = BASE_TOOLS
        self.agent_executor = None
        self.research_agent = ResearchAgent()
        self.planner_agent = planner
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the LangChain agent with tools."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", ORCHESTRATOR_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=20,
            handle_parsing_errors=True
        )

    def _detect_unfamiliar_apis(self, text: str) -> List[str]:
        """Detect unfamiliar APIs or libraries mentioned in the text.
        For demonstration, we check for known libraries and return those not recognized.
        """
        known_libs = set(self.research_agent.DOC_SITES.keys())
        # Simple regex to find words that look like library names (alphanumeric and dots)
        candidates = set(re.findall(r"\b[a-zA-Z0-9_.]+\b", text.lower()))
        # Filter candidates to those that look like known libs or common libs
        # For demo, consider any candidate not in known_libs as unfamiliar
        unfamiliar = [lib for lib in candidates if lib not in known_libs and len(lib) > 2]
        # Limit to a few
        return unfamiliar[:3]

    async def _research_apis(self, apis: List[str]) -> Dict[str, List[str]]:
        """Use ResearchAgent to fetch documentation snippets for given APIs."""
        results = {}
        for api in apis:
            # For demo, try to search in all supported docs
            snippets = []
            for lib in self.research_agent.DOC_SITES.keys():
                try:
                    found = self.research_agent.search(lib, api, max_results=2)
                    if found:
                        snippets.extend([f"[{lib}] {s}" for s in found])
                except Exception:
                    continue
            results[api] = snippets
        return results

    def _is_complex_prompt(self, prompt: str) -> bool:
        """Detect if the prompt is complex based on criteria:
        - 100+ words
        - Mentions multiple subsystems
        - Contains phrases like 'build a complete system'
        """
        word_count = len(prompt.split())
        if word_count >= 100:
            return True
        subsystems = ["agents", "tools", "core", "frontend", "backend", "api", "main entry point"]
        subsystems_mentioned = sum(1 for s in subsystems if s in prompt.lower())
        if subsystems_mentioned >= 2:
            return True
        if re.search(r"build a complete system", prompt.lower()):
            return True
        return False

    async def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run the orchestrator with a specific task.
        
        Args:
            task: The task description
            context: Additional context for the agent
        
        Returns:
            Agent execution result
        """
        # Hash the task prompt
        task_hash = hashlib.sha256(task.encode('utf-8')).hexdigest()

        # Check cache for recent result
        cached_result = await state_manager.get_cached_result(task_hash)
        if cached_result is not None:
            return {"output": cached_result, "cached": True}

        # Get current state
        state = await state_manager.get_state()
        
        # Prepare context
        from ..core import settings
        full_context = {
            "project_root": str(settings.project_root),
            "backend_root": str(settings.backend_root),
            "generated_files": state.generated_files,
            "capabilities": [cap.model_dump() for cap in state.capabilities],
        }
        
        if context:
            full_context.update(context)

        # Detect unfamiliar APIs in the task
        unfamiliar_apis = self._detect_unfamiliar_apis(task)
        if unfamiliar_apis:
            research_results = await self._research_apis(unfamiliar_apis)
            # Add research results to context
            full_context["research_results"] = research_results

        # Detect if task is complex
        if self._is_complex_prompt(task):
            # Use PlannerAgent to decompose into phases
            plan_result = await self.planner_agent.plan(task)
            plan_output = plan_result.get("output", "")

            # Parse plan output to extract phases
            # For simplicity, assume plan output is a numbered list of steps
            phases = re.findall(r"\d+\.\s*(.+)", plan_output)

            aggregated_results = []
            for phase in phases:
                # Execute each phase sequentially
                phase_result = await self.run(phase, context=full_context)
                aggregated_results.append({"phase": phase, "result": phase_result})

            # Aggregate results into a summary
            summary = "\n".join([f"Phase: {r['phase']}\nResult: {r['result'].get('output', '')}" for r in aggregated_results])

            # Cache the aggregated summary
            await state_manager.add_cached_result(task_hash, summary)

            return {"output": summary, "phases_executed": len(phases)}

        # Create build step
        step_id = str(uuid.uuid4())
        step = BuildStep(
            id=step_id,
            agent="orchestrator",
            action=task,
            status="running"
        )
        await state_manager.add_build_step(step)
        
        try:
            # Run agent
            result = await self.agent_executor.ainvoke({
                "input": task,
                **full_context
            })
            
            output_str = str(result.get("output", ""))

            # Update step
            await state_manager.update_build_step(
                step_id,
                status="completed",
                result=output_str
            )

            # Cache the result
            await state_manager.add_cached_result(task_hash, output_str)
            
            # TODO: Re-enable as non-blocking background task instead of blocking post-task hook
            # await self_improver.improve("Sync documentation with new capabilities and improvements.")
            
            return result
        
        except Exception as e:
            # Update step with error
            await state_manager.update_build_step(
                step_id,
                status="failed",
                error=str(e)
            )
            raise

    async def analyze_system(self) -> Dict[str, Any]:
        """Analyze current system state and identify gaps.
        
        Returns:
            Analysis results with identified gaps
        """
        return await self.run(
            "Analyze the current system state. List all files in backend/ and frontend/. "
            "Identify which required components are missing or incomplete. "
            "Return a structured analysis of what needs to be built."
        )
    
    async def build_missing_components(self) -> Dict[str, Any]:
        """Build or update missing system components.
        
        Returns:
            Build results
        """
        return await self.run(
            "Based on the required architecture, generate any missing files. "
            "Start with the most critical components: agents, then API, then main entry point. "
            "Write complete, executable code for each file."
        )
    
    async def validate_system(self) -> Dict[str, Any]:
        """Validate the current system state.
        
        Returns:
            Validation results
        """
        return await self.run(
            "Validate all Python files in the backend. "
            "Check syntax and ensure imports are correct. "
            "Report any issues found."
        )


# Global orchestrator instance
orchestrator = OrchestratorAgent()
