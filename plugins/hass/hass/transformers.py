from typing import Any
from hass_websocket_client.models import HassEntity
from haus_utils import *


class EntityTransformer:
    ICON_MAP = {
        "alarm_control_panel": "bell",
        "binary_sensor": "photo-sensor",
        "button": "layout-bottombar",
        "calendar": "calendar",
        "camera": "camera",
        "climate": "air-conditioning",
        "cover": "car-garage",
        "date": "calendar-event",
        "datetime": "calendar-time",
        "device_tracker": "device-mobile-pin",
        "fan": "propeller",
        "humidifier": "ripple",
        "image": "photo",
        "light": "bulb",
        "lock": "lock",
        "media_player": "music",
        "number": "number",
        "remote": "device-remote",
        "select": "select",
        "sensor": "radar",
        "siren": "bell-school",
        "stt": "ear",
        "switch": "toggle-right",
        "text": "text-size",
        "time": "clock",
        "todo": "list-check",
        "tts": "broadcast",
        "update": "refresh-alert",
        "vacuum": "vacuum-cleaner",
        "water-heater": "droplet-half-filled",
        "weather": "cloud-storm",
        "person": "user",
        "sun": "sun",
    }

    DENIED_KEYS = [
        "assumed_state",
        "attribution",
        "entity_picture",
        "device_class",
        "has_entity_name",
        "should_poll",
        "icon",
        "friendly_name",
        "translation_key",
    ]

    @classmethod
    def transform(cls, entity: HassEntity) -> PluginEntity:
        etype = entity["entity_id"].split(".")[0]

        return PluginEntity(
            id=entity["entity_id"],
            plugin="hass",
            type=etype,
            display=DisplayData(
                label=entity["attributes"].get(
                    "friendly_name", entity["entity_id"].replace("_", " ").title()
                ),
                icon=cls.ICON_MAP.get(etype.lower(), "hexagon"),
            ),
            properties=EntityTransformer.generic_property_transform(entity),
        )

    @staticmethod
    def parse_value(
        value: Any,
    ) -> Union[str, bool, int, float, None, datetime.datetime]:
        if type(value) == str:
            if value.lower() in ["off", "false", "no"]:
                return False, "boolean"
            if value.lower() in ["on", "true", "yes"]:
                return True, "boolean"

            try:
                return int(value), "number"
            except:
                pass

            try:
                return float(value), "number"
            except:
                pass

            try:
                return datetime.datetime.fromisoformat(value), "datetime"
            except:
                pass

            return value, "string"

        return value, str(type(value)).split("'")[1]

    @staticmethod
    def generic_property_transform(entity: HassEntity) -> dict[str, ENTITY_PROPERTIES]:
        props = {}
        for key, value in dict(state=entity["state"], **entity["attributes"]).items():
            if key.lower() in EntityTransformer.DENIED_KEYS:
                continue

            parsed_value, value_type = EntityTransformer.parse_value(value)
            pid = entity["entity_id"] + "." + key
            match value_type:
                case "boolean":
                    props[pid] = BooleanEntityProperty(
                        id=pid,
                        display=DisplayData(
                            label=key.replace("_", " ").title(), icon="toggle-right"
                        ),
                        value=parsed_value,
                    )
                    continue
                case "number":
                    props[pid] = NumberEntityProperty(
                        id=pid,
                        display=DisplayData(
                            label=key.replace("_", " ").title(), icon="number"
                        ),
                        value=parsed_value,
                    )
                    continue
                case "datetime":
                    props[pid] = DateEntityProperty(
                        id=pid,
                        display=DisplayData(
                            label=key.replace("_", " ").title(), icon="calendar-time"
                        ),
                        value=parsed_value,
                    )
                    continue
                case "string":
                    props[pid] = StringEntityProperty(
                        id=pid,
                        display=DisplayData(
                            label=key.replace("_", " ").title(), icon="text-size"
                        ),
                        value=parsed_value,
                    )
                    continue
                case "list":
                    if len(parsed_value) == 0:
                        props[pid] = ListEntityProperty(
                            id=pid,
                            display=DisplayData(
                                label=key.replace("_", " ").title(), icon="list"
                            ),
                            value=parsed_value,
                        )
                        continue

                    if type(parsed_value[0]) == dict:
                        try:
                            props[pid] = TableEntityProperty(
                                id=pid,
                                display=DisplayData(
                                    label=key.replace("_", " ").title(),
                                    icon="table",
                                ),
                                value=parsed_value,
                                columns=[
                                    TablePropertyColumn(
                                        key=k,
                                        value_type=EntityTransformer.parse_value(v)[1],
                                    )
                                    for k, v in parsed_value[0].items()
                                ],
                            )
                            continue
                        except:
                            pass

                    props[pid] = ListEntityProperty(
                        id=pid,
                        display=DisplayData(
                            label=key.replace("_", " ").title(), icon="list"
                        ),
                        value=parsed_value,
                    )
                    continue

                case _:
                    props[pid] = StringEntityProperty(
                        id=pid,
                        display=DisplayData(
                            label=key.replace("_", " ").title(), icon="text-size"
                        ),
                        value=str(parsed_value),
                    )
        return props
