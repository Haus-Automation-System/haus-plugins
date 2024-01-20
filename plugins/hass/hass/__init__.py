from collections.abc import AsyncGenerator
from secrets import token_urlsafe
from typing import Any, Optional, Self
from haus_utils import Plugin, PluginConfig, PluginEntity, EntityAction, PluginEvent
from pydantic import BaseModel
from hass_websocket_client import HassWS
from hass_websocket_client.client import HassEventListener, HassEvent, HassEntity

from .transformers import EntityTransformer, ActionTransformer


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

    async def get_actions(self, ids: list[str] = None) -> list[EntityAction]:
        result = await self.client.fetch_services()
        if not result.success:
            return []

        output = []
        for domain, services in result.data.items():
            for service, data in services.items():
                if ids == None or (domain + "." + service) in ids:
                    output.append(ActionTransformer.transform(
                        domain, service, data))

        return output

    async def call_action(self, action_id: str, target: Optional[str], fields: dict[str, Any]):
        await self.client.call_service(
            action_id.split(".")[0],
            action_id.split(".")[1],
            target={"entity_id": target} if target else {},
            data={k: v for k, v in fields.items() if v != None}
        )

    async def listen_events(self) -> AsyncGenerator[PluginEvent | None, Any]:
        async with self.client.listen_event() as l:
            listener: HassEventListener = l
            async for event in listener:
                e: HassEvent = event
                yield PluginEvent(
                    id=token_urlsafe(nbytes=16),
                    plugin="hass",
                    types=[e["event_type"]],
                    data=e["data"],
                    targets=[e["data"]["entity_id"]] if "entity_id" in e["data"].keys() else [
                    ],
                    new_state=EntityTransformer.transform(HassEntity(
                        e["data"]["new_state"])) if "new_state" in e["data"].keys() else None
                )
