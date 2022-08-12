import csv
import json
import os.path
import re

import parse
from prototypes import DataHolder
import chardet


def export_data_as_translate(data_holder: DataHolder):
    file_path = data_holder.mod_path + r"/translation.translate"
    with open(file_path, "w", newline="", encoding="utf-8") as save_file:
        translates = DataHolder().translates
        for key, weapon in data_holder.weapons.items():
            translates["WEAPON"][key] = {
                "name": weapon.name,
                "tech": weapon.tech,
                "role": weapon.role,
                "accuracy": weapon.accuracy,
                "fly_speed": weapon.fly_speed,
                "tracking": weapon.tracking,
                "turn_rate": weapon.turn_rate,
                "description": weapon.description,
                "desc_foot_note": weapon.desc_foot_note,
                "special_effect_1": weapon.special_effect_1_trans,
                "special_effect_2": weapon.special_effect_2_trans
            }
        for key, hull in data_holder.ship_hulls.items():
            translates["SHIP"][key] = {
                "name": hull.hull_name,
                "tech": hull.tech_manufacturer,
                "role": hull.role,
                "desc_long": hull.desc_long,
                "desc_short": hull.desc_short,
                "desc_fleet": hull.desc_fleet
            }
        for key, system in data_holder.ship_systems.items():
            translates["SHIP_SYSTEM"][key] = {
                "name": system.name,
                "system_type": system.system_type,
                "desc_in_codex": system.desc_in_codex,
                "desc_on_ship": system.desc_on_ship_trans
            }

        save_file.write(json.dumps(translates))


# def inject_translations(data_holder: DataHolder, override=True):
#     ship_csv_path = inject_ship_hull_csv(data_holder)


def inject_ship_hull_csv(data_holder) -> str | None:
    """
    :param data_holder:
    :return: absolute path of temp csv
    """
    # inject ship_hull.csv:
    try:
        ship_csv_path = data_holder.mod_path + r"\data\hulls\ship_data.csv"
        temp_path = data_holder.mod_path + r"\translate\ship_hull.csv_new"
        make_translate_dir(data_holder.mod_path)
        with open(temp_path, "w", newline='',
                  encoding="utf-8") as translate_file:
            writer = csv.writer(translate_file)
            with open(ship_csv_path, "rb") as file:
                encoding_check = chardet.detect(file.read())
            with open(ship_csv_path, "r", encoding=encoding_check["encoding"]) as csv_file:
                reader = csv.reader(csv_file)
                header_row = next(reader)
                id_col = header_row.index("id")
                # write headers.
                writer.writerow(header_row)
                # write other rows
                for row in reader:
                    # empty row or annotation row
                    if row[0].startswith("#") or len(row[id_col]) == 0:
                        writer.writerow(row)
                        continue
                    else:
                        # check translation
                        translation = data_holder.translates["SHIP"].get(row[id_col])
                        if translation is not None:
                            translation_mapping = {
                                "hull_name": r"name",
                                "tech_manufacturer": r"tech/manufacturer",
                                "ship_designation": r"designation"
                            }
                            # change records
                            for key, value in translation_mapping.items():
                                if len(translation[key]) > 0:
                                    row[header_row.index(value)] = translation[key]
                        writer.writerow(row)
    except Exception as e:
        return None
    return temp_path


def inject_weapon_csv(data_holder) -> str | None:
    """
    :param data_holder:
    :return: absolute path of temp csv
    """
    # inject weapon_data.csv:
    try:
        origin_path = data_holder.mod_path + r"\data\weapons\weapon_data.csv"
        temp_path = data_holder.mod_path + r"/translate/weapon_data.csv_new"
        make_translate_dir(data_holder.mod_path)
        with open(temp_path, "w", newline='', encoding="utf-8") as translate_file:
            writer = csv.writer(translate_file)
            with open(origin_path, "rb") as file:
                encoding_check = chardet.detect(file.read())
            with open(origin_path, "r", encoding=encoding_check["encoding"]) as csv_file:
                reader = csv.reader(csv_file)
                header_row = next(reader)
                id_col = header_row.index("id")
                # write headers.
                writer.writerow(header_row)
                # write other rows
                for row in reader:
                    # empty row or annotation row
                    if row[0].startswith("#") or len(row[id_col]) == 0:
                        writer.writerow(row)
                        continue
                    else:
                        # check translation
                        translation = data_holder.translates["WEAPON"].get(row[id_col])
                        if translation is not None:
                            translation_mapping = {
                                "name": "name",
                                "tech": "tech/manufacturer",
                                "role": "primaryRoleStr",
                                "accuracy": "accuracyStr",
                                "fly_speed": "speedStr",
                                "tracking": "trackingStr",
                                "turn_rate": "turnRateStr"
                            }
                            # change records
                            for key, value in translation_mapping.items():
                                if len(translation[key]) > 0:
                                    row[header_row.index(value)] = translation[key]
                            if len(translation["special_effect_1"]) > 0:
                                hi_lights = " | ".join(re.findall(r"\{\{(.+?)\}\}", translation["special_effect_1"]))
                                text_origin = re.sub(r"\{\{.+?\}\}", "%s", translation["special_effect_1"])
                                row[header_row.index("customPrimary")] = text_origin
                                row[header_row.index("customPrimaryHL")] = hi_lights

                            if len(translation["special_effect_2"]) > 0:
                                hi_lights = " | ".join(re.findall(r"\{\{(.+?)\}\}", translation["special_effect_2"]))
                                text_origin = re.sub(r"\{\{.+?\}\}", "%s", translation["special_effect_2"])
                                row[header_row.index("customAncillary")] = text_origin
                                row[header_row.index("customAncillaryHL")] = hi_lights

                        writer.writerow(row)
    except Exception:
        return None
    return temp_path


def inject_shipsystem_csv(data_holder) -> str | None:
    """
        :param data_holder:
        :return: absolute path of temp csv
        """
    # inject ship_system.csv:
    try:
        csv_path = data_holder.mod_path + r"/data/shipsystems/ship_systems.csv"
        new_path = data_holder.mod_path + r"/translate/ship_systems.csv_new"
        make_translate_dir(data_holder.mod_path)
        with open(new_path, "w", newline='', encoding="utf-8") as translate_file:
            writer = csv.writer(translate_file)
            with open(csv_path, "rb") as file:
                encoding_check = chardet.detect(file.read())
            with open(csv_path, "r", encoding=encoding_check["encoding"]) as csv_file:
                reader = csv.reader(csv_file)
                header_row = next(reader)
                id_col = header_row.index("id")
                # write headers.
                writer.writerow(header_row)
                # write other rows
                for row in reader:
                    # empty row or annotation row
                    if row[0].startswith("#") or len(row[id_col]) == 0:
                        writer.writerow(row)
                        continue
                    else:
                        # check translation
                        translation = data_holder.translates["SHIP_SYSTEM"].get(row[id_col])
                        if translation is not None:
                            row[header_row.index("name")] = translation["name"]
                        writer.writerow(row)
    except Exception:
        return None
    return new_path


def inject_descriptions_csv(data_holder) -> str | None:
    try:
        csv_path = data_holder.mod_path + r"/data/strings/descriptions.csv"
        new_path = data_holder.mod_path + r"/translate/descriptions.csv_new"
        make_translate_dir(data_holder.mod_path)
        with open(new_path, "w", newline='', encoding="utf-8") as translate_file:
            writer = csv.writer(translate_file)
            with open(csv_path, "rb") as file:
                encoding_check = chardet.detect(file.read())
            with open(csv_path, "r", encoding=encoding_check["encoding"]) as csv_file:
                reader = csv.reader(csv_file)
                header_row = next(reader)
                id_col = header_row.index("id")
                type_col = header_row.index("type")
                # write headers.
                writer.writerow(header_row)
                # write other rows
                for row in reader:
                    # empty row or annotation row
                    if row[0].startswith("#") or len(row[id_col]) == 0:
                        writer.writerow(row)
                        continue
                    else:
                        translation = None
                        translation_group = data_holder.translates.get(row[type_col])
                        if translation_group is not None:
                            translation = translation_group.get(row[id_col])
                        if translation is not None:
                            if row[type_col] == "SHIP":
                                row[header_row.index("text1")] = translation["desc_long"]
                                row[header_row.index("text2")] = translation["desc_short"]
                                row[header_row.index("text3")] = translation["desc_fleet"]
                            elif row[type_col] == "WEAPON":
                                row[header_row.index("text1")] = translation["description"]
                                row[header_row.index("text2")] = translation["desc_foot_note"]
                            elif row[type_col] == "SHIP_SYSTEM":
                                row[header_row.index("text1")] = translation["desc_in_codex"]
                                row[header_row.index("text2")] = translation["system_type"]
                                if len(translation["desc_on_ship"]) > 0:
                                    hi_lights = " | ".join(re.findall(r"\{\{(.+?)\}\}", translation["desc_on_ship"]))
                                    text_origin = translation["desc_on_ship"].replace(r"{{", "").replace(r"}}", "")
                                    row[header_row.index("text3")] = text_origin
                                    try:
                                        row[header_row.index("text4")] = hi_lights
                                    except ValueError:
                                        pass
                        writer.writerow(row)
    except Exception as e:
        return None
    return new_path


def rewrite_mod_json(data_holder: DataHolder) -> str | None:
    translation = data_holder.translates.get("MOD_META")
    try:
        new_path = data_holder.mod_path + r"/translate/mod_info.json_new"
        info_json: dict = parse.ModParser.parse_metadata(data_holder.mod_path)[1]
        if info_json.get("name"):
            info_json["name"] = translation.get("name")
        if info_json.get("description"):
            info_json["description"] = translation.get("description")
        with open(new_path, "w", encoding="utf8") as file:
            json.dump(info_json, file)
        return new_path
    except Exception:
        return None


def make_translate_dir(mod_path):
    if not os.path.exists(mod_path + r"\translate\\"):
        os.mkdir(mod_path + r"\\translate\\")


if __name__ == '__main__':
    pass
