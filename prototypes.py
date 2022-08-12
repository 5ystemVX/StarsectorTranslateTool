import re
from abc import abstractmethod, ABCMeta


class UniversalConfigs:
    HIGHLIGHT_COLOR = "red"


class ShipSystem:
    """
    舰船的战术系统.
    """
    property_def = {
        "id": "id",
        "name": "name",
        "desc_csv": {
            "desc_in_codex": "text1",
            "system_type": "text2",
            "desc_on_ship": "text3",
            "highlights": "text4"},
    }

    def __init__(self, system_id: str,
                 name: str,
                 system_type: str = None,
                 desc_in_codex: str = None,
                 desc_on_ship: str = None,
                 highlights: str = None):
        self.id: str = system_id
        self.name: str = name
        for key in ShipSystem.property_def["desc_csv"].keys():
            self.__setattr__(key, "")
        self.system_type: str = system_type if system_type else ""
        self.desc_in_codex: str = desc_in_codex if desc_in_codex else ""
        self.desc_on_ship: str = desc_on_ship if desc_on_ship else ""
        self.highlights: str = highlights if highlights else ""

    @property
    def desc_on_ship_display(self) -> str:
        if len(self.highlights) == 0:
            return self.desc_on_ship
        else:
            desc_in_html = self.desc_on_ship
            tag_symbol = "%#s#%"
            for tag in self.highlights.split("|"):
                desc_in_html = desc_in_html.replace(tag, tag_symbol, 1)
            for tag in self.highlights.split("|"):
                # add style wrapping to change color
                hi_light_html = r"<font color=" + UniversalConfigs.HIGHLIGHT_COLOR + r">" + tag + r"</font> "
                #
                desc_in_html = desc_in_html.replace(tag_symbol, hi_light_html, 1)
            return desc_in_html

    @property
    def desc_on_ship_trans(self) -> str:
        if len(self.highlights) == 0:
            return self.desc_on_ship
        else:
            text = self.desc_on_ship
            tag_symbol = "%#s#%"
            for tag in self.highlights.split("|"):
                text = text.replace(tag, tag_symbol, 1)
            for tag in self.highlights.split("|"):
                text = text.replace(tag_symbol, "{{" + tag + "}}", 1)
            return text

    def set_desc_on_ship_trans(self, desc_on_ship_str: str):
        highlights = re.findall(r"\{\{(.+?)\}\}", desc_on_ship_str, )
        if len(highlights) == 0:
            self.highlights = ""
        else:
            self.highlights = " | ".join(highlights)
        self.desc_on_ship = re.sub(r"\{\{|\}\}", "", desc_on_ship_str)


class HullLike:
    """
    一艘完好,能够进行装配的船壳.
    """
    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    @abstractmethod
    def hull_name(self) -> str:
        pass

    @property
    @abstractmethod
    def tech_manufacturer(self) -> str:
        pass

    @property
    @abstractmethod
    def full_description(self) -> str:
        pass

    @property
    @abstractmethod
    def ship_system(self) -> ShipSystem | None:
        pass


class ShipHull(HullLike):
    """
    基本船体数据.
    """
    property_def = {
        "id": "id",
        "name": "name",
        "role": "designation",
        "tech": "tech/manufacturer",
        "desc_csv": {
            "desc_long": "text1",
            "desc_short": "text2",
            "desc_fleet": "text3",
        }
    }

    @property
    def id(self) -> str:
        return self._id

    @property
    def hull_name(self) -> str:
        return self.name

    @property
    def tech_manufacturer(self) -> str | None:
        return self.tech

    @property
    def full_description(self) -> str | None:
        return self.desc_long

    @property
    def ship_system(self) -> ShipSystem | None:
        return self._shipsystem

    def __init__(self,
                 ship_id: str,
                 ship_name: str,
                 ship_role: str,
                 manufacturer: str,
                 desc_long=None,
                 desc_short=None,
                 desc_fleet=None,
                 ship_system=None):
        super().__init__()
        self._id = ship_id
        self.name = ship_name
        self.role = ship_role
        self.tech = manufacturer
        # descriptions
        self.desc_long = "" if desc_long is None else desc_long
        self.desc_short = "" if desc_short is None else desc_short
        self.desc_fleet = "" if desc_fleet is None else desc_fleet
        # other
        self._shipsystem: ShipSystem | None = ship_system


class ShipSkin(HullLike):
    """
    基于某个船体的变体数据.
    """
    property_def = {
        "id": "skinHullId",
        "name": "hullName",
        "tech": "tech",
        "prefix": "descriptionPrefix",
    }

    @property
    def id(self) -> str:
        return self._id

    @property
    def hull_name(self) -> str:
        return self._skin_name

    @property
    def tech_manufacturer(self) -> str:
        if self.tech is None:
            return self.base_hull.tech_manufacturer
        else:
            return self.tech

    @property
    def full_description(self) -> str:
        result = self.base_hull.full_description
        if self.prefix is not None:
            result = self.prefix + "\n\n" + self.base_hull.full_description
        return result

    @property
    def ship_system(self) -> ShipSystem | None:
        if self._shipsystem is None:
            if self.system_changed:
                return None
            else:
                return self.base_hull.ship_system
        else:
            return self._shipsystem

    def __init__(self,
                 skin_id: str,
                 base_hull: ShipHull,
                 skin_name: str,
                 manufacturer: str | None,
                 system_changed: bool,
                 ship_system: ShipSystem | None,
                 prefix=None, ):
        super(ShipSkin, self).__init__()
        self._id = skin_id
        self._skin_name = skin_name

        self.tech: str | None = manufacturer
        self.prefix: str = "" if prefix is None else prefix

        self.base_hull = base_hull
        self._shipsystem = ship_system
        self.system_changed = system_changed


class Weapon:
    property_def = {
        "id": "id",

        "name": "name",
        "tech": "tech/manufacturer",
        "role": "primaryRoleStr",
        "accuracy": "accuracyStr",
        "fly_speed": "speedStr",
        "tracking": "trackingStr",
        "turn_rate": "turnRateStr",
        "desc_csv": {
            "description": "text1",
            "desc_foot_note": "text2"
        }
    }

    def __init__(self,
                 weapon_id: str,
                 is_system_weapon: bool,
                 name: str,
                 manufacturer: str,
                 role: str):
        self.id = weapon_id
        self.is_system_weapon = is_system_weapon
        self.name = name
        self.role = role

        # strings below are all optional
        self.tech: str = manufacturer if manufacturer else ""

        self.description: str = ""
        self.desc_foot_note: str = ""

        self.accuracy: str = ""
        self.turn_rate: str = ""
        self.fly_speed: str = ""
        self.tracking: str = ""
        self.special_effect_1: str = ""
        self.special_effect_1_hl: str = ""
        self.special_effect_2: str = ""
        self.special_effect_2_hl: str = ""

    @property
    def special_effect_1_display(self) -> str:
        if len(self.special_effect_1_hl) == 0:
            return self.special_effect_1
        else:
            display_text = self.special_effect_1
            highlights = self.special_effect_1_hl.split("|")
            for highlight in highlights:
                tag_symbol = "<font color=" + UniversalConfigs.HIGHLIGHT_COLOR + ">" + highlight + "</font>"
                display_text = display_text.replace("%s", tag_symbol, 1)
            return display_text

    @property
    def special_effect_2_display(self) -> str:
        if len(self.special_effect_2_hl) == 0:
            return self.special_effect_2
        else:
            display_text = self.special_effect_2
            highlights = self.special_effect_2_hl.split("|")
            for highlight in highlights:
                tag_symbol = "<font color=" + UniversalConfigs.HIGHLIGHT_COLOR + ">" + highlight + "</font>"
                display_text = display_text.replace("%s", tag_symbol, 1)
            return display_text

    @property
    def special_effect_1_trans(self) -> str:
        if len(self.special_effect_1_hl) == 0:
            return self.special_effect_1
        else:
            display_text = self.special_effect_1
            high_lights = self.special_effect_1_hl.split("|")
            for high_light in high_lights:
                display_text = display_text.replace("%s", "{{" + high_light + "}}", 1)
            return display_text

    @property
    def special_effect_2_trans(self) -> str:
        if len(self.special_effect_2_hl) == 0:
            return self.special_effect_2
        else:
            display_text = self.special_effect_2
            high_lights = self.special_effect_2_hl.split("|")
            for high_light in high_lights:
                display_text = display_text.replace("%s", "{{" + high_light + "}}", 1)
            return display_text


class Faction:
    """
    Faction data.
    """
    property_def = {
        "id": "id",
        "name": "displayName",
        "name_article": "displayNameWithArticle",
        # optional
        "name_long": "displayNameLong",
        "name_long_article": "displayNameLongWithArticle",

        "ship_prefix": "shipNamePrefix",
        "ranks": "ranks.ranks",
        "posts": "ranks.posts",
        "fleet_types": "fleetTypeNames",

        "desc_csv": {
            "description": "text1"
        }
    }

    def __init__(self, faction_id: str, faction_name: str, name_article: str):
        self.id: str = faction_id
        self.name: str = faction_name
        self.name_article: str = name_article

        self.name_long: str = ""
        self.name_long_article: str = ""

        self.ship_prefix: str = ""
        self.ranks = {}
        self.fleet_type = {}


class Variant:
    """
    ship_variants
    """

    def __init__(self,
                 variant_id: str,
                 type_name: str,
                 base_hull: HullLike,
                 weapon_list: list | None = None):
        self._id = variant_id
        self.is_fighter = False  # todo Recognize fighter hull
        self.base_hull = base_hull
        self.weapons = weapon_list
        self.display_name = type_name


class ModInfo:
    """
    metadata of a mod.
    """
    property_def = {
        "id": "id",
        "name": "name",
        # optional
        "version": "version",
        "game_version": "gameVersion",
        "author": "author",
        "description": "description"
    }

    def __init__(self, mod_id: str, mod_name: str):
        for key in ModInfo.property_def.keys():
            self.id = mod_id
            self.name = mod_name

            self.version = None
            self.game_version = None
            self.author = None
            self.description = None


class Resource:
    property_def = {
        "id": "id",
        "name": "name",
        "desc_csv": {
            "description": "text1"
        }
    }

    def __init__(self, resource_id: str, name: str):
        self.id = resource_id
        self.name = name
        self.description = ""


class WholeMOD:
    def __init__(self):
        self.mod_id = ""
        self.mod_name = ""
        self.mod_version = ""
        self.mod_desc = ""
        self.shipsystem_list = {}
        self.hull_dict = {}  # use hullId as key
        self.skin_list = {}  # use skinId as key
        self.variant_list = {}  # use variantId as key
        self.mission_list = {}
        self.weapons_list = []
        self.strings_list = []


class DataHolder:
    empty_translate = {
        "SHIP": {},
        "WEAPON": {},
        "SHIP_SYSTEM": {},
        "FACTION": {},
        "RESOURCE": {},
        "MOD_META": {},
    }

    def __init__(self, game_path=None, mod_path=None):
        self.mod_path = mod_path if mod_path else ""
        self.game_root_path = game_path if game_path else ""

        self.metadata: ModInfo | None = None
        self.translates: dict[str, dict[str, dict]] = self.empty_translate

        self.descriptions: dict | None = None

        self.weapons: dict[str, Weapon] | None = None
        self.ship_hulls: dict[str, ShipHull] | None = None
        self.ship_skins: dict[str, ShipSkin] | None = None
        self.ship_systems: dict[str, ShipSystem] | None = None

        self.resources: dict[str, Resource] | None = None
        self.factions: dict[str, Faction] | None = None

    @property
    def description_csv_path(self):
        if self.mod_path:
            return self.mod_path + r"\data\strings\descriptions.csv"
        else:
            return None

    @property
    def hull_csv_path(self):
        return self.mod_path + r"\data\hulls\ship_data.csv"

    @property
    def weapon_csv_path(self):
        return self.mod_path + r"\data\weapons\weapon_data.csv"

    @property
    def system_csv_path(self):
        return self.mod_path + r"\data\shipsystems\ship_systems.csv"

    @property
    def mod_info_path(self):
        return self.mod_path + r"\mod_info.json"

    def clear(self):
        self.__init__(self.game_root_path,self.mod_path)
        pass
