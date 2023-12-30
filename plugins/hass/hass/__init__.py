from typing import Any, Optional
from haus_utils import Plugin, PluginConfig


class HassPlugin(Plugin):
    def __init__(self, config: PluginConfig, settings: Optional[dict[str, Any]] = None):
        super().__init__(config, settings)
