"""Harbor lifecycle adapter; OpenCluster performs all reasoning and Tool execution."""

import json
import os

from harbor.agents.base import BaseAgent
from harbor.agents.capabilities import AgentCapabilities
from harbor.agents.installed.base import NonZeroAgentExitCodeError
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext
from harbor.models.trajectories import Trajectory


class OpenClusterAgent(BaseAgent):
    capabilities = AgentCapabilities(atif=True)

    @staticmethod
    def name() -> str:
        return "opencluster"

    def version(self) -> str:
        return os.environ["OC_BENCH_COMMIT"]

    async def setup(self, environment: BaseEnvironment) -> None:
        result = await environment.exec(
            command=(
                "cp /opt/opencluster/controlplane /app/controlplane && chmod 0755 /app/controlplane"
            )
        )
        if result.return_code != 0:
            raise NonZeroAgentExitCodeError("could not prepare the OpenCluster binary")

    async def run(
        self, instruction: str, environment: BaseEnvironment, context: AgentContext
    ) -> None:
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        instruction_file = self.logs_dir / "instruction.txt"
        instruction_file.write_text(instruction)
        await environment.upload_file(
            source_path=instruction_file, target_path="/app/instruction.txt"
        )
        result = None
        try:
            result = await environment.exec(
                command="python /opt/opencluster/runtime.py", timeout_sec=570
            )
        finally:
            for name in (
                "trajectory.json",
                "investigation.json",
                "integrations.json",
                "smoke.json",
                "failure.json",
                "backend.log",
            ):
                try:
                    await environment.download_file(
                        source_path="/logs/agent/" + name, target_path=self.logs_dir / name
                    )
                except Exception:
                    self.logger.debug("Artifact unavailable: %s", name)
        path = self.logs_dir / "trajectory.json"
        if path.exists():
            document = json.loads(path.read_text())
            Trajectory.model_validate(document)
            metrics = document["final_metrics"]
            context.n_input_tokens = metrics.get("total_prompt_tokens")
            context.n_output_tokens = metrics.get("total_completion_tokens")
            context.metadata = {
                "controlplaneCommit": self.version(),
                "trajectorySource": "public Investigation and durable Tool Runs",
                "fullToolResultsAvailable": False,
                "smoke": os.environ.get("OC_BENCH_SMOKE") == "1",
                "elapsedSeconds": document["extra"].get("elapsedSeconds"),
            }
        if result is None or result.return_code != 0 or not path.exists():
            raise NonZeroAgentExitCodeError(
                "OpenCluster execution failed; inspect its collected artifacts"
            )
