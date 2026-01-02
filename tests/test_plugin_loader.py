from tools.orchestrator.plugins.loader import load_plugin

def test_load_echo_plugin():
    taskpack = {"plugin": "solutions.security.echo.plugin:EchoPlugin"}
    plugin = load_plugin(taskpack)
    assert plugin.id() == "security/echo"
