from typing import Any, Optional, Self
from haus_utils import Plugin, PluginConfig, PluginEntity
from pydantic import BaseModel
from hass_websocket_client import HassWS
from .transformers import EntityTransformer


class HassPluginSettings(BaseModel):
    hass_server: str
    hass_token: str


class HassPlugin(Plugin):
    settings: HassPluginSettings

    def __init__(self, config: PluginConfig, settings: HassPluginSettings):
        super().__init__(config, settings)
        self.settings = HassPluginSettings(**settings)
        self.client: HassWS = None

    async def initialize(self):
        self.client = await HassWS(self.settings.hass_server, self.settings.hass_token)

    async def close(self):
        if self.client:
            await self.client.close()
            self.client = None

    async def get_entities(self, ids: list[str] = None) -> list[PluginEntity]:
        result = await self.client.fetch_states()
        if not result.success:
            return []

        return [
            EntityTransformer.transform(i)
            for i in result.data
            if ids == None or i["entity_id"] in ids
        ]
