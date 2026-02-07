from __future__ import annotations

import importlib
from typing import Any, Dict, Optional, Tuple

from .interface import SolutionPlugin


class PluginLoadError(RuntimeError):
    pass


def _parse_plugin_spec(spec: str) -> Tuple[str, str]:
    """
    Accepts:
      - "pkg.module:ClassName"
      - "pkg.module" (defaults to symbol "Plugin")
    """
    if ":" in spec:
        module_path, symbol = spec.split(":", 1)
        module_path = module_path.strip()
        symbol = symbol.strip()
        if not module_path or not symbol:
            raise PluginLoadError(f"Invalid plugin spec '{spec}'. Use 'module:ClassName'.")
        return module_path, symbol
    return spec.strip(), "Plugin"


def load_plugin(taskpack: Dict[str, Any]) -> SolutionPlugin:
    spec: Optional[str] = taskpack.get("plugin")
    if not spec:
        raise PluginLoadError("Taskpack missing 'plugin'. Provide e.g. 'solutions.security.echo.plugin:EchoPlugin'.")

    module_path, symbol = _parse_plugin_spec(spec)

    try:
        module = importlib.import_module(module_path)
    except Exception as e:
        raise PluginLoadError(f"Failed importing plugin module '{module_path}': {e}") from e

    try:
        cls = getattr(module, symbol)
    except AttributeError as e:
        raise PluginLoadError(f"Plugin symbol '{symbol}' not found in module '{module_path}'.") from e

    try:
        plugin = cls()  # type: ignore[call-arg]
    except Exception as e:
        raise PluginLoadError(f"Failed instantiating plugin '{spec}': {e}") from e

    # Minimal duck-typing validation (Protocol isn't enforced at runtime)
    for attr in ("id", "version", "capabilities", "validate", "plan", "run", "report"):
        if not hasattr(plugin, attr):
            raise PluginLoadError(f"Plugin '{spec}' is missing required method '{attr}()'.")

    return plugin  # type: ignore[return-value]
