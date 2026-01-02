import os
import tempfile

from tools.orchestrator.plugins.runner import run_plugin
from tools.orchestrator.plugins.interface import ExecutionContext

def test_run_echo_plugin_writes_artifacts():
    taskpack = {
        "plugin": "solutions.security.echo.plugin:EchoPlugin",
        "constraints": {"allow_network": False, "allow_cloud_mutations": False},
    }

    with tempfile.TemporaryDirectory() as d:
        art = os.path.join(d, ".orchestrator_logs")
        os.makedirs(art, exist_ok=True)

        ctx = ExecutionContext(
            run_id="test",
            taskpack_path=d,
            workspace_dir=d,
            constraints=taskpack["constraints"],
            artifact_dir=art,
            log=lambda *_: None,
        )

        run_plugin(taskpack, ctx)

        assert os.path.exists(os.path.join(art, "plugin_result.json"))
        assert os.path.exists(os.path.join(art, "echo.txt"))
        assert os.path.exists(os.path.join(art, "echo_report.md"))
