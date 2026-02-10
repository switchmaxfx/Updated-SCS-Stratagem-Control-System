import sys
import time
import threading
import random
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QMessageBox, QFileDialog,
    QTabWidget, QDoubleSpinBox, QDialog, QListWidget, QListWidgetItem, QComboBox,
    QSizePolicy, QMenu, QCheckBox, QSlider
)
from PyQt6.QtGui import QIcon, QKeySequence, QPainter, QColor, QBrush, QAction
from PyQt6.QtCore import pyqtSignal, QObject, Qt, QTimer, QPoint

# --- Import necessary input libraries ---
import pyautogui
import pydirectinput
from pynput import keyboard, mouse

# --- Default Configuration ---
DEFAULT_STRATAGEM_ACTIVATION_DELAY = 0.08
DEFAULT_PYDIRECTINPUT_PAUSE = 0.05
DEFAULT_REMINDER_OPACITY = 0.8
PROFILES_DIR = "stratagem_profiles"

# Set the initial internal pause for the input library
pydirectinput.PAUSE = DEFAULT_PYDIRECTINPUT_PAUSE

# --- Helper function for PyInstaller to find resources ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Stratagem Data ---
ALL_STRATAGEMS = {
    # Mission Stratagems
    "Reinforce": "UDRLU",
    "Resupply": "DDUR",
    "SOS Beacon": "UDRU",
    "Super Earth Flag": "DUDU",
    "Hellbomb": "DULDURDU",
    "Seismic Probe": "UULRDD",
    "SSSD Delivery": "DDDUU",
    "Prospecting Drill": "DDLRDD",
    "Upload Data": "LRUUU",
    "Dark Fluid Vessel": "ULRDUU",
    "Tectonic Drill": "UDUDUD",
    "Hive Breaker Drill": "LUDRDD",
    "SEAF Artillery": "RUUD",
    # Orbital Cannons
    "Orbital Precision Strike": "RRU",
    "Orbital Gatling Barrage": "RDLUU",
    "Orbital Airburst Strike": "RRR",
    "Orbital 120MM HE Barrage": "RRDLRD",
    "Orbital 380MM HE Barrage": "RDUULDD",
    "Orbital Walking Barrage": "RDRDRD",
    "Orbital Laser": "RDURD",
    "Orbital Railcannon Strike": "RUDDR",
    "Orbital Gas Strike": "RRDR",
    "Orbital EMS Strike": "RRLD",
    "Orbital Smoke Strike": "RRDU",
    "Orbital Napalm Barrage": "RRDLRU",
    "Orbital Illumination Flare": "RRLL",
    # Eagle-1
    "Eagle Rearm": "UULUR",
    "Eagle Strafing Run": "URR",
    "Eagle Airstrike": "URDR",
    "Eagle Cluster Bomb": "URDDR",
    "Eagle Napalm Airstrike": "URDU",
    "Eagle Smoke Strike": "URUD",
    "Eagle 110MM Rocket Pods": "URUL",
    "Eagle 500kg Bomb": "URDDD",
    # Support Weapons
    "MG-43 Machine Gun": "DLDUR",
    "APW-1 Anti-Materiel Rifle": "DLRUD",
    "M-105 Stalwart": "DLDUUL",
    "EAT-17 Expendable Anti-Tank": "DDLUR",
    "GR-8 Recoilless Rifle": "DLRRL",
    "FLAM-40 Flamethrower": "DLUDU",
    "AC-8 Autocannon": "DLDUUR",
    "MG-206 Heavy Machine Gun": "DLUDD",
    "RS-422 Railgun": "DRDULR",
    "FAF-14 Spear": "DDUDD",
    "GL-21 Grenade Launcher": "DLULD",
    "LAS-98 Laser Cannon": "DLDUL",
    "ARC-3 Arc Thrower": "DRDULL",
    "LAS-99 Quasar Cannon": "DDULR",
    "RL-77 Airburst Rocket Launcher": "DUULR",
    "MLS-4X Commando": "DLUDR",
    "SM-63 W.A.S.P. Launcher": "DDUDR",
    "TX-41 Sterilizer": "DLUDL",
    "GL-52 De-Escalator": "LRULR",
    "CDC-1 One True Flag": "DLRRU",
    "PLAS-45 Epoch": "DLULR",
    "S-11 Speargun": "DRDLUR",
    "EAT-700 Expendable Napalm": "DDLUL",
    "MS-11 Solo Silo": "DURDD",
    "CQC-9 Defoliation Tool": "DLRRD",
    "M-1000 Maxigun": "Maxigun",
    "CQC-20 Breaching Hammer": "DLRLU",
    "EAT-411 Leveller": "DDLUD",
    "GL-28 Belt-Fed Grenade Launcher": "DLULUU",
    # Sentry Guns
    "Machine Gun Sentry": "DURRU",
    "Gatling Sentry": "DURL",
    "Mortar Sentry": "DURRD",
    "EMS Mortar Sentry": "DURDR",
    "Autocannon Sentry": "DURULU",
    "Rocket Sentry": "DURRL",
    "Tesla Tower": "DURULR",
    "Flame Sentry": "DURDUU",
    "Laser Sentry": "DURDUR",
    # Mines and Emplacements
    "Anti-Personnel Minefield": "DLUR",
    "Incendiary Mines": "DLLD",
    "Anti-Tank Mines": "DLUU",
    "MD-B Gas Mines": "DLLR",
    "HMG Emplacement": "DULRRL",
    "Anti-Tank Emplacement": "DULRRL",
    "Grenadier Emplacement": "DRDLR",
    "Shield Generator Relay": "DDLRLR",
    # Backpacks
    "LIFT-850 Jump Pack": "DUUDU",
    "LIFT-660 Hover Pack": "DUUDLR",
    "B-1 Supply Pack": "DLDUUD",
    "AX/AR-23 Guard Dog": "DULURD",
    "AX/LAS-5 Guard Dog": "DULURR",
    "AX/ARC-3 Guard Dog": "DULURL",
    "AD/TX-13 Guard Dog": "DULURU",
    "AX/FLAM-75 Hot Dog": "DULULL",
    "SH-20 Ballistic Shield Backpack": "DLDDUL",
    "SH-32 Shield Generator Pack": "DULRLR",
    "SH-51 Directional Shield": "DULRUU",
    "B-100 Portable Hellbomb": "DRUUU",
    "LIFT-182 Warp Pack": "DLRDLR",
    "B/MD C4 Pack": "DRUURU",
    # Vehicles and Mechs
    "EXO-45 Patriot Exosuit": "LDRULDD",
    "EXO-49 Emancipator Exosuit": "LDRULDU",
    "M-102 Fast Recon Vehicle": "LDRDRDU",
}

CATEGORIZED_STRATAGEMS = {
    "Mission Stratagems": [
        "Reinforce", "Resupply", "SOS Beacon", "Super Earth Flag", "Hellbomb",
        "Seismic Probe", "SSSD Delivery", "Prospecting Drill", "Upload Data",
        "Dark Fluid Vessel", "Tectonic Drill", "Hive Breaker Drill", "SEAF Artillery"
    ],
    "Orbital Cannons": [
        "Orbital Precision Strike", "Orbital Gatling Barrage", "Orbital Airburst Strike",
        "Orbital 120MM HE Barrage", "Orbital 380MM HE Barrage", "Orbital Walking Barrage",
        "Orbital Laser", "Orbital Railcannon Strike", "Orbital Gas Strike",
        "Orbital EMS Strike", "Orbital Smoke Strike", "Orbital Napalm Barrage",
        "Orbital Illumination Flare"
    ],
    "Eagle-1": [
        "Eagle Rearm", "Eagle Strafing Run", "Eagle Airstrike", "Eagle Cluster Bomb",
        "Eagle Napalm Airstrike", "Eagle Smoke Strike", "Eagle 110MM Rocket Pods", "Eagle 500kg Bomb"
    ],
    "Support Weapons": [
        "MG-43 Machine Gun", "APW-1 Anti-Materiel Rifle", "M-105 Stalwart", "EAT-17 Expendable Anti-Tank",
        "GR-8 Recoilless Rifle", "FLAM-40 Flamethrower", "AC-8 Autocannon", "MG-206 Heavy Machine Gun",
        "RS-422 Railgun", "FAF-14 Spear", "GL-21 Grenade Launcher", "LAS-98 Laser Cannon",
        "ARC-3 Arc Thrower", "LAS-99 Quasar Cannon", "RL-77 Airburst Rocket Launcher",
        "MLS-4X Commando", "SM-63 W.A.S.P. Launcher", "TX-41 Sterilizer",
        "GL-52 De-Escalator", "CDC-1 One True Flag", "PLAS-45 Epoch", "S-11 Speargun", "EAT-700 Expendable Napalm", "MS-11 Solo Silo", "CQC-9 Defoliation Tool", "M-1000 Maxigun", "CQC-20 Breaching Hammer", "EAT-411 Leveller", "GL-28 Belt-Fed Grenade Launcher"
    ],
    "Sentry Guns": [
        "Machine Gun Sentry", "Gatling Sentry", "Mortar Sentry", "EMS Mortar Sentry",
        "Autocannon Sentry", "Rocket Sentry", "Tesla Tower", "Flame Sentry", "Laser Sentry"
    ],
    "Mines and Emplacements": [
        "Anti-Personnel Minefield", "Incendiary Mines", "Anti-Tank Mines", "MD-B Gas Mines",
        "HMG Emplacement", "Anti-Tank Emplacement", "Grenadier Emplacement", "Shield Generator Relay"
    ],
    "Backpacks": [
        "LIFT-850 Jump Pack", "LIFT-660 Hover Pack", "B-1 Supply Pack", "AX/AR-23 Guard Dog",
        "AX/LAS-5 Guard Dog", "AX/ARC-3 Guard Dog", "AD/TX-13 Guard Dog", "AX/FLAM-75 Hot Dog", 
        "SH-20 Ballistic Shield Backpack", "SH-32 Shield Generator Pack",
        "SH-51 Directional Shield", "B-100 Portable Hellbomb", "B/MD C4 Pack", "LIFT-182 Warp Pack"
    ],
    "Vehicles and Mechs": [
        "EXO-45 Patriot Exosuit", "EXO-49 Emancipator Exosuit", "M-102 Fast Recon Vehicle"
    ]
}

# --- UI Classes ---

class ReminderWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Cyberpunk Drag Handle
        self.drag_handle = QWidget(self)
        self.drag_handle.setFixedHeight(6) 
        self.drag_handle.setStyleSheet("background-color: #fcee0a; border-top-left-radius: 4px; border-top-right-radius: 4px;")
        main_layout.addWidget(self.drag_handle)

        # Content Area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: rgba(13, 13, 13, 230); border: 1px solid #333; border-bottom-left-radius: 4px; border-bottom-right-radius: 4px;")
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(12, 10, 12, 12)
        self.label = QLabel("No hotkeys set.")
        self.label.setStyleSheet("background-color: transparent; color: #fcee0a; font-family: 'Segoe UI Semibold'; font-size: 9pt;")
        self.content_layout.addWidget(self.label)
        main_layout.addWidget(content_widget)

        self._drag_pos = None
        
        self.drag_handle.mousePressEvent = self.handle_mouse_press
        self.drag_handle.mouseMoveEvent = self.handle_mouse_move
        self.drag_handle.mouseReleaseEvent = self.handle_mouse_release

    def handle_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def handle_mouse_move(self, event):
        if self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def handle_mouse_release(self, event):
        self._drag_pos = None
        event.accept()

    def update_reminders(self, hotkeys_dict):
        reminder_text = ""
        if not hotkeys_dict:
            reminder_text = "SYSTEM READY: No hotkeys."
        else:
            sorted_hotkeys = sorted(hotkeys_dict.items())
            for hotkey, (stratagem_name, _) in sorted_hotkeys:
                reminder_text += f"<span style='color: #888;'>[{hotkey.upper()}]</span> &nbsp; <span style='color: #fcee0a;'>{stratagem_name.upper()}</span><br>"
        self.label.setText(reminder_text)
    
class StatusIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(14, 14)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.is_on = False
        self._drag_pos = None

    def set_status(self, is_on):
        self.is_on = is_on
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Industrial Cyan/Yellow for On, Dim Red for Off
        color = QColor("#fcee0a") if self.is_on else QColor("#521010")
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.rect())
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()

class SettingsDialog(QDialog):
    def __init__(self, main_app, parent=None):
        super().__init__(parent)
        self.main_app = main_app
        self.setWindowTitle("SYSTEM CONFIG")
        self.setModal(True)
        
        layout = QGridLayout(self)
        layout.setSpacing(15)

        # Stratagem Menu Key
        menu_key_label = QLabel("<b>MENU KEY:</b>")
        layout.addWidget(menu_key_label, 0, 0)
        self.menu_key_input = HotkeyLineEdit(allow_modifiers=True)
        self.menu_key_input.setText(self.main_app.stratagem_menu_key)
        layout.addWidget(self.menu_key_input, 0, 1)

        # Global Toggle Hotkey
        toggle_label = QLabel("<b>MASTER TOGGLE:</b>")
        layout.addWidget(toggle_label, 1, 0)
        self.global_toggle_hotkey_input = HotkeyLineEdit()
        self.global_toggle_hotkey_input.setText(self.main_app.global_toggle_hotkey)
        layout.addWidget(self.global_toggle_hotkey_input, 1, 1)
        
        # Activation Delay
        activation_label = QLabel("<b>DELAY (SEC):</b>")
        layout.addWidget(activation_label, 2, 0)
        self.delay_spinbox = QDoubleSpinBox()
        self.delay_spinbox.setRange(0.0, 5.0)
        self.delay_spinbox.setSingleStep(0.01)
        self.delay_spinbox.setValue(self.main_app.stratagem_activation_delay)
        layout.addWidget(self.delay_spinbox, 2, 1)
        
        # Internal Delay
        internal_delay_label = QLabel("<b>KEY SPEED:</b>")
        layout.addWidget(internal_delay_label, 3, 0)
        self.pydirectinput_pause_spinbox = QDoubleSpinBox()
        self.pydirectinput_pause_spinbox.setRange(0.0, 2.0)
        self.pydirectinput_pause_spinbox.setSingleStep(0.005)
        self.pydirectinput_pause_spinbox.setValue(pydirectinput.PAUSE)
        layout.addWidget(self.pydirectinput_pause_spinbox, 3, 1)

        # WASD Toggle
        self.wasd_checkbox = QCheckBox("USE WASD INPUT")
        self.wasd_checkbox.setChecked(self.main_app.use_wasd_input)
        layout.addWidget(self.wasd_checkbox, 4, 0, 1, 2)

        # Reminder Opacity
        opacity_label = QLabel("<b>OPACITY:</b>")
        layout.addWidget(opacity_label, 5, 0)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(20, 100)
        self.opacity_slider.setValue(int(self.main_app.reminder_opacity * 100))
        self.opacity_slider.valueChanged.connect(self.update_opacity)
        layout.addWidget(self.opacity_slider, 5, 1)
        
        # OK Button
        button_layout = QHBoxLayout()
        ok_button = QPushButton("APPLY")
        ok_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout, 6, 0, 1, 2)
        
        self.accepted.connect(self.apply_settings)

    def update_opacity(self, value):
        self.main_app.set_reminder_opacity(value / 100.0)

    def apply_settings(self):
        self.main_app.stratagem_menu_key = self.menu_key_input.text() or 'ctrl'
        self.main_app.global_toggle_hotkey = self.global_toggle_hotkey_input.text()
        self.main_app.stratagem_activation_delay = self.delay_spinbox.value()
        self.main_app.use_wasd_input = self.wasd_checkbox.isChecked()
        pydirectinput.PAUSE = self.pydirectinput_pause_spinbox.value()

class HotkeyLineEdit(QLineEdit):
    MOUSE_QT_MAP = {
        Qt.MouseButton.LeftButton: "left",
        Qt.MouseButton.RightButton: "right",
        Qt.MouseButton.MiddleButton: "middle",
        Qt.MouseButton.XButton1: "xbutton1",
        Qt.MouseButton.XButton2: "xbutton2",
    }

    def __init__(self, allow_modifiers=False, parent=None):
        super().__init__(parent)
        self.is_capturing = False
        self.allow_modifiers = allow_modifiers
        self.setPlaceholderText("NOT SET")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def mousePressEvent(self, event):
        if self.is_capturing:
            button = event.button()
            if button in self.MOUSE_QT_MAP:
                self.setText(f"mouse_{self.MOUSE_QT_MAP[button]}")
                self.is_capturing = False
                self.clearFocus()
        else:
            self.is_capturing = True
            self.setText("LISTENING...")
            self.selectAll()
            self.setFocus()

    def focusOutEvent(self, event):
        self.is_capturing = False
        if "LISTENING" in self.text():
            self.clear()
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        if self.is_capturing:
            key = event.key()
            text = ""
            is_modifier_key = key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta)

            if self.allow_modifiers and is_modifier_key:
                key_text_map = {Qt.Key.Key_Control: 'ctrl', Qt.Key.Key_Shift: 'shift', Qt.Key.Key_Alt: 'alt'}
                text = key_text_map.get(key, '')
            elif not self.allow_modifiers and is_modifier_key:
                return
            elif key == Qt.Key.Key_CapsLock:
                 text = "caps_lock"
            elif Qt.Key.Key_F1 <= key <= Qt.Key.Key_F12:
                text = f"f{key - Qt.Key.Key_F1 + 1}"
            elif Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
                if event.modifiers() & Qt.KeyboardModifier.KeypadModifier:
                    text = f"num_{event.text()}"
                else:
                    text = event.text()
            else:
                key_sequence = QKeySequence(key)
                text = key_sequence.toString(QKeySequence.SequenceFormat.NativeText).lower()

            if text:
                self.setText(text)
                self.is_capturing = False
                self.clearFocus()
        else:
            super().keyPressEvent(event)


class HotkeySlot(QWidget):
    stratagem_changed = pyqtSignal()
    hotkey_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.stratagem_button = QPushButton("EMPTY")
        self.stratagem_button.setMinimumHeight(40)
        self.stratagem_button.clicked.connect(self.open_stratagem_menu)
        layout.addWidget(self.stratagem_button)

        self.hotkey_input = HotkeyLineEdit()
        self.hotkey_input.textChanged.connect(self.hotkey_changed.emit)
        layout.addWidget(self.hotkey_input)

    def open_stratagem_menu(self):
        menu = self.create_stratagem_menu()
        menu.exec(self.stratagem_button.mapToGlobal(QPoint(0, self.stratagem_button.height())))

    def create_stratagem_menu(self):
        menu = QMenu(self)
        for category, stratagems in CATEGORIZED_STRATAGEMS.items():
            category_menu = menu.addMenu(category)
            for name in sorted(stratagems):
                action = QAction(name, self)
                action.triggered.connect(lambda _, n=name: self.set_stratagem(n))
                category_menu.addAction(action)
        return menu

    def set_stratagem(self, name):
        self.stratagem_button.setText(name.upper())
        self.stratagem_changed.emit()
    
    def get_stratagem(self):
        text = self.stratagem_button.text()
        # Find the original case name in the data
        for real_name in ALL_STRATAGEMS.keys():
            if real_name.upper() == text:
                return real_name
        return ""

    def get_hotkey(self):
        return self.hotkey_input.text()
    
    def set_hotkey(self, text):
        self.hotkey_input.setText(text)

    def clear_slot(self):
        self.stratagem_button.setText("EMPTY")
        self.hotkey_input.clear()
    
    def set_duplicate_style(self, is_duplicate):
        self.hotkey_input.setObjectName("duplicate" if is_duplicate else "")
        self.hotkey_input.style().polish(self.hotkey_input)

class WorkerSignals(QObject):
    update_status = pyqtSignal(str, str)
    update_reminders = pyqtSignal(dict)

class StratagemMacroApp(QMainWindow):
    # --- Industrial Cyberpunk Palette ---
    CYBER_YELLOW = "#fcee0a"
    CYBER_YELLOW_HOVER = "#d9cd08"
    DEEP_CARBON = "#0d0d0d"
    INDUSTRIAL_GREY = "#1a1b1e"
    UI_LIGHT_GREY = "#e0e0e0"
    UI_BORDER = "#333"
    ERROR_RED = "#ff4136"
    STATUS_STOPPED = "#521010"

    def __init__(self):
        super().__init__()
        self.is_running = False
        self.stratagems_to_execute = {}
        self.stratagem_menu_key = 'ctrl'
        self.global_toggle_hotkey = ""
        self.use_wasd_input = False
        self.stratagem_activation_delay = DEFAULT_STRATAGEM_ACTIVATION_DELAY
        self.reminder_opacity = DEFAULT_REMINDER_OPACITY
        
        self.keyboard_listener = None
        self.mouse_listener = None
        self.signals = WorkerSignals()
        self.status_indicator_window = None
        self.reminder_window = None
        self.hotkey_slots = []
        
        self.initUI()
        self.start_global_listeners()
        self.populate_profiles_dropdown()
        self.validate_hotkeys() 

    def initUI(self):
        self.setWindowTitle('S.C.S // STRATAGEM CONTROL SYSTEM')
        self.setMinimumWidth(900)
        self.setWindowIcon(QIcon(resource_path("icon.ico")))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        self.setup_styles(central_widget)
        
        self.init_toolbar(main_layout)
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {self.UI_BORDER}; max-height: 1px;")
        main_layout.addWidget(line)
        
        self.init_hotkey_grid(main_layout)
        
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet(f"background-color: {self.UI_BORDER}; max-height: 1px;")
        main_layout.addWidget(line2)
        
        self.init_control_area(main_layout)
        
        self.signals.update_status.connect(self.update_status_label)
        self.signals.update_reminders.connect(self.update_reminder_data)
        self.show()

    def init_toolbar(self, parent_layout):
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(8)

        self.profiles_combo = QComboBox()
        self.profiles_combo.setMinimumWidth(180)
        self.profiles_combo.currentIndexChanged.connect(self.load_selected_profile)
        toolbar_layout.addWidget(self.profiles_combo)

        self.save_profile_button = QPushButton("SAVE")
        self.save_profile_button.clicked.connect(self.save_current_profile)
        toolbar_layout.addWidget(self.save_profile_button)

        self.delete_profile_button = QPushButton("DELETE")
        self.delete_profile_button.clicked.connect(self.delete_selected_profile)
        toolbar_layout.addWidget(self.delete_profile_button)
        
        self.clear_all_button = QPushButton("WIPE ALL")
        self.clear_all_button.clicked.connect(self.clear_all_slots)
        toolbar_layout.addWidget(self.clear_all_button)

        toolbar_layout.addStretch()

        self.reminder_button = QPushButton("LIST")
        self.reminder_button.clicked.connect(self.toggle_reminder_window)
        toolbar_layout.addWidget(self.reminder_button)

        self.indicator_button = QPushButton("LED")
        self.indicator_button.clicked.connect(self.toggle_status_indicator)
        toolbar_layout.addWidget(self.indicator_button)

        self.help_button = QPushButton("HELP")
        self.help_button.clicked.connect(self.show_help_dialog)
        toolbar_layout.addWidget(self.help_button)

        self.settings_button = QPushButton("CONFIG")
        self.settings_button.clicked.connect(self.open_settings_dialog)
        toolbar_layout.addWidget(self.settings_button)

        self.toggle_button = QPushButton('INITIALIZE')
        self.toggle_button.setMinimumWidth(120)
        self.toggle_button.clicked.connect(self.toggle_macro)
        toolbar_layout.addWidget(self.toggle_button)
        
        parent_layout.addLayout(toolbar_layout)

    def init_hotkey_grid(self, parent_layout):
        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)

        num_slots = 12
        num_cols = 6
        for i in range(num_slots):
            slot = HotkeySlot()
            slot.hotkey_changed.connect(self.validate_and_update)
            slot.stratagem_changed.connect(self.validate_and_update)
            self.hotkey_slots.append(slot)
            row, col = divmod(i, num_cols)
            grid_layout.addWidget(slot, row, col)
            
        parent_layout.addLayout(grid_layout)

    def init_control_area(self, parent_layout):
        self.status_label = QLabel('STATUS // STANDBY')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"color: {self.STATUS_STOPPED}; font-weight: bold; font-family: 'Consolas'; font-size: 11pt;")
        parent_layout.addWidget(self.status_label)

    def setup_styles(self, parent_widget):
        parent_widget.setStyleSheet(f"""
            QWidget {{ 
                background-color: {self.DEEP_CARBON}; 
                color: {self.UI_LIGHT_GREY}; 
                font-family: 'Segoe UI Semibold', 'Arial';
            }}
            QLabel {{ font-size: 10pt; color: #888; }}
            
            QPushButton {{
                background-color: {self.INDUSTRIAL_GREY}; 
                color: {self.UI_LIGHT_GREY}; 
                padding: 10px;
                border: 1px solid {self.UI_BORDER};
                border-radius: 4px; 
                font-size: 9pt;
                font-weight: bold;
            }}
            QPushButton:hover {{ 
                background-color: #25262b; 
                border-color: #555;
            }}
            QPushButton:pressed {{
                background-color: {self.DEEP_CARBON};
            }}
            
            #toggle_button_running {{ 
                background-color: {self.CYBER_YELLOW}; 
                color: {self.DEEP_CARBON};
                border-color: {self.CYBER_YELLOW};
            }}
            #toggle_button_running:hover {{ 
                background-color: {self.CYBER_YELLOW_HOVER}; 
            }}
            
            QLineEdit, QDoubleSpinBox, QComboBox, QCheckBox {{
                padding: 8px; 
                border: 1px solid {self.UI_BORDER}; 
                border-radius: 4px;
                background-color: #111; 
                color: {self.CYBER_YELLOW};
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 1px solid {self.CYBER_YELLOW};
            }}
            
            QLineEdit#duplicate {{
                border: 1px solid {self.ERROR_RED};
                color: {self.ERROR_RED};
            }}
            
            QDialog {{ background-color: {self.DEEP_CARBON}; border: 1px solid {self.UI_BORDER}; }}
            
            QMenu {{
                background-color: {self.INDUSTRIAL_GREY};
                border: 1px solid {self.UI_BORDER};
                padding: 5px;
            }}
            QMenu::item {{
                padding: 8px 25px;
                border-radius: 2px;
            }}
            QMenu::item:selected {{
                background-color: {self.CYBER_YELLOW};
                color: {self.DEEP_CARBON};
            }}
        """)

    # --- Listener and Execution Logic ---
    
    def start_global_listeners(self):
        threading.Thread(target=self._run_keyboard_listener, daemon=True).start()
        threading.Thread(target=self._run_mouse_listener, daemon=True).start()

    def _run_keyboard_listener(self):
        with keyboard.Listener(on_press=self.on_global_press) as listener:
            self.keyboard_listener = listener
            listener.join()
    
    def _run_mouse_listener(self):
        with mouse.Listener(on_click=self.on_global_click) as listener:
            self.mouse_listener = listener
            listener.join()

    def on_global_press(self, key):
        try:
            hotkey_pressed = self.get_key_str_from_pynput(key)
            if not hotkey_pressed: return
            self.handle_hotkey(hotkey_pressed)
        except Exception as e:
            pass

    def on_global_click(self, x, y, button, pressed):
        if not pressed: return
        try:
            hotkey_name = ""
            if button == mouse.Button.left: hotkey_name = "mouse_left"
            elif button == mouse.Button.right: hotkey_name = "mouse_right"
            elif button == mouse.Button.middle: hotkey_name = "mouse_middle"
            elif button == mouse.Button.x1: hotkey_name = "mouse_xbutton1"
            elif button == mouse.Button.x2: hotkey_name = "mouse_xbutton2"
            
            if hotkey_name:
                self.handle_hotkey(hotkey_name)
        except Exception as e:
            pass

    def handle_hotkey(self, hotkey):
        if self.global_toggle_hotkey and hotkey == self.global_toggle_hotkey:
            QTimer.singleShot(0, self.toggle_macro)
            return

        if self.is_running and hotkey in self.stratagems_to_execute:
            name, sequence = self.stratagems_to_execute[hotkey]
            threading.Thread(target=self.execute_stratagem, args=(name, sequence), daemon=True).start()

    def execute_stratagem(self, name, sequence):
        key_map = {'U': 'w', 'D': 's', 'L': 'a', 'R': 'd'} if self.use_wasd_input else {'U': 'up', 'D': 'down', 'L': 'left', 'R': 'right'}
        try:
            self.signals.update_status.emit(f"EXECUTING // {name.upper()}", self.CYBER_YELLOW)
            pyautogui.keyDown(self.stratagem_menu_key)
            time.sleep(self.stratagem_activation_delay)
            
            for char in sequence:
                if char in key_map: pydirectinput.press(key_map[char])
            
            pyautogui.keyUp(self.stratagem_menu_key)
            QTimer.singleShot(1000, lambda: self.update_ui_for_state() if self.is_running else None)
        except Exception as e:
            self.signals.update_status.emit("CORE ERROR!", self.ERROR_RED)

    # --- Macro State Control ---

    def toggle_macro(self):
        if self.is_running: self.stop_macro()
        else: self.start_macro()

    def start_macro(self):
        self.stratagems_to_execute.clear()
        if self.validate_hotkeys():
             QMessageBox.warning(self, "CONFLICT DETECTED", "Duplicate hotkeys found. Resolve before boot.")
             return

        for slot in self.hotkey_slots:
            hotkey = slot.get_hotkey().strip().lower()
            stratagem_name = slot.get_stratagem()
            if hotkey and stratagem_name:
                sequence = ALL_STRATAGEMS.get(stratagem_name)
                if sequence:
                    self.stratagems_to_execute[hotkey] = (stratagem_name, sequence)

        if not self.stratagems_to_execute:
            QMessageBox.warning(self, "SYSTEM HALT", "No hotkeys configured.")
            return

        self.is_running = True
        self.update_ui_for_state()

    def stop_macro(self):
        self.is_running = False
        self.update_ui_for_state()
    
    def update_ui_for_state(self):
        profile_text = self.profiles_combo.currentText().upper()
        if self.is_running:
            self.toggle_button.setText('TERMINATE')
            self.toggle_button.setObjectName('toggle_button_running')
            self.signals.update_status.emit(f"RUNNING // {profile_text}", self.CYBER_YELLOW)
            self.set_controls_enabled(False)
        else:
            self.toggle_button.setText('INITIALIZE')
            self.toggle_button.setObjectName('')
            self.signals.update_status.emit(f"STANDBY // {profile_text}", self.STATUS_STOPPED)
            self.set_controls_enabled(True)
        self.toggle_button.style().polish(self.toggle_button)
        
        if self.status_indicator_window:
            self.status_indicator_window.set_status(self.is_running)


    def update_status_label(self, text, color):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold; font-family: 'Consolas'; font-size: 11pt;")

    def set_controls_enabled(self, enabled):
        self.profiles_combo.setEnabled(enabled)
        self.save_profile_button.setEnabled(enabled)
        self.delete_profile_button.setEnabled(enabled)
        self.settings_button.setEnabled(enabled)
        self.clear_all_button.setEnabled(enabled)
        self.help_button.setEnabled(enabled)
        self.reminder_button.setEnabled(enabled)
        self.indicator_button.setEnabled(enabled)
        for slot in self.hotkey_slots:
            slot.setEnabled(enabled)

    # --- UI Callbacks & Profile Management ---
    
    def open_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog.exec()
        
    def toggle_status_indicator(self):
        if not self.status_indicator_window:
            self.status_indicator_window = StatusIndicator()
            self.status_indicator_window.set_status(self.is_running)
            self.status_indicator_window.show()
        else:
            if self.status_indicator_window.isVisible():
                self.status_indicator_window.hide()
            else:
                self.status_indicator_window.show()

    def toggle_reminder_window(self):
        if not self.reminder_window:
            self.reminder_window = ReminderWindow()
            self.signals.update_reminders.connect(self.reminder_window.update_reminders)
            self.update_reminder_data(self.get_active_hotkeys())
            self.set_reminder_opacity(self.reminder_opacity)
        
        if self.reminder_window.isVisible():
            self.reminder_window.hide()
        else:
            self.reminder_window.show()
    
    def set_reminder_opacity(self, opacity):
        self.reminder_opacity = opacity
        if self.reminder_window:
            self.reminder_window.setWindowOpacity(self.reminder_opacity)
    
    def update_reminder_data(self, data):
        if self.reminder_window:
            self.reminder_window.update_reminders(data)

    def get_active_hotkeys(self):
        active = {}
        for slot in self.hotkey_slots:
            hotkey = slot.get_hotkey().strip().lower()
            stratagem = slot.get_stratagem()
            if hotkey and stratagem:
                active[hotkey] = (stratagem, None)
        return active
        

    def show_help_dialog(self):
        instructions = f"""
        <h2 style='color: {self.CYBER_YELLOW};'>PROTOCOL OVERVIEW</h2>
        <p><b>1. INTERFACE:</b> Click EMPTY to select a stratagem, then input your desired trigger key.</p>
        <p><b>2. PROFILES:</b> Create and save unique loadouts via the dropdown menu.</p>
        <p><b>3. GAME CONFIG:</b> Set 'Stratagem Menu' to <b>PRESS</b> (not hold) in Helldivers 2 settings. Map directionals to Arrow Keys for movement capability.</p>
        <p><b>4. MASTER TOGGLE:</b> Use the Global Hotkey in Config to toggle the system mid-mission.</p>
        <hr style='border-top: 1px solid #333;'>
        <p>Developed for optimal Helldiver efficiency.</p>
        """
        QMessageBox.information(self, "SYSTEM HELP", instructions)

    def validate_and_update(self):
        self.validate_hotkeys()
        self.signals.update_reminders.emit(self.get_active_hotkeys())

    def validate_hotkeys(self):
        hotkey_counts = {}
        for slot in self.hotkey_slots:
            hotkey = slot.get_hotkey().strip().lower()
            if hotkey:
                hotkey_counts[hotkey] = hotkey_counts.get(hotkey, 0) + 1
        
        has_duplicates = False
        for slot in self.hotkey_slots:
            hotkey = slot.get_hotkey().strip().lower()
            if hotkey and hotkey_counts.get(hotkey, 0) > 1:
                slot.set_duplicate_style(True)
                has_duplicates = True
            else:
                slot.set_duplicate_style(False)
        return has_duplicates
    
    def clear_all_slots(self):
        reply = QMessageBox.question(self, 'CONFIRM WIPE',
                                     "Confirm total deletion of active hotkeys?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for slot in self.hotkey_slots:
                slot.clear_slot()
    
    def populate_profiles_dropdown(self):
        if not os.path.exists(PROFILES_DIR): os.makedirs(PROFILES_DIR)
        self.profiles_combo.blockSignals(True)
        self.profiles_combo.clear()
        self.profiles_combo.addItem("--- NEW PROFILE ---")
        profiles = [f for f in os.listdir(PROFILES_DIR) if f.endswith('.json')]
        for profile in sorted(profiles):
            self.profiles_combo.addItem(profile.replace('.json', '').upper())
        self.profiles_combo.blockSignals(False)

    def save_current_profile(self):
        profile_name = self.profiles_combo.currentText()
        if profile_name == "--- NEW PROFILE ---":
            text, ok = QFileDialog.getSaveFileName(self, "SAVE DATA", PROFILES_DIR, "JSON Files (*.json)")
            if ok and text: profile_name = os.path.basename(text).replace('.json', '')
            else: return
        
        config = {
            "settings": {
                "stratagem_menu_key": self.stratagem_menu_key,
                "global_toggle_hotkey": self.global_toggle_hotkey,
                "use_wasd_input": self.use_wasd_input,
                "activation_delay": self.stratagem_activation_delay,
                "pydirectinput_pause": pydirectinput.PAUSE,
                "reminder_opacity": self.reminder_opacity,
            },
            "hotkeys": []
        }
        for slot in self.hotkey_slots:
            config["hotkeys"].append({
                "stratagem": slot.get_stratagem(), 
                "hotkey": slot.get_hotkey()
            })
        
        filepath = os.path.join(PROFILES_DIR, f"{profile_name}.json")
        try:
            with open(filepath, 'w') as f: json.dump(config, f, indent=4)
            QMessageBox.information(self, "SUCCESS", f"Profile '{profile_name.upper()}' synced.")
            current_selection = self.profiles_combo.currentText()
            self.populate_profiles_dropdown()
            if current_selection == "--- NEW PROFILE ---":
                 self.profiles_combo.setCurrentText(profile_name.upper())
        except Exception as e:
            QMessageBox.warning(self, "ERROR", f"Sync failed: {e}")

    def load_selected_profile(self, index):
        profile_name = self.profiles_combo.itemText(index)
        if profile_name == "--- NEW PROFILE ---":
            for slot in self.hotkey_slots: slot.clear_slot()
            self.stratagem_menu_key = 'ctrl'
            self.global_toggle_hotkey = ""
            self.use_wasd_input = False
            self.stratagem_activation_delay = DEFAULT_STRATAGEM_ACTIVATION_DELAY
            pydirectinput.PAUSE = DEFAULT_PYDIRECTINPUT_PAUSE
            self.set_reminder_opacity(DEFAULT_REMINDER_OPACITY)
            self.update_ui_for_state()
            return
        
        filepath = os.path.join(PROFILES_DIR, f"{profile_name.lower()}.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f: config = json.load(f)
                
                settings = config.get("settings", {})
                self.stratagem_menu_key = settings.get("stratagem_menu_key", "ctrl")
                self.global_toggle_hotkey = settings.get("global_toggle_hotkey", "")
                self.use_wasd_input = settings.get("use_wasd_input", False)
                self.stratagem_activation_delay = settings.get("activation_delay", DEFAULT_STRATAGEM_ACTIVATION_DELAY)
                pydirectinput.PAUSE = settings.get("pydirectinput_pause", DEFAULT_PYDIRECTINPUT_PAUSE)
                self.set_reminder_opacity(settings.get("reminder_opacity", DEFAULT_REMINDER_OPACITY))


                hotkeys = config.get("hotkeys", [])
                for i, slot in enumerate(self.hotkey_slots):
                    if i < len(hotkeys):
                        item = hotkeys[i]
                        slot.set_stratagem(item.get("stratagem", ""))
                        slot.set_hotkey(item.get("hotkey", ""))
                    else: slot.clear_slot()
                
                self.validate_and_update()
                self.update_ui_for_state()
            except Exception as e:
                QMessageBox.warning(self, "ERROR", f"Load failed: {e}")

    def delete_selected_profile(self):
        profile_name = self.profiles_combo.currentText()
        if profile_name == "--- NEW PROFILE ---": return
        
        reply = QMessageBox.question(self, 'CONFIRM PURGE', f"Purge profile '{profile_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            filepath = os.path.join(PROFILES_DIR, f"{profile_name.lower()}.json")
            try:
                if os.path.exists(filepath): os.remove(filepath)
                self.populate_profiles_dropdown()
            except Exception as e:
                QMessageBox.warning(self, "ERROR", f"Purge failed: {e}")

    # --- Utilities ---
    def get_key_str_from_pynput(self, key):
        if hasattr(key, 'vk') and 96 <= key.vk <= 105:
            return f'num_{key.vk - 96}'
        if isinstance(key, keyboard.KeyCode) and key.char: return key.char.lower()
        if isinstance(key, keyboard.Key):
            return key.name.lower()
        return None

    def closeEvent(self, event):
        if self.status_indicator_window: self.status_indicator_window.close()
        if self.reminder_window: self.reminder_window.close()
        if self.keyboard_listener: self.keyboard_listener.stop()
        if self.mouse_listener: self.mouse_listener.stop()
        event.accept()

def main():
    try:
        import pyautogui, pydirectinput, pynput
    except ImportError as e:
        app = QApplication(sys.argv)
        QMessageBox.critical(None, "DEPENDENCY MISSING", f"Required library missing: {e.name}. Install via terminal.")
        sys.exit(1)
        
    app = QApplication(sys.argv)
    ex = StratagemMacroApp()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()