import json
import logging.config
import os
import shutil
import sys

import json5
from PyQt5.QtWidgets import QAction, QFileDialog

import inject
import parse
from pages import *
from prototypes import DataHolder


class AppMainWindow(QMainWindow):
    def __init__(self, parent=None):
        logging.basicConfig(filename="log.log", level=logging.INFO)
        super(AppMainWindow, self).__init__(parent)
        # properties

        self.data_holder = DataHolder()
        self.data_holder.mod_path = ""
        self.data_holder.game_root_path = ""

        self.data_holder.weapons = None
        self.data_holder.descriptions = None
        self.data_holder.ship_hulls = None
        self.data_holder.ship_skins = None

        self.data_holder.translates = {}

        if getattr(sys, "frozen", False):
            path = os.path.dirname(sys.executable)
        else:
            path = os.path.dirname(__file__)

        self.io_path = path

        self.ui_str = parse.parse_ui_str(os.path.join(path, "lang.ini"))
        self._init_gui(self.ui_str)

    def _init_gui(self, ui_str: dict):
        self.setWindowTitle(ui_str["wt_main"])
        # assemble menubar
        menu_bar = self.menuBar()

        menu_file = menu_bar.addMenu(ui_str["m_file"])

        temp = QAction(ui_str["m_file_load_mod"], self)
        temp.triggered.connect(self.load_mod)
        menu_file.addAction(temp)

        menu_file.addSeparator()
        temp = QAction(ui_str["m_file_import"], self)
        temp.triggered.connect(self.import_translates)
        menu_file.addAction(temp)
        temp = QAction(ui_str["m_file_export"], self)
        temp.triggered.connect(self.export_translates)
        menu_file.addAction(temp)
        temp = QAction(ui_str["m_file_export_original"], self)
        temp.triggered.connect(self.export_original)
        menu_file.addAction(temp)

        menu_file.addSeparator()
        temp = QAction(ui_str["m_file_apply"], self)
        temp.triggered.connect(self.apply_translation)
        menu_file.addAction(temp)

        menu_file.addSeparator()
        temp = QAction(ui_str["m_file_exit"], self)
        temp.triggered.connect(self.close)
        menu_file.addAction(temp)

        menu_edit = menu_bar.addMenu(ui_str["m_edit"])

        temp = QAction(ui_str["m_edit_metadata"], self)
        temp.triggered.connect(self._edit_mod_meta)
        menu_edit.addAction(temp)
        temp = QAction(ui_str["m_edit_ship"], self)
        temp.triggered.connect(self._edit_hulls)
        menu_edit.addAction(temp)
        temp = QAction(ui_str["m_edit_weapon"], self)
        temp.triggered.connect(self._edit_weapons)
        menu_edit.addAction(temp)
        temp = QAction(ui_str["m_edit_shipsystem"], self)
        temp.triggered.connect(self._edit_systems)
        menu_edit.addAction(temp)
        temp = QAction(ui_str["m_edit_hullmod"], self)
        temp.triggered.connect(self._edit_hullmods)
        menu_edit.addAction(temp)

        menu_about = menu_bar.addMenu(ui_str["m_about"])
        temp = QAction(ui_str["m_about_info"], self)
        temp.triggered.connect(self.show_about)
        menu_about.addAction(temp)

        self.load_mod()

        self.__turn_to_page(ModMetaPage, self.data_holder)

    def _edit_hulls(self):
        # not jump on its own
        if type(self.centralWidget()) == ShipHullListPage:
            return
        try:
            if getattr(self.centralWidget(), "translate_block", None).is_edited:
                reply = QMessageBox.question(self, "", self.ui_str["msg_unsaved_exit"],
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.No:
                    return
            self.__turn_to_page(ShipHullListPage, self.data_holder)
        except AttributeError:
            # doesn't have module that requires saving
            self.__turn_to_page(ShipHullListPage, self.data_holder)

    def _edit_mod_meta(self):
        # not jump on its own
        if type(self.centralWidget()) == ModMetaPage:
            return
        try:
            if getattr(self.centralWidget(), "translate_block", None).is_edited:
                reply = QMessageBox().question(self, "", self.ui_str["msg_unsaved_exit"],
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.No:
                    return
            self.__turn_to_page(ModMetaPage, self.data_holder)
        except AttributeError:
            # doesn't have module that requires saving
            self.__turn_to_page(ModMetaPage, self.data_holder)

    def _edit_weapons(self):
        # not jump on its own
        if type(self.centralWidget()) == WeaponListPage:
            return
        try:
            if getattr(self.centralWidget(), "translate_block").is_edited:
                reply = QMessageBox.question(self, "", self.ui_str["msg_unsaved_exit"],
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.No:
                    return
            self.__turn_to_page(WeaponListPage, self.data_holder)
        except AttributeError:
            # doesn't have module that requires saving
            self.__turn_to_page(WeaponListPage, self.data_holder)

    def _edit_systems(self):
        # not jump on its own
        if type(self.centralWidget()) == ShipSystemListPage:
            return
        try:
            if getattr(self.centralWidget(), "translate_block").is_edited:
                reply = QMessageBox.question(self, "", self.ui_str["msg_unsaved_exit"],
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.No:
                    return
            self.__turn_to_page(ShipSystemListPage, self.data_holder)
        except AttributeError:
            # doesn't have module that requires saving
            self.__turn_to_page(ShipSystemListPage, self.data_holder)

    def _edit_hullmods(self):
        # not jump on its own
        if type(self.centralWidget()) == HullModListPage:
            return
        try:
            if getattr(self.centralWidget(), "translate_block").is_edited:
                reply = QMessageBox().question(self, "", self.ui_str["msg_unsaved_exit"],
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.No:
                    return
            self.__turn_to_page(HullModListPage, self.data_holder)
        except AttributeError:
            # doesn't have module that requires saving
            self.__turn_to_page(HullModListPage, self.data_holder)

    def __turn_to_page(self, target_class: type, data_holder: DataHolder):
        self.setCentralWidget(target_class(self, self.ui_str, data_holder))

    def import_translates(self):
        translate_url = QFileDialog.getOpenFileName(self,
                                                    self.ui_str["wt_import_translate_file"],
                                                    self.io_path,
                                                    "*.translate")
        if translate_url[0]:
            self.io_path = os.path.dirname(translate_url[0])
            with open(translate_url[0], "r", encoding="utf-8") as file:
                translates = json5.load(file)
                self.data_holder.translates = translates
            QMessageBox().information(self, self.ui_str["wt_msg_success"], self.ui_str["msg_import_success"],
                                      QMessageBox.Close, QMessageBox.Close)
            if self.centralWidget() is not None:
                self.centralWidget().update()

    def export_translates(self):
        file_path = QFileDialog.getSaveFileName(self,
                                                self.ui_str["wt_export_translate_file"],
                                                self.io_path + "/" + self.ui_str[
                                                    "default_savefile_name"] + ".translate",
                                                "*.translate")
        if len(file_path[0]) == 0:
            # abort
            return
        else:
            with open(file_path[0], "w", encoding="utf-8") as save_file:
                save_file.write(json.dumps(self.data_holder.translates))

    def export_original(self):
        file_path = QFileDialog.getSaveFileName(self,
                                                self.ui_str["wt_export_translate_file"],
                                                self.io_path + "/" + self.ui_str[
                                                    "default_savefile_name"] + ".translate",
                                                "*.translate")
        if file_path[0]:
            mod_path = self.data_holder.mod_path
            # load all data
            if not self.data_holder.descriptions:
                desc = ModParser.parse_descriptions(mod_path)
                self.data_holder.descriptions = desc
            else:
                desc = self.data_holder.descriptions
            if not self.data_holder.weapons:
                self.data_holder.weapons = ModParser.parse_weapons(mod_path, desc["WEAPON"])
            if not self.data_holder.ship_hulls:
                self.data_holder.ship_hulls = ModParser.parse_hulls(mod_path, desc["SHIP"])
            if not self.data_holder.ship_systems:
                self.data_holder.ship_systems = ModParser.parse_ship_systems(mod_path, desc["SHIP_SYSTEM"])
            # write file
            inject.export_data_as_translate(file_path[0], self.data_holder)
            QMessageBox().information(self, self.ui_str["wt_msg_success"], self.ui_str["msg_save_success"],
                                      QMessageBox.Close, QMessageBox.Close)

    def load_mod(self):
        get_mod_path = QFileDialog.getExistingDirectory(self,
                                                        self.ui_str["wt_load_mod"],
                                                        self.io_path
                                                        )
        if get_mod_path:
            self.io_path = os.path.realpath(get_mod_path + r"/..")
            self.data_holder.clear()
            self.data_holder.mod_path = get_mod_path
            if self.centralWidget() is not None:
                self.centralWidget().update()

    def apply_translation(self):
        shutil.copy(self.data_holder.description_csv_path, self.data_holder.description_csv_path + "_old")
        shutil.copy(self.data_holder.weapon_csv_path, self.data_holder.weapon_csv_path + "_old")
        shutil.copy(self.data_holder.system_csv_path, self.data_holder.system_csv_path + "_old")
        shutil.copy(self.data_holder.hull_csv_path, self.data_holder.hull_csv_path + "_old")
        shutil.copy(self.data_holder.mod_info_path, self.data_holder.mod_info_path + "_old")
        try:
            temp = inject.inject_descriptions_csv(self.data_holder)
            shutil.copy(temp, self.data_holder.description_csv_path)

            temp = inject.inject_weapon_csv(self.data_holder)
            shutil.copy(temp, self.data_holder.weapon_csv_path)

            temp = inject.inject_shipsystem_csv(self.data_holder)
            shutil.copy(temp, self.data_holder.system_csv_path)

            temp = inject.inject_ship_hull_csv(self.data_holder)
            shutil.copy(temp, self.data_holder.hull_csv_path)

            temp = inject.rewrite_mod_json(self.data_holder)
            shutil.copy(temp, self.data_holder.mod_info_path)

            QMessageBox().information(self, self.ui_str["wt_msg_success"], self.ui_str["msg_apply_success"],
                                      QMessageBox.Close, QMessageBox.Close)
        except Exception:
            shutil.copy(self.data_holder.description_csv_path + "_old", self.data_holder.description_csv_path)
            shutil.copy(self.data_holder.weapon_csv_path + "_old", self.data_holder.weapon_csv_path)
            shutil.copy(self.data_holder.system_csv_path + "_old", self.data_holder.system_csv_path)
            shutil.copy(self.data_holder.hull_csv_path + "_old", self.data_holder.hull_csv_path)
            QMessageBox().critical(self, self.ui_str["wt_msg_fail"], self.ui_str["msg_apply_fail"],
                                   QMessageBox.Close, QMessageBox.Close)

    def show_about(self):
        about_info = """????????????:Sy5temVX(edgfih)\n\nversion 0.0.2"""
        QMessageBox.question(self, self.ui_str["m_about"], about_info, QMessageBox.Close, QMessageBox.Close)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = AppMainWindow()
    demo.show()
    sys.exit(app.exec_())
