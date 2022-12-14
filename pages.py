from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

import prototypes
from parse import ModParser


class ModMetaPage(QWidget):
    def __init__(self, parent, ui_str: dict, data_holder: prototypes.DataHolder):
        super().__init__(parent=parent)
        self.ui_str = ui_str
        self.data_holder = data_holder
        self.mod_meta = self.data_holder.metadata

        self.is_edited = False
        self.translate_data = {}
        self.translate_block = self

        self.get_data()

        self._setup_ui()

        self.update_ui()

    def __text_changed(self):
        self.is_edited = True

    def get_data(self, force_update=False):

        if self.data_holder.metadata is None:
            try:
                self.data_holder.metadata = ModParser.parse_metadata(self.data_holder.mod_path)[0]
            except ValueError:
                QMessageBox().warning(self, "", self.ui_str["msg_file_parse_failed"], QMessageBox.Close,
                                      QMessageBox.Close)
        if self.data_holder.translates:
            self.translate_data = self.data_holder.translates["MOD_META"]

    def _setup_ui(self):
        main_layout = QVBoxLayout()
        # main_title
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignHCenter)
        self.title_label.setAlignment(Qt.AlignHCenter)
        main_layout.addWidget(self.title_label)

        # name
        temp_widget = QLabel(self.ui_str["mod_name"])
        main_layout.addWidget(temp_widget)

        self.name_display = QLineEdit()
        self.name_display.setAlignment(Qt.AlignRight)
        self.name_display.setReadOnly(True)
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self.__text_changed)
        sub_layout = QHBoxLayout()
        sub_layout.addWidget(self.name_display, stretch=1)
        sub_layout.addWidget(self.name_edit, stretch=1)
        main_layout.addLayout(sub_layout)

        self.version_display = QLabel()
        self.version_display.setAlignment(Qt.AlignHCenter)
        self.version_display.setAlignment(Qt.AlignHCenter)
        main_layout.addWidget(self.version_display)

        self.author_display = QLabel()
        self.author_display.setAlignment(Qt.AlignHCenter)
        self.author_display.setAlignment(Qt.AlignHCenter)
        self.author_display.setWordWrap(True)
        main_layout.addWidget(self.author_display)

        temp_widget = QLabel(self.ui_str["mod_description"])
        main_layout.addWidget(temp_widget)
        self.desc_display = QTextEdit()
        self.desc_display.setReadOnly(True)
        self.desc_edit = QTextEdit()
        self.desc_edit.textChanged.connect(self.__text_changed)
        sub_layout = QHBoxLayout()
        sub_layout.addWidget(self.desc_display, stretch=1)
        sub_layout.addWidget(self.desc_edit, stretch=1)
        main_layout.addLayout(sub_layout)

        self.btn_save = QPushButton(self.ui_str["btn_save"])
        self.btn_save.clicked.connect(self.save_translation)
        main_layout.addWidget(self.btn_save)

        self.setLayout(main_layout)

    def update_ui(self):
        mod_info = self.data_holder.metadata
        if mod_info:
            self.title_label.setText(self.ui_str["now_editing"] + self.data_holder.metadata.id)
            self.version_display.setText(self.ui_str["mod_version"] + self.data_holder.metadata.version)
            self.author_display.setText(self.ui_str["mod_author"] + self.data_holder.metadata.author)
            self.name_display.setText(mod_info.name)
            self.version_display.setVisible(bool(mod_info.version))
            self.author_display.setVisible(bool(mod_info.author))
            if mod_info.description:
                self.desc_display.setText(mod_info.description)
                self.desc_edit.setReadOnly(False)
            else:
                self.desc_display.setText(self.ui_str["no_text_here"])
                self.desc_edit.setReadOnly(True)
            # translates
            if self.translate_data.get("name"):
                self.name_edit.setText(self.translate_data["name"])
            else:
                self.name_edit.setText("")
            if self.translate_data.get("description"):
                self.desc_edit.setText(self.translate_data["description"])
            else:
                self.desc_edit.setText("")
            self.is_edited = False
        else:
            self.title_label.setText(self.ui_str["msg_file_not_found"].format(file_name="mod_info.json"))
            self.version_display.setText(self.ui_str["mod_version"])
            self.author_display.setText(self.ui_str["mod_author"])
            self.name_display.setText("")
            self.desc_display.setText("")
            self.name_edit.setText("")
            self.desc_edit.setText("")
            self.is_edited = False

    def save_translation(self):
        if self.is_edited:
            translate = {"id": self.data_holder.metadata.id,
                         "name": self.name_edit.text(),
                         "description": self.desc_edit.toPlainText()}
            self.data_holder.translates["MOD_META"] = translate
            self.translate_data = translate
            QMessageBox().information(self, "", self.ui_str["msg_save_success"], QMessageBox.Close, QMessageBox.Close)
            self.is_edited = False
            return True
        else:
            return False

    def update(self) -> None:
        self.get_data(force_update=True)
        self.update_ui()


class ShipHullListPage(QWidget):
    def __init__(self, parent, ui_str: dict, data_holder: prototypes.DataHolder):
        super().__init__(parent=parent)
        self.ui_str = ui_str
        self.data_holder = data_holder
        self.hull_id_list = []

        self.get_data()

        self._setup_ui()

        self.update_ui()

    def update(self) -> None:
        self.get_data(force_update=True)
        self.update_ui()

    def get_data(self, force_update: bool = False):
        if self.data_holder.descriptions is None or force_update:
            self.data_holder.descriptions = ModParser.parse_descriptions(self.data_holder.mod_path)
        if self.data_holder.ship_hulls is None or force_update:
            self.data_holder.ship_hulls = ModParser.parse_hulls(self.data_holder.mod_path,
                                                                self.data_holder.descriptions.get("SHIP"))
        self.hull_id_list = list(self.data_holder.ship_hulls.keys())

    def _setup_ui(self):
        main_layout = QHBoxLayout()
        splitter = QSplitter(self)
        # left_panel
        self.hull_list = QListWidget()
        self.hull_list.itemClicked.connect(self._hull_list_clicked)
        for hull_id in self.data_holder.ship_hulls.keys():
            self.hull_list.addItem(hull_id)
        # right_main
        self.translate_block = ShipHullTranslateBlock(self, self.ui_str, data_holder=self.data_holder)
        # right_under
        self.prev_button = QPushButton()
        self.prev_button.setText(self.ui_str["btn_prev"])
        self.prev_button.clicked.connect(self._prev_clicked)
        self.next_button = QPushButton()
        self.next_button.setText(self.ui_str["btn_next"])
        self.next_button.clicked.connect(self._next_clicked)
        self.save_button = QPushButton()
        self.save_button.setText(self.ui_str["btn_save"])
        self.save_button.clicked.connect(self._save_clicked)

        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.prev_button)
        temp_layout.addSpacing(1)
        temp_layout.addWidget(self.save_button)
        temp_layout.addSpacing(1)
        temp_layout.addWidget(self.next_button)

        right_panel = QFrame()
        right_panel_layout = QVBoxLayout()

        right_scroll = QScrollArea(self)
        right_scroll.setMinimumSize(600, 400)
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        right_scroll.setWidgetResizable(True)
        right_scroll.setWidget(self.translate_block)
        right_panel_layout.addWidget(right_scroll, stretch=1)
        right_panel_layout.addLayout(temp_layout)
        right_panel.setLayout(right_panel_layout)

        splitter.addWidget(self.hull_list)
        splitter.addWidget(right_panel)
        main_layout.addWidget(splitter)

        self.setLayout(main_layout)

    def update_ui(self):
        self.hull_list.clear()
        for hull_id in self.data_holder.ship_hulls.keys():
            self.hull_list.addItem(hull_id)
        if len(self.hull_id_list) > 0:
            self.translate_block.load_data(self.data_holder.ship_hulls[self.hull_id_list[0]],
                                           self.data_holder.translates["SHIP"].get(self.hull_id_list[0]))

    def _hull_list_clicked(self, item):
        hull_id = item.text()
        if hull_id != self.translate_block.hull.id:
            if self.__check_jump_without_saving():
                self.translate_block.load_data(self.data_holder.ship_hulls[hull_id],
                                               self.data_holder.translates["SHIP"].get(hull_id))

    def _prev_clicked(self):
        now_id = self.translate_block.hull.id
        now_index = self.hull_id_list.index(now_id)
        # already top
        if now_index == 0:
            QMessageBox.question(self, "", self.ui_str["msg_first_in_list"],
                                 QMessageBox.Close, QMessageBox.Close)
        else:
            if self.__check_jump_without_saving():
                prev_id = self.hull_id_list[now_index - 1]
                self.hull_list.setCurrentRow(now_index - 1)
                self.translate_block.load_data(self.data_holder.ship_hulls[prev_id],
                                               self.data_holder.translates["SHIP"].get(prev_id))

    def _next_clicked(self):
        now_id = self.translate_block.hull.id
        now_index = self.hull_id_list.index(now_id)
        # already bottom
        if now_index >= len(self.hull_id_list) - 1:
            QMessageBox.question(self, "", self.ui_str["msg_last_in_list"],
                                 QMessageBox.Close, QMessageBox.Close)
        else:
            if self.__check_jump_without_saving():
                next_id = self.hull_id_list[now_index + 1]
                self.hull_list.setCurrentRow(now_index + 1)
                self.translate_block.load_data(self.data_holder.ship_hulls[next_id],
                                               self.data_holder.translates["SHIP"].get(next_id))

    def _save_clicked(self):
        self.translate_block.save_translation()

    def __check_jump_without_saving(self) -> bool:
        if self.translate_block.is_edited:
            reply = QMessageBox.question(self, "", self.ui_str["msg_unsaved_open_new"],
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                return True
            else:
                return False
        return True


class ShipHullTranslateBlock(QWidget):
    def __init__(self, parent, ui_str: dict, data_holder: prototypes.DataHolder):
        super().__init__(parent=parent)
        self.ui = ui_str
        self.data_holder = data_holder
        self.hull = None
        self.translate_data = {}
        self.is_edited = False
        self.edit_boxes = {}
        self.original_text = {}
        self.groups_def = {
            "name": (self.ui["hull_name"], QLineEdit),
            "tech": (self.ui["tech_manufacturer"], QLineEdit),
            "role": (self.ui["hull_designation"], QLineEdit),
            "desc_long": (self.ui["description"], QTextEdit),
            "desc_short": (self.ui["description_short"], QTextEdit),
            "desc_fleet": (self.ui["desc_in_fleet"], QTextEdit),
        }

        self._setup_ui(ui_str=ui_str)

    def _setup_ui(self, ui_str):
        layout = QVBoxLayout()
        # header
        self.title_label = QLabel()
        layout.addWidget(self.title_label)

        entry_layout = QVBoxLayout()

        for key, group in self.groups_def.items():
            entry_label = QLabel()
            entry_label.setText(group[0])
            entry_layout.addWidget(entry_label)

            origin_text = group[1]()
            origin_text.setReadOnly(True)
            edit_panel = group[1]()

            edit_panel.textChanged.connect(self.__text_changed)
            if isinstance(edit_panel, QLineEdit):
                origin_text.setAlignment(Qt.AlignTop)
                origin_text.setAlignment(Qt.AlignRight)
            elif isinstance(edit_panel, QTextEdit):
                origin_text.setAlignment(Qt.AlignTop)
                origin_text.setAlignment(Qt.AlignLeft)

            temp = QHBoxLayout()
            temp.addWidget(origin_text, stretch=1)
            temp.addWidget(edit_panel, stretch=1)

            self.original_text[key] = origin_text
            self.edit_boxes[key] = edit_panel
            entry_layout.addLayout(temp)

        layout.addLayout(entry_layout)

        self.setLayout(layout)

    def load_data(self, ship_hull: prototypes.ShipHull, translate: dict | None = None):
        # update internal data
        self.hull = ship_hull
        if translate is not None:
            self.translate_data = translate
        else:
            self.translate_data = {}
        # change texts
        self.title_label.setText(self.ui["now_editing"] + " " + self.hull.id)
        for key, label in self.original_text.items():
            text = self.hull.__getattribute__(key)
            if not text:
                self.edit_boxes[key].setReadOnly(True)
                label.setText(self.ui["no_text_here"])
            else:
                label.setText(text)
                self.edit_boxes[key].setReadOnly(False)
            translate = self.translate_data.get(key)
            if translate is not None:
                self.edit_boxes[key].setText(translate)
            else:
                self.edit_boxes[key].setText("")
        # restore edit states
        self.is_edited = False

    def __text_changed(self):
        if not self.is_edited:
            self.is_edited = True

    def save_translation(self) -> bool:
        if self.is_edited:
            for key, edit in self.edit_boxes.items():
                if isinstance(edit, QLineEdit):
                    self.translate_data[key] = edit.text()
                elif isinstance(edit, QTextEdit):
                    self.translate_data[key] = edit.toPlainText()
            self.data_holder.translates["SHIP"][self.hull.id] = self.translate_data
            QMessageBox.question(self, "", self.ui["msg_save_success"], QMessageBox.Close, QMessageBox.Close)
            self.is_edited = False
            return True
        return False


class WeaponListPage(QWidget):
    def __init__(self, parent, ui_str: dict, data_holder: prototypes.DataHolder):
        super().__init__(parent=parent)
        self.ui_str = ui_str
        self.data_holder = data_holder
        self.weapon_id_list = []

        self.get_data()

        self._setup_ui()

        if len(self.weapon_id_list) > 0:
            self.translate_block.load_data(self.data_holder.weapons[self.weapon_id_list[0]],
                                           self.data_holder.translates.get(self.weapon_id_list[0]))

    def get_data(self, force_update: bool = False):
        if self.data_holder.descriptions is None or force_update:
            self.data_holder.descriptions = ModParser.parse_descriptions(self.data_holder.mod_path)
        if self.data_holder.weapons is None or force_update:
            self.data_holder.weapons = ModParser.parse_weapons(self.data_holder.mod_path,
                                                               self.data_holder.descriptions.get("WEAPON"))
        self.weapon_id_list = list(self.data_holder.weapons.keys())

    def _setup_ui(self):
        main_layout = QHBoxLayout()
        splitter = QSplitter(self)
        # left_panel
        self.weapon_list = QListWidget()
        self.weapon_list.itemClicked.connect(self._list_clicked)
        for weapon_id in self.data_holder.weapons.keys():
            self.weapon_list.addItem(weapon_id)
        # right_main
        self.translate_block = WeaponTranslateBlock(self, self.ui_str, data_holder=self.data_holder)
        # right_under
        self.prev_button = QPushButton()
        self.prev_button.setText(self.ui_str["btn_prev"])
        self.prev_button.clicked.connect(self._prev_clicked)
        self.next_button = QPushButton()
        self.next_button.setText(self.ui_str["btn_next"])
        self.next_button.clicked.connect(self._next_clicked)
        self.save_button = QPushButton()
        self.save_button.setText(self.ui_str["btn_save"])
        self.save_button.clicked.connect(self._save_clicked)

        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.prev_button)
        temp_layout.addSpacing(1)
        temp_layout.addWidget(self.save_button)
        temp_layout.addSpacing(1)
        temp_layout.addWidget(self.next_button)

        right_panel = QFrame()
        right_panel_layout = QVBoxLayout()

        right_scroll = QScrollArea(self)
        right_scroll.setMinimumSize(600, 400)
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        right_scroll.setWidgetResizable(True)
        right_scroll.setWidget(self.translate_block)
        right_panel_layout.addWidget(right_scroll, stretch=1)
        right_panel_layout.addLayout(temp_layout)
        right_panel.setLayout(right_panel_layout)

        splitter.addWidget(self.weapon_list)
        splitter.addWidget(right_panel)
        main_layout.addWidget(splitter)

        self.setLayout(main_layout)

    def update_ui(self):
        self.weapon_list.clear()
        for hull_id in self.data_holder.ship_hulls.keys():
            self.weapon_list.addItem(hull_id)
        if len(self.weapon_list) > 0:
            self.translate_block.load_data(self.data_holder.weapons[self.weapon_id_list[0]],
                                           self.data_holder.translates["WEAPON"].get(self.weapon_id_list[0]))

    def _list_clicked(self, item):
        item_id = item.text()
        if item_id != self.translate_block.weapon.id:
            if self.__check_jump_without_saving():
                self.translate_block.load_data(self.data_holder.weapons[item_id],
                                               self.data_holder.translates["WEAPON"].get(item_id))

    def _prev_clicked(self):
        now_id = self.translate_block.weapon.id
        now_index = self.weapon_id_list.index(now_id)
        # already top
        if now_index == 0:
            QMessageBox.question(self, "", self.ui_str["msg_first_in_list"],
                                 QMessageBox.Close, QMessageBox.Close)
        else:
            if self.__check_jump_without_saving():
                prev_id = self.weapon_id_list[now_index - 1]
                self.weapon_list.setCurrentRow(now_index - 1)
                self.translate_block.load_data(self.data_holder.weapons[prev_id],
                                               self.data_holder.translates["WEAPON"].get(prev_id))

    def _next_clicked(self):
        now_id = self.translate_block.weapon.id
        now_index = self.weapon_id_list.index(now_id)
        # already bottom
        if now_index >= len(self.weapon_id_list) - 1:
            QMessageBox.question(self, "", self.ui_str["msg_last_in_list"],
                                 QMessageBox.Close, QMessageBox.Close)
        else:
            if self.__check_jump_without_saving():
                next_id = self.weapon_id_list[now_index + 1]
                self.weapon_list.setCurrentRow(now_index + 1)
                self.translate_block.load_data(self.data_holder.weapons[next_id],
                                               self.data_holder.translates["WEAPON"].get(next_id))

    def _save_clicked(self):
        self.translate_block.save_translation()

    def __check_jump_without_saving(self) -> bool:
        if self.translate_block.is_edited:
            reply = QMessageBox.question(self, "", self.ui_str["msg_unsaved_open_new"],
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                return True
            else:
                return False
        return True

    def update(self) -> None:
        self.get_data(True)
        self.update_ui()


class WeaponTranslateBlock(QWidget):
    def __init__(self, parent, ui_str: dict, data_holder: prototypes.DataHolder):
        super().__init__(parent=parent)
        self.ui = ui_str
        self.data_holder = data_holder
        self.weapon = None
        self.translate_data = {}
        self.is_edited = False
        self.edit_boxes = {}
        self.original_text = {}
        self.groups_def = {
            "name": (self.ui["weapon_name"], QLineEdit),
            "tech": (self.ui["tech_manufacturer"], QLineEdit),
            "role": (self.ui["weapon_role"], QLineEdit),
            "accuracy": (self.ui["accuracy"], QLineEdit),
            "fly_speed": (self.ui["fly_speed"], QLineEdit),
            "tracking": (self.ui["tracking"], QLineEdit),
            "turn_rate": (self.ui["turn_rate"], QLineEdit),
            "description": (self.ui["description"], QTextEdit),
            "desc_foot_note": (self.ui["desc_foot_note"], QTextEdit),
        }

        self._setup_ui(ui_str=ui_str)

    def _setup_ui(self, ui_str):
        layout = QVBoxLayout()
        # header
        self.title_label = QLabel()
        layout.addWidget(self.title_label)

        entry_layout = QVBoxLayout()

        for key, group in self.groups_def.items():
            entry_label = QLabel()
            entry_label.setText(group[0])
            entry_layout.addWidget(entry_label, alignment=Qt.AlignLeft | Qt.AlignHCenter)

            origin_text = group[1]()
            origin_text.setReadOnly(True)
            edit_panel = group[1]()

            edit_panel.textChanged.connect(self.__text_changed)
            if isinstance(edit_panel, QLineEdit):
                origin_text.setAlignment(Qt.AlignTop)
                origin_text.setAlignment(Qt.AlignRight)
            elif isinstance(edit_panel, QTextEdit):
                origin_text.setAlignment(Qt.AlignTop)
                origin_text.setAlignment(Qt.AlignLeft)

            temp = QHBoxLayout()
            temp.addWidget(origin_text, stretch=1)
            temp.addWidget(edit_panel, stretch=1)

            self.original_text[key] = origin_text
            self.edit_boxes[key] = edit_panel
            entry_layout.addLayout(temp)
        # custom primary
        entry_label = QLabel()
        entry_label.setText(self.ui["hint_double_quote_hilight"])
        entry_layout.addWidget(entry_label)
        entry_label = QLabel()
        entry_label.setText(self.ui["custom_primary"])
        entry_layout.addWidget(entry_label)

        origin_text = QTextEdit()
        origin_text.setReadOnly(True)
        edit_panel = QTextEdit()

        edit_panel.textChanged.connect(self.__text_changed)
        origin_text.setAlignment(Qt.AlignTop)
        origin_text.setAlignment(Qt.AlignLeft)

        self.original_text["special_effect_1"] = origin_text
        self.edit_boxes["special_effect_1"] = edit_panel
        temp = QHBoxLayout()
        temp.addWidget(origin_text, stretch=1)
        temp.addWidget(edit_panel, stretch=1)
        entry_layout.addLayout(temp)
        # custom secondary
        entry_label = QLabel()
        entry_label.setText(self.ui["custom_ancillary"])
        entry_layout.addWidget(entry_label)

        origin_text = QTextEdit()
        origin_text.setReadOnly(True)
        edit_panel = QTextEdit()

        edit_panel.textChanged.connect(self.__text_changed)
        origin_text.setAlignment(Qt.AlignTop)
        origin_text.setAlignment(Qt.AlignLeft)

        self.original_text["special_effect_2"] = origin_text
        self.edit_boxes["special_effect_2"] = edit_panel
        temp = QHBoxLayout()
        temp.addWidget(origin_text, stretch=1)
        temp.addWidget(edit_panel, stretch=1)
        entry_layout.addLayout(temp)

        layout.addLayout(entry_layout)

        self.setLayout(layout)

    def load_data(self, weapon: prototypes.Weapon, translate: dict | None = None):
        # update internal data
        self.weapon = weapon
        if translate is not None:
            self.translate_data = translate
        else:
            self.translate_data = {}
        # change text
        self.title_label.setText(self.ui["now_editing"] + " " + self.weapon.id)
        for key, label in self.original_text.items():
            text = self.weapon.__getattribute__(key)
            if text is None or len(text) == 0:
                self.edit_boxes[key].setReadOnly(True)
                label.setText(self.ui["no_text_here"])
            else:
                label.setText(text)
                self.edit_boxes[key].setReadOnly(False)
            translate = self.translate_data.get(key)
            if translate is not None:
                self.edit_boxes[key].setText(translate)
            else:
                self.edit_boxes[key].setText("")

        # special texts
        text = self.weapon.special_effect_1_display
        if len(text) == 0:
            self.original_text["special_effect_1"].setText("--no text here--")
            self.edit_boxes["special_effect_1"].setReadOnly(True)
        else:
            self.original_text["special_effect_1"].setText(text)
            self.edit_boxes["special_effect_1"].setReadOnly(False)
        translate = self.translate_data.get("special_effect_1")
        if translate is not None:
            self.edit_boxes["special_effect_1"].setText(translate)
        else:
            self.edit_boxes["special_effect_1"].setText("")

        text = self.weapon.special_effect_2_display
        if len(text) == 0:
            self.original_text["special_effect_2"].setText("--no text here--")
            self.edit_boxes["special_effect_2"].setReadOnly(True)
        else:
            self.original_text["special_effect_2"].setText(text)
            self.edit_boxes["special_effect_2"].setReadOnly(False)
        translate = self.translate_data.get("special_effect_2")
        if translate is not None:
            self.edit_boxes["special_effect_2"].setText(translate)
        else:
            self.edit_boxes["special_effect_2"].setText("")
        # restore edit states
        self.is_edited = False

    def __text_changed(self):
        if not self.is_edited:
            self.is_edited = True

    def save_translation(self) -> bool:
        if self.is_edited:
            for key, edit in self.edit_boxes.items():
                if isinstance(edit, QLineEdit):
                    self.translate_data[key] = edit.text()
                elif isinstance(edit, QTextEdit):
                    self.translate_data[key] = edit.toPlainText()
            self.data_holder.translates["WEAPON"][self.weapon.id] = self.translate_data
            QMessageBox.question(self, "", self.ui["msg_save_success"], QMessageBox.Close, QMessageBox.Close)
            self.is_edited = False
            return True
        return False


class ShipSystemListPage(QWidget):
    def __init__(self, parent, ui_str: dict, data_holder: prototypes.DataHolder):
        super().__init__(parent=parent)
        self.ui_str = ui_str
        self.data_holder = data_holder
        self.shipsystem_id_list = []

        self.get_data()
        self._setup_ui()

        self.update_ui()

    def get_data(self, force_update: bool = False):
        if self.data_holder.descriptions is None or force_update:
            self.data_holder.descriptions = ModParser.parse_descriptions(self.data_holder.mod_path)
        if self.data_holder.ship_systems is None or force_update:
            self.data_holder.ship_systems = ModParser.parse_ship_systems(self.data_holder.mod_path,
                                                                         self.data_holder.descriptions.get(
                                                                             "SHIP_SYSTEM"))
        self.shipsystem_id_list = list(self.data_holder.ship_systems.keys())

    def _setup_ui(self):
        main_layout = QHBoxLayout()
        splitter = QSplitter(self)
        # left_panel
        self.ship_system_list = QListWidget()
        self.ship_system_list.itemClicked.connect(self._ship_system_list_clicked)
        for ship_system_id in self.data_holder.ship_systems.keys():
            self.ship_system_list.addItem(ship_system_id)
        # right_main
        self.translate_block = ShipSystemTranslateBlock(self, self.ui_str, data_holder=self.data_holder)
        # right_under
        self.prev_button = QPushButton()
        self.prev_button.setText(self.ui_str["btn_prev"])
        self.prev_button.clicked.connect(self._prev_clicked)
        self.next_button = QPushButton()
        self.next_button.setText(self.ui_str["btn_next"])
        self.next_button.clicked.connect(self._next_clicked)
        self.save_button = QPushButton()
        self.save_button.setText(self.ui_str["btn_save"])
        self.save_button.clicked.connect(self._save_clicked)

        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.prev_button)
        temp_layout.addSpacing(1)
        temp_layout.addWidget(self.save_button)
        temp_layout.addSpacing(1)
        temp_layout.addWidget(self.next_button)

        right_panel = QFrame()
        right_panel_layout = QVBoxLayout()

        right_scroll = QScrollArea(self)
        right_scroll.setMinimumSize(600, 400)
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        right_scroll.setWidgetResizable(True)
        right_scroll.setWidget(self.translate_block)
        right_panel_layout.addWidget(right_scroll, stretch=1)
        right_panel_layout.addLayout(temp_layout)
        right_panel.setLayout(right_panel_layout)

        splitter.addWidget(self.ship_system_list)
        splitter.addWidget(right_panel)
        main_layout.addWidget(splitter)

        self.setLayout(main_layout)

    def update_ui(self):
        self.ship_system_list.clear()
        for system_id in self.data_holder.ship_hulls.keys():
            self.ship_system_list.addItem(system_id)
        if len(self.ship_system_list) > 0:
            self.translate_block.load_data(self.data_holder.ship_systems[self.shipsystem_id_list[0]],
                                           self.data_holder.translates["SHIP_SYSTEM"].get(self.shipsystem_id_list[0]))

    def _ship_system_list_clicked(self, item):
        ship_system_id = item.text()
        if ship_system_id != self.translate_block.ship_system.id:
            if self.__check_jump_without_saving():
                self.translate_block.load_data(self.data_holder.ship_systems[ship_system_id],
                                               self.data_holder.translates["SHIP_SYSTEM"].get(ship_system_id))

    def _prev_clicked(self):
        now_id = self.translate_block.ship_system.id
        now_index = self.shipsystem_id_list.index(now_id)
        # already top
        if now_index == 0:
            QMessageBox.question(self, "", self.ui_str["msg_first_in_list"],
                                 QMessageBox.Close, QMessageBox.Close)
        else:
            if self.__check_jump_without_saving():
                prev_id = self.shipsystem_id_list[now_index - 1]
                self.ship_system_list.setCurrentRow(now_index - 1)
                self.translate_block.load_data(self.data_holder.ship_systems[prev_id],
                                               self.data_holder.translates["SHIP_SYSTEM"].get(prev_id))

    def _next_clicked(self):
        now_id = self.translate_block.ship_system.id
        now_index = self.shipsystem_id_list.index(now_id)
        # already bottom
        if now_index >= len(self.shipsystem_id_list) - 1:
            QMessageBox.question(self, "", self.ui_str["msg_last_in_list"],
                                 QMessageBox.Close, QMessageBox.Close)
        else:
            if self.__check_jump_without_saving():
                next_id = self.shipsystem_id_list[now_index + 1]
                self.ship_system_list.setCurrentRow(now_index + 1)
                self.translate_block.load_data(self.data_holder.ship_systems[next_id],
                                               self.data_holder.translates["SHIP_SYSTEM"].get(next_id))

    def _save_clicked(self):
        self.translate_block.save_translation()

    def __check_jump_without_saving(self) -> bool:
        if self.translate_block.is_edited:
            reply = QMessageBox.question(self, "", self.ui_str["msg_unsaved_open_new"],
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                return True
            else:
                return False
        return True

    def update(self) -> None:
        self.get_data(True)
        self.update_ui()


class ShipSystemTranslateBlock(QWidget):
    def __init__(self, parent, ui_str: dict, data_holder: prototypes.DataHolder):
        super().__init__(parent=parent)
        self.ui = ui_str
        self.data_holder = data_holder
        self.ship_system = None
        self.translate_data = {}
        self.is_edited = False
        self.edit_boxes = {}
        self.original_text = {}
        self.groups_def = {
            "name": (self.ui["system_name"], QLineEdit),
            "system_type": (self.ui["system_type"], QLineEdit),
            "desc_in_codex": (self.ui["desc_in_codex"], QTextEdit),
        }

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        # header
        self.title_label = QLabel()
        layout.addWidget(self.title_label)

        entry_layout = QVBoxLayout()

        for key, group in self.groups_def.items():
            entry_label = QLabel()
            entry_label.setText(group[0])
            entry_layout.addWidget(entry_label)

            origin_text = group[1]()
            origin_text.setReadOnly(True)
            edit_panel = group[1]()

            edit_panel.textChanged.connect(self.__text_changed)
            if isinstance(edit_panel, QLineEdit):
                origin_text.setAlignment(Qt.AlignTop)
                origin_text.setAlignment(Qt.AlignRight)
            elif isinstance(edit_panel, QTextEdit):
                origin_text.setAlignment(Qt.AlignTop)
                origin_text.setAlignment(Qt.AlignLeft)

            temp = QHBoxLayout()
            temp.addWidget(origin_text, stretch=1)
            temp.addWidget(edit_panel, stretch=1)

            self.original_text[key] = origin_text
            self.edit_boxes[key] = edit_panel
            entry_layout.addLayout(temp)

        # desc_on_ship
        entry_label = QLabel()
        entry_label.setText(self.ui["hint_double_quote_hilight"])
        entry_layout.addWidget(entry_label)
        entry_label = QLabel()
        entry_label.setText(self.ui["desc_on_ship"])
        entry_layout.addWidget(entry_label)

        origin_text = QTextEdit()
        origin_text.setReadOnly(True)
        edit_panel = QTextEdit()

        edit_panel.textChanged.connect(self.__text_changed)
        origin_text.setAlignment(Qt.AlignTop)
        origin_text.setAlignment(Qt.AlignLeft)

        self.original_text["desc_on_ship"] = origin_text
        self.edit_boxes["desc_on_ship"] = edit_panel
        temp = QHBoxLayout()
        temp.addWidget(origin_text, stretch=1)
        temp.addWidget(edit_panel, stretch=1)
        entry_layout.addLayout(temp)

        layout.addLayout(entry_layout)

        self.setLayout(layout)

    def load_data(self, ship_system: prototypes.ShipSystem, translate: dict | None = None):
        # update internal data
        self.ship_system = ship_system
        if translate is not None:
            self.translate_data = translate
        else:
            self.translate_data = {}
        # change texts

        self.title_label.setText(self.ui["now_editing"] + " " + self.ship_system.id)
        for key, label in self.original_text.items():
            text = self.ship_system.__getattribute__(key)
            if text is None or len(text) == 0:
                self.edit_boxes[key].setReadOnly(True)
                label.setText("--no text here--")
            else:
                label.setText(text)
                self.edit_boxes[key].setReadOnly(False)
            translate = self.translate_data.get(key)
            if translate is not None:
                self.edit_boxes[key].setText(translate)
            else:
                self.edit_boxes[key].setText("")

        # special texts
        if len(self.ship_system.desc_on_ship) == 0:
            self.original_text["desc_on_ship"].setText(self.ui["no_text_here"])
            self.edit_boxes["desc_on_ship"].setReadOnly(True)
        else:
            text = self.ship_system.desc_on_ship_display
            self.original_text["desc_on_ship"].setText(text)
            self.edit_boxes["desc_on_ship"].setReadOnly(False)
        translate = self.translate_data.get("desc_on_ship")
        if translate is not None:
            self.edit_boxes["desc_on_ship"].setText(translate)
        else:
            self.edit_boxes["desc_on_ship"].setText("")

        # restore edit states
        self.is_edited = False

    def __text_changed(self):
        if not self.is_edited:
            self.is_edited = True

    def save_translation(self) -> bool:
        if self.is_edited:
            for key, edit in self.edit_boxes.items():
                if isinstance(edit, QLineEdit):
                    self.translate_data[key] = edit.text()
                elif isinstance(edit, QTextEdit):
                    self.translate_data[key] = edit.toPlainText()
            self.data_holder.translates["SHIP_SYSTEM"][self.ship_system.id] = self.translate_data
            QMessageBox.question(self, "", self.ui["msg_save_success"], QMessageBox.Close, QMessageBox.Close)
            self.is_edited = False
            return True
        return False


class HullModListPage(QWidget):
    def __init__(self, parent, ui_str: dict, data_holder: prototypes.DataHolder):
        super().__init__(parent=parent)
        self.ui_str = ui_str
        self.data_holder = data_holder
        self.hullmod_id_list = []

        self.get_data()

        self._setup_ui()

        self.update_ui()

    def get_data(self, force_update: bool = False):
        if self.data_holder.hullmods is None or force_update:
            self.data_holder.hullmods = ModParser.parse_hullmods(self.data_holder.mod_path)
        self.hullmod_id_list = list(self.data_holder.hullmods.keys())

    def _setup_ui(self):
        main_layout = QHBoxLayout()
        splitter = QSplitter(self)
        # left_panel
        self.item_list = QListWidget()
        self.item_list.itemClicked.connect(self._list_clicked)
        for item_id in self.data_holder.hullmods.keys():
            self.item_list.addItem(item_id)
        # right_main
        self.translate_block = HullModTranslateBlock(self, self.ui_str, data_holder=self.data_holder)
        # right_under
        self.prev_button = QPushButton()
        self.prev_button.setText(self.ui_str["btn_prev"])
        self.prev_button.clicked.connect(self._prev_clicked)
        self.next_button = QPushButton()
        self.next_button.setText(self.ui_str["btn_next"])
        self.next_button.clicked.connect(self._next_clicked)
        self.save_button = QPushButton()
        self.save_button.setText(self.ui_str["btn_save"])
        self.save_button.clicked.connect(self._save_clicked)

        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.prev_button)
        temp_layout.addSpacing(1)
        temp_layout.addWidget(self.save_button)
        temp_layout.addSpacing(1)
        temp_layout.addWidget(self.next_button)

        right_panel = QFrame()
        right_panel_layout = QVBoxLayout()

        right_scroll = QScrollArea(self)
        right_scroll.setMinimumSize(600, 400)
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        right_scroll.setWidgetResizable(True)
        right_scroll.setWidget(self.translate_block)
        right_panel_layout.addWidget(right_scroll, stretch=1)
        right_panel_layout.addLayout(temp_layout)
        right_panel.setLayout(right_panel_layout)

        splitter.addWidget(self.item_list)
        splitter.addWidget(right_panel)
        main_layout.addWidget(splitter)

        self.setLayout(main_layout)

    def update_ui(self):
        self.item_list.clear()
        for system_id in self.data_holder.hullmods.keys():
            self.item_list.addItem(system_id)
        if len(self.item_list) > 0:
            self.translate_block.load_data(self.data_holder.hullmods[self.hullmod_id_list[0]],
                                           None)

    def _list_clicked(self, item):
        item_id = item.text()
        if item_id != self.translate_block.item.id:
            self._jump_to_item(item_id)

    def _jump_to_item(self, item_id):
        if self.__check_jump_without_saving():
            self.item_list.setCurrentRow(self.hullmod_id_list.index(item_id))
            self.translate_block.load_data(self.data_holder.hullmods[item_id],
                                           self.data_holder.translates["HULLMOD"].get(item_id))

    def _prev_clicked(self):
        now_id = self.translate_block.item.id
        now_index = self.hullmod_id_list.index(now_id)
        # already top
        if now_index <= 0:
            QMessageBox().information(self, "", self.ui_str["msg_first_in_list"],
                                      QMessageBox.Close, QMessageBox.Close)
        else:
            # jump to prev one
            self._jump_to_item(self.hullmod_id_list[now_index - 1])

    def _next_clicked(self):
        now_id = self.translate_block.item.id
        now_index = self.hullmod_id_list.index(now_id)
        # already bottom
        if now_index >= len(self.hullmod_id_list) - 1:
            QMessageBox().question(self, "", self.ui_str["msg_last_in_list"],
                                   QMessageBox.Close, QMessageBox.Close)
        else:
            self._jump_to_item(self.hullmod_id_list[now_index + 1])

    def _save_clicked(self):
        self.translate_block.save_translation()

    def __check_jump_without_saving(self) -> bool:
        if self.translate_block.is_edited:
            reply = QMessageBox().question(self, "", self.ui_str["msg_unsaved_open_new"],
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                return True
            else:
                return False
        return True

    def update(self) -> None:
        self.get_data(True)
        self.update_ui()


class HullModTranslateBlock(QWidget):
    def __init__(self, parent, ui_str: dict, data_holder: prototypes.DataHolder):
        super().__init__(parent=parent)
        self.ui = ui_str
        self.data_holder = data_holder
        self.item = None
        self.translate_data = {}
        self.is_edited = False
        self.edit_boxes = {}
        self.original_text = {}
        self.groups_def = {
            "name": (self.ui["hullmod_name"], QLineEdit),
            "description": (self.ui["hullmod_desc"], QTextEdit),
        }

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        # header
        self.title_label = QLabel()
        layout.addWidget(self.title_label)

        entry_layout = QVBoxLayout()

        for key, group in self.groups_def.items():
            entry_label = QLabel()
            entry_label.setText(group[0])
            entry_layout.addWidget(entry_label)

            origin_text = group[1]()
            origin_text.setReadOnly(True)
            edit_panel = group[1]()

            edit_panel.textChanged.connect(self.__text_changed)
            if isinstance(edit_panel, QLineEdit):
                origin_text.setAlignment(Qt.AlignTop)
                origin_text.setAlignment(Qt.AlignRight)
            elif isinstance(edit_panel, QTextEdit):
                origin_text.setAlignment(Qt.AlignTop)
                origin_text.setAlignment(Qt.AlignLeft)

            temp = QHBoxLayout()
            temp.addWidget(origin_text, stretch=1)
            temp.addWidget(edit_panel, stretch=1)

            self.original_text[key] = origin_text
            self.edit_boxes[key] = edit_panel
            entry_layout.addLayout(temp)

        layout.addLayout(entry_layout)
        self.setLayout(layout)

    def load_data(self, hullmod: prototypes.HullMod, translate: dict | None = None):
        # update internal data
        self.item = hullmod
        self.translate_data = translate or {}

        # change texts
        self.title_label.setText(self.ui["now_editing"] + " " + self.item.id)
        for key, label in self.original_text.items():
            text = self.item.__getattribute__(key)
            if text:
                label.setText(text)
                self.edit_boxes[key].setReadOnly(False)
            else:
                self.edit_boxes[key].setReadOnly(True)
                label.setText("--no text here--")
            translate = self.translate_data.get(key)
            if translate is None:
                self.edit_boxes[key].setText("")
            else:
                self.edit_boxes[key].setText(translate)
        # restore edit states
        self.is_edited = False

    def __text_changed(self):
        if not self.is_edited:
            self.is_edited = True

    def save_translation(self) -> bool:
        if self.is_edited:
            for key, edit in self.edit_boxes.items():
                if isinstance(edit, QLineEdit):
                    self.translate_data[key] = edit.text()
                elif isinstance(edit, QTextEdit):
                    self.translate_data[key] = edit.toPlainText()
            self.data_holder.translates["HULLMOD"][self.item.id] = self.translate_data
            QMessageBox().information(self, "", self.ui["msg_save_success"], QMessageBox.Close, QMessageBox.Close)
            self.is_edited = False
            return True
        return False
