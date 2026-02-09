"""Toolsmith agent - creates new LangChain tools when gaps are detected."""
from typing import Dict, Any
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..core import get_llm, state_manager, BuildStep
from ..tools import BASE_TOOLS
import uuid


TOOLSMITH_PROMPT = """You are the Toolsmith agent for a self-building LangChain system.

Your responsibility is to create new LangChain tools when the system needs capabilities not covered by existing tools.

When creating a new tool:
1. Identify the specific capability gap
2. Design a focused, single-purpose tool
3. Use the @tool decorator from langchain_core.tools
4. Add proper type hints and docstrings
5. Handle errors gracefully
6. Make it async if it does I/O
7. Add the tool to the appropriate module

Tool design principles:
- Single responsibility
- Clear input/output contracts
- Descriptive names and docstrings (LLM will read these)
- Type safety
- Error handling

Example tool structure:
```python
from langchain_core.tools import tool

@tool
async def my_new_tool(param: str) -> str:
    \"\"\"Brief description of what the tool does.
    
    Args:
        param: Description of parameter
    
    Returns:
        Description of return value
    \"\"\"
    try:
        # Implementation
        return result
    except Exception as e:
        return f"Error: {{str(e)}}"
```

Save new tools to: backend/tools/custom_tools.py
Update backend/tools/__init__.py to export them

Current tools available: {current_tools}
Generated files: {generated_files}
"""


class ToolsmithAgent:
    """Agent that creates new tools for the system."""
    
    def __init__(self):
        self.llm = get_llm(temperature=0.1)
        self.tools = BASE_TOOLS
        self.agent_executor = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the LangChain agent with tools."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", TOOLSMITH_PROMPT),
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
    
    async def create_tool(self, requirement: str) -> Dict[str, Any]:
        """Create a new tool based on requirements.
        
        Args:
            requirement: Description of the needed capability
        
        Returns:
            Result of tool creation
        """
        if not requirement or not isinstance(requirement, str):
            raise TypeError("Requirement must be a non-empty string")

        # Get current state
        state = await state_manager.get_state()
        
        # Create build step
        step_id = str(uuid.uuid4())
        step = BuildStep(
            id=step_id,
            agent="toolsmith",
            action=f"Create tool: {requirement}",
            status="running"
        )
        await state_manager.add_build_step(step)
        
        try:
            # Run agent
            result = await self.agent_executor.ainvoke({
                "input": f"Create a new LangChain tool for this requirement: {requirement}",
                "current_tools": [tool.name for tool in self.tools],
                "generated_files": state.generated_files,
            })
            
            # Update step
            await state_manager.update_build_step(
                step_id,
                status="completed",
                result=str(result.get("output", ""))
            )
            
            return result
        
        except Exception as e:
            await state_manager.update_build_step(
                step_id,
                status="failed",
                error=str(e)
            )
            raise


# Global toolsmith instance
toolsmith = ToolsmithAgent()
