# File: notification_manager.py
# bToDo - Created by Patrick Britton
# Date: 2025-04-28
# Updated: 2025-04-29 (Use britton.ico for notifications, removed temp icon creation)

import datetime
import os
import sys

# PySide6 imports
from PySide6.QtCore import QObject, QTimer

try:
    # Conditional import for Windows-specific notifications
    from winotify import Notification, audio
except ImportError:
    # Set Notification to None if winotify is not available
    Notification = None
    audio = None # Also set audio to None for consistency

# Define the path to the icon file (assumed to be in the same directory or accessible path)
ICON_PATH = "britton.ico" # <-- Uses direct path

class NotificationManager(QObject):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.notified_ids = set()
        self.timer = QTimer(self)
        # Set timer interval (30 seconds)
        self.timer.setInterval(30 * 1000)
        self.timer.timeout.connect(self.check_notifications)
        self.timer.start()
        # self.icon_path = self._create_temp_icon() # REMOVED

    # _create_temp_icon method REMOVED

    def check_notifications(self):
        # Only proceed if winotify was imported successfully
        if Notification is None:
            print("Warning: 'winotify' module not found. Notifications disabled.", file=sys.stderr)
            if self.timer.isActive():
                self.timer.stop()
            return

        # Check if the icon file actually exists
        icon_exists = os.path.exists(ICON_PATH)
        if not icon_exists:
            print(f"Warning: Notification icon '{ICON_PATH}' not found. Notifications may lack an icon.", file=sys.stderr)

        now = datetime.datetime.now()
        try:
            current_events = list(self.data_manager.events)
        except AttributeError:
            print("Warning: DataManager has no 'events' attribute yet or it's not accessible.", file=sys.stderr)
            return
        except Exception as e:
             print(f"Warning: Unexpected error accessing data_manager events: {e}", file=sys.stderr)
             return

        for ev in current_events:
            if not ev.get('notify', False):
                continue
            notify_time_str = ev.get('notify_time')
            if not notify_time_str:
                continue
            try:
                notify_dt = datetime.datetime.fromisoformat(notify_time_str)
            except (ValueError, TypeError) as e:
                print(f"Warning: Could not parse notify_time '{notify_time_str}': {e}", file=sys.stderr)
                continue
            except Exception as e:
                print(f"Warning: Error processing notify_time '{notify_time_str}': {e}", file=sys.stderr)
                continue

            event_id = ev.get('id')
            if event_id in self.notified_ids:
                continue

            if now >= notify_dt:
                if event_id:
                    self.notified_ids.add(event_id)
                else:
                    print(f"Warning: Event missing ID, cannot mark as notified: {ev.get('title')}", file=sys.stderr)

                title = f"Reminder: {ev.get('title', 'Calendar Event')}"
                msg_lines = []
                event_time_str = ev.get('time')
                date_str = ev.get('date', 'Unknown Date')
                time_part = f" at {event_time_str}" if event_time_str else ""
                msg_lines.append(f"Event on {date_str}{time_part}")
                desc = ev.get('description')
                if desc:
                    msg_lines.append(desc)
                message = "\n".join(msg_lines)

                try:
                    toast = Notification(app_id="BrittonCalendar",
                                         title=title,
                                         msg=message,
                                         # Use the direct path to britton.ico if it exists
                                         icon=ICON_PATH if icon_exists else "") # <-- Uses ICON_PATH
                    if audio:
                        toast.set_audio(audio.Mail, loop=False)
                    toast.show()
                except Exception as e:
                    print(f"Failed to show notification for '{title}': {e}", file=sys.stderr)

    def schedule_notifications(self):
        """
        Placeholder method called when events change.
        The current timer-based check_notifications handles polling.
        """
        print("NotificationManager: schedule_notifications called (potential future use).")
        pass