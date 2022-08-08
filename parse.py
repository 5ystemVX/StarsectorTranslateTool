import codecs
import configparser
import csv
import os
import pprint

import chardet

from prototypes import *


def parse_ui_str(lang_file_path) -> dict:
    result = {}
    cf = configparser.ConfigParser()
    cf.read(lang_file_path,encoding="utf-8")

    keys = cf.options("LanguageDefinition")
    for key in keys:
        result[key] = cf.get("LanguageDefinition", key)
    return result


def parse_mod_data(mod_path):
    strings = parse_descriptions(mod_path)

    #   shipsystem = parse_ship_systems(mod_path, strings["SHIP_SYSTEM"])

    #  hulls = parse_hulls(mod_path, strings["SHIP"})

    weapons = parse_weapons(mod_path, strings["WEAPON"])

    print(strings)


def parse_descriptions(mod_path) -> dict:
    result = {
        "SHIP": {},
        "SHIP_SYSTEM": {},
        "WEAPON": {}
        # more
    }
    strings_file_path = mod_path + r"\data\strings\descriptions.csv"
    # check encoding
    try:
        with open(strings_file_path, "rb") as file:
            encoding_check = chardet.detect(file.read())
        with open(strings_file_path, "r", encoding=encoding_check["encoding"]) as csv_file:
            reader = csv.reader(csv_file)
            # separate headline
            headers = next(reader)
            id_col = headers.index("id")
            type_col = headers.index("type")
            for row in reader:
                # skip empty cols & annotation
                if len(row[id_col]) == 0 or row[0].startswith("#"):
                    continue
                # sort by type
                if row[type_col] == "SHIP":
                    # SHIP_HULL-Like desc
                    result["SHIP"][row[id_col]] = {"desc_full": row[2], "desc_short": row[3], "desc_fleet_info": row[4]}
                elif row[type_col] == "SHIP_SYSTEM":
                    result["SHIP_SYSTEM"][row[id_col]] = {"desc_in_codex": row[2], "type_in_codex": row[3],
                                                          "desc_on_ship": row[4], "hi_light": row[5]}
                elif row[type_col] == "WEAPON":
                    result["WEAPON"][row[id_col]] = {"desc_in_codex": row[2], "desc_quote": row[3]}
    except OSError:
        return {}
    return result


def parse_ship_systems(mod_path, shipsystem_descriptions) -> dict:
    result = {}
    file_path = mod_path + r"\data\shipsystems\ship_systems.csv"
    # check encoding
    try:
        with open(file_path, "rb") as file:
            encoding_check = chardet.detect(file.read())
        with open(file_path, "r", encoding=encoding_check["encoding"]) as csv_file:
            reader = csv.reader(csv_file)
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
                    system.desc_in_codex = system_desc["desc_in_codex"]
                    system.system_type = system_desc["type_in_codex"]
                    system.desc_on_ship = system_desc["desc_on_ship"]
                    system.highlight = system_desc["hi_light"]

                result[system_id] = system
    except OSError:
        return {}
    return result


def parse_hulls(mod_path, hull_descriptions) -> dict:
    result = {}
    file_path = mod_path + r"\data\hulls\ship_data.csv"
    try:
        with open(file_path, "rb") as file:
            encoding_check = chardet.detect(file.read())
        with open(file_path, "r", encoding=encoding_check["encoding"]) as csv_file:
            reader = csv.reader(csv_file)
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
                    hull.desc_long = hull_desc["desc_full"]
                    hull.desc_short = hull_desc["desc_short"]
                    hull.desc_fleet = hull_desc["desc_fleet_info"]
                result[row[id_col]] = hull
    except OSError:
        return {}
    return result


def parse_weapons(mod_path, weapon_descriptions) -> dict:
    result = {}
    file_path = mod_path + r"\data\weapons\weapon_data.csv"
    try:
        with open(file_path, "rb") as file:
            encoding_check = chardet.detect(file.read())
        with open(file_path, "r", encoding=encoding_check["encoding"]) as csv_file:
            reader = csv.reader(csv_file)
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
                    weapon.description = weapon_desc["desc_in_codex"]
                    weapon.desc_foot_note = weapon_desc["desc_quote"]
                result[row[id_col]] = weapon
    except OSError:
        return {}
    return result


if __name__ == '__main__':
    # # modpath = r"E:\MyProjects\StarsectorTraslateTool\testfiles\Hiigaran Descendants"
    # modpath = r"G:\[Games]\Starsector-0951aRC6\starsector-core"
    # parse_mod_data(mod_path=modpath)
    # pass

    a = parse_ui_str(r"E:\MyProjects\StarsectorTranslateTool\zh_cn.ini")
    print(a)