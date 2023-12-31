from typing import Any, Optional
from haus_utils import Plugin, PluginConfig
from pydantic import BaseModel


class HassPluginSettings(BaseModel):
    hass_server: str
    hass_token: str


class HassPlugin(Plugin):
    def __init__(self, config: PluginConfig, settings: HassPluginSettings):
        super().__init__(config, settings)
