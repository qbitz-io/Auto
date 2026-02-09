import unittest
from unittest.mock import AsyncMock, patch
import os
os.environ['OPENAI_API_KEY'] = 'dummy_key'

class TestBuildLoopAgent(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        patcher = patch('backend.agents.build_loop.ResearchAgent')
        self.MockResearcherAgent = patcher.start()
        self.addCleanup(patcher.stop)

        from backend.agents.build_loop import BuildLoop
        self.build_loop = BuildLoop()

    @patch('backend.agents.build_loop.orchestrator.run', new_callable=AsyncMock)
    async def test_researcher_called_before_builder(self, mock_orchestrator_run):
        # Setup mocks
        mock_researcher = self.MockResearcherAgent.return_value

        # Mock research results
        research_results = {'insights': 'some research data'}
        mock_researcher.research_before_build.return_value = research_results

        # Mock orchestrator.run to simulate build and test steps
        mock_orchestrator_run.return_value = {'output': 'code output'}

        # Run the build approach
        result = await self.build_loop.run_approach('Test feature', 1)

        # Assert researcher was called
        mock_researcher.research_before_build.assert_called_once_with('Test feature')

        # Assert orchestrator.run was called at least twice (build and test)
        self.assertGreaterEqual(mock_orchestrator_run.call_count, 2)

        # Assert the final result contains expected keys
        self.assertIn('iteration', result)
        self.assertIn('approach', result)
        self.assertIn('score', result)
        self.assertIn('instance_id', result)

if __name__ == '__main__':
    unittest.main()
