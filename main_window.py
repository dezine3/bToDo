from __future__ import annotations
# File: main_window.py
# Description: Defines the main window, event dialog, and settings dialog for the bToDo.
# Original Date: 2025-04-28
# Updated: 2025-04-29 (Replaced text header with banner image)

# --- Imports ---
import base64
import binascii
import datetime
import os
import sys
import tempfile
import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

# --- PySide6 Imports ---
from PySide6.QtCore import QDate, QDateTime, QSize, Qt, QTime, QUrl
from PySide6.QtGui import (
    QAction, QColor, QDesktopServices, QIcon, QPalette, QPixmap, QCloseEvent
)
from PySide6.QtWidgets import (
    QApplication, QCalendarWidget, QCheckBox, QColorDialog, QComboBox,
    QDialog, QDateEdit, QFileDialog, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QListView, QListWidget, QListWidgetItem, QMainWindow, QMenu,
    QMenuBar, QMessageBox, QPushButton, QTextEdit, QTimeEdit, QVBoxLayout,
    QWidget
)

# --- Type Hinting ---
if TYPE_CHECKING:
    from data_manager import DataManager
    from notification_manager import NotificationManager

# --- Helper function for resource paths ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".") # Use current dir for development

    return os.path.join(base_path, relative_path)

# --- Constants ---
ICON_PATH = resource_path("britton.ico")
BANNER_PATH = resource_path("banner.png") # <-- Define path for banner
DATE_FORMAT = "yyyy-MM-dd"
TIME_FORMAT = "hh:mm AP"
DATETIME_PARSE_FORMAT = "%I:%M %p"
DEFAULT_NOTIFY_MINUTES = 30
ATTACHMENT_ICON_SIZE = QSize(64, 64)
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
USER_ROLE = Qt.ItemDataRole.UserRole
# Style Names - Must match keys in apply_theme and items in SettingsDialog
STYLE_DEFAULT_LIGHT = "Default Light"
STYLE_DEFAULT_DARK = "Default Dark"
STYLE_GRAPHITE_DARK = "Graphite Dark (QSS)"
STYLE_OCEAN_BREEZE = "Ocean Breeze (QSS)"
STYLE_MINTY_LIGHT = "Minty Light (QSS)"
# Define the default style and accent color for fallback
DEFAULT_STYLE = STYLE_DEFAULT_LIGHT
DEFAULT_ACCENT_COLOR = "#2A82DA"

# --- QSS Definitions ---
# (QSS definitions remain unchanged...)
GRAPHITE_DARK_QSS = """
    QWidget {{
        background-color: #2d2d2d; /* Dark background */
        color: #cccccc; /* Light grey text */
        border: 0px; /* No borders by default */
        font-size: 10pt; /* Base font size */
    }}
    QMainWindow, QDialog {{
        background-color: #2d2d2d;
    }}
    QMenuBar, QMenu {{
        background-color: #3c3c3c;
        color: #cccccc;
        border-bottom: 1px solid #4a4a4a; /* Subtle separator */
    }}
    QMenuBar::item:selected, QMenu::item:selected {{
        background-color: {accent_color};
        color: white;
    }}
    QPushButton {{
        background-color: #4a4a4a;
        color: #cccccc;
        border: 1px solid #5a5a5a;
        padding: 5px 10px;
        min-height: 16px; /* Ensure minimum height */
        border-radius: 3px;
    }}
    QPushButton:hover {{
        background-color: #5a5a5a;
        border-color: #6a6a6a;
    }}
    QPushButton:pressed {{
        background-color: {accent_color};
        color: white;
        border-color: {accent_color};
    }}
    QLineEdit, QTextEdit, QDateEdit, QTimeEdit, QComboBox {{
        background-color: #252525;
        color: #cccccc;
        border: 1px solid #4a4a4a;
        border-radius: 3px;
        padding: 3px;
    }}
    QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QTimeEdit:focus, QComboBox:focus {{
        border: 1px solid {accent_color};
    }}
    QListWidget, QCalendarWidget {{
        background-color: #353535;
        border: 1px solid #4a4a4a;
    }}
    QListWidget::item {{
        padding: 3px 0px; /* Add some vertical spacing */
    }}
    QListWidget::item:selected, QCalendarWidget QAbstractItemView:enabled:selected {{
        background-color: {accent_color};
        color: white;
        border: none; /* Remove border on selected */
    }}
    QCalendarWidget QToolButton {{ /* Style calendar navigation buttons */
        color: #cccccc;
        background-color: #4a4a4a;
        border: 1px solid #5a5a5a;
        border-radius: 3px;
        padding: 2px; /* Added padding */
    }}
    QCalendarWidget QToolButton:hover {{ background-color: #5a5a5a; }}
    QCalendarWidget QToolButton:pressed {{ background-color: {accent_color}; }}
    QCalendarWidget QMenu {{ background-color: #2d2d2d; }} /* Month/Year menu */
    QCalendarWidget QSpinBox {{ background-color: #252525; color: #cccccc; border: 1px solid #4a4a4a; }} /* Year input */
    QCalendarWidget QTableView {{ alternate-background-color: #353535; }} /* Ensure cells match background */

    QLabel {{ background-color: transparent; }}
    QCheckBox::indicator {{ width: 13px; height: 13px; border-radius: 3px; }}
    QCheckBox::indicator:unchecked {{ border: 1px solid #5a5a5a; background-color: #3c3c3c; }}
    QCheckBox::indicator:checked {{ background-color: {accent_color}; border: 1px solid {accent_color}; }}
    /* Basic check mark image (often needs adjustment or SVG for better quality) */
    /* QCheckBox::indicator:checked {{ image: url(path/to/check-dark.png); }} */
"""

OCEAN_BREEZE_QSS = """
    QWidget {{
        background-color: #e8f1f2; /* Very light blue/grey */
        color: #2a363b; /* Dark grey/blue text */
        border: 0px;
        font-size: 10pt;
    }}
    QMainWindow, QDialog {{ background-color: #e8f1f2; }}
    QMenuBar, QMenu {{
        background-color: #d1dadd; /* Slightly darker blue/grey */
        color: #2a363b;
        border-bottom: 1px solid #c1c5c8;
    }}
    QMenuBar::item:selected, QMenu::item:selected {{
        background-color: {accent_color};
        color: white;
    }}
    QPushButton {{
        background-color: #99d8d0; /* Teal/aqua */
        color: #2a363b;
        border: 1px solid #87c1b9;
        padding: 6px 12px;
        min-height: 18px;
        border-radius: 4px;
        font-weight: bold;
    }}
    QPushButton:hover {{ background-color: #87c1b9; }}
    QPushButton:pressed {{ background-color: {accent_color}; color: white; border-color: {accent_color}; }}
    QLineEdit, QTextEdit, QDateEdit, QTimeEdit, QComboBox {{
        background-color: #ffffff; /* White inputs */
        color: #2a363b;
        border: 1px solid #c1c5c8;
        border-radius: 4px;
        padding: 4px;
    }}
    QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QTimeEdit:focus, QComboBox:focus {{
        border: 2px solid {accent_color}; /* Thicker focus border */
         padding: 3px; /* Adjust padding for thicker border */
    }}
    QListWidget, QCalendarWidget {{
        background-color: #ffffff;
        border: 1px solid #d1dadd;
    }}
     QListWidget::item {{ padding: 4px 2px; }}
    QListWidget::item:selected, QCalendarWidget QAbstractItemView:enabled:selected {{
        background-color: {accent_color};
        color: white;
        border: none;
    }}
    QCalendarWidget QToolButton {{
        color: #2a363b;
        background-color: #d1dadd;
        border: 1px solid #c1c5c8;
        border-radius: 4px;
        padding: 3px;
    }}
    QCalendarWidget QToolButton:hover {{ background-color: #c1c5c8; }}
    QCalendarWidget QToolButton:pressed {{ background-color: {accent_color}; }}
    QCalendarWidget QMenu {{ background-color: #e8f1f2; }}
    QCalendarWidget QSpinBox {{ background-color: #ffffff; color: #2a363b; border: 1px solid #c1c5c8; }}
    QCalendarWidget QTableView {{ alternate-background-color: #f0f5f6; }} /* Subtle alternate row */

    QLabel {{ background-color: transparent; }}
    QCheckBox::indicator {{ width: 14px; height: 14px; border-radius: 4px; }}
    QCheckBox::indicator:unchecked {{ border: 1px solid #a7b0b4; background-color: #dde4e5; }}
    QCheckBox::indicator:checked {{ background-color: {accent_color}; border: 1px solid {accent_color}; }}
    /* QCheckBox::indicator:checked {{ image: url(path/to/check-light.png); }} */
"""

MINTY_LIGHT_QSS = """
    QWidget {{
        background-color: #f5fcf7; /* Very light green tint */
        color: #3d4c42; /* Dark green/grey text */
        border: 0px;
        font-size: 10pt;
    }}
    QMainWindow, QDialog {{ background-color: #f5fcf7; }}
    QMenuBar, QMenu {{
        background-color: #eaf7ed; /* Light minty green */
        color: #3d4c42;
        border-bottom: 1px solid #d8e9dd;
    }}
    QMenuBar::item:selected, QMenu::item:selected {{
        background-color: {accent_color};
        color: white;
    }}
    QPushButton {{
        background-color: #a3d9b8; /* Mint green */
        color: #2f3a32;
        border: 1px solid #90c2a5;
        padding: 5px 10px;
        min-height: 17px;
        border-radius: 10px; /* Rounded buttons */
    }}
    QPushButton:hover {{ background-color: #90c2a5; }}
    QPushButton:pressed {{ background-color: {accent_color}; color: white; border-color: {accent_color}; }}
    QLineEdit, QTextEdit, QDateEdit, QTimeEdit, QComboBox {{
        background-color: #ffffff;
        color: #3d4c42;
        border: 1px solid #d8e9dd;
        border-radius: 4px;
        padding: 4px;
    }}
    QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QTimeEdit:focus, QComboBox:focus {{
        border: 1px solid {accent_color};
        background-color: #fafffc; /* Slightly different background on focus */
    }}
    QListWidget, QCalendarWidget {{
        background-color: #ffffff;
        border: 1px solid #eaf7ed;
    }}
    QListWidget::item {{ padding: 3px 1px; }}
    QListWidget::item:selected, QCalendarWidget QAbstractItemView:enabled:selected {{
        background-color: {accent_color};
        color: white;
        border: none;
    }}
    QCalendarWidget QToolButton {{
        color: #3d4c42;
        background-color: #eaf7ed;
        border: 1px solid #d8e9dd;
        border-radius: 4px;
        padding: 3px;
    }}
    QCalendarWidget QToolButton:hover {{ background-color: #d8e9dd; }}
    QCalendarWidget QToolButton:pressed {{ background-color: {accent_color}; }}
    QCalendarWidget QMenu {{ background-color: #f5fcf7; }}
    QCalendarWidget QSpinBox {{ background-color: #ffffff; color: #3d4c42; border: 1px solid #d8e9dd; }}
    QCalendarWidget QTableView {{ alternate-background-color: #f8fdfa; }}

    QLabel {{ background-color: transparent; }}
    QCheckBox::indicator {{ width: 13px; height: 13px; border-radius: 3px; }}
    QCheckBox::indicator:unchecked {{ border: 1px solid #b4c7bb; background-color: #e0ebe4; }}
    QCheckBox::indicator:checked {{ background-color: {accent_color}; border: 1px solid {accent_color}; }}
    /* QCheckBox::indicator:checked {{ image: url(path/to/check-light.png); }} */
"""


# --- Helper Functions ---
# (create_temporary_file remains unchanged)
def create_temporary_file(filename: str, content: bytes) -> Optional[str]:
    """Creates a temporary file with the given content."""
    try:
        suffix = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix=f"cal_{filename[:10]}_") as temp_file:
            temp_file.write(content)
            return temp_file.name
    except (IOError, OSError) as e:
        print(f"Error creating temporary file '{filename}': {e}", file=sys.stderr)
        return None

# --- Dialog Classes ---
# (EventDialog and SettingsDialog remain unchanged from the previous version
# where ICON_PATH was updated to use resource_path)
class EventDialog(QDialog):
    """Dialog for creating or editing event details."""
    def __init__(self, parent=None, event_data=None):
        super().__init__(parent)
        self.setWindowTitle("Event Details")
        self.setModal(True)
        if parent and parent.windowIcon():
            self.setWindowIcon(parent.windowIcon())
        else:
            if os.path.exists(ICON_PATH):
                 self.setWindowIcon(QIcon(ICON_PATH))

        self.attachments: List[Tuple[str, str]] = []
        self._setup_ui()
        if event_data:
            self._populate_fields(event_data)

    # ... (rest of EventDialog methods) ...
    def _setup_ui(self):
        form_layout = QFormLayout(self)
        self.title_edit = QLineEdit()
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat(DATE_FORMAT)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat(TIME_FORMAT)
        self.time_edit.setTime(QTime(0, 0))
        self.desc_edit = QTextEdit()
        self.notify_checkbox = QCheckBox("Remind me about this event")
        self.notify_minutes_edit = QLineEdit(str(DEFAULT_NOTIFY_MINUTES))
        self.notify_minutes_edit.setEnabled(False)
        self.attach_list = QListWidget()
        self.attach_list.setViewMode(QListView.ViewMode.IconMode)
        self.attach_list.setIconSize(ATTACHMENT_ICON_SIZE)
        self.attach_list.setSpacing(10)
        self.attach_list.setWordWrap(True)
        attach_btn = QPushButton(QIcon.fromTheme("list-add"), " Add Attachment...")
        remove_attach_btn = QPushButton(QIcon.fromTheme("list-remove"), " Remove Selected")
        form_layout.addRow("Title:", self.title_edit)
        form_layout.addRow("Date:", self.date_edit)
        form_layout.addRow("Time:", self.time_edit)
        form_layout.addRow("Description:", self.desc_edit)
        form_layout.addRow(self.notify_checkbox)
        form_layout.addRow("Notify Minutes Before:", self.notify_minutes_edit)
        attach_layout = QHBoxLayout()
        attach_layout.addWidget(attach_btn)
        attach_layout.addWidget(remove_attach_btn)
        form_layout.addRow(QLabel("Attachments:"), attach_layout)
        form_layout.addRow(self.attach_list)
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        form_layout.addRow(btn_layout)
        self.notify_checkbox.toggled.connect(self.notify_minutes_edit.setEnabled)
        attach_btn.clicked.connect(self._on_add_attachment)
        remove_attach_btn.clicked.connect(self._on_remove_attachment)
        self.attach_list.itemDoubleClicked.connect(self._on_open_attachment)
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def _populate_fields(self, event_data):
        self.title_edit.setText(event_data.get('title', ''))
        self.desc_edit.setText(event_data.get('description', ''))
        date_str = event_data.get('date')
        if date_str:
            qdate = QDate.fromString(date_str, DATE_FORMAT)
            if qdate.isValid():
                self.date_edit.setDate(qdate)
        time_str = event_data.get('time')
        if time_str:
            qtime = QTime.fromString(time_str, TIME_FORMAT)
            if qtime.isValid():
               self.time_edit.setTime(qtime)
            else:
                try:
                    dt_time = datetime.datetime.strptime(time_str, DATETIME_PARSE_FORMAT).time()
                    self.time_edit.setTime(QTime(dt_time.hour, dt_time.minute))
                except ValueError: pass
        notify = event_data.get('notify', False)
        self.notify_checkbox.setChecked(notify)
        notify_minutes = event_data.get('notify_minutes', DEFAULT_NOTIFY_MINUTES)
        self.notify_minutes_edit.setText(str(notify_minutes))
        self.notify_minutes_edit.setEnabled(notify)
        self.attachments = []
        self.attach_list.clear()
        for attach_data in event_data.get('attachments', []):
            filename = attach_data.get('filename')
            data_b64 = attach_data.get('data')
            if filename and data_b64:
                self.attachments.append((filename, data_b64))
                self._add_attachment_item(filename, data_b64)

    def _on_add_attachment(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Attachment")
        if not file_path: return
        filename = os.path.basename(file_path)
        try:
            with open(file_path, 'rb') as f: data_bytes = f.read()
            data_b64 = base64.b64encode(data_bytes).decode('utf-8')
            self.attachments.append((filename, data_b64))
            self._add_attachment_item(filename, data_b64)
        except Exception as e: QMessageBox.warning(self, "Error", f"Failed to add attachment:\n{e}")

    def _add_attachment_item(self, filename, data_b64):
        item = QListWidgetItem(filename)
        item.setToolTip(filename)
        icon = QIcon.fromTheme("document-default")
        if filename.lower().endswith(IMAGE_EXTENSIONS):
            try:
                img_data = base64.b64decode(data_b64)
                pixmap = QPixmap()
                if pixmap.loadFromData(img_data): icon = QIcon(pixmap)
            except Exception as e: print(f"Warning: Could not load preview for {filename}: {e}", file=sys.stderr)
        item.setIcon(icon)
        self.attach_list.addItem(item)

    def _on_remove_attachment(self):
        selected_items = self.attach_list.selectedItems()
        if not selected_items: return
        current_row = self.attach_list.row(selected_items[0])
        if 0 <= current_row < len(self.attachments):
            self.attach_list.takeItem(current_row)
            del self.attachments[current_row]

    def _on_open_attachment(self, item):
        index = self.attach_list.row(item)
        if 0 <= index < len(self.attachments):
            filename, data_b64 = self.attachments[index]
            temp_path = None
            try:
                file_bytes = base64.b64decode(data_b64)
                temp_path = create_temporary_file(filename, file_bytes)
                if temp_path:
                    if not QDesktopServices.openUrl(QUrl.fromLocalFile(temp_path)):
                         QMessageBox.warning(self, "Error", f"Could not find an application to open:\n{filename}")
                else: QMessageBox.warning(self, "Error", f"Failed to create temporary file for:\n{filename}")
            except Exception as e: QMessageBox.warning(self, "Error", f"Failed to open attachment:\n{e}")

    def get_event_data(self):
        title = self.title_edit.text().strip()
        qdate = self.date_edit.date()
        date_str = qdate.toString(DATE_FORMAT)
        qtime = self.time_edit.time()
        time_str = ""
        if qtime != QTime(0, 0): time_str = qtime.toString(TIME_FORMAT)
        description = self.desc_edit.toPlainText().strip()
        notify = self.notify_checkbox.isChecked()
        try: notify_minutes = int(self.notify_minutes_edit.text().strip()) if self.notify_minutes_edit.text().strip() else DEFAULT_NOTIFY_MINUTES
        except ValueError: notify_minutes = DEFAULT_NOTIFY_MINUTES
        notify_time_iso: Optional[str] = None
        if notify:
            year, month, day = qdate.year(), qdate.month(), qdate.day()
            hour = qtime.hour() if time_str else 9
            minute = qtime.minute() if time_str else 0
            try:
                event_dt = datetime.datetime(year, month, day, hour, minute)
                notify_dt = event_dt - datetime.timedelta(minutes=notify_minutes)
                notify_time_iso = notify_dt.isoformat()
            except ValueError as e: print(f"Error calculating notify time: {e}", file=sys.stderr)
        attachment_dicts = [{"filename": name, "data": data} for name, data in self.attachments]
        return {
            "title": title, "date": date_str, "time": time_str, "description": description,
            "attachments": attachment_dicts, "notify": notify,
            "notify_minutes": notify_minutes, "notify_time": notify_time_iso, "id": None
        }


class SettingsDialog(QDialog):
    """Dialog for configuring application settings including style."""
    def __init__(self, parent=None, current_style=DEFAULT_STYLE, current_accent=DEFAULT_ACCENT_COLOR):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        if parent and parent.windowIcon():
            self.setWindowIcon(parent.windowIcon())
        else:
            if os.path.exists(ICON_PATH):
                self.setWindowIcon(QIcon(ICON_PATH))

        self._current_accent = QColor(current_accent)
        self._setup_ui(current_style, current_accent)

    # ... (rest of SettingsDialog methods) ...
    def _setup_ui(self, current_style, current_accent):
        layout = QFormLayout(self)
        self.style_combo = QComboBox()
        self.style_combo.addItems([
            STYLE_DEFAULT_LIGHT,
            STYLE_DEFAULT_DARK,
            STYLE_GRAPHITE_DARK,
            STYLE_OCEAN_BREEZE,
            STYLE_MINTY_LIGHT
        ])
        self.style_combo.setCurrentText(current_style)
        self.accent_color_btn = QPushButton("Select Accent Color")
        self.accent_color_lbl = QLabel(current_accent)
        self._update_accent_label_style(current_accent)
        layout.addRow("Style:", self.style_combo)
        layout.addRow("Accent Color:", self.accent_color_btn)
        layout.addRow("", self.accent_color_lbl)
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
        self.accent_color_btn.clicked.connect(self._select_accent_color)
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def _select_accent_color(self):
        color = QColorDialog.getColor(self._current_accent, self, "Select Accent Color")
        if color.isValid():
            self._current_accent = color
            hex_color = color.name()
            self.accent_color_lbl.setText(hex_color)
            self._update_accent_label_style(hex_color)

    def _get_contrasting_text_color(self, hex_color):
        try:
            color = QColor(hex_color)
            if not color.isValid(): return "black"
            luminance = (0.299 * color.redF() + 0.587 * color.greenF() + 0.114 * color.blueF())
            return "black" if luminance > 0.5 else "white"
        except Exception:
             return "black"

    def _update_accent_label_style(self, hex_color):
        text_color = self._get_contrasting_text_color(hex_color)
        self.accent_color_lbl.setStyleSheet(
            f"background-color: {hex_color}; color: {text_color}; border: 1px solid grey; padding: 2px;"
        )
        self.accent_color_lbl.setFixedWidth(100)

    def get_settings(self):
        return {
            "style_name": self.style_combo.currentText(),
            "accent_color": self._current_accent.name()
        }

class MainWindow(QMainWindow):
    """The main application window."""
    def __init__(self, data_manager: DataManager, notification_manager: NotificationManager):
        super().__init__()
        self.data_manager = data_manager
        self.notification_manager = notification_manager

        self._setup_ui()
        self._connect_signals()

        self.refresh_event_list()

        initial_style = self.data_manager.settings.get('style_name', DEFAULT_STYLE)
        initial_accent = self.data_manager.settings.get('accent_color', DEFAULT_ACCENT_COLOR)
        self.apply_theme(initial_style, initial_accent, save_settings=False)

    def _setup_ui(self):
        self.setWindowTitle("bToDo")
        self.resize(800, 600)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        else:
            print(f"Warning: Icon file not found at expected path: {ICON_PATH}", file=sys.stderr)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Header Section ---
        self.header_label = QLabel() # Create an empty QLabel
        if os.path.exists(BANNER_PATH):
            banner_pixmap = QPixmap(BANNER_PATH)
            # --- Optional: Scale the banner ---
            # If the banner is too large, scale it down. Adjust width/height as needed.
            # target_width = 300 # Example width
            # if banner_pixmap.width() > target_width:
            #     banner_pixmap = banner_pixmap.scaledToWidth(target_width, Qt.TransformationMode.SmoothTransformation)
            # Or scale by height:
            # target_height = 60 # Example height
            # if banner_pixmap.height() > target_height:
            #    banner_pixmap = banner_pixmap.scaledToHeight(target_height, Qt.TransformationMode.SmoothTransformation)
            # ------------------------------------
            self.header_label.setPixmap(banner_pixmap)
            self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.header_label.setStyleSheet("padding: 5px;") # Add some padding
        else:
            # Fallback to text if banner image is missing
            print(f"Warning: Banner image not found at {BANNER_PATH}. Falling back to text header.", file=sys.stderr)
            self.header_label.setText("bToDo") # Fallback text
            self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.header_label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")

        main_layout.addWidget(self.header_label) # Add the label (with image or text) to layout
        # --- End Header Section ---


        body_layout = QHBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        font = self.calendar.font()
        font.setPointSize(11)
        self.calendar.setFont(font)
        body_layout.addWidget(self.calendar, 2)

        self.event_list = QListWidget()
        self.event_list.setStyleSheet("font-size: 11pt;")
        body_layout.addWidget(self.event_list, 1)
        main_layout.addLayout(body_layout)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton(QIcon.fromTheme("list-add", QIcon(":/icons/add.png")), " Add Event")
        self.edit_btn = QPushButton(QIcon.fromTheme("document-edit", QIcon(":/icons/edit.png")), " Edit Event")
        self.del_btn = QPushButton(QIcon.fromTheme("list-remove", QIcon(":/icons/delete.png")), " Delete Event")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.del_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self._create_menu_bar()

    # ... (rest of MainWindow methods remain unchanged) ...
    def _create_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        self.backup_action = file_menu.addAction(QIcon.fromTheme("document-save-as"), "&Backup Data...")
        self.export_action = file_menu.addAction(QIcon.fromTheme("document-export"), "&Export to iCal...")
        file_menu.addSeparator()
        self.exit_action = file_menu.addAction(QIcon.fromTheme("application-exit"), "E&xit")
        settings_menu = menubar.addMenu("&Settings")
        self.pref_action = settings_menu.addAction(QIcon.fromTheme("preferences-system"), "&Preferences...")

    def _connect_signals(self):
        self.calendar.selectionChanged.connect(self.refresh_event_list)
        self.event_list.itemDoubleClicked.connect(self.edit_event)
        self.add_btn.clicked.connect(self.add_event)
        self.edit_btn.clicked.connect(self.edit_event)
        self.del_btn.clicked.connect(self.delete_event)
        self.backup_action.triggered.connect(self.backup_data)
        self.export_action.triggered.connect(self.export_to_ics)
        self.exit_action.triggered.connect(self.close)
        self.pref_action.triggered.connect(self.open_settings)

    def apply_theme(self, style_name: str, accent_color: str, save_settings: bool = True) -> None:
        app = QApplication.instance()
        if not app: return
        app.setStyle("Fusion")
        if style_name == STYLE_DEFAULT_DARK:
            app.setStyleSheet("")
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
            palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(55, 55, 55))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(50, 50, 50))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 220, 220))
            palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
            palette.setColor(QPalette.ColorRole.Button, QColor(60, 60, 60))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
            palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 80, 80))
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            accent = QColor(accent_color)
            palette.setColor(QPalette.ColorRole.Highlight, accent)
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
            disabled_text = QColor(120, 120, 120)
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled_text)
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled_text)
            app.setPalette(palette)
        elif style_name == STYLE_GRAPHITE_DARK:
            app.setStyleSheet(GRAPHITE_DARK_QSS.format(accent_color=accent_color))
        elif style_name == STYLE_OCEAN_BREEZE:
            app.setStyleSheet(OCEAN_BREEZE_QSS.format(accent_color=accent_color))
        elif style_name == STYLE_MINTY_LIGHT:
            app.setStyleSheet(MINTY_LIGHT_QSS.format(accent_color=accent_color))
        else:
            app.setStyleSheet("")
            app.setPalette(app.style().standardPalette())
            light_palette = app.palette()
            accent = QColor(accent_color)
            light_palette.setColor(QPalette.ColorRole.Highlight, accent)
            highlight_text_color = QColor("black") if accent.lightnessF() > 0.5 else QColor("white")
            light_palette.setColor(QPalette.ColorRole.HighlightedText, highlight_text_color)
            app.setPalette(light_palette)

        if save_settings:
            self.data_manager.settings['style_name'] = style_name
            self.data_manager.settings['accent_color'] = accent_color
            self.data_manager.settings['theme'] = 'dark' if style_name in [STYLE_DEFAULT_DARK, STYLE_GRAPHITE_DARK] else 'light'
            try:
                self.data_manager.save_to_file()
            except Exception as e:
                 QMessageBox.warning(self, "Settings Error", f"Could not save settings:\n{e}")

    def refresh_event_list(self):
        self.event_list.clear()
        selected_qdate = self.calendar.selectedDate()
        selected_date_str = selected_qdate.toString(DATE_FORMAT)
        events_on_date = []
        for event in self.data_manager.events:
            if event.get('date') == selected_date_str:
                events_on_date.append(event)
        def sort_key(evt):
            time_str = evt.get('time', '')
            if not time_str: return "00:00"
            try:
                return QTime.fromString(time_str, TIME_FORMAT).toString("HH:mm")
            except: return "99:99"
        events_on_date.sort(key=sort_key)
        for event in events_on_date:
            time_display = event.get('time', "All Day")
            list_text = f"{time_display} - {event.get('title', 'No Title')}"
            item = QListWidgetItem(list_text)
            item.setData(USER_ROLE, event.get('id'))
            item.setToolTip(event.get('description', 'No description.'))
            self.event_list.addItem(item)

    def add_event(self):
        dialog = EventDialog(self)
        selected_qdate = self.calendar.selectedDate()
        dialog.date_edit.setDate(selected_qdate)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_event = dialog.get_event_data()
            if not new_event.get('title'):
                QMessageBox.warning(self, "Missing Title", "Event title cannot be empty.")
                return
            new_event['id'] = str(uuid.uuid4())
            try:
                self.data_manager.add_event(new_event)
                self.refresh_event_list()
                if self.notification_manager: self.notification_manager.schedule_notifications()
            except Exception as e: QMessageBox.critical(self, "Error", f"Failed to add event:\n{e}")

    def edit_event(self):
        item = self.event_list.currentItem()
        if not item:
             QMessageBox.information(self, "Edit Event", "Please select an event to edit.")
             return
        event_id = item.data(USER_ROLE)
        if not event_id: return
        event_data = self.data_manager.get_event_by_id(event_id)
        if not event_data:
            QMessageBox.warning(self, "Error", f"Could not find event data for ID: {event_id}")
            self.refresh_event_list()
            return
        dialog = EventDialog(self, event_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_event = dialog.get_event_data()
            if not updated_event.get('title'):
                QMessageBox.warning(self, "Missing Title", "Event title cannot be empty.")
                return
            updated_event['id'] = event_id
            try:
                self.data_manager.update_event(event_id, updated_event)
                self.refresh_event_list()
                if self.notification_manager: self.notification_manager.schedule_notifications()
            except Exception as e: QMessageBox.critical(self, "Error", f"Failed to update event:\n{e}")

    def delete_event(self):
        item = self.event_list.currentItem()
        if not item:
            QMessageBox.information(self, "Delete Event", "Please select an event to delete.")
            return
        event_id = item.data(USER_ROLE)
        if not event_id: return
        event_title = "this event"
        ev_data = self.data_manager.get_event_by_id(event_id)
        if ev_data: event_title = ev_data.get('title', event_title)

        reply = QMessageBox.question(self, "Delete Event", f"Delete '{event_title}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                deleted = self.data_manager.delete_event(event_id)
                if deleted:
                    self.refresh_event_list()
                    if self.notification_manager: self.notification_manager.schedule_notifications()
                else: QMessageBox.warning(self, "Delete Error", f"Event ID {event_id} not found.")
            except Exception as e: QMessageBox.critical(self, "Error", f"Failed to delete event:\n{e}")

    def backup_data(self):
        default_filename = f"britton_calendar_backup_{datetime.date.today().strftime('%Y%m%d')}.enc"
        file_path, _ = QFileDialog.getSaveFileName(self, "Backup Calendar Data", default_filename,
                                                   "Encrypted Calendar Files (*.enc);;All Files (*)")
        if file_path:
            try:
                self.data_manager.backup_to_file(file_path)
                QMessageBox.information(self, "Backup Successful", f"Data backed up to:\n{file_path}")
            except Exception as e: QMessageBox.critical(self, "Backup Failed", f"Could not backup data:\n{e}")

    def export_to_ics(self):
        default_filename = f"britton_calendar_export_{datetime.date.today().strftime('%Y%m%d')}.ics"
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Calendar to iCal", default_filename,
                                                   "iCalendar Files (*.ics);;All Files (*)")
        if file_path:
            try:
                self.data_manager.export_to_ics(file_path)
                QMessageBox.information(self, "Export Successful", f"Data exported to:\n{file_path}")
            except NotImplementedError:
                 QMessageBox.warning(self, "Export Not Implemented", "iCalendar export failed (not fully implemented).")
            except Exception as e: QMessageBox.critical(self, "Export Failed", f"Could not export data to iCal:\n{e}")

    def open_settings(self):
        current_style = self.data_manager.settings.get('style_name', DEFAULT_STYLE)
        current_accent = self.data_manager.settings.get('accent_color', DEFAULT_ACCENT_COLOR)
        settings_dialog = SettingsDialog(self, current_style, current_accent)
        if settings_dialog.exec() == QDialog.DialogCode.Accepted:
            new_settings = settings_dialog.get_settings()
            self.apply_theme(new_settings['style_name'], new_settings['accent_color'], save_settings=True)

    def closeEvent(self, event: QCloseEvent):
        print("Closing bToDo.")
        event.accept()

# --- Main Execution Guard (for testing) ---
# (This part remains unchanged)
if __name__ == '__main__':
    class MockDataManager:
        def __init__(self):
            self.events = [{'id': '1', 'title': 'Test Event 1', 'date': QDate.currentDate().toString(DATE_FORMAT), 'time': '10:00 AM', 'description': 'Desc 1', 'notify': True, 'notify_minutes': 15, 'notify_time': None, 'attachments': []}]
            self.settings = {'style_name': DEFAULT_STYLE, 'accent_color': DEFAULT_ACCENT_COLOR}
        def get_event_by_id(self, event_id): return next((e for e in self.events if e['id'] == event_id), None)
        def add_event(self, event): event['id'] = str(uuid.uuid4()); self.events.append(event); print("Mock Add")
        def update_event(self, event_id, event_data): print("Mock Update"); return True
        def delete_event(self, event_id): print("Mock Delete"); return True
        def save_to_file(self): print("Mock Save Settings/Events")
        def backup_to_file(self, path): print(f"Mock Backup to {path}")
        def export_to_ics(self, path): print(f"Mock Export to {path}")

    class MockNotificationManager:
        def __init__(self, data_manager): pass
        def schedule_notifications(self): print("Mock Schedule Notifications")

    app = QApplication(sys.argv)
    mock_dm = MockDataManager()
    mock_nm = MockNotificationManager(mock_dm)
    main_win = MainWindow(mock_dm, mock_nm)
    main_win.show()
    sys.exit(app.exec())