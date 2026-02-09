"""DuplicateConsolidator agent - detects and consolidates duplicate implementations."""
import os
import difflib
import asyncio
from typing import List, Dict, Any, Tuple
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..core import get_llm, state_manager, BuildStep
from ..tools import BASE_TOOLS
import uuid


DUPLICATE_CONSOLIDATOR_PROMPT = """You are the DuplicateConsolidator agent for a self-building LangChain system.

Your responsibility is to detect and consolidate duplicate implementations in the codebase.

Tasks:
1. Identify files with similar names, signatures, or purposes.
2. Analyze which implementation is more complete.
3. Consolidate automatically by merging or replacing duplicates.

When consolidating:
- Preserve the most complete and correct implementation.
- Update imports and references accordingly.
- Remove redundant files.
- Update system state to reflect changes.

Output format:
- List of detected duplicates
- Consolidation actions taken

Current generated files: {generated_files}
"""


class DuplicateConsolidatorAgent:
    """Agent that detects and consolidates duplicate implementations."""

    def __init__(self):
        self.llm = get_llm(temperature=0.1)
        self.tools = BASE_TOOLS
        self.agent_executor = None
        self._initialize_agent()

    def _initialize_agent(self):
        """Initialize the LangChain agent with tools."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", DUPLICATE_CONSOLIDATOR_PROMPT),
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

    async def _read_file_content(self, file_path: str) -> str:
        """Read file content asynchronously."""
        read_tool = next((t for t in self.tools if t.name == "read_file"), None)
        if not read_tool:
            raise RuntimeError("read_file tool not found")
        content = await read_tool.arun(file_path=file_path)
        return content

    async def _list_similar_files(self, files: List[str]) -> List[Tuple[str, str]]:
        """Identify pairs of files with similar names or purposes."""
        similar_pairs = []
        # Simple heuristic: files with same base name ignoring suffixes or extensions
        base_names = {}
        for f in files:
            base = os.path.splitext(os.path.basename(f))[0]
            # Normalize base by removing trailing digits or common suffixes
            base_norm = base.rstrip('0123456789_').lower()
            if base_norm in base_names:
                similar_pairs.append((base_names[base_norm], f))
            else:
                base_names[base_norm] = f
        return similar_pairs

    async def _compare_files(self, file1: str, file2: str) -> Dict[str, Any]:
        """Compare two files and analyze which is more complete."""
        content1 = await self._read_file_content(file1)
        content2 = await self._read_file_content(file2)

        # Use difflib to get similarity ratio
        seq = difflib.SequenceMatcher(None, content1, content2)
        similarity = seq.ratio()

        # Heuristic for completeness: file with more lines and more functions/classes
        lines1 = content1.count('\n')
        lines2 = content2.count('\n')

        def count_defs(content: str) -> int:
            return content.count('def ') + content.count('class ')

        defs1 = count_defs(content1)
        defs2 = count_defs(content2)

        completeness1 = lines1 + defs1 * 10  # weight defs higher
        completeness2 = lines2 + defs2 * 10

        more_complete = file1 if completeness1 >= completeness2 else file2

        return {
            "file1": file1,
            "file2": file2,
            "similarity": similarity,
            "more_complete": more_complete,
            "content1": content1,
            "content2": content2
        }

    async def _consolidate_files(self, file_keep: str, file_remove: str) -> str:
        """Consolidate by removing the less complete file and updating state."""
        # Remove the file_remove
        write_tool = next((t for t in self.tools if t.name == "write_file"), None)
        if not write_tool:
            raise RuntimeError("write_file tool not found")

        # Remove file by writing empty content or deleting
        # Here we delete by writing empty content and removing from generated files
        await write_tool.arun(file_path=file_remove, content="")

        # Update state to remove file_remove from generated_files
        state = await state_manager.get_state()
        if file_remove in state.generated_files:
            state.generated_files.remove(file_remove)
            await state_manager.save_state(state)

        return f"Removed duplicate file {file_remove}, kept {file_keep}."

    async def detect_and_consolidate(self) -> Dict[str, Any]:
        """Detect duplicates and consolidate them."""
        state = await state_manager.get_state()
        generated_files = state.generated_files

        # Identify similar files
        similar_pairs = await self._list_similar_files(generated_files)

        consolidation_results = []

        for file1, file2 in similar_pairs:
            comparison = await self._compare_files(file1, file2)
            if comparison["similarity"] > 0.7:  # threshold for similarity
                # Consolidate by keeping more complete
                result = await self._consolidate_files(
                    comparison["more_complete"],
                    file2 if comparison["more_complete"] == file1 else file1
                )
                consolidation_results.append(result)

        return {
            "duplicates_found": len(similar_pairs),
            "consolidation_results": consolidation_results
        }

    async def run(self, prompt: str) -> Dict[str, Any]:
        """Run the duplicate consolidator upon prompt completion."""
        # Create build step
        step_id = str(uuid.uuid4())
        step = BuildStep(
            id=step_id,
            agent="duplicate_consolidator",
            action="Detect and consolidate duplicate implementations",
            status="running"
        )
        await state_manager.add_build_step(step)

        try:
            result = await self.detect_and_consolidate()
            await state_manager.update_build_step(
                step_id,
                status="completed",
                result=str(result)
            )
            return result
        except Exception as e:
            await state_manager.update_build_step(
                step_id,
                status="failed",
                error=str(e)
            )
            raise


# Global duplicate consolidator instance
duplicate_consolidator = DuplicateConsolidatorAgent()
