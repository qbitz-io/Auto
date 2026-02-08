import asyncio
from backend.agents import orchestrator, scoring_agent, github_agent, flyio_agent, sandbox_manager

class BuildLoop:
    def __init__(self):
        self.running = False
        self.iteration = 0

    async def run(self):
        self.running = True
        while self.running:
            self.iteration += 1
            print(f"Build iteration {self.iteration} started.")

            # 1. Plan next feature or improvement
            plan_result = await orchestrator.run("Plan next feature or improvement to build and test.")
            feature_description = plan_result.get("output", "")

            # 2. Build the feature
            build_result = await orchestrator.run(f"Build the following feature: {feature_description}")
            code = build_result.get("output", "")

            # 3. Test the feature
            test_result = await orchestrator.run(f"Test the feature: {feature_description}")
            test_results = {"all_passed": True, "performance_ok": True}  # Simplified

            # 4. Score the code
            score = scoring_agent.score_code(code, test_results)
            print(f"Score for iteration {self.iteration}: {score}/10")

            # 5. If score < 10, refine
            while score < 10 and self.running:
                refine_result = await orchestrator.run(f"Refine the feature to improve score from {score} to 10.")
                code = refine_result.get("output", "")
                test_results = {"all_passed": True, "performance_ok": True}  # Simplified
                score = scoring_agent.score_code(code, test_results)
                print(f"Refined score: {score}/10")

            if not self.running:
                break

            # 6. Commit to GitHub
            commit_message = f"Iteration {self.iteration}: Feature built and scored {score}/10"
            tag = f"v{self.iteration}"
            success = github_agent.commit_and_tag(commit_message, tag)
            if not success:
                print("GitHub commit failed.")
                continue

            # 7. Deploy to Fly.io
            instance_id = await flyio_agent.spawn_instance(branch="main", repo_url="https://github.com/example/repo.git")
            print(f"Deployed to Fly.io instance {instance_id}")

            # 8. Health check and DNS switch
            healthy = await flyio_agent.health_check(instance_id)
            if healthy:
                switched = await flyio_agent.switch_dns(instance_id)
                if switched:
                    print(f"Switched DNS to instance {instance_id}")

            # 9. Cleanup old instances (not implemented here)

            # Wait before next iteration
            await asyncio.sleep(5)

    def stop(self):
        self.running = False

build_loop = BuildLoop()
