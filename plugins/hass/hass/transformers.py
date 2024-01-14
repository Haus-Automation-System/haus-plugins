from typing import Any
from hass_websocket_client.models import HassEntity, HassService, HassServiceField, HassServiceTarget
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
                    "friendly_name", entity["entity_id"].replace(
                        "_", " ").title()
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
                case "bool":
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

                    if "rgb" in pid and len(parsed_value) == 3 and all([type(i) == int for i in parsed_value]):
                        props[pid] = ColorEntityProperty(
                            id=pid,
                            display=DisplayData(
                                label=key.replace("_", " ").title(), icon="list"
                            ),
                            value=f"rgb({', '.join([str(i)
                                                    for i in parsed_value])})",
                            hasAlpha=False
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
                                        value_type=EntityTransformer.parse_value(v)[
                                            1],
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


class ActionTransformer:
    ICON_MAP = {
        "light.turn_on": "bulb",
        "light.turn_off": "bulb-off",
        "light.toggle": "bulb",
        "notify": "bell",
        "scene": "trees",
        "zone": "map",
        "tts": "ear"
    }

    @classmethod
    def transform(cls, domain: str, service: str, data: HassService) -> EntityAction:
        return EntityAction(
            id=domain + "." + service,
            plugin="hass",
            display=DisplayData(
                label=data["name"] if len(data["name"]) > 0 else " ".join(
                    [i.capitalize() for i in service.split("_")]),
                sub_label=data["description"] if "description" in data.keys() and len(
                    data["description"]) > 0 else None,
                icon=ActionTransformer.ICON_MAP.get(
                    domain + "." + service, ActionTransformer.ICON_MAP.get(domain, "settings-2"))
            ),
            target_types=[domain] if data.get("target") else None,
            fields={k: v for k, v in {k: ActionTransformer.transform_field(
                k, v) for k, v in data["fields"].items()}.items() if v}
        )

    @staticmethod
    def transform_field(key: str, field: HassServiceField) -> ENTITY_ACTION_FIELDS:
        selector_type = list(field.get("selector").keys())[0]
        selector_data = field["selector"][selector_type]
        if key == "date" and selector_type == "text":
            return DateActionField(
                key=key,
                display=DisplayData(label=field.get("name", " ".join(
                    [i.capitalize() for i in key.split("_")])), sub_label=field.get("description"), icon="calendar"),
                advanced=field.get("advanced", False),
                default=field.get("default"),
                required=field.get("required", False),
                min=None,
                max=None,
                example=field.get("example")
            )

        if key == "datetime" and selector_type == "text":
            return DateTimeActionField(
                key=key,
                display=DisplayData(label=field.get("name", " ".join(
                    [i.capitalize() for i in key.split("_")])), sub_label=field.get("description"), icon="calendar-clock"),
                advanced=field.get("advanced", False),
                default=field.get("default"),
                required=field.get("required", False),
                min=None,
                max=None,
                example=field.get("example")
            )

        if key == "rgb_color" and selector_type == "object":
            return ColorActionField(
                key=key,
                display=DisplayData(label=field.get("name", " ".join(
                    [i.capitalize() for i in key.split("_")])), sub_label=field.get("description"), icon="color-swatch"),
                advanced=field.get("advanced", False),
                default=field.get("default"),
                required=field.get("required", False),
                example=field.get("example")
            )

        match selector_type:
            case "text":
                return StringActionField(
                    key=key,
                    display=DisplayData(label=field.get("name", " ".join(
                        [i.capitalize() for i in key.split("_")])), sub_label=field.get("description"), icon="cursor-text"),
                    advanced=field.get("advanced", False),
                    default=field.get("default"),
                    required=field.get("required", False),
                    example=field.get("example")
                )

            case "select":
                return SelectionActionField(
                    key=key,
                    display=DisplayData(label=field.get("name", " ".join(
                        [i.capitalize() for i in key.split("_")])), sub_label=field.get("description"), icon="select"),
                    advanced=field.get("advanced", False),
                    default=field.get("default"),
                    required=field.get("required", False),
                    options=[SelectionActionOptions(value=i, label=" ".join(
                        [j.capitalize() for j in i.split("_")])) if type(i) != dict else SelectionActionOptions(value=i["value"], label=i["label"]) for i in selector_data.get("options", [])],
                    multi=False,
                    example=field.get("example")
                )

            case "time":
                return TimeActionField(
                    key=key,
                    display=DisplayData(label=field.get("name", " ".join(
                        [i.capitalize() for i in key.split("_")])), sub_label=field.get("description"), icon="clock"),
                    advanced=field.get("advanced", False),
                    default=field.get("default"),
                    required=field.get("required", False),
                    min=None,
                    max=None,
                    example=field.get("example")
                )

            case "object":
                return JSONActionField(
                    key=key,
                    display=DisplayData(label=field.get("name", " ".join(
                        [i.capitalize() for i in key.split("_")])), sub_label=field.get("description"), icon="json"),
                    advanced=field.get("advanced", False),
                    default=field.get("default"),
                    required=field.get("required", False),
                    example=field.get("example")
                )

            case "number":
                return NumberActionField(
                    key=key,
                    display=DisplayData(label=field.get("name", " ".join(
                        [i.capitalize() for i in key.split("_")])), sub_label=field.get("description"), icon="number"),
                    advanced=field.get("advanced", False),
                    default=field.get("default"),
                    required=field.get("required", False),
                    min=selector_data.get("min"),
                    max=selector_data.get("max"),
                    decimals="step" in selector_data.keys(),
                    unit=selector_data.get("unit_of_measurement"),
                    example=field.get("example")
                )

            case "boolean":
                return BooleanActionField(
                    key=key,
                    display=DisplayData(label=field.get("name", " ".join(
                        [i.capitalize() for i in key.split("_")])), sub_label=field.get("description"), icon="toggle-left"),
                    advanced=field.get("advanced", False),
                    default=field.get("default"),
                    required=field.get("required", False),
                    example=field.get("example")
                )

            case "entity":
                pfx = ""
                if selector_data:
                    if "domain" in selector_data.keys():
                        pfx += selector_data["domain"] + "."

                    if "service" in selector_data.keys():
                        pfx += selector_data["service"] + "."

                return EntitySelectorActionField(key=key,
                                                 display=DisplayData(label=field.get("name", " ".join(
                                                     [i.capitalize() for i in key.split("_")])), sub_label=field.get("description"), icon="category"),
                                                 advanced=field.get(
                                                     "advanced", False),
                                                 default=field.get("default"),
                                                 required=field.get(
                                                     "required", False),
                                                 prefix=[pfx.strip(".")] if len(
                                                     pfx) > 0 else [],
                                                 example=field.get("example")
                                                 )

            case "conversation_agent":
                return EntitySelectorActionField(key=key,
                                                 display=DisplayData(label=field.get("name", " ".join(
                                                     [i.capitalize() for i in key.split("_")])), sub_label=field.get("description"), icon="category"),
                                                 advanced=field.get(
                                                     "advanced", False),
                                                 default=field.get("default"),
                                                 required=field.get(
                                                     "required", False),
                                                 prefix=["conversation_agent"],
                                                 example=field.get("example")
                                                 )

            case "color_temp":
                return NumberActionField(
                    key=key,
                    display=DisplayData(label=field.get("name", " ".join(
                        [i.capitalize() for i in key.split("_")])), sub_label=field.get("description"), icon="color-swatch"),
                    advanced=field.get("advanced", False),
                    default=field.get("default"),
                    required=field.get("required", False),
                    min=selector_data.get(
                        "min_mireds") if selector_data else None,
                    max=selector_data.get(
                        "max_mireds") if selector_data else None,
                    decimals=False,
                    unit=None,
                    example=field.get("example")
                )

            case "color_rgb":
                return ColorActionField(
                    key=key,
                    display=DisplayData(label=field.get("name", " ".join(
                        [i.capitalize() for i in key.split("_")])), sub_label=field.get("description"), icon="color-swatch"),
                    advanced=field.get("advanced", False),
                    default=field.get("default"),
                    required=field.get("required", False),
                    example=field.get("example")
                )

            case "constant":
                return None

            case _:
                return StringActionField(
                    key=key,
                    display=DisplayData(label=field.get("name", " ".join(
                        [i.capitalize() for i in key.split("_")])), sub_label=field.get("description"), icon="cursor-text"),
                    advanced=field.get("advanced", False),
                    default=field.get("default"),
                    required=field.get("required", False),
                    example=field.get("example")
                )
