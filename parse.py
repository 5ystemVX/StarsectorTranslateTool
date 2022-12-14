import configparser
import csv
import logging
from collections import deque

import chardet
import json5

from prototypes import *


def parse_ui_str(lang_file_path) -> dict:
    result = {}
    cf = configparser.ConfigParser()
    cf.read(lang_file_path, encoding="utf-8")

    keys = cf.options("LanguageDefinition")
    for key in keys:
        result[key] = cf.get("LanguageDefinition", key)
    return result


def parse_mod_data(mod_path):
    # strings = parse_descriptions(mod_path)
    #
    # #   shipsystem = parse_ship_systems(mod_path, strings["SHIP_SYSTEM"])
    #
    # #  hulls = parse_hulls(mod_path, strings["SHIP"})
    #
    # weapons = parse_weapons(mod_path, strings["WEAPON"])

    print(mod_path)


class ModParser:
    @staticmethod
    def parse_descriptions(mod_path) -> dict:
        result = {
            "SHIP": {},
            "SHIP_SYSTEM": {},
            "WEAPON": {},
            "RESOURCE": {},
            "FACTION": {},
            "CUSTOM": {}
        }
        file_path = mod_path + r"\data\strings\descriptions.csv"
        try:
            csv_strings = ModParser.__read_text_file(file_path)
            reader = csv.reader(csv_strings)
            # separate headline
            headers = next(reader)
            id_col = headers.index("id")
            type_col = headers.index("type")
            for row in reader:
                # skip empty cols & annotation
                if len(row[id_col]) == 0 or row[0].startswith("#"):
                    continue

                # sort by type
                type_str = row[type_col]
                if type_str == "SHIP":
                    slot_def = ShipHull.property_def["desc_csv"]
                    # SHIP_HULL-Like desc
                    item = dict()
                    for key, value in slot_def.items():
                        item[key] = row[headers.index(value)]
                    result[type_str][row[id_col]] = item
                elif type_str == "WEAPON":
                    slot_def = Weapon.property_def["desc_csv"]
                    item = dict()
                    for key, value in slot_def.items():
                        item[key] = row[headers.index(value)]
                    result[type_str][row[id_col]] = item
                elif type_str == "SHIP_SYSTEM":
                    slot_def = ShipSystem.property_def["desc_csv"]
                    item = dict()
                    for key, value in slot_def.items():
                        try:
                            item[key] = row[headers.index(value)]
                        except ValueError:
                            item[key] = ""
                    result[type_str][row[id_col]] = item
                elif type_str == "FACTION":
                    slot_def = Faction.property_def["desc_csv"]
                    item = dict()
                    for key, value in slot_def.items():
                        item[key] = row[headers.index(value)]
                    result[type_str][row[id_col]] = item
                elif type_str == "RESOURCE":
                    slot_def = Resource.property_def["desc_csv"]
                    item = dict()
                    for key, value in slot_def.items():
                        item[key] = row[headers.index(value)]
                    result[type_str][row[id_col]] = item
                elif type_str == "CUSTOM":
                    item = {"description": row[headers.index("text1")],
                            "market_desc": row[headers.index("text3")]}
                    result[type_str][row[id_col]] = item
        # file parse failed
        except ValueError:
            return {}
        # file read failed
        except OSError:
            return {}
        return result

    @staticmethod
    def parse_ship_systems(mod_path, shipsystem_descriptions) -> dict:
        result = {}
        file_path = mod_path + r"\data\shipsystems\ship_systems.csv"
        # check encoding
        try:
            csv_strings = ModParser.__read_text_file(file_path)
            reader = csv.reader(csv_strings)
            # separate headline
            headers = next(reader)
            id_col = headers.index("id")
            name_col = headers.index("name")
            for row in reader:
                # skip empty cols & annotation
                if len(row[id_col]) == 0 or row[0].startswith("#"):
                    continue

                system_id = row[id_col]
                system_desc = shipsystem_descriptions.get(system_id, None)
                system = ShipSystem(system_id, row[name_col])
                if system_desc is not None:
                    for key in ShipSystem.property_def["desc_csv"].keys():
                        system.__setattr__(key, system_desc[key])
                result[system_id] = system
            return result
        except OSError:
            logging.warning("file(%s) read failed", file_path)
            return {}
        except ValueError:
            logging.warning("file(%s) parse failed,wrong encoding", file_path)
            return {}

    @staticmethod
    def parse_hullmods(mod_path) -> dict:
        result = {}
        file_path = mod_path + r"\\data\hullmods\hull_mods.csv"
        # check encoding
        try:
            csv_strings = ModParser.__read_text_file(file_path)
            reader = csv.reader(csv_strings)
            # separate headline
            headers = next(reader)
            id_col = headers.index("id")
            name_col = headers.index("name")
            for row in reader:
                # skip empty cols & annotation
                if len(row[id_col]) == 0 or row[0].startswith("#"):
                    continue
                hullmod_id = row[id_col]
                hullmod = HullMod(hullmod_id)
                hullmod.name = row[name_col]
                hullmod.description = row[headers.index("desc")]
                result[hullmod_id] = hullmod
            return result
        except OSError:
            logging.warning("file(%s) read failed", file_path)
            return {}
        except ValueError:
            logging.warning("file(%s) parse failed,wrong encoding", file_path)
            return {}

    @staticmethod
    def parse_hulls(mod_path, hull_descriptions) -> dict:
        result = {}
        file_path = mod_path + r"\data\hulls\ship_data.csv"
        try:
            csv_strings = ModParser.__read_text_file(file_path)
            reader = csv.reader(csv_strings)
            # separate headline
            headers = next(reader)
            id_col = headers.index("id")
            name_col = headers.index("name")
            for row in reader:
                # skip empty cols & annotation
                if len(row[id_col]) == 0 or row[0].startswith("#"):
                    continue
                hull_desc = hull_descriptions.get(row[id_col], None)
                hull = ShipHull(row[id_col], row[name_col], row[2], row[3])
                if hull_desc is not None:
                    for key in ShipHull.property_def["desc_csv"].keys():
                        hull.__setattr__(key, hull_desc[key])
                result[row[id_col]] = hull
            return result
        except OSError:
            logging.warning("file(%s) read failed", file_path)
            return {}
        except ValueError:
            logging.warning("file(%s) parse failed,wrong encoding", file_path)
            return {}

    @staticmethod
    def parse_weapons(mod_path, weapon_descriptions) -> dict:
        result = {}
        file_path = mod_path + r"\data\weapons\weapon_data.csv"
        try:
            csv_string = ModParser.__read_text_file(file_path)
            reader = csv.reader(csv_string)
            # separate headline
            headers = next(reader)
            id_col = headers.index("id")
            name_col = headers.index("name")
            hint_col = headers.index("hints")
            tech_col = headers.index("tech/manufacturer")
            role_col = headers.index("primaryRoleStr")

            speed_col = headers.index("speedStr")
            tracking_col = speed_col + 1
            turn_col = tracking_col + 1
            acc_col = turn_col + 1
            primary_str = headers.index("customPrimary")
            for row in reader:
                # skip empty cols & annotation
                if len(row[id_col]) == 0 or row[0].startswith("#"):
                    continue
                is_system_weapon = "SYSTEM" in row[hint_col]
                weapon = Weapon(row[id_col], is_system_weapon, row[name_col], row[tech_col], row[role_col])
                weapon.fly_speed = row[speed_col]
                weapon.tracking = row[tracking_col]
                weapon.accuracy = row[acc_col]
                weapon.turn_rate = row[turn_col]
                weapon.special_effect_1 = row[primary_str]
                weapon.special_effect_1_hl = row[primary_str + 1]
                weapon.special_effect_2 = row[primary_str + 2]
                weapon.special_effect_2_hl = row[primary_str + 3]
                weapon_desc = weapon_descriptions.get(row[id_col])
                if weapon_desc is not None:
                    weapon.description = weapon_desc["description"]
                    weapon.desc_foot_note = weapon_desc["desc_foot_note"]
                result[row[id_col]] = weapon
            return result
        except OSError:
            logging.warning("file(%s) read failed", file_path)
            return {}
        except ValueError:
            logging.warning("file(%s) parse failed,wrong encoding", file_path)
            return {}

    @staticmethod
    def parse_metadata(mod_path) -> (ModInfo, dict):
        file_path = mod_path + r"\mod_info.json"
        try:
            # read file
            file_strs = ModParser.__read_text_file(file_path)
            # remove all #-leading annotations
            json_strs = ModParser.__erase_hash_comment(file_strs)

            info_json: dict = json5.loads(''.join(json_strs))
            metadata = ModInfo(info_json["id"], info_json["name"])
            metadata.game_version = info_json["gameVersion"]
            mod_version = info_json.get("version")
            if mod_version:
                if isinstance(mod_version, str):
                    metadata.version = mod_version
                elif isinstance(mod_version, dict):
                    metadata.version = ".".join(mod_version.values())
            if info_json.get("author"):
                metadata.author = info_json["author"]
            if info_json.get("description"):
                metadata.description = info_json["description"]
            return metadata, info_json
        except OSError:
            return None, None

    @staticmethod
    def __erase_hash_comment(lines: list[str]) -> list[str]:
        result = []
        # removes hashtag#-leading comments
        for line in lines:
            hashtag_index = len(line)
            quote_stack = deque()
            for i in range(0, len(line)):
                if line[i] == '#' and len(quote_stack) == 0:
                    hashtag_index = i
                    break
                elif line[i] == "'":
                    if "'" in quote_stack:
                        while "'" in quote_stack:
                            quote_stack.pop()
                    else:
                        quote_stack.append("'")
                elif line[i] == '"':
                    if '"' in quote_stack:
                        while '"' in quote_stack:
                            quote_stack.pop()
                    else:
                        quote_stack.append('"')
            result.append(line[0: hashtag_index])
        return result

    @staticmethod
    def __read_text_file(file_path, strict_mode=True) -> list[str]:
        common_encodings = ["gbk", "utf-8", "latin_1", ]
        error = "strict" if strict_mode else "ignore"
        with open(file_path, "rb") as binary_file:
            encoding_check = chardet.detect(binary_file.read())
            encoding = encoding_check["encoding"]
            confidence = encoding_check["confidence"]
        if confidence > 0.9:
            try:
                file = open(file_path, "rt", encoding=encoding, errors=error)
                return file.readlines()
            except Exception as e:
                print(e)
                raise ValueError("encoding error:incorrect encoding,file not read")
        else:
            for encoding in common_encodings:
                file = open(file_path, "rt", encoding=encoding, errors=error)
                try:
                    lines = file.readlines()
                    return lines
                except Exception as e:
                    file.close()
            raise ValueError("encoding error:incorrect encoding,file not read")
