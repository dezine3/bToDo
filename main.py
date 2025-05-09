# File: main.py
# Description: Main entry point for the bToDo application.
#              Initializes the application, managers, and main window.

# bToDo - Created by Patrick Britton
# Original Date: 2025-04-28
# Cleaned up on: 2025-04-29

import sys
from typing import List  # For type hinting sys.argv

from PySide6.QtWidgets import QApplication

# Assuming these are in the same directory or project structure
from data_manager import DataManager
from notification_manager import NotificationManager
from main_window import MainWindow

def main() -> None:
    """
    Initializes and runs the bToDo application.

    Sets up the QApplication, DataManager, NotificationManager,
    and the MainWindow, then starts the Qt event loop.
    """
    # Create the core Qt application instance
    # Pass command line arguments (sys.argv) to the application
    app: QApplication = QApplication(sys.argv)

    # Set up the data manager (handles settings, events, encryption)
    data_manager: DataManager = DataManager()

    # Set up the notification manager (handles event notifications)
    notification_manager: NotificationManager = NotificationManager(data_manager)

    # Set up the main application window
    # Pass manager instances to the window for interaction
    window: MainWindow = MainWindow(data_manager, notification_manager)
    window.show()

    # Start the Qt event loop and exit the application when it finishes
    # sys.exit ensures the application's exit code is returned
    sys.exit(app.exec())

# Standard Python entry point guard
if __name__ == "__main__":
    main()