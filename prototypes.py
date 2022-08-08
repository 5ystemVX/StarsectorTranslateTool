from abc import abstractmethod, ABCMeta


class ShipSystem:
    property_def = {
        "name": "name",
        "id": "id",
        "desc_in_codex": "text1",
        "system_type": "text2",
        "desc_on_ship": "text3",
        "highlight": "text4"
    }
    """
    舰船的战术系统.
    """

    def __init__(self, system_id: str,
                 name: str):
        self.id = system_id
        self.name = name
        self.system_type: str = ""
        self.desc_in_codex: str = ""
        self.desc_on_ship: str = ""
        self.highlight: str = ""

    @property
    def desc_on_ship_display(self) -> str:
        if len(self.highlight) == 0:
            return self.desc_on_ship
        else:
            text = self.desc_on_ship
            for tag in self.highlight.split("|"):
                text = text.replace(tag, "%s", 1)
            for tag in self.highlight.split("|"):
                text = text.replace("%s", "<font color=red>" + tag + "</font> ", 1)
            return text

    @property
    def desc_on_ship_trans(self) -> str:
        if len(self.highlight) == 0:
            return self.desc_on_ship
        else:
            text = self.desc_on_ship
            for tag in self.highlight.split("|"):
                text = text.replace(tag, "%s", 1)
            for tag in self.highlight.split("|"):
                text = text.replace("%s", "{{" + tag + "}}", 1)
            return text


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

    @property
    def id(self) -> str:
        return self._id

    @property
    def hull_name(self) -> str:
        return self._ship_name

    @property
    def tech_manufacturer(self) -> str | None:
        return self._tech_manufacturer

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
                 ship_system: ShipSystem | None = None):
        super().__init__()
        self._id = ship_id
        self._ship_name = ship_name
        self.ship_designation = ship_role
        self._tech_manufacturer = manufacturer
        self.desc_long = "" if desc_long is None else desc_long
        self.desc_short = "" if desc_short is None else desc_short
        self.desc_fleet = "" if desc_fleet is None else desc_fleet
        self._shipsystem = ship_system


class ShipSkin(HullLike):
    """
    基于某个船体的变体数据.
    """

    @property
    def id(self) -> str:
        return self._id

    @property
    def hull_name(self) -> str:
        return self._skin_name

    @property
    def tech_manufacturer(self) -> str:
        if self._manufacturer is None:
            return self.base_hull.tech_manufacturer
        else:
            return self._manufacturer

    @property
    def full_description(self) -> str:
        if self._prefix is not None:
            result = self._prefix + "\n\n" + self.base_hull.full_description
        else:
            result = self.base_hull.full_description
        if self._suffix is not None:
            result = result + "\n\n" + self._suffix
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
                 prefix=None,
                 suffix=None, ):
        super(ShipSkin, self).__init__()
        self._id = skin_id

        self._skin_name = skin_name
        self._manufacturer = manufacturer
        self.prefix = prefix
        self.suffix = suffix

        self.base_hull = base_hull
        self._shipsystem = ship_system
        self.system_changed = system_changed


class Weapon:
    property_def = {
        "name": "name",
        "id": "id",
        "tech": "tech/manufacturer",
        "role": "primaryRoleStr",
        "accuracy": "accuracyStr",
        "fly_speed": "speedStr",
        "tracking": "trackingStr",
        "turn_rate": "turnRateStr",
        "description": "text1",
        "desc_foot_note": "text2"
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
        self.tech: str = manufacturer
        self.description: str = ''
        self.desc_foot_note: str = ''
        self.accuracy: str = ''
        self.turn_rate: str = ''
        self.fly_speed: str = ''
        self.tracking: str = ''
        self.special_effect_1: str = ''
        self.special_effect_1_hl: str = ''
        self.special_effect_2: str = ''
        self.special_effect_2_hl: str = ''

    @property
    def special_effect_1_display(self) -> str:
        if len(self.special_effect_1_hl) == 0:
            return self.special_effect_1
        else:
            display_text = self.special_effect_1
            high_lights = self.special_effect_1_hl.split("|")
            for high_light in high_lights:
                display_text = display_text.replace("%s", "<font color=red>" + high_light + "</font>", 1)
            return display_text

    @property
    def special_effect_2_display(self) -> str:
        if len(self.special_effect_2_hl) == 0:
            return self.special_effect_2
        else:
            display_text = self.special_effect_2
            high_lights = self.special_effect_2_hl.split("|")
            for high_light in high_lights:
                display_text = display_text.replace("%s", "<font color=red>" + high_light + "</font>", 1)
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


class Variant:
    def __init__(self,
                 variant_id: str,
                 type_name: str,
                 base_hull: HullLike,
                 weapon_list: list | None = None):
        self._id = variant_id
        self.base_hull = base_hull
        self.weapons = weapon_list
        self.display_name = type_name


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
        "SHIP_SYSTEM": {}
    }

    def __init__(self):
        self.mod_path = ""
        self.game_root_path = ""

        self.weapons: dict[str, Weapon] | None = None
        self.descriptions: dict | None = None
        self.ship_hulls: dict[str, ShipHull] | None = None
        self.ship_skins: dict[str, ShipSkin] | None = None
        self.ship_systems: dict[str, ShipSystem] | None = None
        self.translates: dict[str, dict[str, dict]] = self.empty_translate

    @property
    def description_csv_path(self):
        return self.mod_path + r"\data\strings\descriptions.csv"

    @property
    def hull_csv_path(self):
        return self.mod_path + r"\data\hulls\ship_data.csv"

    @property
    def weapon_csv_path(self):
        return self.mod_path + r"\data\weapons\weapon_data.csv"

    @property
    def system_csv_path(self):
        return self.mod_path + r"\data\shipsystems\ship_systems.csv"
