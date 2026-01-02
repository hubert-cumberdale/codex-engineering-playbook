# Goal

Introduce an **engine-first plugin architecture** in `tools/orchestrator/plugins/` and a minimal reference plugin
at `solutions/security/echo/`.

This enables domain solutions (security/web/gaming) to ship their own adapters/reporters without polluting orchestrator core.

# Requirements

## 1) Plugin interface (domain-agnostic)
Create `tools/orchestrator/plugins/interface.py` defining:

- `PluginCapabilities` (dataclass)
  - `requires_network: bool = False`
  - `requires_cloud_mutations: bool = False`
  - `produces_domain_result: bool = True`

- `ExecutionContext` (dataclass)
  - `run_id: str`
  - `taskpack_path: str`
  - `workspace_dir: str`
  - `constraints: dict`
  - `artifact_dir: str`
  - `log` callable (or std logger)

- `Plan` (dataclass)
  - `steps: list[dict]` (opaque to core; plugin-defined step dicts)
  - `expected_artifacts: list[str]`
  - `metadata: dict`

- `RawOutput` (dataclass)
  - `artifacts: list[str]` (paths written)
  - `metadata: dict`

- `ValidationReport` (dataclass)
  - `ok: bool`
  - `errors: list[str]`
  - `warnings: list[str]`

- `SolutionPlugin` (Protocol / ABC)
  - `id() -> str` (e.g. "security/echo")
  - `version() -> str`
  - `capabilities() -> PluginCapabilities`
  - `validate(taskpack: dict, ctx: ExecutionContext) -> ValidationReport`
  - `plan(taskpack: dict, ctx: ExecutionContext) -> Plan`
  - `run(plan: Plan, ctx: ExecutionContext) -> RawOutput`
  - `report(raw: RawOutput, ctx: ExecutionContext) -> list[str]` (artifact paths)

## 2) Plugin loader
Create `tools/orchestrator/plugins/loader.py`:

- `load_plugin(taskpack: dict) -> SolutionPlugin`
  - Reads `taskpack["plugin"]` as a python import path
    - Example: `solutions.security.echo.plugin:EchoPlugin`
    - If class part is omitted, default to `Plugin` symbol.
  - If `plugin` is null/missing:
    - return a `NullPlugin` (no-op) OR raise a friendly error only if orchestrator is in plugin-only mode
    - MUST remain backward compatible with existing orchestrator behavior.

Include:
- friendly error messages
- no network access
- no dynamic code execution beyond importlib import

## 3) Plugin runner
Create `tools/orchestrator/plugins/runner.py`:

- `run_plugin(taskpack: dict, ctx: ExecutionContext) -> dict`
  - Loads plugin
  - Checks plugin capabilities vs `ctx.constraints`
    - If plugin requires network but constraints disallow -> fail early
    - Same for cloud mutations
  - Calls validate→plan→run→report
  - Writes a `plugin_result.json` artifact in `.orchestrator_logs/` (or ctx.artifact_dir) with:
    - plugin id/version
    - validation report
    - plan metadata (NOT secrets)
    - raw metadata
    - report artifact list

Return a dict summary suitable for orchestrator manifest inclusion.

## 4) Reference plugin: security/echo
Create `solutions/security/echo/plugin.py`:

- `EchoPlugin` implements SolutionPlugin
- validate() always ok
- plan() returns one step like `{"action": "write_file", "path": "echo.txt", "content": "hello"}`
- run() writes `echo.txt` into ctx.artifact_dir
- report() writes `echo_report.md` summarizing run + artifacts

## 5) Tests
Add tests to prove:
- loader imports plugin correctly
- runner enforces constraints
- runner produces `plugin_result.json`, `echo.txt`, and `echo_report.md`

Tests must not depend on network.

# Non-goals (for this pack)
- Do NOT refactor existing orchestrate.py pipeline yet
- Do NOT add BAS-specific schemas
- Do NOT add entrypoints packaging (keep simple import path loading)
