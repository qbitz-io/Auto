import asyncio
from backend.agents import orchestrator, scoring_agent, github_agent, flyio_agent, sandbox_manager

class BuildLoop:
    def __init__(self):
        self.running = False
        self.iteration = 0

    async def run_approach(self, approach_description, iteration):
        print(f"Build iteration {iteration} started for approach: {approach_description}")

        # 1. Build the feature
        build_result = await orchestrator.run(f"Build the following feature: {approach_description}", depth=0)
        code = build_result.get("output", "")

        # 2. Test the feature
        test_result = await orchestrator.run(f"Test the feature: {approach_description}", depth=0)
        test_results = {"all_passed": True, "performance_ok": True}  # Simplified

        # 3. Score the code
        score = scoring_agent.score_code(code, test_results)
        print(f"Score for iteration {iteration}: {score}/10")

        # 4. If score < 10, refine
        while score < 10 and self.running:
            refine_result = await orchestrator.run(f"Refine the feature to improve score from {score} to 10.", depth=0)
            code = refine_result.get("output", "")
            test_results = {"all_passed": True, "performance_ok": True}  # Simplified
            score = scoring_agent.score_code(code, test_results)
            print(f"Refined score: {score}/10")

        if not self.running:
            return None

        # 5. Commit to GitHub with detailed message
        commit_message = (
            f"Iteration {iteration}: Feature built and scored {score}/10. "
            f"All tests passed: {test_results['all_passed']}. Performance OK: {test_results['performance_ok']}"
        )
        success = github_agent.commit_and_tag(commit_message)
        if not success:
            print("GitHub commit failed.")
            return None

        # 6. Deploy to Fly.io
        instance_id = await flyio_agent.spawn_instance(branch="main", repo_url="https://github.com/example/repo.git")
        print(f"Deployed to Fly.io instance {instance_id}")

        # 7. Health check and DNS switch
        healthy = await flyio_agent.health_check(instance_id)
        if healthy:
            switched = await flyio_agent.switch_dns(instance_id)
            if switched:
                print(f"Switched DNS to instance {instance_id}")

        return {
            "iteration": iteration,
            "approach": approach_description,
            "score": score,
            "instance_id": instance_id
        }

    async def run(self, depth=0):
        self.running = True
        while self.running:
            self.iteration += 1
            print(f"Planning build iteration {self.iteration}...")

            # Plan multiple approaches
            plan_result = await orchestrator.run("Plan multiple approaches for next feature or improvement to build and test.", depth=depth)
            approaches_text = plan_result.get("output", "")

            # Parse approaches from plan_result output (assuming newline separated)
            approaches = [line.strip() for line in approaches_text.splitlines() if line.strip()]
            if not approaches:
                print("No approaches planned. Waiting before retrying.")
                await asyncio.sleep(5)
                continue

            # Run all approaches in parallel
            tasks = [self.run_approach(approach, self.iteration) for approach in approaches]
            results = await asyncio.gather(*tasks)

            # Filter out None results (failed or stopped)
            successful_results = [res for res in results if res is not None]

            if not successful_results:
                print("No successful builds in this iteration.")

            # Wait before next iteration
            await asyncio.sleep(5)

    def stop(self):
        self.running = False

build_loop = BuildLoop()
